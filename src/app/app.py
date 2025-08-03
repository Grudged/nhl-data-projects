from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import sqlite3

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('nhl_data.db')
    conn.row_factory = sqlite3.Row
    return conn

# API endpoint to get NHL data
@app.route('/api/nhldata')
def nhldata():
    try:
        conn = get_db_connection()
        games = conn.execute('''
                             SELECT 
                                team,
                                COUNT(*) AS games,
                                SUM(CASE 
                                        WHEN (home_team_name = team AND home_team_score > away_team_score) 
                                        OR (away_team_name = team AND away_team_score > home_team_score) 
                                        THEN 1 
                                        ELSE 0 
                                    END) AS wins,
                                SUM(CASE 
                                        WHEN (home_team_name = team AND home_team_score < away_team_score) 
                                        OR (away_team_name = team AND away_team_score < home_team_score) 
                                        THEN 1 
                                        ELSE 0 
                                    END) AS losses,
                                SUM(CASE 
                                        WHEN (home_team_name = team AND events = 0) 
                                        OR (away_team_name = team AND events = 0) 
                                        THEN 1 
                                        ELSE 0 
                                    END) AS yet_to_play,
                                SUM(CASE 
                                        WHEN home_team_name = team THEN home_team_score 
                                        WHEN away_team_name = team THEN away_team_score 
                                        ELSE 0 
                                    END) AS total_goals
                            FROM (
                                SELECT 
                                    home_team_name AS team,
                                    * 
                                FROM NHL_GAMES
                                UNION ALL
                                SELECT 
                                    away_team_name AS team,
                                    * 
                                FROM NHL_GAMES
                            ) AS combined
                            GROUP BY team
                            ORDER BY total_goals DESC
                             ''').fetchall()
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

    nhldata_list = []
    for game in games:
        nhldata_list.append({
            'team': game['team'],
            'games_count': game['games'],
            'wins': game['wins'],
            'losses': game['losses'],
            'yet_to_play': game['yet_to_play'],
            'total_goals': game['total_goals'],
        })

    return jsonify({'nhldata': nhldata_list})

if __name__ == '__main__':
    app.run(debug=True)