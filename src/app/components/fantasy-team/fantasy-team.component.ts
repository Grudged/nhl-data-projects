import { Component, Input, Output, EventEmitter } from '@angular/core';
import { NFLPlayer } from '../../shared/interfaces';

@Component({
  selector: 'app-fantasy-team',
  standalone: false,
  templateUrl: './fantasy-team.component.html',
  styleUrls: ['./fantasy-team.component.css']
})
export class FantasyTeamComponent {
  @Input() selectedOwner: string = '';
  @Input() fantasyTeam: NFLPlayer[] = [];

  @Output() removePlayer = new EventEmitter<NFLPlayer>();

  getTotalFantasyPoints(): number {
    return this.fantasyTeam.reduce((sum, p) => sum + p.fantasy_points, 0);
  }

  removePlayerFromTeam(player: NFLPlayer): void {
    this.removePlayer.emit(player);
  }
}
