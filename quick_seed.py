#!/usr/bin/env python3
"""
Quick NFL Data Seeder - One-liner for common data types
Usage: python quick_seed.py [data_type] [season]

Examples:
  python quick_seed.py schedule 2024
  python quick_seed.py players 2024  
  python quick_seed.py teams 2024
  python quick_seed.py standings 2024
"""

import sys
from nfl_data_seeder import NFLDataSeeder, NFLDataHelpers
import json

def schedule_processor(raw_game):
    """Process schedule data"""
    if not raw_game.get('GameKey'):
        return None  # Skip BYE weeks
        
    return {
        "game_key": raw_game.get('GameKey'),
        "season": NFLDataHelpers.safe_int(raw_game.get('Season')),
        "week": NFLDataHelpers.safe_int(raw_game.get('Week')),
        "date": raw_game.get('Date'),
        "away_team": raw_game.get('AwayTeam'),
        "home_team": raw_game.get('HomeTeam'),
        "channel": raw_game.get('Channel'),
        "point_spread": NFLDataHelpers.safe_float(raw_game.get('PointSpread')),
        "over_under": NFLDataHelpers.safe_float(raw_game.get('OverUnder')),
        "status": raw_game.get('Status'),
        "stadium_details": NFLDataHelpers.json_field(raw_game.get('StadiumDetails'))
    }

def players_processor(raw_player):
    """Process player stats"""
    return {
        "player_id": NFLDataHelpers.safe_int(raw_player.get('PlayerID')),
        "name": raw_player.get('Name'),
        "team": raw_player.get('Team'),
        "position": raw_player.get('Position'),
        "season": NFLDataHelpers.safe_int(raw_player.get('Season')),
        "passing_yards": NFLDataHelpers.safe_int(raw_player.get('PassingYards')),
        "rushing_yards": NFLDataHelpers.safe_int(raw_player.get('RushingYards')),
        "receiving_yards": NFLDataHelpers.safe_int(raw_player.get('ReceivingYards')),
        "fantasy_points": NFLDataHelpers.safe_float(raw_player.get('FantasyPoints')),
        "all_stats": NFLDataHelpers.json_field(raw_player)
    }

def teams_processor(raw_team):
    """Process team stats"""
    return {
        "team": raw_team.get('Team'),
        "name": raw_team.get('Name'),
        "season": NFLDataHelpers.safe_int(raw_team.get('Season')),
        "wins": NFLDataHelpers.safe_int(raw_team.get('Wins')),
        "losses": NFLDataHelpers.safe_int(raw_team.get('Losses')),
        "points_for": NFLDataHelpers.safe_int(raw_team.get('PointsFor')),
        "points_against": NFLDataHelpers.safe_int(raw_team.get('PointsAgainst')),
        "all_stats": NFLDataHelpers.json_field(raw_team)
    }

def standings_processor(raw_standing):
    """Process standings"""
    return {
        "team": raw_standing.get('Team'),
        "season": NFLDataHelpers.safe_int(raw_standing.get('Season')),
        "conference": raw_standing.get('Conference'),
        "division": raw_standing.get('Division'),
        "wins": NFLDataHelpers.safe_int(raw_standing.get('Wins')),
        "losses": NFLDataHelpers.safe_int(raw_standing.get('Losses')),
        "win_percentage": NFLDataHelpers.safe_float(raw_standing.get('Percentage')),
        "division_rank": NFLDataHelpers.safe_int(raw_standing.get('DivisionRank'))
    }

CONFIGS = {
    "schedule": {
        "url": "https://api.sportsdata.io/v3/nfl/scores/json/Schedules/{season}",
        "table": "nfl_schedule_{season}",
        "processor": schedule_processor,
        "primary_key": "game_key",
        "columns": {
            "game_key": "VARCHAR(20) PRIMARY KEY",
            "season": "INTEGER",
            "week": "INTEGER", 
            "date": "VARCHAR(50)",
            "away_team": "VARCHAR(10)",
            "home_team": "VARCHAR(10)",
            "channel": "VARCHAR(50)",
            "point_spread": "FLOAT",
            "over_under": "FLOAT",
            "status": "VARCHAR(20)",
            "stadium_details": "JSONB"
        }
    },
    
    "players": {
        "url": "https://api.sportsdata.io/v3/nfl/stats/json/PlayerSeasonStats/{season}",
        "table": "nfl_players_{season}",
        "processor": players_processor,
        "primary_key": "player_id",
        "columns": {
            "player_id": "INTEGER PRIMARY KEY",
            "name": "VARCHAR(100)",
            "team": "VARCHAR(10)",
            "position": "VARCHAR(20)",
            "season": "INTEGER",
            "passing_yards": "INTEGER",
            "rushing_yards": "INTEGER", 
            "receiving_yards": "INTEGER",
            "fantasy_points": "FLOAT",
            "all_stats": "JSONB"
        }
    },
    
    "teams": {
        "url": "https://api.sportsdata.io/v3/nfl/stats/json/TeamSeasonStats/{season}",
        "table": "nfl_teams_{season}",
        "processor": teams_processor,
        "primary_key": "team",
        "columns": {
            "team": "VARCHAR(10) PRIMARY KEY",
            "name": "VARCHAR(100)",
            "season": "INTEGER",
            "wins": "INTEGER",
            "losses": "INTEGER",
            "points_for": "INTEGER",
            "points_against": "INTEGER",
            "all_stats": "JSONB"
        }
    },
    
    "standings": {
        "url": "https://api.sportsdata.io/v3/nfl/scores/json/Standings/{season}",
        "table": "nfl_standings_{season}",
        "processor": standings_processor,
        "primary_key": "team",
        "columns": {
            "team": "VARCHAR(10) PRIMARY KEY",
            "season": "INTEGER",
            "conference": "VARCHAR(10)",
            "division": "VARCHAR(20)",
            "wins": "INTEGER",
            "losses": "INTEGER", 
            "win_percentage": "FLOAT",
            "division_rank": "INTEGER"
        }
    }
}

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_seed.py [data_type] [season]")
        print(f"Available types: {', '.join(CONFIGS.keys())}")
        sys.exit(1)
    
    data_type = sys.argv[1].lower()
    season = sys.argv[2] if len(sys.argv) > 2 else "2024"
    
    if data_type not in CONFIGS:
        print(f"❌ Unknown data type: {data_type}")
        print(f"Available types: {', '.join(CONFIGS.keys())}")
        sys.exit(1)
    
    config = CONFIGS[data_type]
    
    # Format URL and table name with season
    url = config["url"].format(season=season)
    table_name = config["table"].format(season=season)
    
    print(f"🏈 Quick seeding {data_type} data for {season} season")
    
    # Seed the data
    seeder = NFLDataSeeder()
    success = seeder.seed_data_from_api(
        api_url=url,
        table_name=table_name,
        columns=config["columns"],
        processor=config["processor"],
        primary_key=config["primary_key"]
    )
    
    if success:
        print(f"\n✨ {data_type.title()} data for {season} is now in NeonDB!")
        print(f"   Table: {table_name}")
    else:
        print(f"\n❌ Failed to seed {data_type} data")

if __name__ == "__main__":
    main()