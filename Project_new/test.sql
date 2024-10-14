use [DataWarehouse1]

SELECT * FROM Seasons;

SELECT * FROM Teams;

SELECT * FROM TeamStats;

SELECT * FROM Matches;

SELECT m.Date, 
       t1.TeamName AS AwayTeam, 
       m.HomeScore, 
       m.AwayScore, 
       t2.TeamName AS HomeTeam
FROM Matches m
JOIN Teams t1 ON m.HomeTeamID = t1.TeamID
JOIN Teams t2 ON m.AwayTeamID = t2.TeamID
WHERE t1.TeamName = 'Manchester United' OR t2.TeamName = 'Manchester United';



SELECT t.TeamName, s.Year, ts.Points
FROM TeamStats ts
JOIN Teams t ON ts.TeamID = t.TeamID
JOIN Seasons s ON ts.SeasonID = s.SeasonID;


SELECT HomeTeamID, AwayTeamID, HomeScore, AwayScore
FROM Matches
ORDER BY Date DESC;


SELECT 
    m.*, 
    t1.TeamName AS HomeTeamName, 
    t2.TeamName AS AwayTeamName
FROM Matches m
JOIN Teams t1 ON m.HomeTeamID = t1.TeamID
JOIN Teams t2 ON m.AwayTeamID = t2.TeamID
