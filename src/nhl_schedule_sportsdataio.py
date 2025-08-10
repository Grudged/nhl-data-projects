import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv(dotenv_path='.env')
except:
    pass

def fetch_nhl_schedule(api_key, season=2025):
    """Fetch NHL schedule from SportsDataIO API"""
    api_url = f"https://api.sportsdata.io/v3/nhl/scores/json/Schedule/{season}?key={api_key}"
    
    print(f"Fetching NHL schedule for {season} season...")
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Successfully fetched {len(data)} games from SportsDataIO")
        return data
    else:
        print(f"Failed to fetch data: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def inspect_schedule_structure(schedule_data):
    """Inspect and display the structure of the schedule data"""
    if schedule_data and len(schedule_data) > 0:
        print("\nSample game structure:")
        first_game = schedule_data[0]
        
        # Print all fields and their types
        for key, value in first_game.items():
            print(f"  {key}: {type(value).__name__} = {value}")
        
        # Save sample to file for inspection
        with open('sample_nhl_schedule.json', 'w') as f:
            json.dump(schedule_data[:5], f, indent=2)
        print(f"\nSaved first 5 games to 'sample_nhl_schedule.json' for inspection")
        print(f"Total games in schedule: {len(schedule_data)}")
        
        return True
    return False

def flatten_schedule_data(schedule_data):
    """Flatten the schedule data for database insertion"""
    flattened = []
    
    for game in schedule_data:
        # Helper function to safely convert values
        def safe_int(value):
            if value is None or value == '':
                return None
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        
        # Helper function to parse datetime
        def parse_datetime(date_str):
            if date_str:
                try:
                    # Parse the datetime string (assuming ISO format)
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    return dt
                except:
                    return None
            return None
        
        game_datetime = parse_datetime(game.get('DateTime') or game.get('Date'))
        
        flattened_game = {
            "game_id": safe_int(game.get('GameID')),
            "season": safe_int(game.get('Season')),
            "season_type": safe_int(game.get('SeasonType')),
            "status": game.get('Status'),
            "day": game.get('Day'),
            "datetime": game_datetime.isoformat() if game_datetime else None,
            "date": game_datetime.date().isoformat() if game_datetime else None,
            "time": game_datetime.time().isoformat() if game_datetime else None,
            "away_team": game.get('AwayTeam'),
            "home_team": game.get('HomeTeam'),
            "away_team_id": safe_int(game.get('AwayTeamID')),
            "home_team_id": safe_int(game.get('HomeTeamID')),
            "away_team_score": safe_int(game.get('AwayTeamScore')),
            "home_team_score": safe_int(game.get('HomeTeamScore')),
            "period": game.get('Period'),
            "time_remaining": game.get('TimeRemaining'),
            "stadium_id": safe_int(game.get('StadiumID')),
            "channel": game.get('Channel'),
            "updated": game.get('Updated'),
            "created": game.get('Created'),
            "is_closed": game.get('IsClosed'),
            "game_endpoint": game.get('GameEndDateTime'),
            "neutral_venue": game.get('NeutralVenue'),
            "datetime_utc": game.get('DateTimeUTC')
        }
        
        flattened.append(flattened_game)
    
    return flattened

def create_schedule_table(db_config, table_name="nhl_schedule_2025"):
    """Create table for NHL schedule data"""
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    # Drop table if exists for fresh start (optional)
    # cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        game_id INTEGER PRIMARY KEY,
        season INTEGER,
        season_type INTEGER,
        status VARCHAR(20),
        day VARCHAR(50),
        datetime TIMESTAMP,
        date DATE,
        time TIME,
        away_team VARCHAR(10),
        home_team VARCHAR(10),
        away_team_id INTEGER,
        home_team_id INTEGER,
        away_team_score INTEGER,
        home_team_score INTEGER,
        period VARCHAR(20),
        time_remaining VARCHAR(20),
        stadium_id INTEGER,
        channel VARCHAR(50),
        updated TIMESTAMP,
        created TIMESTAMP,
        is_closed BOOLEAN,
        game_endpoint TIMESTAMP,
        neutral_venue BOOLEAN,
        datetime_utc TIMESTAMP
    )
    """
    
    cursor.execute(create_table_query)
    conn.commit()
    
    print(f"Table '{table_name}' created successfully")
    
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
            game_id = game["game_id"]
            
            if i % 100 == 0:
                print(f"Processing game {i+1}/{len(data)} (ID: {game_id})")
            
            # Check if the game already exists
            cursor.execute(f'SELECT 1 FROM "{table_name}" WHERE game_id = %s', (game_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing row
                update_query = f"""
                UPDATE "{table_name}"
                SET season = %s, season_type = %s, status = %s, day = %s,
                    datetime = %s, date = %s, time = %s, away_team = %s,
                    home_team = %s, away_team_id = %s, home_team_id = %s,
                    away_team_score = %s, home_team_score = %s, period = %s,
                    time_remaining = %s, stadium_id = %s, channel = %s,
                    updated = %s, created = %s, is_closed = %s,
                    game_endpoint = %s, neutral_venue = %s, datetime_utc = %s
                WHERE game_id = %s
                """
                cursor.execute(update_query, (
                    game['season'], game['season_type'], game['status'], game['day'],
                    game['datetime'], game['date'], game['time'], game['away_team'],
                    game['home_team'], game['away_team_id'], game['home_team_id'],
                    game['away_team_score'], game['home_team_score'], game['period'],
                    game['time_remaining'], game['stadium_id'], game['channel'],
                    game['updated'], game['created'], game['is_closed'],
                    game['game_endpoint'], game['neutral_venue'], game['datetime_utc'],
                    game_id
                ))
                successful_updates += 1
            else:
                # Insert new row
                insert_query = f"""
                INSERT INTO "{table_name}" (
                    game_id, season, season_type, status, day, datetime, date, time,
                    away_team, home_team, away_team_id, home_team_id,
                    away_team_score, home_team_score, period, time_remaining,
                    stadium_id, channel, updated, created, is_closed,
                    game_endpoint, neutral_venue, datetime_utc
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    game['game_id'], game['season'], game['season_type'], game['status'],
                    game['day'], game['datetime'], game['date'], game['time'],
                    game['away_team'], game['home_team'], game['away_team_id'],
                    game['home_team_id'], game['away_team_score'], game['home_team_score'],
                    game['period'], game['time_remaining'], game['stadium_id'],
                    game['channel'], game['updated'], game['created'], game['is_closed'],
                    game['game_endpoint'], game['neutral_venue'], game['datetime_utc']
                ))
                successful_inserts += 1
            
            # Commit every 50 games
            if i % 50 == 0:
                conn.commit()
                
        except Exception as e:
            print(f"Error processing game {game_id}: {str(e)}")
            errors += 1
            continue
    
    # Final commit
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nDatabase operation completed:")
    print(f"- New inserts: {successful_inserts}")
    print(f"- Updates: {successful_updates}")
    print(f"- Errors: {errors}")
    
    return successful_inserts + successful_updates

def main():
    # API configuration
    API_KEY = "3e9687eaec604f83af8b14709ea95172"
    SEASON = 2025  # Try 2025 first, can fall back to 2024
    
    # Database configuration - using same config as your existing NHL script
    db_config = {
        'host': os.environ.get('DB_HOST_PROD', os.environ.get('DB_HOST', 'localhost')),
        'database': os.environ.get('DB_NAME_PROD', os.environ.get('DB_NAME', 'devdb')),
        'user': os.environ.get('DB_USER_PROD', os.environ.get('DB_USER', 'devuser')),
        'password': os.environ.get('DB_PASSWORD_PROD', os.environ.get('DB_PASSWORD', 'devpass')),
        'port': os.environ.get('DB_PORT_PROD', os.environ.get('DB_PORT', '5432'))
    }
    
    table_name = "nhl_schedule_2025"
    
    print(f"NHL Schedule Fetcher - SportsDataIO")
    print(f"====================================")
    print(f"Season: {SEASON}")
    print(f"Database: {db_config['host']}")
    print(f"Table: {table_name}\n")
    
    # Fetch schedule data
    schedule_data = fetch_nhl_schedule(API_KEY, SEASON)
    
    if schedule_data:
        # Inspect the structure
        inspect_schedule_structure(schedule_data)
        
        # Ask user if they want to save to database
        save_to_db = input("\nDo you want to save this data to the database? (y/n): ").lower().strip()
        
        if save_to_db == 'y':
            print("\nProcessing data for database insertion...")
            
            # Flatten the data
            flattened_data = flatten_schedule_data(schedule_data)
            
            # Create table if it doesn't exist
            print(f"\nCreating/verifying table '{table_name}'...")
            create_schedule_table(db_config, table_name)
            
            # Upsert data to database
            print(f"\nUpserting {len(flattened_data)} games to database...")
            upsert_schedule_data(db_config, table_name, flattened_data)
            
            print(f"\n✅ Successfully processed {len(schedule_data)} games!")
        else:
            print("\nData fetched but not saved to database.")
            print("Schedule data saved to 'sample_nhl_schedule.json' for review.")
    else:
        print("\n❌ Failed to fetch schedule data from SportsDataIO")

if __name__ == "__main__":
    main()