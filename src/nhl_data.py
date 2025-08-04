import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import os
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv(dotenv_path='.env')
except:
    pass

# Function to flatten the data from the API
def flatten_data(api_data):
    flattened = []
    for game in api_data:
        # Helper function to safely convert to integer
        def safe_int(value):
            if value is None or value == '' or value == '0-0':
                return None
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        
        # Helper function to convert timestamp to date
        def timestamp_to_date(timestamp):
            from datetime import datetime
            try:
                return datetime.fromtimestamp(int(timestamp)).date().isoformat()
            except:
                return None
            
        # Convert ISO timestamp to simple date
        def parse_date(date_str):
            try:
                from datetime import datetime
                if 'T' in date_str:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date().isoformat()
                return date_str
            except:
                return date_str
        
        flattened.append({
            "id": str(game['id']),  # Convert to string for VARCHAR(20)
            "date": parse_date(game['date']),  # Convert ISO to date
            "time": parse_date(game['date']),  # Use date for TIME column
            "timestamp": parse_date(game['date']),  # Use date for TIMESTAMP column
            "timezone": game['timezone'],
            "status_long": game['status']['long'],
            "status_short": game['status']['short'],
            "country_name": game['country']['name'],
            "country_code": game['country']['code'],
            "league_name": game['league']['name'],
            "league_season": safe_int(game['league']['season']),  # Convert to int for INT4
            "home_team_name": game['teams']['home']['name'],
            "away_team_name": game['teams']['away']['name'],
            "home_team_score": safe_int(game['scores']['home']),
            "away_team_score": safe_int(game['scores']['away']),
            "periods_first": str(game['periods']['first']) if game['periods']['first'] is not None else None,
            "periods_second": str(game['periods']['second']) if game['periods']['second'] is not None else None,
            "periods_third": str(game['periods']['third']) if game['periods']['third'] is not None else None,
            "periods_overtime": str(game['periods']['overtime']) if game['periods']['overtime'] is not None else None,
            "periods_penalties": str(game['periods']['penalties']) if game['periods']['penalties'] is not None else None,
            "events": 1 if game['events'] else 0  # Convert boolean to 1/0 for INT2
        })
    return flattened

# Function to upsert data into the PostgreSQL database
def upsert_data(db_config, table_name, data):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    successful_inserts = 0
    successful_updates = 0
    errors = 0

    for i, game in enumerate(data):
        try:
            # Extract data from the flattened dictionary
            game_id = game["id"]
            
            if i % 100 == 0:
                print(f"Processing game {i+1}/{len(data)} (ID: {game_id})")

            # Check if the game already exists (use quotes for case-sensitive table name)
            cursor.execute(f'SELECT 1 FROM "{table_name}" WHERE id = %s', (game_id,))
            exists = cursor.fetchone()

            if exists:
                # Update the existing row
                update_query = f"""
                UPDATE "{table_name}"
                SET date = %s, time = %s, timestamp = %s, timezone = %s, 
                    status_long = %s, status_short = %s, country_name = %s, 
                    country_code = %s, league_name = %s, league_season = %s, 
                    home_team_name = %s, away_team_name = %s, home_team_score = %s, 
                    away_team_score = %s, periods_first = %s, periods_second = %s, 
                    periods_third = %s, periods_overtime = %s, periods_penalties = %s, 
                    events = %s
                WHERE id = %s
                """
                cursor.execute(update_query, (
                    game['date'], game['time'], game['timestamp'], game['timezone'],
                    game['status_long'], game['status_short'], game['country_name'],
                    game['country_code'], game['league_name'], game['league_season'],
                    game['home_team_name'], game['away_team_name'], game['home_team_score'],
                    game['away_team_score'], game['periods_first'], game['periods_second'],
                    game['periods_third'], game['periods_overtime'], game['periods_penalties'],
                    game['events'], game_id
                ))
                successful_updates += 1
            else:
                # Insert a new row
                insert_query = f"""
                INSERT INTO "{table_name}" (
                    id, date, time, timestamp, timezone, status_long, 
                    status_short, country_name, country_code, league_name, 
                    league_season, home_team_name, away_team_name, 
                    home_team_score, away_team_score, periods_first, 
                    periods_second, periods_third, periods_overtime, 
                    periods_penalties, events
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    game['id'], game['date'], game['time'], game['timestamp'], game['timezone'],
                    game['status_long'], game['status_short'], game['country_name'],
                    game['country_code'], game['league_name'], game['league_season'],
                    game['home_team_name'], game['away_team_name'], game['home_team_score'],
                    game['away_team_score'], game['periods_first'], game['periods_second'],
                    game['periods_third'], game['periods_overtime'], game['periods_penalties'],
                    game['events']
                ))
                successful_inserts += 1
                
            # Commit every 50 games to avoid long transactions
            if i % 50 == 0:
                conn.commit()
                
        except Exception as e:
            print(f"Error processing game {game_id}: {str(e)}")
            errors += 1
            continue

    # Final commit
    conn.commit()
    conn.close()
    
    print(f"Database operation completed:")
    print(f"- New inserts: {successful_inserts}")
    print(f"- Updates: {successful_updates}")  
    print(f"- Errors: {errors}")
    
    return successful_inserts + successful_updates

# Main function
def main():
    # API request setup
    api_url = "https://api-hockey.p.rapidapi.com/games/"
    headers = {
        "x-rapidapi-key": "03195fa11amsh88def1f843f0b0ap111eaejsnd592e4b8560c",
        "x-rapidapi-host": "api-hockey.p.rapidapi.com"
    }
    params = {"league": "57", "season": "2025"}

    # Use production environment variables if available, fallback to dev
    db_config = {
        'host': os.environ.get('DB_HOST_PROD', os.environ.get('DB_HOST', 'localhost')),
        'database': os.environ.get('DB_NAME_PROD', os.environ.get('DB_NAME', 'devdb')),
        'user': os.environ.get('DB_USER_PROD', os.environ.get('DB_USER', 'devuser')),
        'password': os.environ.get('DB_PASSWORD_PROD', os.environ.get('DB_PASSWORD', 'devpass')),
        'port': os.environ.get('DB_PORT_PROD', os.environ.get('DB_PORT', '5432'))
    }
    table_name = "nhl_games"

    print(f"Connecting to database: {db_config['host']}")
    
    # Fetch API response
    print("Fetching NHL game data from API...")
    response = requests.get(f"{api_url}", headers=headers, params=params)
    if response.status_code == 200:
        api_data = response.json()['response']
        print(f"Found {len(api_data)} games from API")
        
        print("Processing and flattening game data...")
        flattened_data = flatten_data(api_data)
        
        print("Upserting data to database...")
        upsert_data(db_config, table_name, flattened_data)
        print(f"Successfully upserted {len(flattened_data)} games to database!")
    else:
        print(f"Failed to fetch API data: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    main()