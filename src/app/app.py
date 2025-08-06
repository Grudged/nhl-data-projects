from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')  # Load local .env in development

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
    # Get league_season from query parameters, default to '2025'
    league_season = request.args.get('league_season', '2025')
    conn = None
    try:
        print("Attempting to connect to database...")
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print(f"Connected successfully, executing query with season_type='{season_type}' and league_season='{league_season}'...")
        
        # First, check what league_season values are available
        cursor.execute('SELECT DISTINCT league_season, season_type FROM "nhl_games" ORDER BY league_season, season_type')
        available_seasons = cursor.fetchall()
        print(f"Available seasons in database: {available_seasons}")
        
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
            WHERE season_type = %s AND league_season = %s
            GROUP BY team
            ORDER BY total_goals DESC
        ''', (season_type, league_season))
        
        games = cursor.fetchall()
        print(f"Query executed successfully, found {len(games)} teams for season_type='{season_type}' and league_season='{league_season}'")
        
        # Log first few results to debug
        if games:
            print(f"First team result: {games[0]}")
        else:
            print("No teams found for the specified filters")
        
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

# Endpoint to get available seasons
@app.route('/api/seasons')
def get_seasons():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('SELECT DISTINCT league_season, season_type FROM "nhl_games" ORDER BY league_season DESC, season_type')
        seasons = cursor.fetchall()
        
        return jsonify({'seasons': seasons})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# Debug endpoint to test specific queries
@app.route('/api/debug')
def debug():
    season_type = request.args.get('season_type', 'regular')
    league_season = request.args.get('league_season', '2025')
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check raw data count
        cursor.execute('SELECT COUNT(*) as total FROM "nhl_games" WHERE season_type = %s AND league_season = %s', (season_type, league_season))
        count_result = cursor.fetchone()
        
        # Get sample data
        cursor.execute('SELECT * FROM "nhl_games" WHERE season_type = %s AND league_season = %s LIMIT 5', (season_type, league_season))
        sample_data = cursor.fetchall()
        
        return jsonify({
            'filters': {'season_type': season_type, 'league_season': league_season},
            'total_games': count_result['total'] if count_result else 0,
            'sample_data': sample_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# API endpoint to get NFL data
@app.route('/api/nfldata')
def nfldata():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT 
                name,
                team,
                position,
                fantasypoints AS fantasy_points,
                touchdowns,
                passingyards AS passing_yards,
                rushingyards AS rushing_yards,
                receivingyards AS receiving_yards,
                receptions,
                tackles,
                sacks,
                interceptions
            FROM nfl_player_season_stats_2024
            ORDER BY fantasy_points DESC
        ''')
        
        players = cursor.fetchall()
        
    except Exception as e:
        print(f"Error in nfldata endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

    nfldata_list = []
    for player in players:
        nfldata_list.append({
            'name': player['name'],
            'team': player['team'],
            'position': player['position'],
            'fantasy_points': player['fantasy_points'],
            'touchdowns': player['touchdowns'],
            'passing_yards': player['passing_yards'],
            'rushing_yards': player['rushing_yards'],
            'receiving_yards': player['receiving_yards'],
            'receptions': player['receptions'],
            'tackles': player['tackles'],
            'sacks': player['sacks'],
            'interceptions': player['interceptions']
        })

    return jsonify({'nfldata': nfldata_list})

# API endpoint to get fantasy teams
@app.route('/api/fantasy-teams')
def fantasy_teams():
    # Mock fantasy teams data
    mock_teams = {
        'chris': [],
        'aaron': [],
        'jay': []
    }
    return jsonify({'fantasy_teams': mock_teams})

# Simple test endpoint
@app.route('/api/test')
def test():
    return jsonify({'message': 'Flask app is working!'})

# API endpoint to get NFL player data
@app.route('/api/nfldata')
def nfldata():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT 
                name,
                team,
                position,
                fantasypoints as fantasy_points,
                (passingtouchdowns + rushingtouchdowns + receivingtouchdowns) as touchdowns,
                passingyards as passing_yards,
                rushingyards as rushing_yards,
                receivingyards as receiving_yards,
                receptions,
                tackles,
                sacks,
                interceptions,
                fantasy_team_owner
            FROM nfl_player_season_stats_2024
            WHERE fantasypoints > 0
            ORDER BY fantasypoints DESC
            LIMIT 500
        ''')
        
        players = cursor.fetchall()
        
    except Exception as e:
        print(f"Error fetching NFL data: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

    nfldata_list = []
    for player in players:
        nfldata_list.append({
            'name': player['name'],
            'team': player['team'],
            'position': player['position'],
            'fantasy_points': player['fantasy_points'],
            'touchdowns': player['touchdowns'],
            'passing_yards': player['passing_yards'],
            'rushing_yards': player['rushing_yards'],
            'receiving_yards': player['receiving_yards'],
            'receptions': player['receptions'],
            'tackles': player['tackles'],
            'sacks': player['sacks'],
            'interceptions': player['interceptions'],
            'fantasy_team_owner': player['fantasy_team_owner']
        })

    return jsonify({'nfldata': nfldata_list})

# API endpoint to get fantasy teams
@app.route('/api/fantasy-teams')
def get_fantasy_teams():
    # For now, return empty teams - user will populate these later
    fantasy_teams = {
        'chris': [],
        'aaron': [],
        'jay': []
    }
    return jsonify({'fantasy_teams': fantasy_teams})

# API endpoint to save fantasy team
@app.route('/api/fantasy-teams/<owner>', methods=['POST'])
def save_fantasy_team(owner):
    if owner not in ['chris', 'aaron', 'jay']:
        return jsonify({'error': 'Invalid owner'}), 400
    
    team_data = request.get_json()
    # In a real app, you'd save this to database
    # For now, just return success
    return jsonify({'success': True, 'owner': owner, 'team': team_data})

# Endpoint to check for NFL tables
@app.route('/api/tables')
def check_tables():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # List all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        table_list = [table['table_name'] for table in tables]
        
        # Check specifically for NFL tables
        nfl_tables = [table for table in table_list if 'nfl' in table.lower()]
        
        # Get details for NFL tables if they exist
        nfl_table_details = {}
        for nfl_table in nfl_tables:
            cursor.execute(f'SELECT COUNT(*) as count FROM "{nfl_table}"')
            count = cursor.fetchone()['count']
            nfl_table_details[nfl_table] = {'row_count': count}
            
            # Get sample columns if data exists
            if count > 0:
                cursor.execute(f'SELECT * FROM "{nfl_table}" LIMIT 1')
                sample = cursor.fetchone()
                if sample:
                    nfl_table_details[nfl_table]['columns'] = list(sample.keys())
        
        return jsonify({
            'all_tables': table_list,
            'nfl_tables': nfl_tables,
            'nfl_table_details': nfl_table_details,
            'nfl_player_season_stats_2024_exists': 'nfl_player_season_stats_2024' in table_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)