import requests
import pandas as pd
from bs4 import BeautifulSoup
import datetime
import string
import time
import NBAPlayer
import RequestTracker

#https://www.espn.com/nba/schedule/_/date/20241022

def getTeamsPlayingToday():
    scrape_link ='https://www.espn.com/nba/schedule'
    try:
        page = requests.get(scrape_link, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "*",
        })
        # Format the date as "Day, Month Date, Year"
        today = datetime.date.today().strftime("%A, %B %d, %Y")

        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "html.parser")

            #class ="Table__Title", go buy date?? Format = Tuesday, October 22, 2024
            fullScheduleCard = soup.find("div", class_ ="Wrapper Card__Content overflow-visible")
            todaysGames = (fullScheduleCard.find("div", text_=today)


            #scrapedTeams = gameCards.find_all("span", class_="MatchupCardTeamName_teamName__9YaBA")
            # for team in scrapedTeams:
            #     print(team.text)
            #     # todayTeams.append(team.text)

    except Exception as e:
        print(e)


def espnScrape(player, tracker):
    scrape_link = 'https://www.espn.com/nba/player/gamelog/_/id/' + player
    try:
        page = requests.get(scrape_link, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "*",
            "Connection": "close"
        })
        tracker.add_request()

        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "html.parser")
            teamDiv = soup.find("div", class_="PlayerHeader__Team")
            teamItem = teamDiv.find('a', class_="AnchorLink")
            teamName = teamItem.text

            if teamName:
                playerData.append(teamName)
            else:
                teamName = "No Team Name data"

            injuredStatus = soup.find("span", class_="TextStatus").get_text()
            print(playerName + ": " + injuredStatus)

            monthLogs = soup.find_all("table", class_="Table Table--align-right")

            for monthLog in monthLogs:
                gameLogs = monthLog.tbody.find_all("tr", class_=["Table__TR Table__TR--sm Table__even",
                                                                 "filled Table__TR Table__TR--sm Table__even"])
                for gameLog in gameLogs:
                    if gameLog:
                        if (len(points) < howManyGames):
                            statBoxes = gameLog.find_all("td")
                            points.append(statBoxes[16].text.strip())
                            rebounds.append(statBoxes[10].text.strip())
                            assist.append(statBoxes[11].text.strip())
                            threesMade.append(statBoxes[6].text.strip().split('-', 1)[0])
                    else:
                        points.append("No point data")
                        rebounds.append("No rebound data")
                        assist.append("No assist data")
                        threesMade.append("No threes made data")
                        page.close()
        else:
            print(page.status_code)
            page.close()

    except Exception as e:
        print(e)

def how_many_points(array):
    onefive_or_more = 0
    twozero_or_more = 0
    twofive_or_more = 0
    threezero_or_more = 0

    for element in array:
        element = int(element)

        if element >= 15:
            onefive_or_more += 1
            if element >= 20:
                twozero_or_more += 1
                if element >= 25:
                    twofive_or_more += 1
                    if element >= 30:
                        threezero_or_more += 1

    playerData.append((onefive_or_more / howManyGames) * 100)
    playerData.append((twozero_or_more / howManyGames) * 100)
    playerData.append((twofive_or_more / howManyGames) * 100)
    playerData.append((threezero_or_more / howManyGames) * 100)


def how_many_assists_or_rebounds(array):
    four_or_more = 0
    six_or_more = 0
    eight_or_more = 0
    ten_or_more = 0

    for element in array:
        element = int(element)
        if element >= 4:
            four_or_more += 1
            if element >= 6:
                six_or_more += 1
                if element >= 8:
                    eight_or_more += 1
                    if element >= 10:
                        ten_or_more += 1

    playerData.append(int((four_or_more / howManyGames) * 100))
    playerData.append(int((six_or_more / howManyGames) * 100))
    playerData.append(int((eight_or_more / howManyGames) * 100))
    playerData.append(int((ten_or_more / howManyGames) * 100))


def how_many_threes(array):
    two_or_more = 0
    three_or_more = 0

    for element in array:
        element = int(element)
        if element >= 2:
            two_or_more += 1
            if element >= 3:
                three_or_more += 1

    playerData.append(int((two_or_more / howManyGames) * 100))
    playerData.append(int((three_or_more / howManyGames) * 100))


ESPNPlayers = [
    # Atlanta
    # '4277905/trae-young', '3907497/dejounte-murray', '3037789/bogdan-bogdanovic', '4701230/jalen-johnson',
 #   '4065732/deandre-hunter', '4397136/saddiq-bey', '3102529/clint-capela', '4431680/onyeka-okongwu',

    # # Boston
    # '4065648/jayson-tatum', '3917376/jaylen-brown', '3102531/kristaps-porzingis',
    # '3078576/derrick-white', '3995/jrue-holiday', '3213/al-horford',
    #
    # # Brooklyn
    # '3147657/mikal-bridges', '4432174/cam-thomas', '3138196/cameron-johnson', '2580782/spencer-dinwiddie',
    # '3907387/ben-simmons', '4278067/nic-claxton',
    #
    # # Charlotte Hornets
    # '4432816/lamelo-ball', '4066383/miles-bridges', '4433287/brandon-miller',
    # '4249/gordon-hayward', '4278078/pj-washington',
    #
    # # Chicago Bulls
    # '3978/demar-derozan', '3064440/zach-lavine', '4395651/coby-white', '6478/nikola-vucevic', '2991350/alex-caruso',
    # '4431687/patrick-williams', '4397002/ayo-dosunmu', '6585/andre-drummond',
    #
    # # Cleveland Cavaliers
    # '3908809/donovan-mitchell', '4396907/darius-garland',
    # '4432158/evan-mobley', '2991043/caris-levert', '4066328/jarrett-allen', '4065778/max-strus',
    #
    # # Dallas Mavericks
     '3945274/luka-doncic', '6442/kyrie-irving', '2528210/tim-hardaway-jr', '3936099/derrick-jones-jr'
    # '3102528/dante-exum','4683688/dereck-lively-ii', '4066218/grant-williams', '4432811/josh-green',
    #
    # # Denver Nuggets
    # '3112335/nikola-jokic', '3936299/jamal-murray', '4278104/michael-porter-jr', '6443/reggie-jackson',
    # '2581018/kentavious-caldwell-pope', '4431767/christian-braun',
    #
    # # Detroit Pistons
    # '4432166/cade-cunningham', '3593/bojan-bogdanovic', '4433218/jaden-ivey', '4433621/jalen-duren',
    # '6429/alec-burks', '4684742/ausar-thompson', '4432810/isaiah-stewart', '4683024/killian-hayes',
    #
    # # Golden State Warriors
    # '3975/stephen-curry', '6475/klay-thompson', '3059319/andrew-wiggins', '3032978/dario-saric',
    # '4432171/moses-moody','2779/chris-paul', '4709138/brandin-podziemski', '6589/draymond-green',
    #
    # # Houston Rockets
    # '2991230/fred-vanvleet', '3155526/dillon-brooks', '4432639/jabari-smith-jr',
    # '4433192/tari-eason', '4437244/jalen-green', '4871144/alperen-sengun',
    #
    # # Indiana Pacers
    # '4396993/tyrese-haliburton', '3149673/pascal-siakam', '3133628/myles-turner', '4395712/andrew-nembhard',
    # '4683634/bennedict-mathurin', '4396909/aaron-nesmith', '2990984/buddy-hield', '4278355/obi-toppin',
    #
    # # Los Angeles Clippers
    # '4251/paul-george', '3992/james-harden', '2595516/norman-powell', '4017837/ivica-zubac',
    # '3468/russell-westbrook', '3907823/terance-mann', '6450/kawhi-leonard',
    #
    # # Los Angeles Lakers
    # '6583/anthony-davis', '1966/lebron-james', '3136776/dangelo-russell', '4066457/austin-reaves',
    # '2990962/taurean-prince', '3137259/gabe-vincent', '4395627/cam-reddish', '4066648/rui-hachimura',
    # '4278077/jarred-vanderbilt',
    #
    # # Memphis Grizzlies
    # # # '', '', '', '', '', '',
    # # # '', '', '', '', '', '',
    #
    # # Miami Heat
    # '4066261/bam-adebayo', '4395725/tyler-herro', '6430/jimmy-butler', '4432848/jaime-jaquez-jr',
    # '3074752/terry-rozier', '3157465/duncan-robinson', '3138160/caleb-martin', '3449/kevin-love',
    #
    # # Milwaukee Bucks
    # '3032977/giannis-antetokounmpo', '6606/damian-lillard', '6609/khris-middleton', '3448/brook-lopez',
    # '3064482/bobby-portis', '6581/jae-crowder', '3064230/cameron-payne', '2578239/pat-connaughton',
    #
    # # Minnesota Timberwolves
    # '4594268/anthony-edwards', '3136195/karl-anthony-towns', '3032976/rudy-gobert', '4396971/naz-reid',
    # '4431671/jaden-mcdaniels', '3195/mike-conley', '4278039/nickeil-alexander-walker', '2993874/kyle-anderson',
    #
    # # New Orleans Pelicans
    # '4395628/zion-williamson', '3913176/brandon-ingram', '2490149/cj-mccollum', '6477/jonas-valanciunas',
    # '4397688/trey-murphy-iii', '4277813/herbert-jones', '4683750/jordan-hawkins',
    # '3908336/matt-ryan', '4869342/dyson-daniels',
    #
    # # New York Knicks
    # '3934719/og-anunoby', '3934672/jalen-brunson', '3064514/julius-randle',
    # # '4351852/mitchell-robinson',
    # '3062679/josh-hart', '4222252/isaiah-hartenstein', '3934673/donte-divincenzo', '4397014/quentin-grimes',
    #
    # # Oklahoma City Thunder
    # '4278073/shai-gilgeous-alexander', '4593803/jalen-williams', '4433255/chet-holmgren',
    # '4397020/luguentz-dort', '4871145/josh-giddey', '4683692/cason-wallace',
    # #
    # # # Orlando Magic
    # '4432573/paolo-banchero', '4566434/franz-wagner', '4432165/jalen-suggs', '4277847/wendell-carter-jr',
    # '4066636/markelle-fultz', '4432809/cole-anthony', '2999547/gary-harris',
    #
    # # Philadelphia 76ers
    # '3059318/joel-embiid', '4431678/tyrese-maxey', '6440/tobias-harris',
    # '4066436/deanthony-melton', '3133603/kelly-oubre-jr', '3416/nicolas-batum', '6462/marcus-morris-sr',
    # '2490620/robert-covington', '4278562/paul-reed',
    #
    # # Phoenix Suns
    # '3202/kevin-durant', '3136193/devin-booker', '6580/bradley-beal', '3135045/grayson-allen', '3431/eric-gordon',
    # '3102530/jusuf-nurkic', '4065663/josh-okogie', '3914285/drew-eubanks', '3136779/keita-bates-diop',
    #
    # # Portland Trail Blazers
    # '2991070/jerami-grant', '4351851/anfernee-simons', '4914336/shaedon-sharpe',
    # '4278129/deandre-ayton', '2566769/malcolm-brogdon', '4683678/scoot-henderson',
    # '4431736/toumani-camara', '3907498/matisse-thybulle', '4432446/jabari-walker',
    #
    # # Sacramento Kings
    # '4066259/deaaron-fox', '3155942/domantas-sabonis', '4594327/keegan-murray',
    # '6578/harrison-barnes', '4066262/malik-monk', '4066372/kevin-huerter', '3136196/trey-lyles',
    #
    # # San Antonio Spurs
    # '5104157/victor-wembanyama', '4395630/devin-vassell', '4395723/keldon-johnson',
    # '4610139/jeremy-sochan', '4395626/tre-jones', '4066650/zach-collins', '4565201/malaki-branham',
    #
    # # Toronto Raptors
    # '4433134/scottie-barnes', '4395724/immanuel-quickley', '3032979/dennis-schroder',
    # '4065670/bruce-brown', '4277843/gary-trent-jr',
    # '3134908/jakob-poeltl',
    #
    # # Utah Jazz
    # '4066336/lauri-markkanen', '2528426/jordan-clarkson', '3908845/john-collins',
    # '4277811/collin-sexton', '4433627/keyonte-george', '4433136/walker-kessler', '3899664/simone-fontecchio',
    # '4396991/talen-horton-tucker', '2489663/kelly-olynyk', '4397018/ochai-agbaji',
    #
    # # Washington Wizards
    # '3134907/kyle-kuzma', '4277956/jordan-poole', '3135046/tyus-jones',
    # '4683021/deni-avdija', '5104155/bilal-coulibaly', '4278049/daniel-gafford',
    # '4277848/marvin-bagley-iii', '4280151/corey-kispert', '3064447/delon-wright'

]

dataCoulmns = [
    "Player", "Team", "15+ Points", "20+ Points", "25+ Points", "30+ Points",
    "4+ Assist", "6+ Assist", "8+ Assist", "10+ Assist",
    "4+ Reb", "6+ Reb", "8+ Reb", "10+ Reb",
    "2+ 3PM", "3+ 3PM"
]

d1 = datetime.datetime.now().strftime('%x').replace('/', '.')
fileName = 'C:/Users/Dylan/Desktop/ESPN_PlayerData ' + d1 + '.xlsx'

#tracker = RequestTracker()

howManyGames: int = 5
fileData = []
points = []
rebounds = []
assist = []
threesMade = []
playerData = []
playerName =''

getTeamsPlayingToday()


#
# global teamName
# if ESPNPlayers:
#     for player in ESPNPlayers:
#         # parse players name from link
#         playerName = str(player.strip().split('/', 1)[1].replace('-', ' '))
#         playerName = string.capwords(playerName)
#
#         points = []
#         rebounds = []
#         assist = []
#         threesMade = []
#
#         teamName = ''
#         # scrap ProBallers for data
#         playerData = [playerName]
#         print('Processing ' + playerName + "...........")
#
#         espnScrape(player, tracker)
#         # print('After:' + playerName)
#         print(f"Requests in the last minute: {tracker.get_requests_per_minute()}")
#         time.sleep(7)
#         # get percentage of stat benchmarks hit over last 5 games and add to playerData[]
#         how_many_points(points)
#         how_many_assists_or_rebounds(assist)
#         how_many_assists_or_rebounds(rebounds)
#         how_many_threes(threesMade)
#
#         # Add data to CSV file
#         fileData.append(playerData)
#
#     df = pd.DataFrame(fileData, columns=dataCoulmns)
#     with pd.ExcelWriter(fileName) as writer:
#         df.to_excel(writer, index=False, )
#
#
#
#
#