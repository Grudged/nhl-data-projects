import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv(dotenv_path='.env')
except:
    pass

def inspect_api_response(api_key):
    """First inspect the API response to understand the data structure"""
    api_url = f"https://api.sportsdata.io/v3/nfl/stats/json/PlayerSeasonStats/2024?key={api_key}"
    
    print("Fetching sample data to inspect structure...")
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Successfully fetched {len(data)} player records")
        
        # Inspect the first few records to understand structure
        if data and len(data) > 0:
            print("\nSample record structure:")
            first_record = data[0]
            
            # Print all fields and their types
            for key, value in first_record.items():
                print(f"  {key}: {type(value).__name__} = {value}")
            
            # Save sample to file for inspection
            with open('sample_nfl_data.json', 'w') as f:
                json.dump(data[:5], f, indent=2)
            print("\nSaved first 5 records to 'sample_nfl_data.json' for inspection")
            
            return data
        else:
            print("No data returned from API")
            return None
    else:
        print(f"Failed to fetch data: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def create_nfl_table_dynamic(db_config, table_name, sample_data):
    """Create table based on the actual API response structure"""
    if not sample_data:
        print("No sample data to create table from")
        return
    
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    # Analyze the first record to determine field types
    first_record = sample_data[0]
    
    # Helper function to determine PostgreSQL type from Python value
    def get_postgres_type(value):
        if value is None:
            return "TEXT"  # Default for null values
        elif isinstance(value, bool):
            return "BOOLEAN"
        elif isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "DECIMAL(10,2)"
        elif isinstance(value, str):
            # Check if it looks like a date
            if len(value) == 10 and value.count('-') == 2:
                return "DATE"
            else:
                return "VARCHAR(255)"
        else:
            return "TEXT"
    
    # Build CREATE TABLE statement dynamically
    field_definitions = []
    
    for field_name, field_value in first_record.items():
        postgres_type = get_postgres_type(field_value)
        field_definitions.append(f"{field_name} {postgres_type}")
    
    create_table_query = f'''
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        {",\n        ".join(field_definitions)},
        PRIMARY KEY (PlayerID)
    );
    '''
    
    print("Creating table with the following structure:")
    print(create_table_query)
    
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()
    print(f"Table '{table_name}' created successfully.")

def upsert_nfl_data(db_config, table_name, data):
    """Upsert NFL player data into PostgreSQL database"""
    if not data:
        print("No data to insert")
        return
    
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    successful_inserts = 0
    successful_updates = 0
    errors = 0
    
    # Get field names from first record
    field_names = list(data[0].keys())
    
    for i, player in enumerate(data):
        try:
            player_id = player.get('PlayerID')
            
            if i % 100 == 0:
                print(f"Processing player {i+1}/{len(data)} (ID: {player_id})")
            
            # Check if player already exists
            cursor.execute(f'SELECT 1 FROM "{table_name}" WHERE PlayerID = %s', (player_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing record
                update_fields = []
                update_values = []
                
                for field in field_names:
                    if field != 'PlayerID':  # Skip primary key
                        update_fields.append(f'{field} = %s')
                        update_values.append(player.get(field))
                
                update_values.append(player_id)  # Add WHERE clause value
                
                update_query = f'UPDATE "{table_name}" SET {", ".join(update_fields)} WHERE PlayerID = %s'
                cursor.execute(update_query, update_values)
                successful_updates += 1
            else:
                # Insert new record
                placeholders = ', '.join(['%s'] * len(field_names))
                values = [player.get(field) for field in field_names]
                
                insert_query = f'INSERT INTO "{table_name}" ({", ".join(field_names)}) VALUES ({placeholders})'
                cursor.execute(insert_query, values)
                successful_inserts += 1
            
            # Commit every 50 records
            if i % 50 == 0:
                conn.commit()
        
        except Exception as e:
            print(f"Error processing player {player_id}: {str(e)}")
            errors += 1
            continue
    
    # Final commit
    conn.commit()
    conn.close()
    
    print(f"\nDatabase operation completed:")
    print(f"- New inserts: {successful_inserts}")
    print(f"- Updates: {successful_updates}")
    print(f"- Errors: {errors}")
    
    return successful_inserts + successful_updates

def main():
    # Configuration
    api_key = "3e9687eaec604f83af8b14709ea95172"
    api_url = f"https://api.sportsdata.io/v3/nfl/stats/json/PlayerSeasonStats/2024?key={api_key}"
    
    # Database configuration
    db_config = {
        'host': os.environ.get('DB_HOST_PROD', os.environ.get('DB_HOST', 'localhost')),
        'database': os.environ.get('DB_NAME_PROD', os.environ.get('DB_NAME', 'devdb')),
        'user': os.environ.get('DB_USER_PROD', os.environ.get('DB_USER', 'devuser')),
        'password': os.environ.get('DB_PASSWORD_PROD', os.environ.get('DB_PASSWORD', 'devpass')),
        'port': os.environ.get('DB_PORT_PROD', os.environ.get('DB_PORT', '5432'))
    }
    table_name = "nfl_player_season_stats_2024"
    
    print(f"Connecting to database: {db_config['host']}")
    
    # Step 1: Inspect API response structure
    print("Step 1: Inspecting API response structure...")
    sample_data = inspect_api_response(api_key)
    
    if not sample_data:
        print("Failed to get sample data. Exiting.")
        return
    
    # Step 2: Create table based on API structure
    print("\nStep 2: Creating database table...")
    create_nfl_table_dynamic(db_config, table_name, sample_data)
    
    # Step 3: Fetch all data and load into database
    print("\nStep 3: Fetching all NFL player season stats...")
    response = requests.get(api_url)
    
    if response.status_code == 200:
        all_data = response.json()
        print(f"Successfully fetched {len(all_data)} player season stats")
        
        print("\nStep 4: Loading data into database...")
        upsert_nfl_data(db_config, table_name, all_data)
        print(f"Successfully processed all {len(all_data)} player season stats!")
    else:
        print(f"Failed to fetch all data: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    main()