import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { FormsModule } from "@angular/forms";
import { provideHttpClient } from "@angular/common/http";
import { AppComponent } from "./app.component";
import { HeaderComponent } from "./components/header/header.component";
import { ControlsComponent } from "./components/controls/controls.component";
import { StatsOverviewComponent } from "./components/stats-overview/stats-overview.component";
import { FantasyTeamComponent } from "./components/fantasy-team/fantasy-team.component";
import { NhlTableComponent } from "./components/nhl-table/nhl-table.component";
import { NflTableComponent } from "./components/nfl-table/nfl-table.component";
import { LoadingComponent } from "./components/loading/loading.component";
import { NoDataComponent } from "./components/no-data/no-data.component";

@NgModule({
    declarations: [
        AppComponent,
        HeaderComponent,
        ControlsComponent,
        StatsOverviewComponent,
        FantasyTeamComponent,
        NhlTableComponent,
        NflTableComponent,
        LoadingComponent,
        NoDataComponent
    ],
    imports: [BrowserModule, FormsModule],
    providers: [provideHttpClient()],
    bootstrap: [AppComponent]
})
export class AppModule {}