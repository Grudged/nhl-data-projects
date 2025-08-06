import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-controls',
  standalone: false,
  templateUrl: './controls.component.html',
  styleUrls: ['./controls.component.css']
})
export class ControlsComponent {
  @Input() selectedSport: string = 'nhl';
  @Input() selectedSeasonType: string = 'preseason';
  @Input() selectedLeagueSeason: string = '2025';
  @Input() selectedOwner: string = 'Pretty Fly 4a Dicker Guy';
  @Input() searchTerm: string = '';
  @Input() sortBy: string = 'fantasy_points';
  @Input() sortDirection: 'asc' | 'desc' = 'desc';

  @Output() sportChange = new EventEmitter<string>();
  @Output() seasonTypeChange = new EventEmitter<string>();
  @Output() leagueSeasonChange = new EventEmitter<string>();
  @Output() ownerChange = new EventEmitter<string>();
  @Output() searchTermChange = new EventEmitter<string>();
  @Output() sortByChange = new EventEmitter<string>();
  @Output() sortDirectionToggle = new EventEmitter<void>();

  sports = [
    { value: 'nhl', label: 'NHL', icon: '🏒' },
    { value: 'nfl', label: 'NFL', icon: '🏈' }
  ];

  owners = [
    { value: 'Pretty Fly 4a Dicker Guy', label: 'Pretty Fly 4a Dicker Guy', icon: '👨' },
    { value: 'BlevelandClowns', label: 'BlevelandClowns', icon: '🧑🏾' },
    { value: 'Team 610jason', label: 'Team 610jason', icon: '🧑‍🦲' }
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

  setSport(sport: string): void {
    this.sportChange.emit(sport);
  }

  setSeasonType(seasonType: string): void {
    this.seasonTypeChange.emit(seasonType);
  }

  setLeagueSeason(leagueSeason: string): void {
    this.leagueSeasonChange.emit(leagueSeason);
  }

  setOwner(owner: string): void {
    this.ownerChange.emit(owner);
  }

  onSearchTermChange(searchTerm: string): void {
    this.searchTermChange.emit(searchTerm);
  }

  onSortChange(): void {
    this.sortByChange.emit(this.sortBy);
  }

  toggleSortDirection(): void {
    this.sortDirectionToggle.emit();
  }
}
