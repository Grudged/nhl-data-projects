import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-header',
  standalone: false,
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {
  @Input() selectedSport: string = 'nhl';
  @Output() sportChange = new EventEmitter<string>();
  @Output() tabChange = new EventEmitter<string>();
  
  selectedNFLTab: string = 'players';
  
  sports = [
    { value: 'nhl', label: 'NHL', icon: '🏒' },
    { value: 'nfl', label: 'NFL', icon: '🏈' }
  ];
  
  nflTabs = [
    { value: 'players', label: 'All Players', icon: '👥' },
    { value: 'draft', label: 'Draft Board', icon: '📋' }
  ];
  
  onSportChange(sport: string): void {
    this.sportChange.emit(sport);
  }
  
  onTabChange(tab: string): void {
    this.selectedNFLTab = tab;
    this.tabChange.emit(tab);
  }
}
