#!/usr/bin/env python3
"""
Quick script to seed NFL 2025 schedule data to NeonDB using the DATABASE_URL from Poke-Project
"""

import psycopg2
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Load .env file from Poke-Project
load_dotenv('/home/grudged/Repos/Poke-Project/.env')

# Get DATABASE_URL from environment (no hardcoded password!)
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment!")
    print("Please set DATABASE_URL or check Poke-Project/.env")
    exit(1)

def fetch_nfl_schedule(api_key, season=2025):
    """Fetch NFL schedule from SportsDataIO API"""
    api_url = f"https://api.sportsdata.io/v3/nfl/scores/json/Schedules/{season}?key={api_key}"
    
    print(f"Fetching NFL schedule for {season} season...")
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Fetched {len(data)} games from SportsDataIO")
        return data
    else:
        print(f"❌ Failed to fetch data: {response.status_code}")
        return None

def flatten_schedule_data(schedule_data):
    """Flatten the schedule data for database insertion"""
    flattened = []
    
    for game in schedule_data:
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

def seed_to_neondb(data):
    """Create table and seed data to NeonDB"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("📊 Creating table if not exists...")
    
    # Create table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS nfl_schedule_2025 (
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
    print("✅ Table ready")
    
    # Insert data
    successful = 0
    updated = 0
    errors = 0
    
    print(f"💾 Inserting {len(data)} games...")
    
    for i, game in enumerate(data):
        try:
            if i % 50 == 0 and i > 0:
                print(f"  Progress: {i}/{len(data)} games...")
            
            # Check if exists
            cursor.execute('SELECT 1 FROM nfl_schedule_2025 WHERE game_key = %s', (game["game_key"],))
            if cursor.fetchone():
                # Update
                update_query = """
                UPDATE nfl_schedule_2025
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
                updated += 1
            else:
                # Insert
                insert_query = """
                INSERT INTO nfl_schedule_2025 (
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
    
    return successful, updated, errors

def main():
    print("🏈 NFL 2025 Schedule Seeder for NeonDB")
    print("=" * 50)
    
    # Test connection first
    print("📡 Testing NeonDB connection...")
    try:
        test_conn = psycopg2.connect(DATABASE_URL)
        cursor = test_conn.cursor()
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(f"✅ Connected to database: {db_name}")
        
        # Check if table exists and has data
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'nfl_schedule_2025'
        """)
        table_exists = cursor.fetchone()[0] > 0
        
        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM nfl_schedule_2025")
            existing_count = cursor.fetchone()[0]
            print(f"ℹ️  Table exists with {existing_count} games")
        
        test_conn.close()
    except Exception as e:
        print(f"❌ Failed to connect: {str(e)}")
        return
    
    # Fetch schedule
    API_KEY = "3e9687eaec604f83af8b14709ea95172"
    SEASON = 2025
    
    print(f"\n📅 Fetching {SEASON} NFL Schedule from SportsDataIO...")
    schedule_data = fetch_nfl_schedule(API_KEY, SEASON)
    
    if not schedule_data:
        print("❌ Failed to fetch schedule data")
        return
    
    # Process data
    print("🔄 Processing schedule data...")
    flattened_data = flatten_schedule_data(schedule_data)
    print(f"📊 {len(flattened_data)} games ready (excluding BYE weeks)")
    
    # Seed data
    print("\n💾 Seeding to NeonDB...")
    successful, updated, errors = seed_to_neondb(flattened_data)
    
    print("\n" + "=" * 50)
    print("🎉 Seeding Complete!")
    print(f"  ✅ New inserts: {successful} games")
    print(f"  🔄 Updated: {updated} games") 
    print(f"  ❌ Errors: {errors} games") if errors > 0 else None
    print(f"  📍 Table: nfl_schedule_2025")
    print(f"  🌐 Database: NeonDB")
    print("\n✨ Your NFL 2025 schedule is now in NeonDB!")

if __name__ == "__main__":
    main()