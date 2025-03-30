import sqlite3
import csv
from datetime import datetime, timedelta
import time
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# County code to name mapping
COUNTY_MAPPING = {
    "1": "AITKIN", "2": "ANOKA", "3": "BECKER", "4": "BELTRAMI", "5": "BENTON", "6": "BIG STONE",
    "7": "BLUE EARTH", "8": "BROWN", "9": "CARLTON", "10": "CARVER", "11": "CASS", "12": "CHIPPEWA",
    "13": "CHISAGO", "14": "CLAY", "15": "CLEARWATER", "16": "COOK", "17": "COTTONWOOD", "18": "CROW WING",
    "19": "DAKOTA", "20": "DODGE", "21": "DOUGLAS", "22": "FARIBAULT", "23": "FILLMORE", "24": "FREEBORN",
    "25": "GOODHUE", "26": "GRANT", "27": "HENNEPIN", "28": "HOUSTON", "29": "HUBBARD", "30": "ISANTI",
    "31": "ITASCA", "32": "JACKSON", "33": "KANABEC", "34": "KANDIYOHI", "35": "KITTSON", "36": "KOOCHICHING",
    "37": "LAC QUI PARLE", "38": "LAKE", "39": "LAKE OF THE WOODS", "40": "LE SUEUR", "41": "LINCOLN",
    "42": "LYON", "43": "MCLEOD", "44": "MAHNOMEN", "45": "MARSHALL", "46": "MARTIN", "47": "MEEKER",
    "48": "MILLE LACS", "49": "MORRISON", "50": "MOWER", "51": "MURRAY", "52": "NICOLLET", "53": "NOBLES",
    "54": "NORMAN", "55": "OLMSTED", "56": "OTTER TAIL", "57": "PENNINGTON", "58": "PINE", "59": "PIPESTONE",
    "60": "POLK", "61": "POPE", "62": "RAMSEY", "63": "RED LAKE", "64": "REDWOOD", "65": "RENVILLE",
    "66": "RICE", "67": "ROCK", "68": "ROSEAU", "69": "ST. LOUIS", "70": "SCOTT", "71": "SHERBURNE",
    "72": "SIBLEY", "73": "STEARNS", "74": "STEELE", "75": "STEVENS", "76": "SWIFT", "77": "TODD",
    "78": "TRAVERSE", "79": "WABASHA", "80": "WADENA", "81": "WASECA", "82": "WASHINGTON", "83": "WATONWAN",
    "84": "WILKIN", "85": "WINONA", "86": "WRIGHT", "87": "YELLOW MEDICINE"
}

def find_inactive_voters(db_name="voters.db", output_csv="inactive_voters.csv", batch_size=1000):
    """Query voters.db for inactive voters and export to CSV with county mapping."""
    logging.info("Starting inactive voter search...")

    # Calculate the date 4 years ago from today
    today = datetime.now()
    four_years_ago = today - timedelta(days=4 * 365)  # Approximate 4 years, ignoring leap years
    cutoff_date = four_years_ago.strftime('%Y-%m-%d')
    logging.info(f"Using cutoff date: {cutoff_date} (4 years prior to {today.strftime('%Y-%m-%d')})")

    # Connect to the database
    start_time = time.time()
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        logging.info(f"Connected to database {db_name} in {time.time() - start_time:.2f} seconds")
    except sqlite3.Error as e:
        logging.error(f"Failed to connect to database: {e}")
        return

    # Create a temporary table for last election dates
    temp_start_time = time.time()
    try:
        cursor.execute("DROP TABLE IF EXISTS temp_last_election;")
        cursor.execute("""
        CREATE TEMPORARY TABLE temp_last_election AS
        SELECT VoterId, MAX(ElectionDate) AS LastElectionDate
        FROM election_history
        GROUP BY VoterId;
        """)
        conn.commit()
        logging.info(f"Created temporary table temp_last_election in {time.time() - temp_start_time:.2f} seconds")
    except sqlite3.Error as e:
        logging.error(f"Failed to create temporary table: {e}")
        conn.close()
        return

    # Query for inactive voters using dynamic cutoff date
    query_start_time = time.time()
    query = f"""
    SELECT 
        v.VoterId,
        v.FirstName,
        v.MiddleName,
        v.LastName,
        v.City,
        v.State,
        v.ZipCode,
        v.RegistrationDate,
        v.DOBYear,
        v.CountyCode,
        tle.LastElectionDate
    FROM 
        voters v
    LEFT JOIN 
        election_history eh ON v.VoterId = eh.VoterId AND eh.ElectionDate >= '{cutoff_date}'
    LEFT JOIN 
        temp_last_election tle ON v.VoterId = tle.VoterId
    WHERE 
        v.RegistrationDate < '{cutoff_date}'
        AND eh.VoterId IS NULL;
    """
    try:
        logging.debug("Executing query...")
        cursor.execute(query)
        logging.info(f"Query executed in {time.time() - query_start_time:.2f} seconds")
    except sqlite3.Error as e:
        logging.error(f"Query failed: {e}")
        conn.close()
        return

    # Fetch and process results incrementally
    fetch_start_time = time.time()
    results = []
    total_rows = 0
    logging.debug("Fetching results incrementally...")
    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        for i, row in enumerate(batch, 1):
            voter_id, first_name, middle_name, last_name, city, state, zipcode, reg_date, dob_year, county_code, last_election = row
            county_name = COUNTY_MAPPING.get(str(county_code), "Unknown")
            results.append((voter_id, first_name, middle_name, last_name, city, state, zipcode, reg_date, dob_year, county_name, county_code, last_election))
            total_rows += 1
            if total_rows % 1000 == 0:
                logging.debug(f"Fetched and processed {total_rows} rows so far...")
    logging.info(f"Fetched and processed {total_rows} rows in {time.time() - fetch_start_time:.2f} seconds")

    # Print results to console
    print_start_time = time.time()
    print(f"\nInactive Voters Found (No votes since {cutoff_date}, Registered before {cutoff_date}):")
    print("VoterId | FirstName | MiddleName | LastName | City | State | ZipCode | RegistrationDate | DOBYear | County | CountyCode | LastElectionDate")
    for row in results:
        print(" | ".join(str(col) if col is not None else "" for col in row))
    logging.info(f"Printed {len(results)} results to console in {time.time() - print_start_time:.2f} seconds")

    # Export results to inactive_voters.csv
    csv_start_time = time.time()
    headers = [
        "VoterId", "FirstName", "MiddleName", "LastName", "City", "State", "ZipCode",
        "RegistrationDate", "DOBYear", "County", "CountyCode", "LastElectionDate"
    ]
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(results)
        logging.info(f"Exported {len(results)} inactive voters to {output_csv} in {time.time() - csv_start_time:.2f} seconds")
    except IOError as e:
        logging.error(f"Failed to write to CSV: {e}")

    # Close connection
    conn.close()
    logging.info(f"Total execution time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    find_inactive_voters()