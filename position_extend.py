import pandas as pd

# CSV 파일 읽기
players_df = pd.read_csv('players.csv')

# 선수 ID를 키로, 포지션 리스트를 값으로 갖는 딕셔너리 생성
player_positions_dict = {}

# 데이터 조작
for index, row in players_df.iterrows():
    player_id = row['id']
    primary_position = row['primaryPosition']

    # 주 포지션과 연관된 다른 포지션들 처리
    additional_positions = []  # 해당 선수의 다른 포지션들을 담을 리스트
    # 여기서 다른 포지션들을 얻는 로직을 추가

    # 예시로 primary_position이 'P'인 경우, 투수는 'SP'나 'RP'도 소화할 수 있도록 추가
    if primary_position == 5:
        additional_positions.extend([3])
    elif primary_position == 6:
        additional_positions.extend([4])
    elif primary_position == 8:
        additional_positions.extend([7])
        additional_positions.extend([9])
    elif primary_position == 7:
        additional_positions.extend([9])
    elif primary_position == 9:
        additional_positions.extend([7])


    # 선수 ID를 키로 하여 딕셔너리에 추가
    player_positions_dict[player_id] = [primary_position] + additional_positions

# 딕셔너리를 DataFrame으로 변환
player_positions_df = pd.DataFrame([(k, pos) for k, v in player_positions_dict.items() for pos in v],
                                   columns=['player_id', 'position'])

# 결과 저장
player_positions_df.to_csv('player_positions.csv', index=False)
