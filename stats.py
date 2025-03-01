import statsapi
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
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
    scaler = MinMaxScaler(feature_range=(20, 80))
    return scaler.fit_transform(series.values.reshape(-1, 1)).flatten()

def calculate_batter_stat(data):
    df = pd.DataFrame(data)

    df["Contact"] = scale_to_20_80(df["BattingAverage"])  
    df["Power"] = scale_to_20_80(df["SluggingPercentage"] - df["BattingAverage"])
    df["Discipline"] = scale_to_20_80(df["OnBasePercentage"] - df["BattingAverage"])

    df["Weight"] = np.clip(np.log1p(df["AtBats"]) / np.log1p(600), 0.3, 1)  # 최소 30% 반영

    df["Contact"] *= df["Weight"]
    df["Power"] *= df["Weight"]
    df["Discipline"] *= df["Weight"]

    X = df[["AtBats", "BattingAverage", "OnBasePercentage", "SluggingPercentage"]]
    y = df[["Contact", "Power", "Discipline"]]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Pipeline([
        ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    pred_df = pd.DataFrame(predictions, columns=["Contact", "Power", "Discipline"])
    print(pred_df)