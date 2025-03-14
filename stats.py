import statsapi
import joblib
import pandas as pd
import numpy as np
import requests
import os
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline

def extract_batter_stat(player_id):
    try:
        player = statsapi.player_stats(player_id, group="[hitting]", type="season")
        plate = player['plateAppearances']
        avg = float(player['avg'])
        obp = float(player['obp'])
        slg = float(player['slg'])

        if avg >= 0.337:
            contact = 100
        elif 0.300 <= avg < 0.337:
            contact = 100 - ((avg - 0.300) / (0.337 - 0.300)) * (100 - 85)
        elif 0.270 <= avg < 0.300:
            contact = 85 - ((avg - 0.270) / (0.300 - 0.270)) * (85 - 70)
        elif 0.250 <= avg < 0.270:
            contact = 70 - ((avg - 0.250) / (0.270 - 0.250)) * (70 - 55)
        elif 0.200 <= avg < 0.250:
            contact = 55 - ((avg - 0.220) / (0.250 - 0.200)) * (55 - 40)
        else:
            contact = 40

        calculated_score = slg * 2 - avg
        if calculated_score >= 0.9:
            power = 100
        elif 0.8 <= calculated_score < 0.9:
            power = 100 - ((calculated_score - 0.8) / (0.9 - 0.8)) * (100 - 85)
        elif 0.7 <= calculated_score < 0.8:
            power = 85 - ((calculated_score - 0.7) / (0.8 - 0.7)) * (85 - 75)
        elif 0.6 <= calculated_score < 0.7:
            power = 75 - ((calculated_score - 0.6) / (0.7 - 0.6)) * (75 - 60)
        elif 0.5 <= calculated_score < 0.6:
            power = 60 - ((calculated_score - 0.5) / (0.6 - 0.5)) * (60 - 50)
        elif 0.4 <= calculated_score < 0.5:
            power = 60 - ((calculated_score - 0.4) / (0.5 - 0.4)) * (50 - 20)
        else:
            power = 20

        calculated_score = obp * 2 - avg

        if calculated_score >= 0.500:
            discipline = 100
        elif 0.45 <= calculated_score < 0.500:
            discipline = 100 - ((calculated_score - 0.45) / (0.500 - 0.45)) * (100 - 75)
        elif 0.4 <= calculated_score < 0.45:
            discipline = 75 - ((calculated_score - 0.4) / (0.45 - 0.4)) * (75 - 65)
        elif 0.35 <= calculated_score < 0.4:
            discipline = 65 - ((calculated_score - 0.35) / (0.4 - 0.35)) * (65 - 30)
        else:
            discipline = 30

        if plate < 100:
            contact = contact - 40 if contact - 40 > 40 else 40
            power = power - 20 if power - 20 > 20 else 20
            discipline = discipline - 30 if discipline - 30 > 30 else 30
        elif plate < 200:
            contact = contact - 15 if contact - 15 > 40 else 40
            power = power - 10 if power - 10 > 20 else 20
            discipline = discipline - 15 if discipline - 15 > 30 else 30

    except IndexError:
        contact = 40
        power = 20
        discipline = 20

    return [round(contact), round(power), round(discipline)]


def extract_pitcher_stat(player_id):
    try:
        player = statsapi.player_stat_data(player_id, group="[pitching]", type="season")['stats'][0]['stats']
        innings = float(player['inningsPitched'])
        games = player['gamesPlayed']
        era = float(player['era'])
        if innings < 10:
            era = 9
        elif era == 0:
            era = 0.01
        k_per_9 = float(player['strikeoutsPer9Inn']) if float(player['strikeoutsPer9Inn']) != 0 else 1
        walks_per_9 = float(player['walksPer9Inn']) if float(player['walksPer9Inn']) != 0 else 5

        if k_per_9 / era >= 3.6:
            stuff = 100
        elif 2.8 <= k_per_9 / era < 3.6:
            stuff = 100 - ((k_per_9 / era - 2.8) / (3.6 - 2.8)) * (100 - 80)
        elif 1.9 <= k_per_9 / era < 2.8:
            stuff = 80 - ((k_per_9 / era - 1.9) / (2.8 - 1.9)) * (80 - 60)
        else:
            stuff = 60 - ((k_per_9 / era - 1.9) / (1.9 - 0)) * (60 - 50)

        if walks_per_9 <= 0.9:
            control = 100
        elif 0.9 < walks_per_9 <= 2.5:
            control = 100 - ((walks_per_9 - 0.9) / (2.5 - 0.9)) * (100 - 75)
        elif 2.5 < walks_per_9 <= 4.5:
            control = 75 - ((walks_per_9 - 2.5) / (4.5 - 2.5)) * (75 - 55)
        else:
            control = 55 - ((walks_per_9 - 4.5) / (10 - 4.5)) * (55 - 0)

        if innings / games >= 4:
            position = '1'
        else:
            position = '0'

    except IndexError:
        stuff = 20
        control = 20
        position = '0'

    return [round(stuff), round(control), position]

def scale_to_20_80(series):
    scaler = StandardScaler()
    z_scores = scaler.fit_transform(series.values.reshape(-1, 1)).flatten()
    
    scaled_values = 50 + (z_scores * 15)

    return np.clip(scaled_values, 20, 80)

def scale_stamina(series, min_val, max_val):
    scaler = MinMaxScaler(feature_range=(min_val, max_val))
    scaled_values = scaler.fit_transform(series.values.reshape(-1, 1)).flatten()
    return np.round(scaled_values).astype(int)

def train_players():
    load_dotenv()

    api_key = os.getenv("API_KEY")

    url = "https://api.sportsdata.io/v3/mlb/stats/json/PlayerSeasonStats/2024?key=" + api_key
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        df_stat = pd.DataFrame(data)
        rows = ['Games', 'Started', 'Position', 'PositionCategory', 'InningsPitchedDecimal', 'EarnedRunAverage', 'PitchingStrikeouts', 'PitchingWalks', 'AtBats', 'BattingAverage', 'OnBasePercentage', 'SluggingPercentage']
        df_stat = df_stat[rows]
    else:
        print(f"Error: {response.status_code}, {response.text}")

    df_pitcher = df_stat.loc[df_stat['PositionCategory'] == 'P']
    df_batter = df_stat.loc[df_stat['PositionCategory'] != 'P']

    train_pitcher_model(df_pitcher)
    train_batter_model(df_batter)

def train_batter_model(data):
    data["Contact"] = scale_to_20_80(data["BattingAverage"])
    data["Power"] = scale_to_20_80(data["SluggingPercentage"] - data["BattingAverage"])
    data["Discipline"] = scale_to_20_80(data["OnBasePercentage"] - data["BattingAverage"])

    # 학습 데이터 준비
    X = data[["AtBats", "BattingAverage", "OnBasePercentage", "SluggingPercentage"]]
    y = data[["Contact", "Power", "Discipline"]]

    # 훈련/검증 데이터 분리
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 하이퍼파라미터 탐색 범위 설정
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5, 10]
    }

    # GridSearchCV를 활용한 최적 모델 탐색
    rf = RandomForestRegressor(random_state=42)
    grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='neg_mean_squared_error', n_jobs=1)
    grid_search.fit(X_train, y_train)

    # 최적의 모델 선택
    best_model = grid_search.best_estimator_

    # 검증 데이터에서 성능 확인
    y_pred = best_model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"최적 모델 MSE: {mse:.4f}")

    # 모델 저장
    joblib.dump(best_model, "best_batter_model.pkl")
    print("최적 모델이 best_batter_model.pkl 파일로 저장되었습니다.")

    return best_model

def calculate_batter_stat(data):
    df = pd.DataFrame(data)
    X_test = df[["AtBats", "BattingAverage", "OnBasePercentage", "SluggingPercentage"]]

    model = joblib.load('best_batter_model.pkl')

    # 4️⃣ 예측 수행
    predictions = model.predict(X_test)
    pred_df = pd.DataFrame(predictions, columns=["Contact", "Power", "Discipline"])

    # 5️⃣ 가중치 적용 (타석 수 기반 Weight 반영)
    df["Weight"] = np.clip(np.log1p(df["AtBats"]) / np.log1p(600), 0.3, 1)

    # 가중치 적용
    pred_df["Contact"] *= df["Weight"]
    pred_df["Power"] *= df["Weight"]
    pred_df["Discipline"] *= df["Weight"]

    # 최종 결과 출력
    print(pred_df)

def train_pitcher_model(data):
    data = data.copy()

    data = data[(data['InningsPitchedDecimal'] > 0) & (data['EarnedRunAverage'] > 0)]

    # 20-80 스케일 변환
    data['Stuff'] = scale_to_20_80(data['PitchingStrikeouts'] / data['InningsPitchedDecimal'] / data['EarnedRunAverage'])
    data['Control'] = scale_to_20_80(data['PitchingWalks'] / data['InningsPitchedDecimal'] / data["EarnedRunAverage"])
    data['Stamina'] = np.where(
        data['Position'] == 'SP', 
        scale_stamina(data['InningsPitchedDecimal'] / data['Games'], 40, 80),  # 선발투수 40~80
        scale_stamina(data['InningsPitchedDecimal'] / data['Games'], 20, 40)   # 불펜투수 20~40
    )

    # 학습 데이터 준비
    X = data[["InningsPitchedDecimal", "PitchingStrikeouts", "PitchingWalks", "EarnedRunAverage"]]
    y = data[["Stuff", "Control", "Stamina"]]

    # 훈련/검증 데이터 분리
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 하이퍼파라미터 탐색 범위 설정
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5, 10]
    }

    # GridSearchCV를 활용한 최적 모델 탐색
    rf = RandomForestRegressor(random_state=42)
    grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='neg_mean_squared_error', n_jobs=1)
    grid_search.fit(X_train, y_train)

    # 최적의 모델 선택
    best_model = grid_search.best_estimator_

    # 검증 데이터에서 성능 확인
    y_pred = best_model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"최적 모델 MSE: {mse:.4f}")

    # 모델 저장
    joblib.dump(best_model, "best_pitcher_model.pkl")
    print("최적 모델이 best_pitcher_model.pkl 파일로 저장되었습니다.")

    return best_model

def calculate_pitcher_stat(data):
    df = pd.DataFrame(data)

    X_test = df[["InningsPitchedDecimal", "PitchingStrikeouts", "PitchingWalks", "EarnedRunAverage"]]

    model = joblib.load('best_pitcher_model.pkl')

    # 4️⃣ 예측 수행
    predictions = model.predict(X_test)
    pred_df = pd.DataFrame(predictions, columns=["Stuff", "Control", "Stamina"])

    df["StarterWeight"] = np.clip(np.log1p(df["Games"]) / np.log1p(600), 0.3, 1)
    df["RelieverWeight"] = np.clip(np.log1p(df["Games"]) / np.log1p(600), 0.4, 1)
    
    if df['Position'] == 'SP':
        df["Stuff"] *= df["StarterWeight"]
        df["Control"] *= df["StarterWeight"]
    else:
        df["Stuff"] *= df["RelieverWeight"]
        df["Control"] *= df["RelieverWeight"]

    print(pred_df)