import random
from stats import extract_pitcher_stat, extract_batter_stat

def pitcher_versus_batter(pitcher, batter):
    pitcher_stat = extract_pitcher_stat(pitcher)
    batter_stat = extract_batter_stat(batter)
    print(pitcher_stat, batter_stat)
    result = 0  # 삼진 : 0, 아웃 : 1, 안타 : 2, 2루타 : 3, 홈런 : 4, 볼넷 : 5

    hit_rate = (batter_stat[0] * 10 + batter_stat[1] * 2) / 10 - (pitcher_stat[0] * 7 + pitcher_stat[1] * 3) / 10 + 5
    print(hit_rate)
    if hit_rate < 15:
        hit_rate = 15
    elif hit_rate > 42:
        hit_rate = 42

    slug_rate = batter_stat[1] - (pitcher_stat[0] / 5)

    bb_rate = (100 - pitcher_stat[1]) / 5 + (batter_stat[2] / 5)
    if bb_rate > 40:
        bb_rate = 40

    rand_bb = random.randint(0, 99)
    rand_hit = random.randint(0, 99)

    # hit_rate의 확률로 안타인지 판단
    if rand_bb < bb_rate:
        result = 5
    elif rand_hit < hit_rate:
        if rand_hit * 4 < slug_rate:
            result = 4
        elif rand_hit * 2 < slug_rate:
            result = 3
        else:
            result = 2
    elif rand_hit < pitcher_stat[0] / 1.4:
        result = 0
    else:
        result = 1

    print(rand_bb, rand_hit, hit_rate, slug_rate, bb_rate, result)