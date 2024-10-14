from flask import Flask, render_template, request
import pickle
import pandas as pd
import numpy as np
import pyodbc

app = Flask(__name__)

# Kết nối đến SQL Server để lấy dữ liệu
connection_string = (
    "DRIVER={SQL Server};"
    "SERVER=LAPTOP-IBQB3FPP\MSSQLSERVER01;"
    "DATABASE=DataWarehouse1;"
    "Trusted_Connection=yes;"  # Sử dụng Windows Authentication
)
conn = pyodbc.connect(connection_string)

# Truy vấn dữ liệu từ bảng Matches
query = """
SELECT 
    m.*, 
    t1.TeamName AS HomeTeamName, 
    t2.TeamName AS AwayTeamName
FROM Matches m
JOIN Teams t1 ON m.HomeTeamID = t1.TeamID
JOIN Teams t2 ON m.AwayTeamID = t2.TeamID
"""

df_matches = pd.read_sql_query(query, conn)

# Đóng kết nối
conn.close()

# Load model và LabelEncoders
best_rf = pickle.load(open('model/best_rf_model.pkl', 'rb'))
le_home = pickle.load(open('model/le_home.pkl', 'rb'))
le_away = pickle.load(open('model/le_away.pkl', 'rb'))

# Danh sách các cột đặc trưng cho mô hình
features = [
    'home_team_encoded', 'away_team_encoded', 'ShotsHome', 'ShotsAway', 
    'ShotsOnGoalHome', 'ShotsOnGoalAway', 'PassesHome', 'PassesAway',
    'AccuratePassesHome', 'AccuratePassesAway', 'FoulsHome', 'FoulsAway',
    'YellowCardsHome', 'YellowCardsAway', 'PossessionTimeHome', 'PossessionTimeAway'
]

@app.route('/')
def index():
    teams = df_matches['HomeTeamName'].unique()  # Lấy danh sách các đội bóng
    return render_template('index.html', teams=teams)

@app.route('/predict', methods=['POST'])
def predict():
    home_team = request.form['home_team']
    away_team = request.form['away_team']

    # Kiểm tra tên đội bóng có trong dữ liệu hay không
    if home_team not in df_matches['HomeTeamName'].values or away_team not in df_matches['AwayTeamName'].values:
        return "Lỗi: Tên đội bóng không có trong dữ liệu."
    if home_team == away_team:
        return "Lỗi: Hai đội bóng không thể giống nhau."

    # Mã hóa tên đội bóng
    home_team_enc = le_home.transform([home_team])[0]
    away_team_enc = le_away.transform([away_team])[0]

    # Tìm kiếm thống kê trung bình cho hai đội
    home_stats = df_matches[df_matches['HomeTeamName'] == home_team][features[2:]].mean()
    away_stats = df_matches[df_matches['AwayTeamName'] == away_team][features[2:]].mean()

    # Kiểm tra thông tin thống kê
    if home_stats.isnull().any() or away_stats.isnull().any():
        return "Không tìm thấy thông tin thống kê cho một trong hai đội."

    input_data = np.array([[
        home_team_enc, away_team_enc,
        home_stats['ShotsHome'], away_stats['ShotsAway'],
        home_stats['ShotsOnGoalHome'], away_stats['ShotsOnGoalAway'],
        home_stats['PassesHome'], away_stats['PassesAway'],
        home_stats['AccuratePassesHome'], away_stats['AccuratePassesAway'],
        home_stats['FoulsHome'], away_stats['FoulsAway'],
        home_stats['YellowCardsHome'], away_stats['YellowCardsAway'],
        home_stats['PossessionTimeHome'], away_stats['PossessionTimeAway']
    ]])

    # Dự đoán kết quả
    result = best_rf.predict(input_data)[0]

    if result == 1:
        prediction = f"{home_team} sẽ thắng {away_team}"
    elif result == 0:
        prediction = f"{home_team} và {away_team} sẽ hòa"
    else:
        prediction = f"{away_team} sẽ thắng {home_team}"

    return render_template('result.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)
