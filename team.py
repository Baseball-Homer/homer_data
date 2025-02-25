import statsapi

def extract_team_info():
    teams = []
    for team in statsapi.lookup_team(''):
        team_id = team['id']
        team_name = team['name']
        team_location = team['locationName']
        team_logo = "https://www.mlbstatic.com/team-logos/" + str(team['id']) + ".svg"

        teams_info_json = {
            'team_id': team_id,
            'team_name': team_name,
            'team_location': team_location,
            'team_logo': team_logo
        }

        teams.append(teams_info_json)

    return teams