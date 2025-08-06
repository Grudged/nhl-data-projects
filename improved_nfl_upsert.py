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

def improved_upsert_nfl_data(db_config, table_name, data):
    """Improved upsert with better error handling and logging"""
    if not data:
        print("No data to insert")
        return
    
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    successful_inserts = 0
    successful_updates = 0
    errors = []
    
    # Get field names from first record
    field_names = list(data[0].keys())
    print(f"Processing {len(data)} players with {len(field_names)} fields")
    
    # Pre-check: validate all PlayerIDs
    invalid_records = []
    valid_data = []
    
    for i, player in enumerate(data):
        player_id = player.get('PlayerID')
        if not player_id or not isinstance(player_id, int):
            invalid_records.append((i, player.get('Name', 'Unknown'), player_id))
        else:
            valid_data.append(player)
    
    if invalid_records:
        print(f"WARNING: Found {len(invalid_records)} records with invalid PlayerIDs:")
        for i, name, player_id in invalid_records[:10]:  # Show first 10
            print(f"  - Record {i}: {name} (PlayerID: {player_id})")
        print(f"Skipping these records. Processing {len(valid_data)} valid records.")
    
    # Process valid records
    for i, player in enumerate(valid_data):
        try:
            player_id = player.get('PlayerID')
            
            if i % 100 == 0:
                print(f"Processing player {i+1}/{len(valid_data)} - {player.get('Name', 'Unknown')} (ID: {player_id})")
            
            # Check if player already exists (use lowercase field name)
            cursor.execute(f'SELECT 1 FROM "{table_name}" WHERE playerid = %s', (player_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing record (convert field names to lowercase)
                update_fields = []
                update_values = []
                
                for field in field_names:
                    if field != 'PlayerID':  # Skip primary key
                        lowercase_field = field.lower()
                        update_fields.append(f'{lowercase_field} = %s')
                        value = player.get(field)
                        # Handle None values and JSON objects
                        if value is None:
                            update_values.append(None)
                        elif isinstance(value, (dict, list)):
                            # Convert dict/list to JSON string for storage
                            update_values.append(json.dumps(value))
                        else:
                            update_values.append(value)
                
                update_values.append(player_id)  # Add WHERE clause value
                
                update_query = f'UPDATE "{table_name}" SET {", ".join(update_fields)} WHERE playerid = %s'
                cursor.execute(update_query, update_values)
                successful_updates += 1
            else:
                # Insert new record (convert field names to lowercase)
                placeholders = ', '.join(['%s'] * len(field_names))
                lowercase_fields = [field.lower() for field in field_names]
                values = []
                
                for field in field_names:
                    value = player.get(field)
                    if value is None:
                        values.append(None)
                    elif isinstance(value, (dict, list)):
                        # Convert dict/list to JSON string for storage
                        values.append(json.dumps(value))
                    else:
                        values.append(value)
                
                insert_query = f'INSERT INTO "{table_name}" ({", ".join(lowercase_fields)}) VALUES ({placeholders})'
                cursor.execute(insert_query, values)
                successful_inserts += 1
            
            # Commit every 50 records
            if i % 50 == 0:
                conn.commit()
        
        except psycopg2.Error as e:
            error_msg = f"Database error for player {player.get('Name', 'Unknown')} (ID: {player_id}): {str(e)}"
            print(error_msg)
            errors.append(error_msg)
            conn.rollback()  # Rollback failed transaction
            continue
        except Exception as e:
            error_msg = f"General error for player {player.get('Name', 'Unknown')} (ID: {player_id}): {str(e)}"
            print(error_msg)
            errors.append(error_msg)
            continue
    
    # Final commit
    try:
        conn.commit()
    except Exception as e:
        print(f"Error during final commit: {str(e)}")
        conn.rollback()
    
    conn.close()
    
    print(f"\n=== DATABASE OPERATION SUMMARY ===")
    print(f"Valid records processed: {len(valid_data)}")
    print(f"Invalid records skipped: {len(invalid_records)}")
    print(f"New inserts: {successful_inserts}")
    print(f"Updates: {successful_updates}")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nFirst 10 errors:")
        for error in errors[:10]:
            print(f"  - {error}")
        
        # Save all errors to file
        with open('nfl_upsert_errors.log', 'w') as f:
            f.write("NFL Data Upsert Errors\\n")
            f.write("=" * 50 + "\\n")
            for error in errors:
                f.write(error + "\\n")
        print(f"All errors saved to 'nfl_upsert_errors.log'")
    
    return successful_inserts + successful_updates

def verify_data_after_upsert(db_config, table_name):
    """Verify the data after upsert operation"""
    print("\\n=== POST-UPSERT VERIFICATION ===")
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Basic counts
        cursor.execute(f'SELECT COUNT(*) as total FROM "{table_name}"')
        total = cursor.fetchone()['total']
        
        cursor.execute(f'SELECT COUNT(*) as with_fp FROM "{table_name}" WHERE fantasypoints > 0')
        with_fantasy_points = cursor.fetchone()['with_fp']
        
        cursor.execute(f'SELECT COUNT(DISTINCT position) as positions FROM "{table_name}"')
        positions = cursor.fetchone()['positions']
        
        cursor.execute(f'SELECT COUNT(DISTINCT team) as teams FROM "{table_name}"')
        teams = cursor.fetchone()['teams']
        
        print(f"Total players in database: {total}")
        print(f"Players with fantasy points > 0: {with_fantasy_points}")
        print(f"Unique positions: {positions}")
        print(f"Unique teams: {teams}")
        
        # Top performers
        cursor.execute(f'SELECT name, team, position, fantasypoints FROM "{table_name}" WHERE fantasypoints > 0 ORDER BY fantasypoints DESC LIMIT 10')
        top_players = cursor.fetchall()
        
        print("\\nTop 10 fantasy performers:")
        for i, player in enumerate(top_players, 1):
            print(f"  {i:2d}. {player['name']} ({player['team']} {player['position']}): {player['fantasypoints']:.1f} pts")
        
        conn.close()
        
    except Exception as e:
        print(f"Error during verification: {str(e)}")

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
    
    print(f"=== IMPROVED NFL DATA UPSERT ===")
    print(f"Database: {db_config['host']}")
    print(f"Table: {table_name}")
    print("=" * 50)
    
    # Fetch data from API
    print("Fetching data from API...")
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Successfully fetched {len(data)} records from API")
        
        # Perform improved upsert
        print("\\nStarting improved upsert...")
        processed_count = improved_upsert_nfl_data(db_config, table_name, data)
        
        # Verify results
        verify_data_after_upsert(db_config, table_name)
        
        print(f"\\nOperation completed. Processed {processed_count} records.")
    else:
        print(f"Failed to fetch data from API: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    main()