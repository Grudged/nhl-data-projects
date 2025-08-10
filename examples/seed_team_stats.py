#!/usr/bin/env python3
"""
Example: Seed NFL Team Season Stats
Usage: python examples/seed_team_stats.py [season]
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nfl_data_seeder import NFLDataSeeder, NFLDataHelpers

def process_team_stats(raw_team):
    """Process raw team stats from SportsDataIO"""
    return {
        "team": raw_team.get('Team'),
        "season": NFLDataHelpers.safe_int(raw_team.get('Season')),
        "season_type": NFLDataHelpers.safe_int(raw_team.get('SeasonType')),
        
        # Basic info
        "name": raw_team.get('Name'),
        "conference": raw_team.get('Conference'),
        "division": raw_team.get('Division'),
        
        # Record
        "wins": NFLDataHelpers.safe_int(raw_team.get('Wins')),
        "losses": NFLDataHelpers.safe_int(raw_team.get('Losses')),
        "ties": NFLDataHelpers.safe_int(raw_team.get('Ties')),
        "win_percentage": NFLDataHelpers.safe_float(raw_team.get('Percentage')),
        
        # Scoring
        "points_for": NFLDataHelpers.safe_int(raw_team.get('PointsFor')),
        "points_against": NFLDataHelpers.safe_int(raw_team.get('PointsAgainst')),
        "net_points": NFLDataHelpers.safe_int(raw_team.get('NetPoints')),
        
        # Offensive stats
        "touchdowns": NFLDataHelpers.safe_int(raw_team.get('Touchdowns')),
        "rushing_attempts": NFLDataHelpers.safe_int(raw_team.get('RushingAttempts')),
        "rushing_yards": NFLDataHelpers.safe_int(raw_team.get('RushingYards')),
        "rushing_tds": NFLDataHelpers.safe_int(raw_team.get('RushingTouchdowns')),
        
        "passing_attempts": NFLDataHelpers.safe_int(raw_team.get('PassingAttempts')),
        "passing_completions": NFLDataHelpers.safe_int(raw_team.get('PassingCompletions')),
        "passing_yards": NFLDataHelpers.safe_int(raw_team.get('PassingYards')),
        "passing_tds": NFLDataHelpers.safe_int(raw_team.get('PassingTouchdowns')),
        "passing_ints": NFLDataHelpers.safe_int(raw_team.get('PassingInterceptions')),
        
        # Defensive stats
        "opponent_points": NFLDataHelpers.safe_int(raw_team.get('OpponentPointsFor')),
        "opponent_touchdowns": NFLDataHelpers.safe_int(raw_team.get('OpponentTouchdowns')),
        "opponent_rushing_yards": NFLDataHelpers.safe_int(raw_team.get('OpponentRushingYards')),
        "opponent_passing_yards": NFLDataHelpers.safe_int(raw_team.get('OpponentPassingYards')),
        
        # Turnovers
        "turnovers": NFLDataHelpers.safe_int(raw_team.get('Turnovers')),
        "opponent_turnovers": NFLDataHelpers.safe_int(raw_team.get('OpponentTurnovers')),
        "turnover_differential": NFLDataHelpers.safe_int(raw_team.get('TurnoverDifferential')),
        
        # Additional stats as JSON
        "additional_stats": NFLDataHelpers.json_field({
            k: v for k, v in raw_team.items() 
            if k not in ['Team', 'Season', 'SeasonType', 'Name', 'Conference', 'Division']
        })
    }

def main():
    season = sys.argv[1] if len(sys.argv) > 1 else "2024"
    
    # Table schema
    columns = {
        "team": "VARCHAR(10) PRIMARY KEY",
        "season": "INTEGER",
        "season_type": "INTEGER",
        
        # Basic info
        "name": "VARCHAR(100)",
        "conference": "VARCHAR(10)",
        "division": "VARCHAR(20)",
        
        # Record
        "wins": "INTEGER",
        "losses": "INTEGER",
        "ties": "INTEGER", 
        "win_percentage": "FLOAT",
        
        # Scoring
        "points_for": "INTEGER",
        "points_against": "INTEGER",
        "net_points": "INTEGER",
        
        # Offensive stats
        "touchdowns": "INTEGER",
        "rushing_attempts": "INTEGER",
        "rushing_yards": "INTEGER",
        "rushing_tds": "INTEGER",
        "passing_attempts": "INTEGER",
        "passing_completions": "INTEGER",
        "passing_yards": "INTEGER",
        "passing_tds": "INTEGER",
        "passing_ints": "INTEGER",
        
        # Defensive stats
        "opponent_points": "INTEGER",
        "opponent_touchdowns": "INTEGER",
        "opponent_rushing_yards": "INTEGER",
        "opponent_passing_yards": "INTEGER",
        
        # Turnovers
        "turnovers": "INTEGER",
        "opponent_turnovers": "INTEGER",
        "turnover_differential": "INTEGER",
        
        # Additional data
        "additional_stats": "JSONB"
    }
    
    # Seed the data
    seeder = NFLDataSeeder()
    api_url = f"https://api.sportsdata.io/v3/nfl/stats/json/TeamSeasonStats/{season}"
    
    success = seeder.seed_data_from_api(
        api_url=api_url,
        table_name=f"nfl_team_stats_{season}",
        columns=columns,
        processor=process_team_stats,
        primary_key="team"
    )
    
    if success:
        print(f"\n✨ {season} NFL team stats are now in NeonDB!")
    else:
        print(f"\n❌ Failed to seed {season} NFL team stats")

if __name__ == "__main__":
    main()