#!/usr/bin/env python3
"""
Example: Seed Custom NFL Data (from your own data sources)
This shows how to use the seeder with your own data, not from SportsDataIO
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nfl_data_seeder import NFLDataSeeder, NFLDataHelpers

def process_custom_data(raw_data):
    """Process your custom data format"""
    # Example: processing custom injury report data
    return {
        "player_id": NFLDataHelpers.safe_int(raw_data.get('id')),
        "player_name": raw_data.get('name'),
        "team": raw_data.get('team'),
        "position": raw_data.get('pos'),
        "injury_status": raw_data.get('status'),  # 'OUT', 'QUESTIONABLE', etc.
        "injury_description": raw_data.get('injury'),
        "week": NFLDataHelpers.safe_int(raw_data.get('week')),
        "season": NFLDataHelpers.safe_int(raw_data.get('season')),
        "last_updated": raw_data.get('updated'),
        
        # Store original data as JSON for reference
        "raw_data": NFLDataHelpers.json_field(raw_data)
    }

def main():
    # Example custom data (could be from CSV, JSON file, scraping, etc.)
    custom_data = [
        {
            "id": 1001,
            "name": "Aaron Rodgers",
            "team": "NYJ",
            "pos": "QB",
            "status": "OUT",
            "injury": "Ankle",
            "week": 1,
            "season": 2025,
            "updated": "2025-01-10T10:00:00Z"
        },
        {
            "id": 1002,
            "name": "Christian McCaffrey", 
            "team": "SF",
            "pos": "RB",
            "status": "QUESTIONABLE",
            "injury": "Knee",
            "week": 1,
            "season": 2025,
            "updated": "2025-01-10T09:30:00Z"
        }
        # Add more data...
    ]
    
    # Table schema
    columns = {
        "player_id": "INTEGER PRIMARY KEY",
        "player_name": "VARCHAR(100)",
        "team": "VARCHAR(10)",
        "position": "VARCHAR(20)",
        "injury_status": "VARCHAR(20)",
        "injury_description": "VARCHAR(200)",
        "week": "INTEGER",
        "season": "INTEGER", 
        "last_updated": "TIMESTAMP",
        "raw_data": "JSONB"
    }
    
    # Seed the data
    seeder = NFLDataSeeder()
    
    success = seeder.seed_data_from_dict(
        data=custom_data,
        table_name="nfl_injury_reports",
        columns=columns,
        processor=process_custom_data,
        primary_key="player_id"
    )
    
    if success:
        print(f"\n✨ Custom NFL injury data is now in NeonDB!")
    else:
        print(f"\n❌ Failed to seed custom NFL data")

if __name__ == "__main__":
    main()