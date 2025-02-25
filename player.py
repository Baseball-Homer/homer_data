import statsapi
from stats import extract_batter_stat, extract_pitcher_stat

def players_info(teamId):
    team = statsapi.roster(teamId)
    players_info = team.strip().split('\n')  # 각 선수 정보를 줄 단위로 분할하여 리스트로 저장

    player_full_names = []
    for player_info in players_info:
        player_full_name = player_info.split(' ')[-2:]
        full_name = ' '.join(player_full_name)
        player_full_names.append(full_name)

    return extract_players_info(player_full_names)


def print_all_active_players():
    teams = []
    players = []
    for team in statsapi.lookup_team(''):
        team_id = team['id']
        teams.append(team_id)
        players.append(players_info(team_id))

    print(players)


def extract_player_info(name):
    player_data = statsapi.lookup_player(name, )

    player_id = player_data[0]['id']
    first_name = player_data[0]['useName']
    last_name = player_data[0]['lastName']
    team_id = player_data[0]['currentTeam']['id']
    position_code = player_data[0]['primaryPosition']['code']
    pitcher = [10, 10, '0']
    batter = [10, 10, 10]

    if position_code == '1':
        pitcher = extract_pitcher_stat(player_id)
        position_code = pitcher[2]
    else:
        batter = extract_batter_stat(player_id)

    if 'primaryNumber' in player_data[0]:
        primary_num = player_data[0]['primaryNumber']
    else:
        primary_num = "None"

    # 선수 정보를 JSON 형식으로 생성하여 리스트에 추가
    player_info_json = {
        'id': player_id,
        'firstName': first_name,
        'lastName': last_name,
        'player_photo': "https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/" + str(
            player_id) + "/headshot/67/current",
        'primary_num': primary_num,
        'teamId': team_id,
        'primaryPosition': position_code,
        'stuff': pitcher[0],
        'control': pitcher[1],
        'contact': batter[0],
        'power': batter[1],
        'discipline': batter[2]
    }


def extract_players_info(players):
    player_info_list = []

    for name in players:
        player_data = statsapi.lookup_player(name)
        player_id = player_data[0]['id']
        first_name = player_data[0]['useName']
        last_name = player_data[0]['lastName']
        team_id = player_data[0]['currentTeam']['id']
        position_code = player_data[0]['primaryPosition']['code']
        pitcher = [10, 10, '0']
        batter = [10, 10, 10]

        if position_code == '1':
            pitcher = extract_pitcher_stat(player_id)
            position_code = pitcher[2]
        else:
            batter = extract_batter_stat(player_id)

        if 'primaryNumber' in player_data[0]:
            primary_num = player_data[0]['primaryNumber']
        else:
            primary_num = "None"

        # 선수 정보를 JSON 형식으로 생성하여 리스트에 추가
        player_info_json = {
            'id': player_id,
            'firstName': first_name,
            'lastName': last_name,
            'player_photo': "https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/" + str(
                player_id) + "/headshot/67/current",
            'primary_num': primary_num,
            'teamId': team_id,
            'primaryPosition': position_code,
            'stuff': pitcher[0],
            'control': pitcher[1],
            'contact': batter[0],
            'power': batter[1],
            'discipline': batter[2]
        }

        player_info_list.append(player_info_json)

    return player_info_list