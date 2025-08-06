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

def diagnose_database_state(db_config, table_name):
    """Check current state of the database table"""
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print(f"=== DATABASE DIAGNOSTICS FOR {table_name} ===")
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, (table_name,))
        
        table_exists = cursor.fetchone()['exists']
        print(f"Table exists: {table_exists}")
        
        if table_exists:
            # Get row count
            cursor.execute(f'SELECT COUNT(*) as count FROM "{table_name}"')
            row_count = cursor.fetchone()['count']
            print(f"Total rows: {row_count}")
            
            # Get column info
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table_name,))
            columns = cursor.fetchall()
            print(f"Columns ({len(columns)}):")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
            # Check for any null PlayerIDs
            cursor.execute(f'SELECT COUNT(*) as count FROM "{table_name}" WHERE playerid IS NULL')
            null_player_ids = cursor.fetchone()['count']
            print(f"Records with null PlayerID: {null_player_ids}")
            
            # Check for duplicate PlayerIDs
            cursor.execute(f'''
                SELECT playerid, COUNT(*) as count 
                FROM "{table_name}" 
                GROUP BY playerid 
                HAVING COUNT(*) > 1
            ''')
            duplicates = cursor.fetchall()
            print(f"Duplicate PlayerIDs: {len(duplicates)}")
            if duplicates:
                for dup in duplicates[:5]:  # Show first 5
                    print(f"  - PlayerID {dup['playerid']}: {dup['count']} occurrences")
            
            # Check fantasy points distribution
            cursor.execute(f'SELECT MIN(fantasypoints) as min_fp, MAX(fantasypoints) as max_fp, AVG(fantasypoints) as avg_fp FROM "{table_name}"')
            fp_stats = cursor.fetchone()
            if fp_stats['min_fp'] is not None:
                print(f"FantasyPoints range: {fp_stats['min_fp']:.2f} - {fp_stats['max_fp']:.2f} (avg: {fp_stats['avg_fp']:.2f})")
            
            # Check for players with 0 fantasy points
            cursor.execute(f'SELECT COUNT(*) as count FROM "{table_name}" WHERE fantasypoints = 0')
            zero_fp = cursor.fetchone()['count']
            print(f"Players with 0 fantasy points: {zero_fp}")
            
            # Show top 5 players by fantasy points
            cursor.execute(f'SELECT name, team, position, fantasypoints FROM "{table_name}" ORDER BY fantasypoints DESC LIMIT 5')
            top_players = cursor.fetchall()
            print("Top 5 players by fantasy points:")
            for player in top_players:
                print(f"  - {player['name']} ({player['team']} {player['position']}): {player['fantasypoints']} pts")
        
        conn.close()
        
    except Exception as e:
        print(f"Error during database diagnosis: {str(e)}")

def diagnose_api_data(api_key):
    """Diagnose the API data to identify potential issues"""
    api_url = f"https://api.sportsdata.io/v3/nfl/stats/json/PlayerSeasonStats/2024?key={api_key}"
    
    print("=== API DATA DIAGNOSTICS ===")
    
    try:
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"API returned {len(data)} records")
            
            # Check for missing PlayerIDs
            missing_player_ids = [i for i, player in enumerate(data) if not player.get('PlayerID')]
            print(f"Records with missing PlayerID: {len(missing_player_ids)}")
            
            # Check for duplicate PlayerIDs
            player_ids = [player.get('PlayerID') for player in data if player.get('PlayerID')]
            unique_ids = set(player_ids)
            print(f"Unique PlayerIDs: {len(unique_ids)}")
            print(f"Duplicate PlayerIDs: {len(player_ids) - len(unique_ids)}")
            
            # Check data types consistency
            if data:
                first_record = data[0]
                inconsistent_fields = []
                
                for field in first_record.keys():
                    field_types = set()
                    for player in data[:100]:  # Check first 100 records
                        if field in player and player[field] is not None:
                            field_types.add(type(player[field]).__name__)
                    
                    if len(field_types) > 1:
                        inconsistent_fields.append((field, field_types))
                
                print(f"Fields with inconsistent data types: {len(inconsistent_fields)}")
                for field, types in inconsistent_fields[:5]:  # Show first 5
                    print(f"  - {field}: {types}")
                
                # Check fantasy points distribution in API data
                fantasy_points = [player.get('FantasyPoints', 0) for player in data if player.get('FantasyPoints') is not None]
                if fantasy_points:
                    print(f"FantasyPoints in API - Min: {min(fantasy_points):.2f}, Max: {max(fantasy_points):.2f}")
                    zero_fp_api = len([fp for fp in fantasy_points if fp == 0])
                    print(f"Players with 0 fantasy points in API: {zero_fp_api}")
                
                # Show sample of high-scoring players from API
                sorted_players = sorted(data, key=lambda x: x.get('FantasyPoints', 0), reverse=True)
                print("Top 5 players in API data:")
                for player in sorted_players[:5]:
                    print(f"  - {player.get('Name', 'N/A')} ({player.get('Team', 'N/A')} {player.get('Position', 'N/A')}): {player.get('FantasyPoints', 0)} pts")
        
        else:
            print(f"API request failed: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"Error during API diagnosis: {str(e)}")

def find_missing_players(db_config, table_name, api_key):
    """Compare API data with database to find missing players"""
    print("=== FINDING MISSING PLAYERS ===")
    
    try:
        # Get API data
        api_url = f"https://api.sportsdata.io/v3/nfl/stats/json/PlayerSeasonStats/2024?key={api_key}"
        response = requests.get(api_url)
        
        if response.status_code != 200:
            print(f"Failed to get API data: {response.status_code}")
            return
        
        api_data = response.json()
        api_player_ids = set(player.get('PlayerID') for player in api_data if player.get('PlayerID'))
        print(f"API has {len(api_player_ids)} unique players")
        
        # Get database data
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute(f'SELECT DISTINCT playerid FROM "{table_name}" WHERE playerid IS NOT NULL')
        db_player_ids = set(row[0] for row in cursor.fetchall())
        print(f"Database has {len(db_player_ids)} unique players")
        
        # Find missing players
        missing_in_db = api_player_ids - db_player_ids
        extra_in_db = db_player_ids - api_player_ids
        
        print(f"Players in API but missing from DB: {len(missing_in_db)}")
        print(f"Players in DB but not in API: {len(extra_in_db)}")
        
        if missing_in_db:
            print("Sample of missing players (first 10):")
            missing_players = [p for p in api_data if p.get('PlayerID') in list(missing_in_db)[:10]]
            for player in missing_players:
                print(f"  - {player.get('Name', 'N/A')} (ID: {player.get('PlayerID')}, {player.get('Team', 'N/A')} {player.get('Position', 'N/A')}): {player.get('FantasyPoints', 0)} pts")
        
        conn.close()
        
    except Exception as e:
        print(f"Error finding missing players: {str(e)}")

def main():
    # Configuration
    api_key = "3e9687eaec604f83af8b14709ea95172"
    
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
    print(f"Diagnosing table: {table_name}")
    print("=" * 60)
    
    # Run diagnostics
    diagnose_database_state(db_config, table_name)
    print("\n" + "=" * 60)
    diagnose_api_data(api_key)
    print("\n" + "=" * 60)
    find_missing_players(db_config, table_name, api_key)

if __name__ == "__main__":
    main()