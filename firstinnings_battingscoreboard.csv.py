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
        table = soup.find('table', class_='ci-scorecard-table')

        # Find the team name based on the provided HTML structure
        team_name = soup.find('span', class_='ds-text-title-xs ds-font-bold ds-capitalize')
        
        if team_name:
            team_name = team_name.text.strip()
        else:
            team_name = "Team Name Not Found"

        # Check if the table is found
        if table:
            # Initialize lists to store data from each column
            batsman_names = []
            wickets_taken = []
            runs_scored = []
            balls_faced = []
            fours = []
            sixes = []
            strike_rates = []

            # Extract and store the data from the rows
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                for row in rows:
                    # Extract and store the data from each column
                    cells = row.find_all('td')
                    if len(cells) >= 8:  # Ensure there are enough columns
                        batsman_names.append(cells[0].text.strip())
                        wickets_taken.append(cells[1].text.strip())
                        runs_scored.append(cells[2].text.strip())
                        balls_faced.append(cells[3].text.strip())
                        fours.append(cells[5].text.strip())
                        sixes.append(cells[6].text.strip())
                        strike_rates.append(cells[7].text.strip())

            # Store the extracted data in the 'fixtures.db' database
            try:
                # Connect to the 'fixtures.db' database
                conn = sqlite3.connect('fixtures.db')
                cursor = conn.cursor()

                # Create the 'firstinnings_scoreboard' table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS firstinnings_battingscoreboardteam (
                        team_name TEXT,
                        batsman_name TEXT,
                        wickets_taken TEXT,
                        runs_scored TEXT,
                        balls_faced TEXT,
                        fours TEXT,
                        sixes TEXT,
                        strike_rate TEXT,
                        scoreboard_url TEXT,
                        FOREIGN KEY (scoreboard_url) REFERENCES matches(scoreboard_url)
                    )
                ''')

                # Insert data into the 'firstinnings_scoreboard' table
                for i in range(len(batsman_names)):
                    cursor.execute('''
                        INSERT INTO firstinnings_battingscoreboardteam(team_name, batsman_name, wickets_taken, runs_scored, balls_faced, fours, sixes, strike_rate, scoreboard_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (team_name, batsman_names[i], wickets_taken[i], runs_scored[i], balls_faced[i], fours[i], sixes[i], strike_rates[i], url))

                # Commit changes and close the database connection
                conn.commit()
                conn.close()

                print(f"Data from URL {url} has been stored in the 'fixtures.db' database.")

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
