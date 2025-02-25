#스쿼드를 가진 사용자 목록 조회
SELECT u.owner_name
FROM squad s
JOIN user u ON s.user_id = u.user_id
WHERE u.user_id = 0;

#사용자 정보 조회
SELECT owner_name, email
FROM user
WHERE user_id = 0;

#사용자 스쿼드 게임 통계 정보 뷰(최종 승률, HOME 승률, AWAY승률)
CREATE view squad_statistics as
SELECT
    s.squad_id,
    SUM(CASE WHEN g.home_id = s.squad_id THEN 1 ELSE 0 END) AS home_games,
    SUM(CASE WHEN g.home_id = s.squad_id AND g.win_team = 'home' THEN 1 ELSE 0 END) AS home_wins,
    (SUM(CASE WHEN g.home_id = s.squad_id AND g.win_team = 'home' THEN 1 ELSE 0 END) / SUM(CASE WHEN g.home_id = s.squad_id THEN 1 ELSE 0 END)) * 100 AS home_win_rate,
    SUM(CASE WHEN g.away_id = s.squad_id THEN 1 ELSE 0 END) AS away_games,
    SUM(CASE WHEN g.away_id = s.squad_id AND g.win_team = 'away' THEN 1 ELSE 0 END) AS away_wins,
    (SUM(CASE WHEN g.away_id = s.squad_id AND g.win_team = 'away' THEN 1 ELSE 0 END) / SUM(CASE WHEN g.away_id = s.squad_id THEN 1 ELSE 0 END)) * 100 AS away_win_rate,
    COUNT(g.game_id) AS total_games,
    (SUM(CASE WHEN g.home_id = s.squad_id AND g.win_team = 'home' THEN 1 ELSE 0 END) + SUM(CASE WHEN g.away_id = s.squad_id AND g.win_team = 'away' THEN 1 ELSE 0 END)) AS total_wins,
    ((SUM(CASE WHEN g.home_id = s.squad_id AND g.win_team = 'home' THEN 1 ELSE 0 END) + SUM(CASE WHEN g.away_id = s.squad_id AND g.win_team = 'away' THEN 1 ELSE 0 END)) / COUNT(g.game_id)) * 100 AS total_rate
FROM
    squad s
LEFT JOIN
    game g ON g.home_id = s.squad_id OR g.away_id = s.squad_id
GROUP BY
    s.squad_id;

# 뷰 적용 후 스쿼드 게임 통계 정보 조회
SELECT user_id, home_win_rate, away_win_rate, total_games, total_wins, total_rate
FROM squad_statistics ss
JOIN squad s ON s.squad_id = ss.squad_id
WHERE s.user_id = ?;
    
# 투수 기록 조회
SELECT p.first_name, p.last_name, c.name, ps.position, ps.games_played, ps.innings, ps.wins, ps.losses, 
CASE
WHEN ps.innings = 0 THEN 0
ELSE (ps.earned_runs / ps.innings * 9) END AS era
FROM player p 
JOIN pitcher ps ON p.id = ps.player_id
JOIN club c ON p.club_id = c.club_id
WHERE ps.squad_id = 0
AND ps.position IN (0, 1);

# 타자 기록 조회
SELECT p.first_name, p.last_name, c.name, bs.position, bs.games_played, bs.homeruns, bs.plates,
CASE 
WHEN bs.plates = 0 THEN 0
ELSE bs.hits / bs.plates END AS avg
FROM player p 
JOIN batter bs ON p.id = bs.player_id
JOIN club c ON p.club_id = c.club_id
WHERE bs.squad_id = 0
AND bs.position NOT IN (0, 1);

# 스쿼드 감독 조회
SELECT m.name, m.manager_image
FROM manager m JOIN squad s ON m.manager_id = s.manager_id
WHERE s.squad_id = 0;

# 스쿼드 투수 조회
SELECT p.first_name, p.last_name, s.position, p.stuff, p.control
FROM player p JOIN pitcher s ON p.id = s.player_id
WHERE s.squad_id = 0
AND s.position IN (0,1);

# 스쿼드 타자 조회
SELECT p.first_name, p.last_name, s.position, p.contact, p.power, p.discipline
FROM player p JOIN batter b ON p.id = b.player_id
WHERE b.squad_id = 0
AND b.position NOT IN (0,1);

# 스쿼드 선수 전체 조회
select p.first_name, p.last_name, p.player_photo, pp.position
from player p
join (
    select player_id, position, squad_id
    from batter
    union
    select player_id, position, squad_id
    from pitcher
) as pp on p.id = pp.player_id
join squad s on pp.squad_id = s.squad_id
where s.squad_id = 0;

#스쿼드 만들기
INSERT INTO squad (squad_id, user_id, manager_id)
VALUES (0, 0, 4);

#투수 입력
INSERT INTO pitcher (player_id, squad_id, position)
VALUES (0, 660271, 1);

#타자 입력
INSERT INTO batter (player_id, squad_id, position)
VALUES (0, 660271, 1);

#투수 전적 UPDATE
UPDATE pitcher SET games_played = (games_played + 1), innings = (innings + 9), wins = (wins + 1), losses = (losses + 0), earned_runs = (earned_runs  + 2)
WHERE squad_id = 660271 and player_id = 0;

#타자 전적 UPDATE
update batter 
set games_played = 1, homeruns = 1, plates = 3, hits = 2
where player_id = 660271 and squad_id = 0;

#감독 변경
UPDATE squad
SET manager_id = 3
WHERE squad_id = 0;

#투수 변경
UPDATE pitcher
SET player_id = 660271
WHERE squad_id = 0 AND position = 1;

#타자 변경
UPDATE batter
SET player_id = 660271
WHERE squad_id = 0 AND position = 10;

# 감독 검색
SELECT m.name, m.manager_image, m.pitcher_boost, m.batter_boost
FROM manager m;

#타자 검색(포지션 별)
SELECT p.first_name, p.last_name, p.player_photo, p.contact, p.power, p.discipline
FROM player p 
JOIN club c ON p.club_id = c.club_id 
JOIN player_position pp ON p.id = pp.player_id
WHERE pp.position = 4
AND c.name = 'San Diego Padres' AND (p.first_name LIKE CONCAT('%', 'seong', '%') OR p.last_name LIKE CONCAT('%', 'seong', '%')); 

#투수 검색
SELECT p.first_name, p.last_name, p.player_photo, p.stuff, p.control
FROM player p 
JOIN club c ON p.club_id = c.club_id 
JOIN player_position pp ON p.id = pp.player_id
WHERE pp.position IN (0,1)
AND c.name = 'Los Angeles Angels' AND (p.first_name LIKE CONCAT('%', 'ohtani', '%') OR p.last_name LIKE CONCAT('%', 'ohtani', '%')); 

#게임 정보 저장
insert into game (start_date, home_id, away_id, win_team, home_score, away_score)
values ('2023/12/12', 0, 1, 'home', 3, 1);