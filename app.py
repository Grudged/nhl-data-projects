from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import sys

# Try to load .env file, but don't fail if it doesn't exist
try:
    load_dotenv(dotenv_path='src/.env')  # Load local .env in development
except:
    pass

# Use production environment variables if available, fallback to dev
DB_HOST = os.environ.get('DB_HOST_PROD', os.environ.get('DB_HOST', 'localhost'))
DB_NAME = os.environ.get('DB_NAME_PROD', os.environ.get('DB_NAME', 'devdb'))
DB_USER = os.environ.get('DB_USER_PROD', os.environ.get('DB_USER', 'devuser'))
DB_PASSWORD = os.environ.get('DB_PASSWORD_PROD', os.environ.get('DB_PASSWORD', 'devpass'))
DB_PORT = os.environ.get('DB_PORT_PROD', os.environ.get('DB_PORT', '5432'))

SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

# API endpoint to get NHL data
@app.route('/api/nhldata')
def nhldata():
    # Get season_type from query parameters, default to 'regular'
    season_type = request.args.get('season_type', 'regular')
    conn = None
    try:
        print("Attempting to connect to database...")
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("Connected successfully, executing query...")
        cursor.execute('''
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
                FROM "nhl_games"
                UNION ALL
                SELECT 
                    away_team_name AS team,
                    * 
                FROM "nhl_games"
            ) AS combined
            WHERE season_type = %s
            GROUP BY team
            ORDER BY total_goals DESC
        ''', (season_type,))
        
        games = cursor.fetchall()
        print(f"Query executed successfully, found {len(games)} teams")
        
    except psycopg2.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        print(f"General error: {str(e)}")
        return jsonify({'error': f'General error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print("Database connection closed")

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

    print(f"Returning data for {len(nhldata_list)} teams")
    return jsonify({'nhldata': nhldata_list})

# Health check at root
@app.route('/')
def health():
    return jsonify({'status': 'OK', 'app': 'NHL Data API'})

# Simple test endpoint
@app.route('/api/test')
def test():
    return jsonify({'message': 'Flask app is working!'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)