import { Component, Input, Output, EventEmitter, Renderer2, ElementRef } from '@angular/core';
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

  showDialog: boolean = false;
  private dialogElement: HTMLElement | null = null;

  constructor(private renderer: Renderer2, private elementRef: ElementRef) {}

  getTotalFantasyPoints(): number {
    return this.fantasyTeam.reduce((sum, p) => sum + p.fantasy_points, 0);
  }

  removePlayerFromTeam(player: NFLPlayer): void {
    this.removePlayer.emit(player);
  }

  showPoopDialog(): void {
    this.showDialog = true;
    this.createDialog();
  }

  closeDialog(): void {
    this.showDialog = false;
    this.removeDialog();
  }

  private createDialog(): void {
    // Create dialog overlay
    const overlay = this.renderer.createElement('div');
    this.renderer.addClass(overlay, 'poop-dialog-overlay');
    this.renderer.setStyle(overlay, 'position', 'fixed');
    this.renderer.setStyle(overlay, 'top', '0');
    this.renderer.setStyle(overlay, 'left', '0');
    this.renderer.setStyle(overlay, 'width', '100vw');
    this.renderer.setStyle(overlay, 'height', '100vh');
    this.renderer.setStyle(overlay, 'background', 'rgba(0,0,0,0.9)');
    this.renderer.setStyle(overlay, 'display', 'flex');
    this.renderer.setStyle(overlay, 'justify-content', 'center');
    this.renderer.setStyle(overlay, 'align-items', 'center');
    this.renderer.setStyle(overlay, 'z-index', '2147483647');
    
    // Create dialog content
    const content = this.renderer.createElement('div');
    this.renderer.addClass(content, 'poop-dialog-content');
    this.renderer.setStyle(content, 'background', 'linear-gradient(135deg, #FF1493, #FF6347, #FFD700)');
    this.renderer.setStyle(content, 'border', '5px solid #FF0000');
    this.renderer.setStyle(content, 'border-radius', '30px');
    this.renderer.setStyle(content, 'max-width', '600px');
    this.renderer.setStyle(content, 'width', '90%');
    this.renderer.setStyle(content, 'box-shadow', '0 20px 50px rgba(0,0,0,0.5)');
    this.renderer.setStyle(content, 'overflow', 'hidden');
    this.renderer.setStyle(content, 'animation', 'popIn 0.5s ease-out');
    
    // Create header
    const header = this.renderer.createElement('div');
    this.renderer.setStyle(header, 'background', 'linear-gradient(135deg, #8B0000, #FF4500)');
    this.renderer.setStyle(header, 'padding', '1.5rem');
    this.renderer.setStyle(header, 'text-align', 'center');
    this.renderer.setStyle(header, 'border-bottom', '3px solid #FFD700');
    
    const headerTitle = this.renderer.createElement('h2');
    this.renderer.setStyle(headerTitle, 'color', '#FFD700');
    this.renderer.setStyle(headerTitle, 'font', '900 1.5rem "Inter", system-ui, sans-serif');
    this.renderer.setStyle(headerTitle, 'margin', '0');
    this.renderer.setStyle(headerTitle, 'text-shadow', '3px 3px 6px rgba(0,0,0,0.7)');
    this.renderer.setStyle(headerTitle, 'animation', 'pulse 1s ease-in-out infinite');
    const headerText = this.renderer.createText('🤡 👉 IMPORTANT QUESTION 👈 🤡');
    this.renderer.appendChild(headerTitle, headerText);
    this.renderer.appendChild(header, headerTitle);
    
    // Create body
    const body = this.renderer.createElement('div');
    this.renderer.setStyle(body, 'padding', '2rem');
    this.renderer.setStyle(body, 'text-align', 'center');
    this.renderer.setStyle(body, 'background', 'linear-gradient(135deg, #FFD700, #FFA500)');
    
    const question = this.renderer.createElement('h1');
    this.renderer.setStyle(question, 'color', '#8B0000');
    this.renderer.setStyle(question, 'font', '900 2.5rem "Inter", system-ui, sans-serif');
    this.renderer.setStyle(question, 'margin', '0 0 1rem 0');
    this.renderer.setStyle(question, 'text-shadow', '3px 3px 6px rgba(0,0,0,0.3)');
    this.renderer.setStyle(question, 'animation', 'shake 0.5s ease-in-out infinite');
    const questionText = this.renderer.createText('💩 ARE YOU POOPING?? 💩');
    this.renderer.appendChild(question, questionText);
    
    const emojiParade = this.renderer.createElement('div');
    this.renderer.setStyle(emojiParade, 'font-size', '2rem');
    this.renderer.setStyle(emojiParade, 'margin', '1rem 0');
    this.renderer.setStyle(emojiParade, 'animation', 'rainbowText 2s ease-in-out infinite');
    const emojiText = this.renderer.createText('💩 👉 🤡 💩 👉 🤡 💩 👉 🤡');
    this.renderer.appendChild(emojiParade, emojiText);
    
    this.renderer.appendChild(body, question);
    this.renderer.appendChild(body, emojiParade);
    
    // Create footer
    const footer = this.renderer.createElement('div');
    this.renderer.setStyle(footer, 'padding', '1.5rem');
    this.renderer.setStyle(footer, 'text-align', 'center');
    this.renderer.setStyle(footer, 'background', 'linear-gradient(135deg, #FF4500, #FF1493)');
    this.renderer.setStyle(footer, 'border-top', '3px solid #FFD700');
    
    const closeButton = this.renderer.createElement('button');
    this.renderer.setStyle(closeButton, 'background', 'linear-gradient(135deg, #32CD32, #228B22)');
    this.renderer.setStyle(closeButton, 'color', '#fff');
    this.renderer.setStyle(closeButton, 'border', '3px solid #FFD700');
    this.renderer.setStyle(closeButton, 'border-radius', '20px');
    this.renderer.setStyle(closeButton, 'padding', '1rem 2rem');
    this.renderer.setStyle(closeButton, 'font', '700 1rem "Inter", system-ui, sans-serif');
    this.renderer.setStyle(closeButton, 'cursor', 'pointer');
    this.renderer.setStyle(closeButton, 'transition', 'all 0.3s ease');
    this.renderer.setStyle(closeButton, 'box-shadow', '0 6px 15px rgba(0,0,0,0.3)');
    this.renderer.setStyle(closeButton, 'text-shadow', '2px 2px 4px rgba(0,0,0,0.5)');
    const buttonText = this.renderer.createText('🤡 Close This Masterpiece 🤡');
    this.renderer.appendChild(closeButton, buttonText);
    this.renderer.appendChild(footer, closeButton);
    
    // Assemble dialog
    this.renderer.appendChild(content, header);
    this.renderer.appendChild(content, body);
    this.renderer.appendChild(content, footer);
    this.renderer.appendChild(overlay, content);
    
    // Add event listeners
    this.renderer.listen(overlay, 'click', () => this.closeDialog());
    this.renderer.listen(content, 'click', (event) => event.stopPropagation());
    this.renderer.listen(closeButton, 'click', () => this.closeDialog());
    
    // Append to document body
    this.renderer.appendChild(document.body, overlay);
    this.dialogElement = overlay;
  }

  private removeDialog(): void {
    if (this.dialogElement) {
      this.renderer.removeChild(document.body, this.dialogElement);
      this.dialogElement = null;
    }
  }
}
