#!/usr/bin/env python3
"""
Example: Seed NFL Player Season Stats
Usage: python examples/seed_player_stats.py [season]
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nfl_data_seeder import NFLDataSeeder, NFLDataHelpers
import json

def process_player_stats(raw_player):
    """Process raw player stats from SportsDataIO"""
    return {
        "player_id": NFLDataHelpers.safe_int(raw_player.get('PlayerID')),
        "season": NFLDataHelpers.safe_int(raw_player.get('Season')),
        "season_type": NFLDataHelpers.safe_int(raw_player.get('SeasonType')),
        "team": raw_player.get('Team'),
        "name": raw_player.get('Name'),
        "position": raw_player.get('Position'),
        "number": NFLDataHelpers.safe_int(raw_player.get('Number')),
        
        # Passing stats
        "passing_attempts": NFLDataHelpers.safe_int(raw_player.get('PassingAttempts')),
        "passing_completions": NFLDataHelpers.safe_int(raw_player.get('PassingCompletions')),
        "passing_yards": NFLDataHelpers.safe_int(raw_player.get('PassingYards')),
        "passing_tds": NFLDataHelpers.safe_int(raw_player.get('PassingTouchdowns')),
        "passing_ints": NFLDataHelpers.safe_int(raw_player.get('PassingInterceptions')),
        "passing_rating": NFLDataHelpers.safe_float(raw_player.get('PassingRating')),
        
        # Rushing stats
        "rushing_attempts": NFLDataHelpers.safe_int(raw_player.get('RushingAttempts')),
        "rushing_yards": NFLDataHelpers.safe_int(raw_player.get('RushingYards')),
        "rushing_tds": NFLDataHelpers.safe_int(raw_player.get('RushingTouchdowns')),
        
        # Receiving stats
        "receptions": NFLDataHelpers.safe_int(raw_player.get('Receptions')),
        "receiving_yards": NFLDataHelpers.safe_int(raw_player.get('ReceivingYards')),
        "receiving_tds": NFLDataHelpers.safe_int(raw_player.get('ReceivingTouchdowns')),
        "targets": NFLDataHelpers.safe_int(raw_player.get('Targets')),
        
        # Fantasy stats
        "fantasy_points": NFLDataHelpers.safe_float(raw_player.get('FantasyPoints')),
        "fantasy_points_ppr": NFLDataHelpers.safe_float(raw_player.get('FantasyPointsPPR')),
        
        # Additional stats as JSON
        "additional_stats": NFLDataHelpers.json_field({
            k: v for k, v in raw_player.items() 
            if k not in ['PlayerID', 'Season', 'SeasonType', 'Team', 'Name', 'Position']
        })
    }

def main():
    season = sys.argv[1] if len(sys.argv) > 1 else "2024"
    
    # Table schema
    columns = {
        "player_id": "INTEGER PRIMARY KEY",
        "season": "INTEGER",
        "season_type": "INTEGER",
        "team": "VARCHAR(10)",
        "name": "VARCHAR(100)",
        "position": "VARCHAR(20)",
        "number": "INTEGER",
        
        # Passing
        "passing_attempts": "INTEGER",
        "passing_completions": "INTEGER", 
        "passing_yards": "INTEGER",
        "passing_tds": "INTEGER",
        "passing_ints": "INTEGER",
        "passing_rating": "FLOAT",
        
        # Rushing
        "rushing_attempts": "INTEGER",
        "rushing_yards": "INTEGER",
        "rushing_tds": "INTEGER",
        
        # Receiving
        "receptions": "INTEGER",
        "receiving_yards": "INTEGER",
        "receiving_tds": "INTEGER",
        "targets": "INTEGER",
        
        # Fantasy
        "fantasy_points": "FLOAT",
        "fantasy_points_ppr": "FLOAT",
        
        # Additional data
        "additional_stats": "JSONB"
    }
    
    # Seed the data
    seeder = NFLDataSeeder()
    api_url = f"https://api.sportsdata.io/v3/nfl/stats/json/PlayerSeasonStats/{season}"
    
    success = seeder.seed_data_from_api(
        api_url=api_url,
        table_name=f"nfl_player_stats_{season}",
        columns=columns,
        processor=process_player_stats,
        primary_key="player_id"
    )
    
    if success:
        print(f"\n✨ {season} NFL player stats are now in NeonDB!")
    else:
        print(f"\n❌ Failed to seed {season} NFL player stats")

if __name__ == "__main__":
    main()