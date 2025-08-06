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

def create_nfl_table_if_not_exists(db_config, table_name):
    """Create NFL player stats table if it doesn't exist"""
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    create_table_query = f'''
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        PlayerID INTEGER PRIMARY KEY,
        Team VARCHAR(10),
        Number INTEGER,
        FirstName VARCHAR(100),
        LastName VARCHAR(100),
        Name VARCHAR(200),
        Position VARCHAR(10),
        PositionCategory VARCHAR(20),
        Activated INTEGER,
        Played INTEGER,
        Started INTEGER,
        PassingAttempts INTEGER,
        PassingCompletions INTEGER,
        PassingYards INTEGER,
        PassingCompletionPercentage DECIMAL(5,2),
        PassingYardsPerAttempt DECIMAL(5,2),
        PassingYardsPerCompletion DECIMAL(5,2),
        PassingTouchdowns INTEGER,
        PassingInterceptions INTEGER,
        PassingRating DECIMAL(6,2),
        PassingLong INTEGER,
        PassingSacks INTEGER,
        PassingSackYards INTEGER,
        RushingAttempts INTEGER,
        RushingYards INTEGER,
        RushingYardsPerAttempt DECIMAL(5,2),
        RushingTouchdowns INTEGER,
        RushingLong INTEGER,
        ReceivingTargets INTEGER,
        Receptions INTEGER,
        ReceivingYards INTEGER,
        ReceivingYardsPerReception DECIMAL(5,2),
        ReceivingTouchdowns INTEGER,
        ReceivingLong INTEGER,
        Fumbles INTEGER,
        FumblesLost INTEGER,
        PuntReturns INTEGER,
        PuntReturnYards INTEGER,
        PuntReturnYardsPerAttempt DECIMAL(5,2),
        PuntReturnTouchdowns INTEGER,
        PuntReturnLong INTEGER,
        KickReturns INTEGER,
        KickReturnYards INTEGER,
        KickReturnYardsPerAttempt DECIMAL(5,2),
        KickReturnTouchdowns INTEGER,
        KickReturnLong INTEGER,
        SoloTackles INTEGER,
        AssistedTackles INTEGER,
        TacklesForLoss INTEGER,
        Sacks DECIMAL(4,1),
        SackYards INTEGER,
        QuarterbackHits INTEGER,
        PassesDefended INTEGER,
        FumblesForced INTEGER,
        FumblesRecovered INTEGER,
        FumbleReturnYards INTEGER,
        FumbleReturnTouchdowns INTEGER,
        Interceptions INTEGER,
        InterceptionReturnYards INTEGER,
        InterceptionReturnTouchdowns INTEGER,
        BlockedKicks INTEGER,
        SpecialTeamsSoloTackles INTEGER,
        SpecialTeamsAssistedTackles INTEGER,
        MiscSoloTackles INTEGER,
        MiscAssistedTackles INTEGER,
        Punts INTEGER,
        PuntYards INTEGER,
        PuntAverage DECIMAL(5,2),
        FieldGoalsAttempted INTEGER,
        FieldGoalsMade INTEGER,
        FieldGoalsLongestMade INTEGER,
        ExtraPointsMade INTEGER,
        TwoPointConversionPasses INTEGER,
        TwoPointConversionRuns INTEGER,
        TwoPointConversionReceptions INTEGER,
        FantasyPoints DECIMAL(6,2),
        FantasyPointsPPR DECIMAL(6,2),
        ReceptionPercentage DECIMAL(5,2),
        ReceivingYardsPerTarget DECIMAL(5,2),
        Tackles INTEGER,
        OffensiveSnapsPlayed INTEGER,
        DefensiveSnapsPlayed INTEGER,
        SpecialTeamsSnapsPlayed INTEGER,
        OffensiveTeamSnaps INTEGER,
        DefensiveTeamSnaps INTEGER,
        SpecialTeamsTeamSnaps INTEGER,
        VictiveSoloTackles INTEGER,
        AuctionValue INTEGER,
        AuctionValuePPR INTEGER,
        TwoPointConversionReturns INTEGER,
        FantasyPosition VARCHAR(10),
        FieldGoalPercentage DECIMAL(5,2),
        GlobalTeamID INTEGER,
        Updated VARCHAR(30),
        FantasyPointsStandardDeviationYear DECIMAL(6,2),
        FantasyPointsStandardDeviation DECIMAL(6,2),
        FantasyPointsStandardDeviationPPR DECIMAL(6,2),
        Season INTEGER,
        SeasonType INTEGER,
        fantasy_team_owner VARCHAR(255) DEFAULT NULL
    );
    '''
    
    print(f"Creating table '{table_name}' if it doesn't exist...")
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()
    print(f"Table '{table_name}' ready.")

def upsert_nfl_data(db_config, table_name, data):
    """Upsert NFL player data into PostgreSQL database"""
    if not data:
        print("No data to insert")
        return 0
    
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    successful_inserts = 0
    successful_updates = 0
    errors = 0
    
    # Define field mapping from API response to database columns
    field_mapping = {
        'PlayerID': 'PlayerID',
        'Team': 'Team',
        'Number': 'Number',
        'FirstName': 'FirstName',
        'LastName': 'LastName',
        'Name': 'Name',
        'Position': 'Position',
        'PositionCategory': 'PositionCategory',
        'Activated': 'Activated',
        'Played': 'Played',
        'Started': 'Started',
        'PassingAttempts': 'PassingAttempts',
        'PassingCompletions': 'PassingCompletions',
        'PassingYards': 'PassingYards',
        'PassingCompletionPercentage': 'PassingCompletionPercentage',
        'PassingYardsPerAttempt': 'PassingYardsPerAttempt',
        'PassingYardsPerCompletion': 'PassingYardsPerCompletion',
        'PassingTouchdowns': 'PassingTouchdowns',
        'PassingInterceptions': 'PassingInterceptions',
        'PassingRating': 'PassingRating',
        'PassingLong': 'PassingLong',
        'PassingSacks': 'PassingSacks',
        'PassingSackYards': 'PassingSackYards',
        'RushingAttempts': 'RushingAttempts',
        'RushingYards': 'RushingYards',
        'RushingYardsPerAttempt': 'RushingYardsPerAttempt',
        'RushingTouchdowns': 'RushingTouchdowns',
        'RushingLong': 'RushingLong',
        'ReceivingTargets': 'ReceivingTargets',
        'Receptions': 'Receptions',
        'ReceivingYards': 'ReceivingYards',
        'ReceivingYardsPerReception': 'ReceivingYardsPerReception',
        'ReceivingTouchdowns': 'ReceivingTouchdowns',
        'ReceivingLong': 'ReceivingLong',
        'Fumbles': 'Fumbles',
        'FumblesLost': 'FumblesLost',
        'PuntReturns': 'PuntReturns',
        'PuntReturnYards': 'PuntReturnYards',
        'PuntReturnYardsPerAttempt': 'PuntReturnYardsPerAttempt',
        'PuntReturnTouchdowns': 'PuntReturnTouchdowns',
        'PuntReturnLong': 'PuntReturnLong',
        'KickReturns': 'KickReturns',
        'KickReturnYards': 'KickReturnYards',
        'KickReturnYardsPerAttempt': 'KickReturnYardsPerAttempt',
        'KickReturnTouchdowns': 'KickReturnTouchdowns',
        'KickReturnLong': 'KickReturnLong',
        'SoloTackles': 'SoloTackles',
        'AssistedTackles': 'AssistedTackles',
        'TacklesForLoss': 'TacklesForLoss',
        'Sacks': 'Sacks',
        'SackYards': 'SackYards',
        'QuarterbackHits': 'QuarterbackHits',
        'PassesDefended': 'PassesDefended',
        'FumblesForced': 'FumblesForced',
        'FumblesRecovered': 'FumblesRecovered',
        'FumbleReturnYards': 'FumbleReturnYards',
        'FumbleReturnTouchdowns': 'FumbleReturnTouchdowns',
        'Interceptions': 'Interceptions',
        'InterceptionReturnYards': 'InterceptionReturnYards',
        'InterceptionReturnTouchdowns': 'InterceptionReturnTouchdowns',
        'BlockedKicks': 'BlockedKicks',
        'SpecialTeamsSoloTackles': 'SpecialTeamsSoloTackles',
        'SpecialTeamsAssistedTackles': 'SpecialTeamsAssistedTackles',
        'MiscSoloTackles': 'MiscSoloTackles',
        'MiscAssistedTackles': 'MiscAssistedTackles',
        'Punts': 'Punts',
        'PuntYards': 'PuntYards',
        'PuntAverage': 'PuntAverage',
        'FieldGoalsAttempted': 'FieldGoalsAttempted',
        'FieldGoalsMade': 'FieldGoalsMade',
        'FieldGoalsLongestMade': 'FieldGoalsLongestMade',
        'ExtraPointsMade': 'ExtraPointsMade',
        'TwoPointConversionPasses': 'TwoPointConversionPasses',
        'TwoPointConversionRuns': 'TwoPointConversionRuns',
        'TwoPointConversionReceptions': 'TwoPointConversionReceptions',
        'FantasyPoints': 'FantasyPoints',
        'FantasyPointsPPR': 'FantasyPointsPPR',
        'ReceptionPercentage': 'ReceptionPercentage',
        'ReceivingYardsPerTarget': 'ReceivingYardsPerTarget',
        'Tackles': 'Tackles',
        'OffensiveSnapsPlayed': 'OffensiveSnapsPlayed',
        'DefensiveSnapsPlayed': 'DefensiveSnapsPlayed',
        'SpecialTeamsSnapsPlayed': 'SpecialTeamsSnapsPlayed',
        'OffensiveTeamSnaps': 'OffensiveTeamSnaps',
        'DefensiveTeamSnaps': 'DefensiveTeamSnaps',
        'SpecialTeamsTeamSnaps': 'SpecialTeamsTeamSnaps',
        'VictiveSoloTackles': 'VictiveSoloTackles',
        'AuctionValue': 'AuctionValue',
        'AuctionValuePPR': 'AuctionValuePPR',
        'TwoPointConversionReturns': 'TwoPointConversionReturns',
        'FantasyPosition': 'FantasyPosition',
        'FieldGoalPercentage': 'FieldGoalPercentage',
        'GlobalTeamID': 'GlobalTeamID',
        'Updated': 'Updated',
        'FantasyPointsStandardDeviationYear': 'FantasyPointsStandardDeviationYear',
        'FantasyPointsStandardDeviation': 'FantasyPointsStandardDeviation',
        'FantasyPointsStandardDeviationPPR': 'FantasyPointsStandardDeviationPPR',
        'Season': 'Season',
        'SeasonType': 'SeasonType'
    }
    
    for i, player in enumerate(data):
        try:
            player_id = player.get('PlayerID')
            
            if i % 100 == 0:
                print(f"Processing player {i+1}/{len(data)} (ID: {player_id})")
            
            # Check if player already exists
            cursor.execute(f'SELECT 1 FROM "{table_name}" WHERE PlayerID = %s', (player_id,))
            exists = cursor.fetchone()
            
            # Prepare values using field mapping
            field_values = []
            for api_field, db_field in field_mapping.items():
                value = player.get(api_field)
                field_values.append(value)
            
            if exists:
                # Update existing record
                update_fields = []
                for api_field, db_field in field_mapping.items():
                    if db_field != 'PlayerID':  # Skip primary key
                        update_fields.append(f'{db_field} = %s')
                
                # Values for update (exclude PlayerID from values, add it for WHERE clause)
                update_values = [player.get(api_field) for api_field, db_field in field_mapping.items() if db_field != 'PlayerID']
                update_values.append(player_id)  # Add WHERE clause value
                
                update_query = f'UPDATE "{table_name}" SET {", ".join(update_fields)} WHERE PlayerID = %s'
                cursor.execute(update_query, update_values)
                successful_updates += 1
            else:
                # Insert new record
                db_fields = list(field_mapping.values())
                placeholders = ', '.join(['%s'] * len(db_fields))
                
                insert_query = f'INSERT INTO "{table_name}" ({", ".join(db_fields)}) VALUES ({placeholders})'
                cursor.execute(insert_query, field_values)
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
    
    # Use production environment variables if available, fallback to dev (same pattern as NHL script)
    db_config = {
        'host': os.environ.get('DB_HOST_PROD', os.environ.get('DB_HOST', 'localhost')),
        'database': os.environ.get('DB_NAME_PROD', os.environ.get('DB_NAME', 'devdb')),
        'user': os.environ.get('DB_USER_PROD', os.environ.get('DB_USER', 'devuser')),
        'password': os.environ.get('DB_PASSWORD_PROD', os.environ.get('DB_PASSWORD', 'devpass')),
        'port': os.environ.get('DB_PORT_PROD', os.environ.get('DB_PORT', '5432'))
    }
    table_name = "nfl_player_season_stats_2024"
    
    print(f"Connecting to database: {db_config['host']}")
    
    # Step 1: Ensure table exists
    print("Step 1: Creating NFL table if needed...")
    create_nfl_table_if_not_exists(db_config, table_name)
    
    # Step 2: Fetch API data
    print("Step 2: Fetching NFL player season stats from API...")
    response = requests.get(api_url)
    
    if response.status_code == 200:
        api_data = response.json()
        print(f"Successfully fetched {len(api_data)} player season stats")
        
        print("Step 3: Upserting data to database...")
        total_processed = upsert_nfl_data(db_config, table_name, api_data)
        print(f"Successfully processed {total_processed} player season stats!")
    else:
        print(f"Failed to fetch API data: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    main()