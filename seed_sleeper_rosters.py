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

def fetch_sleeper_roster_data(league_id="1257449367455944704"):
    """Fetch roster data from Sleeper API"""
    api_url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    
    print(f"Fetching Sleeper roster data for league {league_id}...")
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Successfully fetched {len(data)} rosters from Sleeper API")
        return data
    else:
        print(f"Failed to fetch data: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def inspect_roster_structure(roster_data):
    """Inspect and display the structure of the roster data"""
    if roster_data and len(roster_data) > 0:
        print("\nSample roster structure:")
        first_roster = roster_data[0]
        
        # Print all fields and their types
        for key, value in first_roster.items():
            print(f"  {key}: {type(value).__name__} = {value}")
        
        # Save sample to file for inspection
        with open('sample_sleeper_rosters.json', 'w') as f:
            json.dump(roster_data[:3], f, indent=2)
        print(f"\nSaved first 3 rosters to 'sample_sleeper_rosters.json' for inspection")
        print(f"Total rosters: {len(roster_data)}")
        
        return True
    return False

def flatten_roster_data(roster_data):
    """Flatten the roster data for database insertion"""
    flattened = []
    
    for roster in roster_data:
        # Helper function to safely convert values
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
        
        # Extract settings data
        settings = roster.get('settings', {})
        
        flattened_roster = {
            "roster_id": safe_int(roster.get('roster_id')),
            "league_id": roster.get('league_id'),
            "owner_id": roster.get('owner_id'),
            "players": json.dumps(roster.get('players')) if roster.get('players') else None,
            "starters": json.dumps(roster.get('starters')) if roster.get('starters') else None,
            "keepers": json.dumps(roster.get('keepers')) if roster.get('keepers') else None,
            "reserve": json.dumps(roster.get('reserve')) if roster.get('reserve') else None,
            "taxi": json.dumps(roster.get('taxi')) if roster.get('taxi') else None,
            "co_owners": json.dumps(roster.get('co_owners')) if roster.get('co_owners') else None,
            "metadata": json.dumps(roster.get('metadata')) if roster.get('metadata') else None,
            "player_map": json.dumps(roster.get('player_map')) if roster.get('player_map') else None,
            "wins": safe_int(settings.get('wins', 0)),
            "losses": safe_int(settings.get('losses', 0)),
            "ties": safe_int(settings.get('ties', 0)),
            "fpts": safe_float(settings.get('fpts', 0)),
            "total_moves": safe_int(settings.get('total_moves', 0)),
            "waiver_position": safe_int(settings.get('waiver_position')),
            "waiver_budget_used": safe_int(settings.get('waiver_budget_used', 0))
        }
        
        flattened.append(flattened_roster)
    
    return flattened

def create_sleeper_rosters_table(db_config, table_name="sleeper_rosters"):
    """Create table for Sleeper roster data"""
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        id SERIAL PRIMARY KEY,
        roster_id INTEGER NOT NULL,
        league_id VARCHAR(50) NOT NULL,
        owner_id VARCHAR(50) NOT NULL,
        players JSONB,
        starters JSONB,
        keepers JSONB,
        reserve JSONB,
        taxi JSONB,
        co_owners JSONB,
        metadata JSONB,
        player_map JSONB,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        ties INTEGER DEFAULT 0,
        fpts DECIMAL(10, 2) DEFAULT 0,
        total_moves INTEGER DEFAULT 0,
        waiver_position INTEGER,
        waiver_budget_used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(league_id, roster_id)
    )
    """
    
    cursor.execute(create_table_query)
    
    # Create indexes
    index_queries = [
        f'CREATE INDEX IF NOT EXISTS idx_{table_name}_league_id ON "{table_name}"(league_id)',
        f'CREATE INDEX IF NOT EXISTS idx_{table_name}_owner_id ON "{table_name}"(owner_id)',
        f'CREATE INDEX IF NOT EXISTS idx_{table_name}_roster_id ON "{table_name}"(roster_id)'
    ]
    
    for index_query in index_queries:
        cursor.execute(index_query)
    
    conn.commit()
    
    print(f"Table '{table_name}' created successfully with indexes")
    
    cursor.close()
    conn.close()

def upsert_roster_data(db_config, table_name, data):
    """Upsert roster data into PostgreSQL database"""
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    successful_inserts = 0
    successful_updates = 0
    errors = 0
    
    for i, roster in enumerate(data):
        try:
            roster_id = roster["roster_id"]
            league_id = roster["league_id"]
            
            print(f"Processing roster {i+1}/{len(data)} (ID: {roster_id}, Owner: {roster['owner_id']})")
            
            # Check if the roster already exists
            cursor.execute(f'SELECT 1 FROM "{table_name}" WHERE league_id = %s AND roster_id = %s', 
                         (league_id, roster_id))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing row
                update_query = f"""
                UPDATE "{table_name}"
                SET owner_id = %s, players = %s, starters = %s, keepers = %s,
                    reserve = %s, taxi = %s, co_owners = %s, metadata = %s,
                    player_map = %s, wins = %s, losses = %s, ties = %s,
                    fpts = %s, total_moves = %s, waiver_position = %s,
                    waiver_budget_used = %s, updated_at = CURRENT_TIMESTAMP
                WHERE league_id = %s AND roster_id = %s
                """
                cursor.execute(update_query, (
                    roster['owner_id'], roster['players'], roster['starters'], roster['keepers'],
                    roster['reserve'], roster['taxi'], roster['co_owners'], roster['metadata'],
                    roster['player_map'], roster['wins'], roster['losses'], roster['ties'],
                    roster['fpts'], roster['total_moves'], roster['waiver_position'],
                    roster['waiver_budget_used'], league_id, roster_id
                ))
                successful_updates += 1
            else:
                # Insert new row
                insert_query = f"""
                INSERT INTO "{table_name}" (
                    roster_id, league_id, owner_id, players, starters, keepers,
                    reserve, taxi, co_owners, metadata, player_map, wins, losses,
                    ties, fpts, total_moves, waiver_position, waiver_budget_used
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    roster['roster_id'], roster['league_id'], roster['owner_id'],
                    roster['players'], roster['starters'], roster['keepers'],
                    roster['reserve'], roster['taxi'], roster['co_owners'],
                    roster['metadata'], roster['player_map'], roster['wins'],
                    roster['losses'], roster['ties'], roster['fpts'],
                    roster['total_moves'], roster['waiver_position'],
                    roster['waiver_budget_used']
                ))
                successful_inserts += 1
            
            conn.commit()
                
        except Exception as e:
            print(f"Error processing roster {roster_id}: {str(e)}")
            errors += 1
            continue
    
    cursor.close()
    conn.close()
    
    print(f"\nDatabase operation completed:")
    print(f"- New inserts: {successful_inserts}")
    print(f"- Updates: {successful_updates}")
    print(f"- Errors: {errors}")
    
    return successful_inserts + successful_updates

def main():
    # Configuration
    LEAGUE_ID = "1257449367455944704"
    
    # Database configuration - using same config pattern as NFL script
    db_config = {
        'host': os.environ.get('DB_HOST_PROD', os.environ.get('DB_HOST', 'localhost')),
        'database': os.environ.get('DB_NAME_PROD', os.environ.get('DB_NAME', 'devdb')),
        'user': os.environ.get('DB_USER_PROD', os.environ.get('DB_USER', 'devuser')),
        'password': os.environ.get('DB_PASSWORD_PROD', os.environ.get('DB_PASSWORD', 'devpass')),
        'port': os.environ.get('DB_PORT_PROD', os.environ.get('DB_PORT', '5432'))
    }
    
    table_name = "sleeper_rosters"
    
    print(f"Sleeper Roster Seeder")
    print(f"====================")
    print(f"League ID: {LEAGUE_ID}")
    print(f"Database: {db_config['host']}")
    print(f"Table: {table_name}\n")
    
    # Fetch roster data
    roster_data = fetch_sleeper_roster_data(LEAGUE_ID)
    
    if roster_data:
        # Inspect the structure
        inspect_roster_structure(roster_data)
        
        # Save to database
        print("\nProcessing data for database insertion...")
        
        # Flatten the data
        flattened_data = flatten_roster_data(roster_data)
        
        # Create table if it doesn't exist
        print(f"\nCreating/verifying table '{table_name}'...")
        create_sleeper_rosters_table(db_config, table_name)
        
        # Upsert data to database
        print(f"\nUpserting {len(flattened_data)} rosters to database...")
        upsert_roster_data(db_config, table_name, flattened_data)
        
        print(f"\n✅ Successfully processed {len(roster_data)} rosters!")
        
        # Verify the data was inserted
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}" WHERE league_id = %s', (LEAGUE_ID,))
            count = cursor.fetchone()[0]
            print(f"✅ Verification: {count} rosters found in database for league {LEAGUE_ID}")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"⚠️  Could not verify data: {str(e)}")
    else:
        print("\n❌ Failed to fetch roster data from Sleeper API")

if __name__ == "__main__":
    main()