#!/usr/bin/env python3
"""
Interactive script to seed NFL 2025 schedule data to NeonDB
Prompts for credentials if not found in environment
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv
import getpass

# Load environment variables
try:
    load_dotenv(dotenv_path='.env')
except:
    pass

def get_neon_credentials():
    """Get NeonDB credentials from environment or prompt user"""
    print("🔐 NeonDB Connection Setup")
    print("=" * 40)
    
    # Check for existing credentials
    host = os.environ.get('DB_HOST_PROD')
    dbname = os.environ.get('DB_NAME_PROD')
    user = os.environ.get('DB_USER_PROD')
    password = os.environ.get('DB_PASSWORD_PROD')
    port = os.environ.get('DB_PORT_PROD', '5432')
    
    if all([host, dbname, user, password]):
        print("✅ Found credentials in environment")
        use_env = input("Use existing credentials? (y/n): ").lower().strip()
        if use_env == 'y':
            return {
                'host': host,
                'database': dbname,
                'user': user,
                'password': password,
                'port': port,
                'sslmode': 'require'
            }
    
    # Prompt for credentials
    print("\nEnter your NeonDB credentials:")
    print("(You can find these in your Neon dashboard)")
    
    host = input("Host (e.g., ep-cool-darkness-123456.us-east-2.aws.neon.tech): ").strip()
    dbname = input("Database name (default: neondb): ").strip() or "neondb"
    user = input("Username (default: neondb_owner): ").strip() or "neondb_owner"
    password = getpass.getpass("Password: ").strip()
    port = input("Port (default: 5432): ").strip() or "5432"
    
    # Optionally save to .env
    save_env = input("\nSave credentials to .env file for future use? (y/n): ").lower().strip()
    if save_env == 'y':
        with open('.env', 'a') as f:
            f.write(f"\n# NeonDB Production Credentials (added {datetime.now().isoformat()})\n")
            f.write(f"DB_HOST_PROD={host}\n")
            f.write(f"DB_NAME_PROD={dbname}\n")
            f.write(f"DB_USER_PROD={user}\n")
            f.write(f"DB_PASSWORD_PROD={password}\n")
            f.write(f"DB_PORT_PROD={port}\n")
        print("✅ Credentials saved to .env file")
    
    return {
        'host': host,
        'database': dbname,
        'user': user,
        'password': password,
        'port': port,
        'sslmode': 'require'
    }

def fetch_nfl_schedule(api_key, season=2025):
    """Fetch NFL schedule from SportsDataIO API"""
    api_url = f"https://api.sportsdata.io/v3/nfl/scores/json/Schedules/{season}?key={api_key}"
    
    print(f"Fetching NFL schedule for {season} season...")
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Successfully fetched {len(data)} games from SportsDataIO")
        return data
    else:
        print(f"❌ Failed to fetch data: {response.status_code}")
        return None

def flatten_schedule_data(schedule_data):
    """Flatten the schedule data for database insertion"""
    flattened = []
    
    for game in schedule_data:
        # Helper functions
        def safe_int(value):
            if value is None or value == '':
                return None
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        
        def safe_float(value):
            if value is None or value == '':
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        # Skip BYE week entries
        if not game.get('GameKey'):
            continue
            
        flattened_game = {
            "game_key": game.get('GameKey'),
            "season_type": safe_int(game.get('SeasonType')),
            "season": safe_int(game.get('Season')),
            "week": safe_int(game.get('Week')),
            "date": game.get('Date'),
            "away_team": game.get('AwayTeam'),
            "home_team": game.get('HomeTeam'),
            "channel": game.get('Channel'),
            "point_spread": safe_float(game.get('PointSpread')),
            "over_under": safe_float(game.get('OverUnder')),
            "stadium_id": safe_int(game.get('StadiumID')),
            "canceled": game.get('Canceled'),
            "geo_lat": safe_float(game.get('GeoLat')),
            "geo_long": safe_float(game.get('GeoLong')),
            "forecast_temp_low": safe_int(game.get('ForecastTempLow')),
            "forecast_temp_high": safe_int(game.get('ForecastTempHigh')),
            "forecast_description": game.get('ForecastDescription'),
            "forecast_wind_chill": safe_int(game.get('ForecastWindChill')),
            "forecast_wind_speed": safe_int(game.get('ForecastWindSpeed')),
            "away_team_money_line": safe_int(game.get('AwayTeamMoneyLine')),
            "home_team_money_line": safe_int(game.get('HomeTeamMoneyLine')),
            "day": game.get('Day'),
            "datetime": game.get('DateTime'),
            "global_game_id": safe_int(game.get('GlobalGameID')),
            "global_away_team_id": safe_int(game.get('GlobalAwayTeamID')),
            "global_home_team_id": safe_int(game.get('GlobalHomeTeamID')),
            "score_id": safe_int(game.get('ScoreID')),
            "status": game.get('Status'),
            "stadium_details": json.dumps(game.get('StadiumDetails')) if game.get('StadiumDetails') else None,
            "away_team_id": safe_int(game.get('AwayTeamID')),
            "home_team_id": safe_int(game.get('HomeTeamID'))
        }
        
        flattened.append(flattened_game)
    
    return flattened

def create_and_seed_table(db_config, table_name, data):
    """Create table and insert data"""
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    # Create table
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        game_key VARCHAR(20) PRIMARY KEY,
        season_type INTEGER,
        season INTEGER,
        week INTEGER,
        date VARCHAR(50),
        away_team VARCHAR(10),
        home_team VARCHAR(10),
        channel VARCHAR(50),
        point_spread FLOAT,
        over_under FLOAT,
        stadium_id INTEGER,
        canceled BOOLEAN,
        geo_lat FLOAT,
        geo_long FLOAT,
        forecast_temp_low INTEGER,
        forecast_temp_high INTEGER,
        forecast_description VARCHAR(100),
        forecast_wind_chill INTEGER,
        forecast_wind_speed INTEGER,
        away_team_money_line INTEGER,
        home_team_money_line INTEGER,
        day VARCHAR(50),
        datetime VARCHAR(50),
        global_game_id INTEGER,
        global_away_team_id INTEGER,
        global_home_team_id INTEGER,
        score_id INTEGER,
        status VARCHAR(20),
        stadium_details TEXT,
        away_team_id INTEGER,
        home_team_id INTEGER
    )
    """
    
    cursor.execute(create_table_query)
    conn.commit()
    print(f"✅ Table '{table_name}' created/verified")
    
    # Insert data
    successful = 0
    errors = 0
    
    for i, game in enumerate(data):
        try:
            if i % 50 == 0:
                print(f"  Processing game {i+1}/{len(data)}...")
            
            # Check if exists
            cursor.execute(f'SELECT 1 FROM "{table_name}" WHERE game_key = %s', (game["game_key"],))
            if cursor.fetchone():
                # Update
                update_query = f"""
                UPDATE "{table_name}"
                SET season_type = %s, season = %s, week = %s, date = %s,
                    away_team = %s, home_team = %s, channel = %s, point_spread = %s,
                    over_under = %s, stadium_id = %s, canceled = %s, geo_lat = %s,
                    geo_long = %s, forecast_temp_low = %s, forecast_temp_high = %s,
                    forecast_description = %s, forecast_wind_chill = %s,
                    forecast_wind_speed = %s, away_team_money_line = %s,
                    home_team_money_line = %s, day = %s, datetime = %s,
                    global_game_id = %s, global_away_team_id = %s,
                    global_home_team_id = %s, score_id = %s, status = %s,
                    stadium_details = %s, away_team_id = %s, home_team_id = %s
                WHERE game_key = %s
                """
                cursor.execute(update_query, (
                    game['season_type'], game['season'], game['week'], game['date'],
                    game['away_team'], game['home_team'], game['channel'], game['point_spread'],
                    game['over_under'], game['stadium_id'], game['canceled'], game['geo_lat'],
                    game['geo_long'], game['forecast_temp_low'], game['forecast_temp_high'],
                    game['forecast_description'], game['forecast_wind_chill'],
                    game['forecast_wind_speed'], game['away_team_money_line'],
                    game['home_team_money_line'], game['day'], game['datetime'],
                    game['global_game_id'], game['global_away_team_id'],
                    game['global_home_team_id'], game['score_id'], game['status'],
                    game['stadium_details'], game['away_team_id'], game['home_team_id'],
                    game["game_key"]
                ))
            else:
                # Insert
                insert_query = f"""
                INSERT INTO "{table_name}" (
                    game_key, season_type, season, week, date, away_team, home_team,
                    channel, point_spread, over_under, stadium_id, canceled,
                    geo_lat, geo_long, forecast_temp_low, forecast_temp_high,
                    forecast_description, forecast_wind_chill, forecast_wind_speed,
                    away_team_money_line, home_team_money_line, day, datetime,
                    global_game_id, global_away_team_id, global_home_team_id,
                    score_id, status, stadium_details, away_team_id, home_team_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    game['game_key'], game['season_type'], game['season'], game['week'],
                    game['date'], game['away_team'], game['home_team'], game['channel'],
                    game['point_spread'], game['over_under'], game['stadium_id'],
                    game['canceled'], game['geo_lat'], game['geo_long'],
                    game['forecast_temp_low'], game['forecast_temp_high'],
                    game['forecast_description'], game['forecast_wind_chill'],
                    game['forecast_wind_speed'], game['away_team_money_line'],
                    game['home_team_money_line'], game['day'], game['datetime'],
                    game['global_game_id'], game['global_away_team_id'],
                    game['global_home_team_id'], game['score_id'], game['status'],
                    game['stadium_details'], game['away_team_id'], game['home_team_id']
                ))
            
            successful += 1
            
            if i % 50 == 0:
                conn.commit()
                
        except Exception as e:
            print(f"  ❌ Error with game {game['game_key']}: {str(e)}")
            errors += 1
            conn.rollback()
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return successful, errors

def main():
    print("🏈 NFL Schedule Seeder for NeonDB")
    print("=" * 40)
    
    # Get NeonDB credentials
    neon_config = get_neon_credentials()
    
    # Test connection
    print("\n📡 Testing NeonDB connection...")
    try:
        test_conn = psycopg2.connect(**neon_config)
        cursor = test_conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected to: {version.split(',')[0]}")
        test_conn.close()
    except Exception as e:
        print(f"❌ Failed to connect: {str(e)}")
        print("\nPlease check your credentials and try again.")
        sys.exit(1)
    
    # Fetch schedule
    API_KEY = "3e9687eaec604f83af8b14709ea95172"
    SEASON = 2025
    
    print(f"\n📅 Fetching {SEASON} NFL Schedule")
    schedule_data = fetch_nfl_schedule(API_KEY, SEASON)
    
    if not schedule_data:
        print("❌ Failed to fetch schedule data")
        sys.exit(1)
    
    # Process data
    print("\n🔄 Processing schedule data...")
    flattened_data = flatten_schedule_data(schedule_data)
    print(f"  📊 {len(flattened_data)} games ready (excluding BYE weeks)")
    
    # Confirm before proceeding
    print(f"\n⚠️  Ready to seed {len(flattened_data)} games to NeonDB")
    print(f"   Host: {neon_config['host']}")
    print(f"   Database: {neon_config['database']}")
    print(f"   Table: nfl_schedule_2025")
    
    proceed = input("\nProceed with database seeding? (y/n): ").lower().strip()
    if proceed != 'y':
        print("❌ Seeding cancelled")
        sys.exit(0)
    
    # Seed data
    print("\n💾 Seeding data to NeonDB...")
    successful, errors = create_and_seed_table(neon_config, "nfl_schedule_2025", flattened_data)
    
    print("\n" + "=" * 40)
    print("🎉 Seeding Complete!")
    print(f"  ✅ Successful: {successful} games")
    if errors > 0:
        print(f"  ❌ Errors: {errors} games")
    print(f"  📍 Table: nfl_schedule_2025")
    print(f"  🌐 Database: {neon_config['database']} @ {neon_config['host']}")

if __name__ == "__main__":
    main()