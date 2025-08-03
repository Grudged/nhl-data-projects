import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

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
  private apiUrl = 'http://127.0.0.1:5000/api/nhldata'; // Flask API URL

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.nhlData$ = this.http.get<NHLDataResponse>(this.apiUrl);
  }
}