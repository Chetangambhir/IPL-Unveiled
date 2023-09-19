import requests
from bs4 import BeautifulSoup
import sqlite3
import csv

# Function to scrape data from a given URL and store it in the database
def scrape_and_store_data(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table element with the specified class
        table = soup.find('table', class_='ds-w-full ds-table ds-table-md ds-table-auto')

        team_name = soup.find_all('span', class_='ds-text-title-xs ds-font-bold ds-capitalize')

        if len(team_name) >= 2:
        # Get the second table (index 1)
            team_name = team_name[1]
        
            if team_name:
                team_name = team_name.text.strip()
            else:
                team_name = "Team Name Not Found"

        # Check if the table is found
        if table:
            # Initialize lists to store data from each column
            bowler_names = []
            overs_bowled = []
            maiden_oversbowled = []
            runs_given = []
            wickets_taken = []
            Economy = []
            dotballs = []

            # Extract and store the data from the rows
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                for row in rows:
                    # Extract and store the data from each column
                    cells = row.find_all('td')
                    if len(cells) >= 8:  # Ensure there are enough columns
                        bowler_names.append(cells[0].text.strip())
                        overs_bowled.append(cells[1].text.strip())
                        maiden_oversbowled.append(cells[2].text.strip())
                        runs_given.append(cells[3].text.strip())
                        
                        # Extract "W" (wickets taken) data
                        wickets_cell = cells[4].find('strong')
                        if wickets_cell:
                            wickets_taken.append(wickets_cell.text.strip())
                        else:
                            wickets_taken.append("0")  # If no wickets, add 0
                        
                        Economy.append(cells[5].text.strip())
                        dotballs.append(cells[6].text.strip())

            # Store the extracted data in an SQLite database
            try:
                # Connect to the database or create it if it doesn't exist
                conn = sqlite3.connect('fixtures.db')
                cursor = conn.cursor()

                # Create the "scoreboard" table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS firstinnings_bowlingscoreboardteam (
                        scoreboard_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        team_name TEXT,
                        bowler_names TEXT,
                        overs_bowled TEXT,
                        maiden_oversbowled TEXT,
                        runs_given TEXT,
                        wickets_taken TEXT,
                        Economy TEXT,
                        dotballs TEXT,
                        scoreboard_url TEXT,
                        FOREIGN KEY (scoreboard_url) REFERENCES matches(scoreboard_url)
                    )
                ''')

                # Insert data into the "scoreboard" table
                for i in range(len(bowler_names)):
                    cursor.execute('''
                        INSERT INTO firstinnings_bowlingscoreboardteam (team_name, bowler_names, overs_bowled, maiden_oversbowled, runs_given, wickets_taken, Economy, dotballs, scoreboard_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (team_name, bowler_names[i], overs_bowled[i], maiden_oversbowled[i], runs_given[i], wickets_taken[i], Economy[i], dotballs[i], url))

                # Commit changes and close the database connection
                conn.commit()
                conn.close()

                print(f"Data from URL {url} has been stored in the 'firstinnings_bowlingscoreboard.db' database.")

            except sqlite3.Error as e:
                print("SQLite error:", e)

        else:
            print(f"Table not found on the webpage at URL {url}.")

    else:
        print(f"Failed to retrieve the webpage at URL {url}.")

# Read input URLs from a CSV file
with open('urls.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        if len(row) > 0:
            url = row[0]
            scrape_and_store_data(url)
