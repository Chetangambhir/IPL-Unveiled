import requests
from bs4 import BeautifulSoup
import sqlite3

# Function to scrape match data from a given match URL and store it in the SQLite database
def scrape_and_store_match_data(match_url, sqlite_cursor):
    # Send an HTTP GET request to the URL
    response = requests.get(match_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the main div with the class 'ds-grow ds-px-0'
        main_div = soup.find('div', class_='ds-flex ds-space-x-5')

        # Find all divs with the specified class for dates
        date_divs = main_div.find_all('div', class_='ds-text-compact-xs ds-font-bold ds-w-24')

        # Find all divs with the specified class containing match numbers and places
        match_info_divs = main_div.find_all('div', class_='ds-text-tight-s ds-font-regular ds-truncate ds-text-typo-mid3')

        # Find all divs with the specified class for team 1 and team 2 info
        team1_info_divs = main_div.find_all('p', class_='ds-text-tight-m ds-font-bold ds-capitalize ds-truncate')[::2]  # Every second div
        team2_info_divs = main_div.find_all('p', class_='ds-text-tight-m ds-font-bold ds-capitalize ds-truncate')[1::2]  # Every second div starting from the second
        team1_info_score = main_div.find_all('div', class_='ds-text-compact-s ds-text-typo ds-text-right ds-whitespace-nowrap')[::2]
        team2_info_score = main_div.find_all('div', class_='ds-text-compact-s ds-text-typo ds-text-right ds-whitespace-nowrap')[1::2]

        # Find all p elements with the specified class for match results
        match_result_p_elements = main_div.find_all('p', class_='ds-text-tight-s ds-font-regular ds-line-clamp-2 ds-text-typo')

        # Find scoreboard URLs
        scoreboard_urls = []

        # Iterate through the divs and extract the scoreboard URLs
        for div in main_div.find_all('div', class_='ds-grow ds-px-4 ds-border-r ds-border-line-default-translucent'):
            link = div.find('a', class_='ds-no-tap-higlight')
            if link:
                url = 'https://www.espncricinfo.com' + link['href']
                scoreboard_urls.append(url)

        # Initialize lists to store the extracted data
        dates = []
        match_numbers = []
        places = []
        team1_names = []
        team1_scores = []
        team2_names = []
        team2_scores = []
        match_results = []

        # Initialize variables to keep track of whether "Match abandoned" was encountered
        match_abandoned = False
        team1_shifted = 0
        team2_shifted = 0

        # Extract data from the elements
        for i in range(len(date_divs)):
            date = date_divs[i].text.strip()

            # If the date is empty or null, copy it from the previous row
            if not date:
                date = dates[i - 1]

            dates.append(date)

            # Extract match number and place from the match_info_divs
            match_info_text = match_info_divs[i].text.strip()
            match_info_parts = match_info_text.split('•')
            if len(match_info_parts) == 2:
                match_number = match_info_parts[0].strip()
                place = match_info_parts[1].strip()
            else:
                match_number = ""
                place = match_info_text.strip()

            match_numbers.append(match_number)
            places.append(place)

            # Extract match result
            match_result = match_result_p_elements[i].text.strip()

            # Extract team 1 name and score
            team1_name = team1_info_divs[i].text.strip()
            # Check if team1_score has enough elements, if not set it to an empty string
            if "Match abandoned" in match_result:
                if team1_shifted < 1:
                    team1_score = ""
                    team1_shifted += 1
                else:
                    team1_score = team1_info_score[i - team1_shifted].find('strong').text.strip()
            else:
                # Check if team1_score has enough elements, if not set it to an empty string
                if len(team1_info_score) > i - team1_shifted:
                    team1_score = team1_info_score[i - team1_shifted].find('strong').text.strip()
                else:
                    team1_score = ""

            # Extract team 2 name and score
            team2_name = team2_info_divs[i].text.strip()
            if "Match abandoned" in match_result:
                if team2_shifted < 1:
                    team2_score = ""
                    team2_shifted += 1
                else:
                    team2_score = team2_info_score[i - team2_shifted].find('strong').text.strip()
            else:
                # Check if team2_score has enough elements, if not set it to an empty string
                if len(team2_info_score) > i - team2_shifted:
                    team2_score = team2_info_score[i - team2_shifted].find('strong').text.strip()
                else:
                    team2_score = ""

            # Append the data to the respective lists
            team1_names.append(team1_name)
            team1_scores.append(team1_score)
            team2_names.append(team2_name)
            team2_scores.append(team2_score)
            match_results.append(match_result)

        # Insert data into the table
        for i in range(len(dates)):
            sqlite_cursor.execute("INSERT INTO matches (date, match_number, place, team1_name, team1_score, team2_name, team2_score, match_result, scoreboard_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                  (dates[i], match_numbers[i], places[i], team1_names[i],
                                   team1_scores[i], team2_names[i], team2_scores[i], match_results[i], scoreboard_urls[i]))

        print(f"Data from {match_url} has been stored in the SQLite database.")

    else:
        print(f"Failed to retrieve the web page from {match_url}. Status code:", response.status_code)

# Define a list of URLs
urls = [
    "https://www.espncricinfo.com/series/indian-premier-league-2007-08-313494/match-schedule-fixtures-and-results",
    "https://www.espncricinfo.com/series/indian-premier-league-2009-374163/match-schedule-fixtures-and-results",
    "https://www.espncricinfo.com/series/indian-premier-league-2009-10-418064/match-schedule-fixtures-and-results",
    "https://www.espncricinfo.com/series/indian-premier-league-2011-466304/match-schedule-fixtures-and-results",
    "https://www.espncricinfo.com/series/indian-premier-league-2012-520932/match-schedule-fixtures-and-results",
    "https://www.espncricinfo.com/series/indian-premier-league-2013-586733/match-schedule-fixtures-and-results",
    "https://www.espncricinfo.com/series/pepsi-indian-premier-league-2014-695871/match-schedule-fixtures-and-results",
    "https://www.espncricinfo.com/series/pepsi-indian-premier-league-2015-791129/match-schedule-fixtures-and-results",
    "https://www.espncricinfo.com/series/ipl-2016-968923/match-schedule-fixtures-and-results",
    "https://www.espncricinfo.com/series/ipl-2017-1078425/match-schedule-fixtures-and-results",
    "https://www.espncricinfo.com/series/ipl-2018-1131611/match-schedule-fixtures-and-results",
    "https://www.espncricinfo.com/series/ipl-2019-1165643/match-schedule-fixtures-and-results",
    "https://www.espncricinfo.com/series/ipl-2020-21-1210595/match-schedule-fixtures-and-results",
    "https://www.espncricinfo.com/series/ipl-2021-1249214/match-schedule-fixtures-and-results",
    "https://www.espncricinfo.com/series/indian-premier-league-2022-1298423/match-schedule-fixtures-and-results",
    "https://www.espncricinfo.com/series/indian-premier-league-2023-1345038/match-schedule-fixtures-and-results",
]

# Create an SQLite database and a connection
conn = sqlite3.connect('fixtures.db')
cursor = conn.cursor()

# Create a new table to store the data
cursor.execute('''CREATE TABLE IF NOT EXISTS matches
                  (date TEXT, match_number TEXT, place TEXT, team1_name TEXT,
                   team1_score TEXT, team2_name TEXT, team2_score TEXT, match_result TEXT, scoreboard_url TEXT PRIMARY KEY)''')

# Loop through each URL and scrape match data
for url in urls:
    # Call the function to scrape match data and store it in the SQLite database
    scrape_and_store_match_data(url, cursor)

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"Match data from {len(urls)} webpages have been saved to the 'fixtures.db' database.")
