import statsapi
from player import extract_player_info, players_info, extract_players_stat, print_all_active_players
from team import extract_team_info
from game import pitcher_versus_batter
from stats import extract_batter_stat, train_players, calculate_batter_stat, calculate_pitcher_stat

if __name__ == '__main__':
    # print_all_active_players()

    # result = pitcher_versus_batter(543037, 660670)  # 예시 투수 vs 타자
    # print(f"Match Result: {result}")

    # train_players()
    
    calculate_batter_stat()
    calculate_pitcher_stat()