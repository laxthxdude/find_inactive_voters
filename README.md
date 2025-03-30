# Inactive Voters Finder

This Python script queries an existing SQLite database (`voters.db`) to identify voters who:
- Have not voted in the last 4 years.
- Were registered more than 4 years ago.
It exports the results to a CSV file (`inactive_voters.csv`) with details including the voter’s county name, county code, and last election date (if any).

## Features
- Queries the `voters` and `election_history` tables in `voters.db`.
- Maps `CountyCode` to county names using a predefined Minnesota county list.
- Outputs:
  - Console display of inactive voters.
  - CSV file (`inactive_voters.csv`) with columns: `VoterId`, `FirstName`, `MiddleName`, `LastName`, `City`, `State`, `ZipCode`, `RegistrationDate`, `DOBYear`, `County`, `CountyCode`, `LastElectionDate`.
- Includes debugging logs for performance tracking and troubleshooting.
- Processes large datasets efficiently with batch fetching.

## Prerequisites
- Python 3 installed (see installation steps below if needed).
- An existing `voters.db` SQLite database with:
  - `voters` table: Includes `VoterId`, `FirstName`, `MiddleName`, `LastName`, `City`, `State`, `ZipCode`, `RegistrationDate`, `DOBYear`, `CountyCode`, etc.
  - `election_history` table: Includes `VoterId`, `ElectionDate`, etc.
- Required Python libraries: `sqlite3`, `csv`, `datetime`, `time`, `logging` (all standard library, no external dependencies).

## Installation

### Step 1: Install Python
If Python isn’t installed, follow these steps:

#### macOS
1. Open Terminal (Applications > Utilities > Terminal).
2. Check: `python3 --version`
   - If installed (e.g., `Python 3.9.6`), proceed to Usage. Otherwise:
3. Install Homebrew (if not present): `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
4. Install Python: `brew install python`
5. Verify: `python3 --version`

#### Windows
1. Download Python from [python.org/downloads](https://www.python.org/downloads/) (e.g., Python 3.11.x).
2. Run the installer, check "Add Python to PATH," and select "Install Now."
3. Verify: Open Command Prompt (cmd) and run `python --version`.

#### Linux (Ubuntu/Debian)
1. Open a terminal.
2. Update: `sudo apt update`
3. Install: `sudo apt install python3`
4. Verify: `python3 --version`

### Step 2: Dependencies
- No external libraries are required; all used modules (`sqlite3`, `csv`, `datetime`, `time`, `logging`) are part of Python’s standard library.

## Usage

1. **Prepare the Database**:
   - Ensure `voters.db` is in the same directory as the script or update the `db_name` parameter in the script if it’s elsewhere.
   - The database should have `voters` and `election_history` tables populated with data.

2. **Run the Script**:
   - Save the script as `find_inactive_voters.py`.
   - Open a terminal in the script’s directory.
   - Execute: `python3 find_inactive_voters.py`
   - The script uses defaults: `voters.db` for input, `inactive_voters.csv` for output.

3. **Output**:
   - **Console**: Displays inactive voters with columns: `VoterId`, `FirstName`, `MiddleName`, `LastName`, `City`, `State`, `ZipCode`, `RegistrationDate`, `DOBYear`, `County`, `CountyCode`, `LastElectionDate`. Includes debug logs (e.g., query time, fetch progress).
   - **CSV**: Creates `inactive_voters.csv` with the same columns.
   - Example console output:
     ```
     2025-03-30 12:00:00,123 - INFO - Starting inactive voter search...
     2025-03-30 12:00:00,125 - INFO - Connected to database voters.db in 0.02 seconds
     ...
     Inactive Voters Found:
     VoterId | FirstName | MiddleName | LastName | City | State | ZipCode | RegistrationDate | DOBYear | County | CountyCode | LastElectionDate
     12345 | John | A | Doe | Houston | MN | 55943 | 2019-05-15 | 1980 | HOUSTON | 28 | 2020-11-03
     ...
     2025-03-30 12:00:00,137 - INFO - Exported 1 inactive voters to inactive_voters.csv in 0.02 seconds
     ```

## Example CSV Output (`inactive_voters.csv`)
```
VoterId,FirstName,MiddleName,LastName,City,State,ZipCode,RegistrationDate,DOBYear,County,CountyCode,LastElectionDate
12345,John,A,Doe,Houston,MN,55943,2019-05-15,1980,HOUSTON,28,2020-11-03
```

## Notes
- **Performance**: Optimized for large datasets with batch fetching (1000 rows at a time) and a temporary table for last election dates. Ensure indexes exist on `election_history(VoterId, ElectionDate)` for best performance.
- **County Mapping**: Uses a static list of Minnesota county codes (e.g., `"28"` for `"HOUSTON"`). Unknown codes map to `"Unknown"`.
- **Debugging**: Logs timing and progress (e.g., every 1000 rows fetched). Reduce verbosity by changing `level=logging.DEBUG` to `level=logging.INFO`.
- **Date Cutoff**: Calculated automatically from the execution of script.

## Troubleshooting
- **Script Hangs**: Check logs for where it stops (e.g., "Executing query..." or "Fetching results..."). Large datasets may require more memory or query optimization.
- **No Results**: Verify `voters.db` has data and the `CountyCode` matches the mapping (e.g., `"28"`, not `28`).
- **Errors**: Logs detail connection, query, or file issues. Ensure `voters.db` is not locked or corrupted.

## Contributing
Fork this repository, submit issues, or create pull requests with enhancements (e.g., dynamic date cutoffs, additional fields).

## License
This project is unlicensed and provided as-is for personal use. No warranty is implied.
