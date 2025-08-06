import { Component, Input } from '@angular/core';
import { NHLGame } from '../../shared/interfaces';

@Component({
  selector: 'app-stats-overview',
  standalone: false,
  templateUrl: './stats-overview.component.html',
  styleUrls: ['./stats-overview.component.css']
})
export class StatsOverviewComponent {
  @Input() nhlData: NHLGame[] = [];

  getTotalGames(data: NHLGame[]): number {
    return data.reduce((sum, game) => sum + game.games_count, 0);
  }

  getTotalGoals(data: NHLGame[]): number {
    return data.reduce((sum, game) => sum + game.total_goals, 0);
  }
}
