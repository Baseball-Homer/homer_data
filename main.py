from player import extract_player_info, players_info
from team import extract_team_info
from game import pitcher_versus_batter

if __name__ == '__main__':
    teams = extract_team_info()
    print(f"MLB Teams: {teams}")

    team_id = 121  # 예시: 뉴욕 메츠
    players = players_info(team_id)
    print(f"Players in Team {team_id}: {players}")

    player_info = extract_player_info(players[0]['lastName'])
    print(f"First Player Info: {player_info}")

    result = pitcher_versus_batter(543037, 660670)  # 예시 투수 vs 타자
    print(f"Match Result: {result}")

