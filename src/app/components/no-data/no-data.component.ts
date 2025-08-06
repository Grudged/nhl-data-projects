import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-no-data',
  standalone: false,
  templateUrl: './no-data.component.html',
  styleUrls: ['./no-data.component.css']
})
export class NoDataComponent {
  @Input() selectedSport: string = 'nhl';
  @Input() selectedLeagueSeason: string = '';
  @Input() seasonTypeLabel: string = '';
}
