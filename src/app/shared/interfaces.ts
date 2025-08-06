export interface NHLGame {
  team: string;
  games_count: number;
  wins: number;
  losses: number;
  yet_to_play: number;
  total_goals: number;
}

export interface NFLPlayer {
  name: string;
  team: string;
  position: string;
  fantasy_points: number;
  touchdowns: number;
  passing_yards: number;
  rushing_yards: number;
  receiving_yards: number;
  receptions: number;
  tackles: number;
  sacks: number;
  interceptions: number;
  fantasy_team_owner?: string;
}

export interface NHLDataResponse {
  nhldata: NHLGame[];
}

export interface NFLDataResponse {
  nfldata: NFLPlayer[];
}

export interface FantasyTeam {
  [key: string]: NFLPlayer[];
}
