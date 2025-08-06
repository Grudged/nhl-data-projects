import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';

interface NHLGame {
  team: string;
  games_count: number;
  wins: number;
  losses: number;
  yet_to_play: number;
  total_goals: number;
}

interface NFLPlayer {
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

interface NHLDataResponse {
  nhldata: NHLGame[];
}

interface NFLDataResponse {
  nfldata: NFLPlayer[];
}

interface FantasyTeam {
  [key: string]: NFLPlayer[];
}

@Component({
  selector: 'app-root',
  standalone: false,
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {
  nhlData$!: Observable<NHLDataResponse>;
  nflData$!: Observable<NFLDataResponse>;
  private baseApiUrl = 'http://localhost:5000/api';
  
  selectedSport: string = 'nfl';
  searchTerm: string = '';
  sortBy: string = 'fantasy_points';
  sortDirection: 'asc' | 'desc' = 'desc';
  selectedSeasonType: string = 'preseason';
  selectedLeagueSeason: string = '2025';
  selectedOwner: string = 'Pretty Fly 4a Dicker Guy';
  isLoading: boolean = false;
  
  fantasyTeams: FantasyTeam = {
    'Pretty Fly 4a Dicker Guy': [],
    'BlevelandClowns': [],
    'Team 610jason': []
  };
  
  sports = [
    { value: 'nhl', label: 'NHL', icon: '🏒' },
    { value: 'nfl', label: 'NFL', icon: '🏈' }
  ];
  
  owners = [
    { value: 'Pretty Fly 4a Dicker Guy', label: 'Pretty Fly 4a Dicker Guy', icon: '👨' },
    { value: 'BlevelandClowns', label: 'BlevelandClowns', icon: '🧑' },
    { value: 'Team 610jason', label: 'Team 610jason', icon: '🧔' }
  ];
  
  seasonTypes = [
    { value: 'preseason', label: 'Preseason', icon: '🏃' },
    { value: 'regular', label: 'Regular', icon: '🏒' },
    { value: 'playoff', label: 'Playoffs', icon: '🏆' }
  ];
  
  leagueSeasons = [
    { value: '2024', label: '2024' },
    { value: '2025', label: '2025' }
  ];
  
  private nhlDataSubject = new BehaviorSubject<NHLGame[]>([]);
  private nflDataSubject = new BehaviorSubject<NFLPlayer[]>([]);

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadData();
  }

  private loadData(): void {
    this.isLoading = true;
    
    if (this.selectedSport === 'nhl') {
      this.loadNHLData();
    } else if (this.selectedSport === 'nfl') {
      this.loadNFLData();
    }
  }
  
  private loadNHLData(): void {
    this.nhlDataSubject.next([]);
    const apiUrl = `${this.baseApiUrl}/nhldata?season_type=${this.selectedSeasonType}&league_season=${this.selectedLeagueSeason}`;
    console.log('Loading NHL data from:', apiUrl);
    this.nhlData$ = this.http.get<NHLDataResponse>(apiUrl);
    this.nhlData$.subscribe({
      next: (data) => {
        console.log('Received NHL data:', data);
        const convertedData = data.nhldata.map(game => ({
          ...game,
          games_count: Number(game.games_count),
          wins: Number(game.wins),
          losses: Number(game.losses),
          yet_to_play: Number(game.yet_to_play),
          total_goals: Number(game.total_goals)
        }));
        this.nhlDataSubject.next(convertedData);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading NHL data:', error);
        this.isLoading = false;
      }
    });
  }
  
  private loadNFLData(): void {
    this.nflDataSubject.next([]);
    const apiUrl = `${this.baseApiUrl}/nfldata`;
    console.log('Loading NFL data from:', apiUrl);
    this.nflData$ = this.http.get<NFLDataResponse>(apiUrl);
    this.nflData$.subscribe({
      next: (data) => {
        console.log('Received NFL data:', data);
        const convertedData = data.nfldata.map(player => ({
          ...player,
          fantasy_points: Number(player.fantasy_points),
          touchdowns: Number(player.touchdowns),
          passing_yards: Number(player.passing_yards),
          rushing_yards: Number(player.rushing_yards),
          receiving_yards: Number(player.receiving_yards),
          fantasy_team_owner: player.fantasy_team_owner || undefined
        }));
        
        // Debug: Log players with team assignments
        const playersWithTeams = convertedData.filter(p => p.fantasy_team_owner);
        console.log('Players with fantasy team assignments:', playersWithTeams);
        
        this.nflDataSubject.next(convertedData);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading NFL data:', error);
        this.isLoading = false;
      }
    });
  }

  getFilteredAndSortedNHLData(): NHLGame[] {
    let data = this.nhlDataSubject.value;
    
    // Filter by search term
    if (this.searchTerm) {
      data = data.filter(game => 
        game.team.toLowerCase().includes(this.searchTerm.toLowerCase())
      );
    }
    
    // Sort data
    data = [...data].sort((a, b) => {
      let aVal = a[this.sortBy as keyof NHLGame];
      let bVal = b[this.sortBy as keyof NHLGame];
      
      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = (bVal as string).toLowerCase();
      }
      
      if (this.sortDirection === 'asc') {
        return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      } else {
        return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
      }
    });
    
    return data;
  }
  
  getFilteredAndSortedNFLData(): NFLPlayer[] {
    let data = this.nflDataSubject.value;
    
    // Filter by search term
    if (this.searchTerm) {
      data = data.filter(player => 
        player.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        player.team.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        player.position.toLowerCase().includes(this.searchTerm.toLowerCase())
      );
    }
    
    // Sort data
    data = [...data].sort((a, b) => {
      let aVal = a[this.sortBy as keyof NFLPlayer];
      let bVal = b[this.sortBy as keyof NFLPlayer];
      
      // Handle undefined values
      if (aVal === undefined && bVal === undefined) return 0;
      if (aVal === undefined) return 1;
      if (bVal === undefined) return -1;
      
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }
      
      if (this.sortDirection === 'asc') {
        return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      } else {
        return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
      }
    });
    
    return data;
  }
  
  getCurrentData(): (NHLGame | NFLPlayer)[] {
    if (this.selectedSport === 'nhl') {
      return this.getFilteredAndSortedNHLData();
    } else {
      return this.getFilteredAndSortedNFLData();
    }
  }

  sort(column: string): void {
    if (this.sortBy === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortBy = column;
      this.sortDirection = 'desc';
    }
  }

  onSortChange(): void {
    // Method called when sort dropdown changes
  }

  toggleSortDirection(): void {
    this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
  }

  getWinPercentage(game: NHLGame): number {
    const gamesPlayed = game.games_count - game.yet_to_play;
    return gamesPlayed > 0 ? (game.wins / gamesPlayed) * 100 : 0;
  }

  getTotalGames(data: NHLGame[]): number {
    return data.reduce((sum, game) => sum + game.games_count, 0);
  }

  getTotalGoals(data: NHLGame[]): number {
    return data.reduce((sum, game) => sum + game.total_goals, 0);
  }
  
  setSport(sport: string): void {
    this.selectedSport = sport;
    this.searchTerm = '';
    if (sport === 'nfl') {
      this.sortBy = 'fantasy_points';
    } else {
      this.sortBy = 'total_goals';
    }
    this.loadData();
  }
  
  setOwner(owner: string): void {
    this.selectedOwner = owner;
  }
  
  addPlayerToTeam(player: NFLPlayer): void {
    if (!player.fantasy_team_owner) {
      // Update the player object locally
      player.fantasy_team_owner = this.selectedOwner;
      
      // TODO: Make API call to update the database
      // Example: this.http.put(`${this.baseApiUrl}/nfldata/assign-player`, { 
      //   playerId: player.PlayerID, 
      //   owner: this.selectedOwner 
      // }).subscribe();
    }
  }
  
  removePlayerFromTeam(player: NFLPlayer): void {
    if (player.fantasy_team_owner === this.selectedOwner) {
      // Update the player object locally
      player.fantasy_team_owner = undefined;
      
      // TODO: Make API call to update the database
      // Example: this.http.put(`${this.baseApiUrl}/nfldata/unassign-player`, { 
      //   playerId: player.PlayerID 
      // }).subscribe();
    }
  }
  
  getFantasyTeam(): NFLPlayer[] {
    const team = this.nflDataSubject.value.filter(player => player.fantasy_team_owner === this.selectedOwner);
    console.log(`Fantasy team for ${this.selectedOwner}:`, team);
    console.log(`Total NFL players loaded:`, this.nflDataSubject.value.length);
    return team;
  }

  setSeasonType(seasonType: string): void {
    this.selectedSeasonType = seasonType;
    this.loadData();
  }

  setLeagueSeason(leagueSeason: string): void {
    this.selectedLeagueSeason = leagueSeason;
    this.loadData();
  }

  getSeasonTypeLabel(): string {
    const seasonType = this.seasonTypes.find(s => s.value === this.selectedSeasonType);
    return seasonType ? seasonType.label : '';
  }

  isPlayerInTeam(player: NFLPlayer): boolean {
    return player.fantasy_team_owner === this.selectedOwner;
  }

  getTotalFantasyPoints(): number {
    return this.getFantasyTeam().reduce((sum, p) => sum + p.fantasy_points, 0);
  }

}