import { Component, Input, Output, EventEmitter } from '@angular/core';
import { NFLPlayer } from '../../shared/interfaces';

@Component({
  selector: 'app-draft-board',
  standalone: false,
  templateUrl: './draft-board.component.html',
  styleUrls: ['./draft-board.component.css']
})
export class DraftBoardComponent {
  @Input() nflData: NFLPlayer[] = [];
  @Input() selectedOwner: string = '';
  @Input() owners: any[] = [];
  @Output() ownerChange = new EventEmitter<string>();
  @Output() addPlayer = new EventEmitter<NFLPlayer>();
  @Output() removePlayer = new EventEmitter<NFLPlayer>();
  
  positionFilter: string = '';
  positions = ['', 'QB', 'RB', 'WR', 'TE', 'K', 'DEF'];
  
  setOwner(owner: string): void {
    this.ownerChange.emit(owner);
  }
  
  setPositionFilter(position: string): void {
    this.positionFilter = position;
  }
  
  getAvailablePlayers(): NFLPlayer[] {
    let players = this.nflData.filter(p => !p.fantasy_team_owner);
    
    if (this.positionFilter) {
      players = players.filter(p => p.position === this.positionFilter);
    }
    
    return players.sort((a, b) => b.fantasy_points - a.fantasy_points).slice(0, 50);
  }
  
  getFantasyTeam(): NFLPlayer[] {
    return this.nflData.filter(player => player.fantasy_team_owner === this.selectedOwner);
  }
  
  getTotalFantasyPoints(): number {
    return this.getFantasyTeam().reduce((sum, p) => sum + p.fantasy_points, 0);
  }
  
  onAddPlayer(player: NFLPlayer): void {
    this.addPlayer.emit(player);
  }
  
  onRemovePlayer(player: NFLPlayer): void {
    this.removePlayer.emit(player);
  }
}