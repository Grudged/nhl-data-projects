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
  selectedOwner: string = 'chris';
  isLoading: boolean = false;
  
  fantasyTeams: FantasyTeam = {
    chris: [],
    aaron: [],
    jay: []
  };
  
  sports = [
    { value: 'nhl', label: 'NHL', icon: '🏒' },
    { value: 'nfl', label: 'NFL', icon: '🏈' }
  ];
  
  owners = [
    { value: 'chris', label: 'Pretty Fly 4a Dicker Guy', icon: '👨' },
    { value: 'aaron', label: 'BlevelandClowns', icon: '🧑' },
    { value: 'jay', label: 'Team 610jason', icon: '🧔' }
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
    if (this.selectedSport === 'nfl') {
      this.loadFantasyTeams();
    }
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
        this.nhlDataSubject.next(data.nhldata);
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
        this.nflDataSubject.next(data.nfldata);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading NFL data:', error);
        this.isLoading = false;
      }
    });
  }
  
  private loadFantasyTeams(): void {
    const apiUrl = `${this.baseApiUrl}/fantasy-teams`;
    this.http.get<{fantasy_teams: FantasyTeam}>(apiUrl).subscribe({
      next: (data) => {
        this.fantasyTeams = data.fantasy_teams;
      },
      error: (error) => {
        console.error('Error loading fantasy teams:', error);
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
      this.loadFantasyTeams();
    } else {
      this.sortBy = 'total_goals';
    }
    this.loadData();
  }
  
  setOwner(owner: string): void {
    this.selectedOwner = owner;
  }
  
  addPlayerToTeam(player: NFLPlayer): void {
    if (!this.fantasyTeams[this.selectedOwner].find(p => p.name === player.name)) {
      this.fantasyTeams[this.selectedOwner].push(player);
    }
  }
  
  removePlayerFromTeam(player: NFLPlayer): void {
    const team = this.fantasyTeams[this.selectedOwner];
    const index = team.findIndex(p => p.name === player.name);
    if (index > -1) {
      team.splice(index, 1);
    }
  }
  
  getFantasyTeam(): NFLPlayer[] {
    return this.fantasyTeams[this.selectedOwner] || [];
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
    return this.fantasyTeams[this.selectedOwner]?.find(p => p.name === player.name) !== undefined;
  }

  getTotalFantasyPoints(): number {
    return this.getFantasyTeam().reduce((sum, p) => sum + p.fantasy_points, 0);
  }
}