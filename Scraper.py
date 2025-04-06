import requests
import datetime
import string
from bs4 import BeautifulSoup

def getTeamsPlayingToday():
    scrape_link = 'https://www.espn.com/nba/schedule'
    try:
        page = requests.get(scrape_link, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "*",
        })
        # Format the date as "Day, Month Date, Year"
        today = datetime.date.today().strftime("%A, %B %#d, %Y")
        teamsPlaying = []
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "html.parser")

            fullScheduleCard = soup.find("div", class_="Wrapper Card__Content overflow-visible")
            dateDivs = fullScheduleCard.find_all("div", class_="Table__Title")
            todaysGames = ""
            for date in dateDivs:
                dateText = date.get_text(strip=True).strip()
                if dateText == today:
                    todaysGames = date.find_next("table")
                    break

            if todaysGames:
                rows = todaysGames.find_all("tr", class_="Table__TR Table__TR--sm Table__even")
                for row in rows:
                    team_spans = row.find_all('span', class_='Table__Team')
                    for span in team_spans:
                        # Extract and append the text (team name) to the list
                        teamsPlaying.append(span.get_text(strip=True))

            print("Got teams playing")
            return teamsPlaying

    except Exception as e:
        print(e)


def espnScraper(nbaPlayer, tracker):
    playerLink = nbaPlayer.link
    scrape_link = 'https://www.espn.com/nba/player/gamelog/_/id/' + playerLink

    # try to access link
    try:
        page = requests.get(scrape_link, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "*",
            "Connection": "close"
        })
        # add request to tracker
        tracker.add_request()

        howManyGames: int = 5

        # when page status is 200 scrape info
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "html.parser")

            playerName = string.capwords(str(playerLink.strip().split('/', 1)[1].replace('-', ' ')))

            # Get Team name and city
            teamDiv = soup.find("div", class_="PlayerHeader__Team")
            teamItem = teamDiv.find('a', class_="AnchorLink")
            if teamItem:
                team = teamItem.text
                num_spaces = team.count(" ")
                words = team.split()
                teamCity = ' '.join(team.split()[:num_spaces])
                teamName = words[-1]
            else:
                teamName = "Free Agent"
                teamCity = 'N/A'

            # Update Team info if required
            if teamName != nbaPlayer.teamName:
                nbaPlayer.teamName = teamName

            if teamCity != nbaPlayer.teamCity:
                nbaPlayer.teamCity = teamCity

            # Get injury status
            if soup.find("span", class_="TextStatus"):
                injuredStatus = soup.find("span", class_="TextStatus").get_text()
            else:
                injuredStatus = "Out Of League"
                nbaPlayer.status = injuredStatus
                return nbaPlayer

            # nbaPlayer = NBAPlayer.NBAPlayer(playerName, teamName, teamCity, '', injuredStatus)
            nbaPlayer.status = injuredStatus

            print(playerName + ": " + injuredStatus)

            seasonDivs = soup.find_all("div", class_='Table__Title')
            for seasonDiv in seasonDivs:
                if "Regular Season" in seasonDiv.text:
                    regularSeasonDiv = seasonDiv.previous_element
                    monthLogs = regularSeasonDiv.find_all("table", class_="Table Table--align-right")

                    for monthLog in monthLogs:
                        gameLogs = monthLog.tbody.find_all("tr", class_=["Table__TR Table__TR--sm Table__even",
                                                                         "filled Table__TR Table__TR--sm Table__even"])

                        for gameLog in gameLogs:
                            if gameLog:
                                gameCounter = len(nbaPlayer.games['points'])
                                if gameCounter < howManyGames:
                                    # or gameCounter < len(gameLogs):
                                    statBoxes = gameLog.find_all("td")
                                    nbaPlayer.add_game_stats(int(statBoxes[16].text.strip()),
                                                             int(statBoxes[10].text.strip()),
                                                             int(statBoxes[11].text.strip()),
                                                             int(statBoxes[6].text.strip().split('-', 1)[0]))
                            else:
                                nbaPlayer.add_game_stats("No point data",
                                                         "No rebound data",
                                                         "No assist data",
                                                         "No 3PT data")

            page.close()
            return nbaPlayer
        else:
            print(page.status_code)
            page.close()

    except Exception as e:
        print(e)

