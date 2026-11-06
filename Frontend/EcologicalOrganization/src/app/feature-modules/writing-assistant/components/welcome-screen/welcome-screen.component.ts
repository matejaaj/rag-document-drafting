import { Component, EventEmitter, Output } from '@angular/core';

@Component({
  selector: 'wa-welcome-screen',
  templateUrl: './welcome-screen.component.html',
  styleUrls: ['./welcome-screen.component.css'],
})
export class WelcomeScreenComponent {
  @Output() createRequested = new EventEmitter<void>();
}
