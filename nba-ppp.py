
def searchStats(url):
    # print(url)
    result = requests.get(url)

    # if result.status_code != 200:
    #     print('Could not find page')
    #     return None
   
    soup = BeautifulSoup(result.text, "html.parser")


    # Find the table body
    table = soup.find('tbody', {'class': 'divide-y divide-gray-6 dark:divide-gray-4 leading-[22px]'})
    if not table:
        print('Table not found')
        return None

    # Define a regex pattern to match dates in the format MM/DD/YYYY
    date_pattern = re.compile(r'\b\d{1,2}/\d{1,2}/\d{4}\b')
    pattern = re.compile(r'\b\d{1,2}/\d{1,2}/\d{4} [A-Z]{3} (vs|@) [A-Z]{3}\b')
    stat_pattern = re.compile(r'^[+-]?\d{1,2}$')

    # Define the stat names in the correct order (matching columns)
    stat_cat = ['mp', 'pts', 'reb', 'ast', 'stl', 'blk', 'fgm', 'fga', '3pm', '3pa', 'ftm', 'fta', 'oreb', 'dreb', 'tov', 'pf', '+/-']

    # Regex for finding the game title (e.g., "CHI vs OKC")
    matchup_pattern = re.compile(r'[A-Z]{3} (vs|@) [A-Z]{3}')


    results = []  # To store the final results

    # Iterate through each row in the table
    for row in table.find_all('tr'):
        # print(row.text)
        # Find the anchor tag containing the game title
        a_tag = row.find('a', attrs={'title': pattern})
        if not a_tag:
            continue  # Skip rows without the expected anchor tag

        # Extract the game title (e.g., "Rockets vs Nuggets")
        game_title = a_tag['title']
        # print(f"Game: {game_title}")

        # Find all stats in the row
        stat_spans = row.find_all('span')
        if not stat_spans:
            print('No stats found')
            continue  # Skip rows without stats

        # Extract and match stats
        game_stats = []
        after_matchup = False

        for td in row.find_all('td'):
            # Skip all the data before the matchup
            if not after_matchup:
                if matchup_pattern.search(td.text):
                    after_matchup = True
                continue

            # Ignore any cell with the "bg-team-primary text-team-secondary" class (highlighted stat)
            if 'bg-team-primary' in td.get('class', []):
                continue
        for span in stat_spans:
            if stat_pattern.match(span.text):
                game_stats.append(span.text)

        # Pair stats with their categories
        paired_stats = list(zip(stat_cat, game_stats))
        
        results.append({
                'game': game_title,
                'stats': paired_stats
            })
        # if len(game_stats) == len(stat_cat):
        # else:
        #     print(f"Skipping row due to mismatched stats: {game_stats}")
    # print(results)

    return results

def calcAvgPoints(results):
    """Calculates the average points scored from a list of game results."""
    points = []
    for game in results:
        for stat in game['stats']:
            if stat[0] == 'pts':
                points.append(int(stat[1]))
    

    return sum((points))/len(points)

def calcAvgPointsAndScale(results):
    """
    Calculates the average points and performance scale (max - min) 
    from a list of game results. Useful for setting distribution parameters.
    """
    points = []
    for game in results:
        for stat in game['stats']:
            if stat[0] == 'pts':
                points.append(int(stat[1]))

    if not points:
        return None, None  # Handle empty lists

    avg_points = sum(points) / len(points)
    scale = max(points) - min(points)  # Difference between best and worst performance

    return avg_points, scale
    
    

if __name__ == '__main__':
    import requests
    from bs4 import BeautifulSoup
    import re
    from sklearn.tree import DecisionTreeRegressor
    import numpy as np
    import pandas as pd

    # Hard coded team_pace
    # in the future I could use nba_api or find another way to update data frequently
    team_pace = {
    "MEM": {"team": "Memphis Grizzlies", "pace": 104.14},
    "ATL": {"team": "Atlanta Hawks", "pace": 103.95},
    "CHI": {"team": "Chicago Bulls", "pace": 103.47},
    "WAS": {"team": "Washington Wizards", "pace": 102.15},
    "DEN": {"team": "Denver Nuggets", "pace": 100.94},
    "OKC": {"team": "Oklahoma City Thunder", "pace": 100.82},
    "UTA": {"team": "Utah Jazz", "pace": 100.59},
    "IND": {"team": "Indiana Pacers", "pace": 100.57},
    "MIL": {"team": "Milwaukee Bucks", "pace": 100.49},
    "CLE": {"team": "Cleveland Cavaliers", "pace": 100.48},
    "DET": {"team": "Detroit Pistons", "pace": 100.30},
    "SAS": {"team": "San Antonio Spurs", "pace": 100.10},
    "NOP": {"team": "New Orleans Pelicans", "pace": 99.96},
    "DAL": {"team": "Dallas Mavericks", "pace": 99.96},
    "TOR": {"team": "Toronto Raptors", "pace": 99.87},
    "GSW": {"team": "Golden State Warriors", "pace": 99.70},
    "SAC": {"team": "Sacramento Kings", "pace": 99.53},
    "POR": {"team": "Portland Trail Blazers", "pace": 99.50},
    "HOU": {"team": "Houston Rockets", "pace": 99.05},
    "PHX": {"team": "Phoenix Suns", "pace": 98.82},
    "LAC": {"team": "LA Clippers", "pace": 98.55},
    "LAL": {"team": "Los Angeles Lakers", "pace": 98.39},
    "CHA": {"team": "Charlotte Hornets", "pace": 98.32},
    "NYK": {"team": "New York Knicks", "pace": 98.11},
    "MIN": {"team": "Minnesota Timberwolves", "pace": 98.07},
    "PHI": {"team": "Philadelphia 76ers", "pace": 97.63},
    "BOS": {"team": "Boston Celtics", "pace": 97.39},
    "MIA": {"team": "Miami Heat", "pace": 97.16},
    "ORL": {"team": "Orlando Magic", "pace": 96.70},
    "BKN": {"team": "Brooklyn Nets", "pace": 96.36}
    }

    prevMatches = []

    print('Starting...')

    # searching for nba stats
    name = input('Player Name: ')
    
    format_name = name.lower().replace(' ','-')

    url = f'https://www.statmuse.com/nba/ask/{format_name}-last-10-games'
    last10Home = searchStats(url)

    url = f'https://www.statmuse.com/nba/ask/{format_name}-last-10-games'
    last10Away = searchStats(url)

    url = f'https://www.statmuse.com/nba/ask/{format_name}-last-10-games'
    last10 = searchStats(url)

    url = f'https://www.statmuse.com/nba/ask/{format_name}-last-5-games'
    last5 = searchStats(url)


    oppTeam = input("Opponent Team Abbreviation: ")

    
    url = f'https://www.statmuse.com/nba/ask/{format_name}-vs-{team_pace[oppTeam]["team"]}-last-2-years'
    h2h = searchStats(url)

   
    L10Points,L10Scale = calcAvgPointsAndScale(last10)
    L5Points,L5Scale = calcAvgPointsAndScale(last5)
    L10HomePoints,L10HomeScale = calcAvgPointsAndScale(last10Home)
    L10AwayPoints,L10AwayScale = calcAvgPointsAndScale(last10Away)
    H2HPoints,H2HScale = calcAvgPointsAndScale(h2h)

    print(calcAvgPoints(last10), 'PPG in the L10')
    print(calcAvgPoints(last5), 'PPG in the L5')
    print(calcAvgPoints(last10Home), 'PPG at Home')
    print(calcAvgPoints(last10Away), 'PPG Away')
    print(calcAvgPoints(h2h), 'PPG vs',team_pace[oppTeam]["team"])
    
    
    # Seed val for random numbers
    np.random.seed(42)

    oppAllowedPPG = input('Opponent Allowed PPG: ')

    # Generate realistic player data
    train_data = pd.DataFrame({
        "L10_PPG": np.random.normal(loc=L10Points, scale=L10Scale, size=5000),
        "L5_PPG": np.random.normal(loc=L5Points, scale=L5Scale, size=5000),
        "Home_PPG": np.random.normal(loc=L10HomePoints, scale=L10HomeScale, size=5000),
        "Away_PPG": np.random.normal(loc=L10AwayPoints, scale=L10AwayScale, size=5000),
        "PPG_vs_Opponent": np.random.normal(loc=H2HPoints, scale=H2HScale, size=5000),
        "Team_Pace": np.random.normal(loc=100, scale=3, size=5000),
        "Opponent_Pace": np.random.normal(loc=team_pace[oppTeam]["pace"], scale=3, size=5000),
        "Opponent_Allowed_PPG": np.random.normal(loc=float(oppAllowedPPG), scale=4, size=5000)
    })

    locationInput = input('H (Home) or A (Away)?: ')

    # Adjust points based on pace, opponent defense, home/away splits
    train_data['Predicted_PTS'] = (
        train_data['L10_PPG'] * 0.3 +  # Recent form (most important)
        train_data['L5_PPG'] * 0.34 +  # Short-term form (slight impact)
        np.where(locationInput == 'H', train_data['Home_PPG'] * 0.2, train_data['Away_PPG'] * 0.2) +  # Home/Away split
        (train_data['Team_Pace'] - train_data['Opponent_Pace']) * 0.15 +  # Pace impact
        (train_data['Opponent_Allowed_PPG']) * 0.06 +  # Defense impact
        ((train_data['PPG_vs_Opponent'] - train_data['L10_PPG']) * 0.2)  # Differential impact
    )


    # Train the Decision Tree
    X = train_data.drop("Predicted_PTS", axis=1)
    y = train_data["Predicted_PTS"]

    reg = DecisionTreeRegressor()
    reg.fit(X, y)

    PlayerTeam = input('Player Team Abbreviation: ')
    

    #Predict Tomorrow's Player Prop
    player_data = pd.DataFrame({
        "L10_PPG": [L10Points],
        "L5_PPG": [L5Points],
        "Home_PPG": [L10HomePoints],
        "Away_PPG": [L10AwayPoints],
        "PPG_vs_Opponent": [H2HPoints],
        "Team_Pace": [team_pace[PlayerTeam]["pace"]],
        "Opponent_Pace": [team_pace[oppTeam]["pace"]],
        "Opponent_Allowed_PPG": [oppAllowedPPG]
    })

    predicted_pts = reg.predict(player_data)
    print(f"Predicted Points: {round(predicted_pts[0], 1)}")

