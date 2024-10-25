import requests
import pandas as pd
from bs4 import BeautifulSoup
import datetime
import string
import time

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.utils import get_column_letter
from pyarrow import null

import PlayerTrendEmail
import NBAPlayer
import RequestTracker


def getTeamsPlayingToday():
    scrape_link = 'https://www.espn.com/nba/schedule'
    try:
        page = requests.get(scrape_link, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "*",
        })
        # Format the date as "Day, Month Date, Year"
        today = datetime.date.today().strftime("%A, %B %d, %Y")
        teamsPlaying = []
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "html.parser")

            fullScheduleCard = soup.find("div", class_="Wrapper Card__Content overflow-visible")
            dateDivs = fullScheduleCard.find_all("div", class_="Table__Title")
            todaysGames = ""
            for date in dateDivs:
                if date.get_text(strip=True) == today:
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


def espnScraper(playerLink, tracker):
    scrape_link = 'https://www.espn.com/nba/player/gamelog/_/id/' + playerLink
    try:
        page = requests.get(scrape_link, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "*",
            "Connection": "close"
        })
        tracker.add_request()
        howManyGames: int = 5

        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "html.parser")
            playerName = string.capwords(str(playerLink.strip().split('/', 1)[1].replace('-', ' ')))
            teamDiv = soup.find("div", class_="PlayerHeader__Team")
            teamItem = teamDiv.find('a', class_="AnchorLink")

            if teamItem:
                teamName = teamItem.text
            else:
                teamName = "Free Agent"

            if soup.find("span", class_="TextStatus"):
                injuredStatus = soup.find("span", class_="TextStatus").get_text()
            else:
                injuredStatus = "Out Of League"
                return NBAPlayer.NBAPlayer(playerName, teamName, injuredStatus)

            nbaPlayer = NBAPlayer.NBAPlayer(playerName, teamName, injuredStatus)

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
                                if gameCounter < howManyGames or gameCounter < len(gameLogs):
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


def write_to_excel(fileData, fileName):
    dataColumns = [
        "Player", "Team",
        "15+ Points", "20+ Points", "25+ Points", "30+ Points",
        "4+ Reb", "6+ Reb", "8+ Reb", "10+ Reb", "12+ Reb",
        "4+ Assist", "6+ Assist", "8+ Assist", "10+ Assist", "12+ Assist",
        "2+ 3PM", "3+ 3PM", "4+ 3PM", "5+ 3PM"
    ]

    df = pd.DataFrame(fileData, columns=dataColumns)

    with (pd.ExcelWriter(fileName) as writer):
        df.to_excel(writer, sheet_name='espnPlayerData', index=False)

    format_excel(fileName)


def format_excel(fileName):
    # formattedfileName = './DataSheets/ESPN_PlayerData_' + d1 + '_FORMATTED.xlsx'
    workbook = load_workbook(fileName)
    sheet = workbook.active

    # Read the data from the sheet
    data = []
    for row in sheet.iter_rows(values_only=True):
        data.append(row)

    # Create a new workbook for output
    output_workbook = Workbook()
    output_sheet = output_workbook.active

    # Write the data to the new sheet
    for row in data:
        output_sheet.append(row)

    # Determine the range for conditional formatting
    last_row = output_sheet.max_row

    if last_row < 2:
        print("Not enough rows for conditional formatting.")
    else:
        for column in output_sheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            output_sheet.column_dimensions[get_column_letter(column[0].column)].width = adjusted_width

        formatting_range = f'C2:T{last_row}'
        color_scale = ColorScaleRule(start_type='percentile', start_value='0', start_color="F8696B",
                                     mid_type='percentile', mid_value='50', mid_color="FFEB84",
                                     end_type='percentile', end_value='100', end_color="63BE7B")

        output_sheet.conditional_formatting.add(formatting_range, color_scale)

    # Save the new workbook
    output_workbook.save(fileName)


def main():
    ESPNPlayers = [
        # Atlanta
        '4277905/trae-young', '3907497/dejounte-murray', '3037789/bogdan-bogdanovic', '4701230/jalen-johnson',
        '4065732/deandre-hunter', '4397136/saddiq-bey', '3102529/clint-capela', '4431680/onyeka-okongwu',

        # Boston
        '4065648/jayson-tatum', '3917376/jaylen-brown', '3102531/kristaps-porzingis',
        '3078576/derrick-white', '3995/jrue-holiday', '3213/al-horford',

        # Brooklyn
        '3147657/mikal-bridges', '4432174/cam-thomas', '3138196/cameron-johnson', '2580782/spencer-dinwiddie',
        '3907387/ben-simmons', '4278067/nic-claxton',

        # Charlotte Hornets
        '4432816/lamelo-ball', '4066383/miles-bridges', '4433287/brandon-miller', '4278078/pj-washington',

        # Chicago Bulls
        '3978/demar-derozan', '3064440/zach-lavine', '4395651/coby-white', '6478/nikola-vucevic',
        '2991350/alex-caruso', '4431687/patrick-williams', '4397002/ayo-dosunmu', '6585/andre-drummond',

        # Cleveland Cavaliers
        '3908809/donovan-mitchell', '4396907/darius-garland',
        '4432158/evan-mobley', '2991043/caris-levert', '4066328/jarrett-allen', '4065778/max-strus',

        # Dallas Mavericks
        '3945274/luka-doncic', '6442/kyrie-irving', '2528210/tim-hardaway-jr', '3936099/derrick-jones-jr',
        '3102528/dante-exum', '4683688/dereck-lively-ii', '4066218/grant-williams', '4432811/josh-green',

        # Denver Nuggets
        '3112335/nikola-jokic', '3936299/jamal-murray', '4278104/michael-porter-jr', '6443/reggie-jackson',
        '2581018/kentavious-caldwell-pope', '4431767/christian-braun',

        # Detroit Pistons
        '4432166/cade-cunningham', '3593/bojan-bogdanovic', '4433218/jaden-ivey', '4433621/jalen-duren',
        '6429/alec-burks', '4684742/ausar-thompson', '4432810/isaiah-stewart',

        # Golden State Warriors
        '3975/stephen-curry', '6475/klay-thompson', '3059319/andrew-wiggins', '3032978/dario-saric',
        '4432171/moses-moody', '2779/chris-paul', '4709138/brandin-podziemski', '6589/draymond-green',

        # Houston Rockets
        '2991230/fred-vanvleet', '3155526/dillon-brooks', '4432639/jabari-smith-jr',
        '4433192/tari-eason', '4437244/jalen-green', '4871144/alperen-sengun',

        # Indiana Pacers
        '4396993/tyrese-haliburton', '3149673/pascal-siakam', '3133628/myles-turner', '4395712/andrew-nembhard',
        '4683634/bennedict-mathurin', '4396909/aaron-nesmith', '2990984/buddy-hield', '4278355/obi-toppin',

        # Los Angeles Clippers
        '4251/paul-george', '3992/james-harden', '2595516/norman-powell', '4017837/ivica-zubac',
        '3468/russell-westbrook', '3907823/terance-mann', '6450/kawhi-leonard',

        # Los Angeles Lakers
        '6583/anthony-davis', '1966/lebron-james', '3136776/dangelo-russell', '4066457/austin-reaves',
        '2990962/taurean-prince', '3137259/gabe-vincent', '4395627/cam-reddish', '4066648/rui-hachimura',
        '4278077/jarred-vanderbilt',

        # Memphis Grizzlies
        '4593125/santi-aldama', '4279888/ja-morant', '4066320/desmond-bane', '2990992/marcus-smart',
        '5112087/jaylen-wells', '4065731/jay-huff', '4431785/scotty-pippen-jr',

        # Miami Heat
        '4066261/bam-adebayo', '4395725/tyler-herro', '6430/jimmy-butler', '4432848/jaime-jaquez-jr',
        '3074752/terry-rozier', '3157465/duncan-robinson', '3138160/caleb-martin', '3449/kevin-love',

        # Milwaukee Bucks
        '3032977/giannis-antetokounmpo', '6606/damian-lillard', '6609/khris-middleton', '3448/brook-lopez',
        '3064482/bobby-portis', '3064230/cameron-payne', '2578239/pat-connaughton',

        # Minnesota Timberwolves
        '4594268/anthony-edwards', '3136195/karl-anthony-towns', '3032976/rudy-gobert', '4396971/naz-reid',
        '4431671/jaden-mcdaniels', '3195/mike-conley', '4278039/nickeil-alexander-walker', '2993874/kyle-anderson',

        # New Orleans Pelicans
        '4395628/zion-williamson', '3913176/brandon-ingram', '2490149/cj-mccollum', '6477/jonas-valanciunas',
        '4397688/trey-murphy-iii', '4277813/herbert-jones', '4683750/jordan-hawkins',
        '4869342/dyson-daniels',

        # New York Knicks
        '3934719/og-anunoby', '3934672/jalen-brunson', '3064514/julius-randle',
        # '4351852/mitchell-robinson',
        '3062679/josh-hart', '4222252/isaiah-hartenstein', '3934673/donte-divincenzo', '4397014/quentin-grimes',

        # Oklahoma City Thunder
        '4278073/shai-gilgeous-alexander', '4593803/jalen-williams', '4433255/chet-holmgren',
        '4397020/luguentz-dort', '4871145/josh-giddey', '4683692/cason-wallace',
        #
        # # Orlando Magic
        '4432573/paolo-banchero', '4566434/franz-wagner', '4432165/jalen-suggs', '4277847/wendell-carter-jr',
        '4066636/markelle-fultz', '4432809/cole-anthony', '2999547/gary-harris',

        # Philadelphia 76ers
        '3059318/joel-embiid', '4431678/tyrese-maxey', '6440/tobias-harris',
        '4066436/deanthony-melton', '3133603/kelly-oubre-jr', '3416/nicolas-batum', '6462/marcus-morris-sr',
        '2490620/robert-covington', '4278562/paul-reed',

        # Phoenix Suns
        '3202/kevin-durant', '3136193/devin-booker', '6580/bradley-beal', '3135045/grayson-allen', '3431/eric-gordon',
        '3102530/jusuf-nurkic', '4065663/josh-okogie', '3914285/drew-eubanks', '3136779/keita-bates-diop',

        # Portland Trail Blazers
        '2991070/jerami-grant', '4351851/anfernee-simons', '4914336/shaedon-sharpe',
        '4278129/deandre-ayton', '2566769/malcolm-brogdon', '4683678/scoot-henderson',
        '4431736/toumani-camara', '3907498/matisse-thybulle', '4432446/jabari-walker',

        # Sacramento Kings
        '4066259/deaaron-fox', '3155942/domantas-sabonis', '4594327/keegan-murray',
        '6578/harrison-barnes', '4066262/malik-monk', '4066372/kevin-huerter', '3136196/trey-lyles',

        # San Antonio Spurs
        '5104157/victor-wembanyama', '4395630/devin-vassell', '4395723/keldon-johnson',
        '4610139/jeremy-sochan', '4395626/tre-jones', '4066650/zach-collins', '4565201/malaki-branham',

        # Toronto Raptors
        '4433134/scottie-barnes', '4395724/immanuel-quickley', '3032979/dennis-schroder',
        '4065670/bruce-brown', '4277843/gary-trent-jr',
        '3134908/jakob-poeltl',

        # Utah Jazz
        '4066336/lauri-markkanen', '2528426/jordan-clarkson', '3908845/john-collins',
        '4277811/collin-sexton', '4433627/keyonte-george', '4433136/walker-kessler', '3899664/simone-fontecchio',
        '4396991/talen-horton-tucker', '2489663/kelly-olynyk', '4397018/ochai-agbaji',

        # Washington Wizards
        '3134907/kyle-kuzma', '4277956/jordan-poole', '3135046/tyus-jones',
        '4683021/deni-avdija', '5104155/bilal-coulibaly', '4278049/daniel-gafford',
        '4277848/marvin-bagley-iii', '4280151/corey-kispert', '3064447/delon-wright'

    ]

    tracker = RequestTracker.RequestTracker()

    fileData = []
    playerData = []

    teamsPlaying = getTeamsPlayingToday()
    d1 = datetime.datetime.now().strftime('%x').replace('/', '.')
    fileName = './DataSheets/ESPN_PlayerData_' + d1 + '.xlsx'

    print('Processing...........')
    if ESPNPlayers:
        for espnPlayer in ESPNPlayers:
            # parse players name from link
            playerData = []

            player = espnScraper(espnPlayer, tracker)
            print(f"Requests in the last minute: {tracker.get_requests_per_minute()}")
            if player:
                if len(player.games['points']) > 0:
                    teamCity = player.team.split(" ", 1)[0]
                    if (player.status == 'Active') and (teamCity in teamsPlaying):
                        allBenchmarks = player.get_all_benchmarks()
                        # player.print_benchmarks()
                        playerData.append(player.name)
                        playerData.append(player.team)

                        for stat, benchmarks in allBenchmarks.items():
                            for threshold, frequency in benchmarks.items():
                                playerData.append(frequency)

                        fileData.append(playerData)

                else:
                    print(f"{player.name} has no stats. {player.status}")
            else:
                print(f"Issue getting info for {espnPlayer}")
            time.sleep(5)

            # Add data to CSV file
    if fileData:
        write_to_excel(fileData, fileName)
        print("File saved to " + fileName)
        creds = PlayerTrendEmail.get_google_creds()
        PlayerTrendEmail.send_player_trends_email(creds, fileName)

    else:
        print("Issue with fileData. Cannot write to Excel")


if __name__ == "__main__":
    main()
