import { Component, Input, Output, EventEmitter } from '@angular/core';
import { NFLPlayer } from '../../shared/interfaces';

@Component({
  selector: 'app-nfl-table',
  standalone: false,
  templateUrl: './nfl-table.component.html',
  styleUrls: ['./nfl-table.component.css']
})
export class NflTableComponent {
  @Input() nflData: NFLPlayer[] = [];
  @Input() sortBy: string = '';
  @Input() sortDirection: 'asc' | 'desc' = 'desc';
  @Input() selectedOwner: string = '';

  @Output() sortChange = new EventEmitter<string>();
  @Output() addPlayer = new EventEmitter<NFLPlayer>();
  @Output() removePlayer = new EventEmitter<NFLPlayer>();

  sort(column: string): void {
    this.sortChange.emit(column);
  }

  isPlayerInTeam(player: NFLPlayer): boolean {
    return player.fantasy_team_owner === this.selectedOwner;
  }

  addPlayerToTeam(player: NFLPlayer): void {
    this.addPlayer.emit(player);
  }

  removePlayerFromTeam(player: NFLPlayer): void {
    this.removePlayer.emit(player);
  }
}
