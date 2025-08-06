import { Component, Input, Output, EventEmitter } from '@angular/core';
import { NHLGame } from '../../shared/interfaces';

@Component({
  selector: 'app-nhl-table',
  standalone: false,
  templateUrl: './nhl-table.component.html',
  styleUrls: ['./nhl-table.component.css']
})
export class NhlTableComponent {
  @Input() nhlData: NHLGame[] = [];
  @Input() sortBy: string = '';
  @Input() sortDirection: 'asc' | 'desc' = 'desc';

  @Output() sortChange = new EventEmitter<string>();

  sort(column: string): void {
    this.sortChange.emit(column);
  }

  getWinPercentage(game: NHLGame): number {
    const gamesPlayed = game.games_count - game.yet_to_play;
    return gamesPlayed > 0 ? (game.wins / gamesPlayed) * 100 : 0;
  }
}
