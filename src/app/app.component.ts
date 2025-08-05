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

interface NHLDataResponse {
  nhldata: NHLGame[];
}

@Component({
  selector: 'app-root',
  standalone: false,
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {
  nhlData$!: Observable<NHLDataResponse>;
  private baseApiUrl = 'https://nhl-data-projects-production.up.railway.app/api/nhldata';
  
  searchTerm: string = '';
  sortBy: string = 'total_goals';
  sortDirection: 'asc' | 'desc' = 'desc';
  selectedSeasonType: string = 'preseason';
  selectedLeagueSeason: string = '2025';
  isLoading: boolean = false;
  
  seasonTypes = [
    { value: 'preseason', label: 'Preseason', icon: '🏃' },
    { value: 'regular', label: 'Regular', icon: '🏒' },
    { value: 'playoff', label: 'Playoffs', icon: '🏆' }
  ];
  
  leagueSeasons = [
    { value: '2024', label: '2024' },
    { value: '2025', label: '2025' }
  ];
  
  private dataSubject = new BehaviorSubject<NHLGame[]>([]);

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadData();
  }

  private loadData(): void {
    // Clear the existing data first and set loading state
    this.dataSubject.next([]);
    this.isLoading = true;
    
    const apiUrl = `${this.baseApiUrl}?season_type=${this.selectedSeasonType}&league_season=${this.selectedLeagueSeason}`;
    console.log('Loading data from:', apiUrl); // Debug log
    this.nhlData$ = this.http.get<NHLDataResponse>(apiUrl);
    this.nhlData$.subscribe({
      next: (data) => {
        console.log('Received data:', data); // Debug log
        this.dataSubject.next(data.nhldata);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading data:', error);
        this.isLoading = false;
      }
    });
  }

  getFilteredAndSortedData(): NHLGame[] {
    let data = this.dataSubject.value;
    
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
}