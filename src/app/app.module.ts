import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { FormsModule } from "@angular/forms";
import { provideHttpClient } from "@angular/common/http";
import { AppComponent } from "./app.component";

@NgModule({
    declarations: [AppComponent],
    imports: [BrowserModule, FormsModule],
    providers: [provideHttpClient()],
    bootstrap: [AppComponent]
})
export class AppModule {}