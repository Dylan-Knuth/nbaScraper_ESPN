import datetime
import time
import pyodbc
import ExcelFile
import PlayerTrendEmail
import NBAPlayer
import RequestTracker
import Scraper
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def get_NBA_Players():
    # Set up Selenium WebDriver (make sure to specify the path to your WebDriver)
    driver = webdriver.Chrome(executable_path='path/to/chromedriver')

    # Navigate to the ESPN NBA stats page
    url = "https://www.espn.com/nba/stats/player/_/table/general/sort/avgMinutes/dir/desc/"
    driver.get(url)

    # Click "Show More" until we have at least 200 rows
    while True:
        try:
            # Wait for the "Show More" button to be clickable and click it
            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Show More')]"))
            )
            show_more_button.click()

            # Wait for new rows to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table/tbody/tr"))
            )

            # Check the number of rows in the table
            rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
            if len(rows) >= 200:
                break

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    # Scrape the data from the table
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table')
    data = []

    # Extract header information
    headers = [header.text for header in table.find_all('th')]
    data.append(headers)

    # Extract row data
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        data.append([col.text.strip() for col in cols])

    # Convert to DataFrame and save to CSV or display
    df = pd.DataFrame(data[1:], columns=data[0])
    print(df)

    # Close the driver
    driver.quit()


def get_NBAPlayers_DB(teamsPlaying):
    cnxn = pyodbc.connect(r'Driver=SQL Server;Server=.\SQLEXPRESS;Database=espnScraper;Trusted_Connection=yes;')
    cursor = cnxn.cursor()
    placeholders = tuple(teamsPlaying)

    cursor.execute("SELECT * FROM [espnScraper].[dbo].[NBAPlayers] WHERE teamCity in {}".format(placeholders))
    rows = cursor.fetchall()
    result_list = [list(row) for row in rows]
    cnxn.close()
    return result_list


def main():
    tracker = RequestTracker.RequestTracker()
    fileData = []
    playerData = []

    # get teams playing
    teamsPlaying = Scraper.getTeamsPlayingToday()

    # get players from DB that are playing today
    ESPNPlayers = get_NBAPlayers_DB(teamsPlaying)

    d1 = datetime.datetime.now().strftime('%x').replace('/', '.')
    fileName = './DataSheets/ESPN_PlayerData_' + d1 + '.xlsx'

    print('Processing...........')
    if ESPNPlayers:
        for espnPlayer in ESPNPlayers:
            # parse players name from link
            playerData = []

            nbaPlayer = NBAPlayer.NBAPlayer(espnPlayer[0].strip(), espnPlayer[1].strip(),
                                            espnPlayer[4].strip(), espnPlayer[2].strip(), '?')

            nbaPlayer = Scraper.espnScraper(nbaPlayer, tracker)

            player = nbaPlayer
            print(f"Requests in the last minute: {tracker.get_requests_per_minute()}")
            if tracker.get_requests_per_minute() >= 17:
                time.sleep(10)
            if player:
                if len(player.games['points']) > 0:
                    if player.status != 'OUT':
                        allBenchmarks = player.get_all_benchmarks()
                        # player.print_benchmarks()
                        playerData.append(player.name)
                        playerData.append(player.teamCity + " " + player.teamName)

                        for stat, benchmarks in allBenchmarks.items():
                            for threshold, frequency in benchmarks.items():
                                playerData.append(frequency)

                        fileData.append(playerData)

                else:
                    print(f"{player.name} has no stats. {player.status}")
            else:
                print(f"Issue getting info for {espnPlayer}")
            time.sleep(3)

            # Add data to CSV file
    if fileData:
        ExcelFile.write_to_excel(fileData, fileName)
        print("File saved to " + fileName)
        isEmail = input("Do you want to email the file?? /nEnter 'Y' or 'N'")
        if isEmail.upper() == "Y":
            creds = PlayerTrendEmail.get_google_creds()
            PlayerTrendEmail.send_player_trends_email(creds, fileName)

    else:
        print("Issue with fileData. Cannot write to Excel")


if __name__ == "__main__":
    main()
