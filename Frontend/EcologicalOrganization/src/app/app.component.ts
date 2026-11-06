import { Component, OnInit } from '@angular/core';
import { AuthService } from './infrastructure/auth/auth.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {
  title = 'EcologicalOrganization';

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.restoreUserFromStoredToken();
  }

  private restoreUserFromStoredToken(): void {
    this.authService.restoreUserFromStoredToken();
  }
}
