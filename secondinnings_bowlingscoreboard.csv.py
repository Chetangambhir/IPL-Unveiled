import requests
from bs4 import BeautifulSoup
import sqlite3
import csv

def scrape_and_store_data(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table element with the specified class
        tables = soup.find_all('table', class_='ds-w-full ds-table ds-table-md ds-table-auto')

        # Find the team name based on the provided HTML structure
        team_name = soup.find('span', class_='ds-text-title-xs ds-font-bold ds-capitalize')
        
        if team_name:
            team_name = team_name.text.strip()
        else:
            team_name = "Team Name Not Found"

        # Check if at least two tables are found
        if len(tables) >= 2:
            # Get the second table (index 1)
            table = tables[1]

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

                            # Check if there are enough columns for Economy and dotballs
                            if len(cells) >= 7:
                                Economy.append(cells[5].text.strip())
                                dotballs.append(cells[6].text.strip())
                            else:
                                Economy.append("N/A")
                                dotballs.append("N/A")

                # Store the extracted data in an SQLite database
                try:
                    # Connect to the database or create it if it doesn't exist
                    conn = sqlite3.connect('fixtures.db')
                    cursor = conn.cursor()

                    # Create the "scoreboard" table if it doesn't exist
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS secondinnings_bowlingscoreboardteam (
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
                            INSERT INTO secondinnings_bowlingscoreboardteam (team_name, bowler_names, overs_bowled, maiden_oversbowled, runs_given, wickets_taken, Economy, dotballs, scoreboard_url)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (team_name, bowler_names[i], overs_bowled[i], maiden_oversbowled[i], runs_given[i], wickets_taken[i], Economy[i], dotballs[i], url))

                    # Commit changes and close the database connection
                    conn.commit()
                    conn.close()

                    print("Data has been stored in the 'secondinnings_bowlingscoreboard.db' database.")

                except sqlite3.Error as e:
                    print("SQLite error:", e)

            else:
                print("Table not found on the webpage.")

        else:
            print("Not enough tables found on the webpage.")

    else:
        print("Failed to retrieve the webpage.")


# Read input URLs from a CSV file
with open('urls.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        if len(row) > 0:
            url = row[0]
            scrape_and_store_data(url)
