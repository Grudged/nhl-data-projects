#!/usr/bin/env python3
"""
Example: Seed NFL Standings
Usage: python examples/seed_standings.py [season]
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nfl_data_seeder import NFLDataSeeder, NFLDataHelpers

def process_standings(raw_standing):
    """Process raw standings from SportsDataIO"""
    return {
        "team": raw_standing.get('Team'),
        "season": NFLDataHelpers.safe_int(raw_standing.get('Season')),
        "season_type": NFLDataHelpers.safe_int(raw_standing.get('SeasonType')),
        
        # Basic info
        "name": raw_standing.get('Name'),
        "conference": raw_standing.get('Conference'),
        "division": raw_standing.get('Division'),
        
        # Record
        "wins": NFLDataHelpers.safe_int(raw_standing.get('Wins')),
        "losses": NFLDataHelpers.safe_int(raw_standing.get('Losses')),
        "ties": NFLDataHelpers.safe_int(raw_standing.get('Ties')),
        "win_percentage": NFLDataHelpers.safe_float(raw_standing.get('Percentage')),
        
        # Division/Conference record
        "division_wins": NFLDataHelpers.safe_int(raw_standing.get('DivisionWins')),
        "division_losses": NFLDataHelpers.safe_int(raw_standing.get('DivisionLosses')),
        "conference_wins": NFLDataHelpers.safe_int(raw_standing.get('ConferenceWins')),
        "conference_losses": NFLDataHelpers.safe_int(raw_standing.get('ConferenceLosses')),
        
        # Rankings
        "division_rank": NFLDataHelpers.safe_int(raw_standing.get('DivisionRank')),
        "conference_rank": NFLDataHelpers.safe_int(raw_standing.get('ConferenceRank')),
        
        # Points
        "points_for": NFLDataHelpers.safe_int(raw_standing.get('PointsFor')),
        "points_against": NFLDataHelpers.safe_int(raw_standing.get('PointsAgainst')),
        "net_points": NFLDataHelpers.safe_int(raw_standing.get('NetPoints')),
        
        # Streaks
        "streak": raw_standing.get('Streak'),
        "streak_type": raw_standing.get('StreakType'),
        "streak_length": NFLDataHelpers.safe_int(raw_standing.get('StreakLength')),
        
        # Head to head (stored as JSON for flexibility)
        "head_to_head": NFLDataHelpers.json_field(raw_standing.get('HeadToHeadWins', {}))
    }

def main():
    season = sys.argv[1] if len(sys.argv) > 1 else "2024"
    
    # Table schema
    columns = {
        "team": "VARCHAR(10)",
        "season": "INTEGER",
        "season_type": "INTEGER",
        
        # Composite primary key
        "PRIMARY KEY": "(team, season, season_type)",
        
        # Basic info
        "name": "VARCHAR(100)",
        "conference": "VARCHAR(10)",
        "division": "VARCHAR(20)",
        
        # Record
        "wins": "INTEGER",
        "losses": "INTEGER", 
        "ties": "INTEGER",
        "win_percentage": "FLOAT",
        
        # Division/Conference record
        "division_wins": "INTEGER",
        "division_losses": "INTEGER",
        "conference_wins": "INTEGER",
        "conference_losses": "INTEGER",
        
        # Rankings
        "division_rank": "INTEGER",
        "conference_rank": "INTEGER",
        
        # Points
        "points_for": "INTEGER",
        "points_against": "INTEGER",
        "net_points": "INTEGER",
        
        # Streaks
        "streak": "VARCHAR(10)",
        "streak_type": "VARCHAR(10)",
        "streak_length": "INTEGER",
        
        # Head to head data
        "head_to_head": "JSONB"
    }
    
    # Custom upsert since we have composite primary key
    def custom_upsert(seeder_instance, table_name, data, primary_key):
        """Custom upsert for composite primary key"""
        conn = seeder_instance.get_connection()
        cursor = conn.cursor()
        
        inserted = 0
        updated = 0
        errors = 0
        
        for i, record in enumerate(data):
            try:
                # Check if exists using composite key
                cursor.execute(
                    f'SELECT 1 FROM {table_name} WHERE team = %s AND season = %s AND season_type = %s',
                    (record['team'], record['season'], record['season_type'])
                )
                exists = cursor.fetchone()
                
                columns = list(record.keys())
                
                if exists:
                    # Update
                    set_clause = ", ".join([f"{col} = %s" for col in columns])
                    update_query = f"""UPDATE {table_name} SET {set_clause} 
                                     WHERE team = %s AND season = %s AND season_type = %s"""
                    values = [record[col] for col in columns]
                    values.extend([record['team'], record['season'], record['season_type']])
                    
                    cursor.execute(update_query, values)
                    updated += 1
                else:
                    # Insert
                    placeholders = ", ".join(["%s"] * len(columns))
                    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                    values = [record[col] for col in columns]
                    
                    cursor.execute(insert_query, values)
                    inserted += 1
                
                if i % 10 == 0:
                    conn.commit()
                    
            except Exception as e:
                print(f"  ❌ Error with team {record.get('team')}: {str(e)}")
                errors += 1
                conn.rollback()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return (inserted, updated, errors)
    
    # Seed the data
    seeder = NFLDataSeeder()
    api_url = f"https://api.sportsdata.io/v3/nfl/scores/json/Standings/{season}"
    
    success = seeder.seed_data_from_api(
        api_url=api_url,
        table_name=f"nfl_standings_{season}",
        columns=columns,
        processor=process_standings,
        primary_key="team"  # We'll handle composite key in custom upsert
    )
    
    if success:
        print(f"\n✨ {season} NFL standings are now in NeonDB!")
    else:
        print(f"\n❌ Failed to seed {season} NFL standings")

if __name__ == "__main__":
    main()