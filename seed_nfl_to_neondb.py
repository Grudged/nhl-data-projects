#!/usr/bin/env python3
"""
Script to seed NFL 2025 schedule data to NeonDB
Usage: 
    python seed_nfl_to_neondb.py
    
Set these environment variables before running:
    export DB_HOST_PROD=your-neon-host.neon.tech
    export DB_NAME_PROD=neondb
    export DB_USER_PROD=neondb_owner
    export DB_PASSWORD_PROD=your-password
    export DB_PORT_PROD=5432
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv(dotenv_path='.env')
except:
    pass

def fetch_nfl_schedule(api_key, season=2025):
    """Fetch NFL schedule from SportsDataIO API"""
    api_url = f"https://api.sportsdata.io/v3/nfl/scores/json/Schedules/{season}?key={api_key}"
    
    print(f"Fetching NFL schedule for {season} season...")
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Successfully fetched {len(data)} games from SportsDataIO")
        return data
    else:
        print(f"Failed to fetch data: {response.status_code}")
        print(f"Response: {response.text}")
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
        
        def parse_datetime(date_str):
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    return dt
                except:
                    return None
            return None
        
        # Skip BYE week entries (they don't have GameKey)
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

def create_schedule_table(db_config, table_name="nfl_schedule_2025"):
    """Create table for NFL schedule data"""
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
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
    
    print(f"✅ Table '{table_name}' created/verified successfully")
    
    cursor.close()
    conn.close()

def upsert_schedule_data(db_config, table_name, data):
    """Upsert schedule data into PostgreSQL database"""
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    successful_inserts = 0
    successful_updates = 0
    errors = 0
    
    for i, game in enumerate(data):
        try:
            game_key = game["game_key"]
            
            if i % 50 == 0:
                print(f"Processing game {i+1}/{len(data)} (Key: {game_key})")
            
            # Check if the game already exists
            cursor.execute(f'SELECT 1 FROM "{table_name}" WHERE game_key = %s', (game_key,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing row
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
                    game_key
                ))
                successful_updates += 1
            else:
                # Insert new row
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
                successful_inserts += 1
            
            # Commit every 50 games
            if i % 50 == 0:
                conn.commit()
                
        except Exception as e:
            print(f"Error processing game {game_key}: {str(e)}")
            errors += 1
            conn.rollback()
            continue
    
    # Final commit
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ Database operation completed:")
    print(f"   - New inserts: {successful_inserts}")
    print(f"   - Updates: {successful_updates}")
    print(f"   - Errors: {errors}")
    
    return successful_inserts + successful_updates

def main():
    # Check for production database credentials
    prod_host = os.environ.get('DB_HOST_PROD')
    prod_name = os.environ.get('DB_NAME_PROD')
    prod_user = os.environ.get('DB_USER_PROD')
    prod_password = os.environ.get('DB_PASSWORD_PROD')
    prod_port = os.environ.get('DB_PORT_PROD', '5432')
    
    if not all([prod_host, prod_name, prod_user, prod_password]):
        print("❌ ERROR: NeonDB credentials not found!")
        print("\nPlease set the following environment variables:")
        print("  export DB_HOST_PROD=your-neon-host.neon.tech")
        print("  export DB_NAME_PROD=neondb")
        print("  export DB_USER_PROD=neondb_owner")
        print("  export DB_PASSWORD_PROD=your-password")
        print("  export DB_PORT_PROD=5432")
        print("\nOr create a .env file with these variables.")
        sys.exit(1)
    
    # API configuration
    API_KEY = "3e9687eaec604f83af8b14709ea95172"
    SEASON = 2025
    
    # NeonDB configuration
    neon_config = {
        'host': prod_host,
        'database': prod_name,
        'user': prod_user,
        'password': prod_password,
        'port': prod_port,
        'sslmode': 'require'  # NeonDB requires SSL
    }
    
    table_name = "nfl_schedule_2025"
    
    print(f"🏈 NFL Schedule Seeder for NeonDB")
    print(f"==================================")
    print(f"Season: {SEASON}")
    print(f"NeonDB Host: {prod_host}")
    print(f"Database: {prod_name}")
    print(f"Table: {table_name}\n")
    
    # Test connection first
    print("Testing NeonDB connection...")
    try:
        test_conn = psycopg2.connect(**neon_config)
        test_conn.close()
        print("✅ Successfully connected to NeonDB!\n")
    except Exception as e:
        print(f"❌ Failed to connect to NeonDB: {str(e)}")
        sys.exit(1)
    
    # Fetch schedule data
    schedule_data = fetch_nfl_schedule(API_KEY, SEASON)
    
    if schedule_data:
        print(f"\n📊 Found {len(schedule_data)} total entries")
        
        # Process data
        print("Processing data for database insertion...")
        flattened_data = flatten_schedule_data(schedule_data)
        print(f"📈 {len(flattened_data)} games to insert (excluding BYE weeks)")
        
        # Create table if it doesn't exist
        print(f"\nCreating/verifying table '{table_name}' in NeonDB...")
        create_schedule_table(neon_config, table_name)
        
        # Upsert data to database
        print(f"\nUpserting {len(flattened_data)} games to NeonDB...")
        total_processed = upsert_schedule_data(neon_config, table_name, flattened_data)
        
        print(f"\n🎉 Successfully seeded {total_processed} games to NeonDB!")
        print(f"   Table: {table_name}")
        print(f"   Database: {prod_name}")
        print(f"   Host: {prod_host}")
    else:
        print("\n❌ Failed to fetch schedule data from SportsDataIO")
        sys.exit(1)

if __name__ == "__main__":
    main()