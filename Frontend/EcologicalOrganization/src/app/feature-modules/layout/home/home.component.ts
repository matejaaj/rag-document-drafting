import { Component } from '@angular/core';
import {
  AuthService,
  Subsystem,
} from 'src/app/infrastructure/auth/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})
export class HomeComponent {
  constructor(private authService: AuthService, private router: Router) {}

  routeBySubsystem: Record<Subsystem, string> = {
    WA: '/writing-assistant',
  };

  enterSubsystem(subsystem: Subsystem, event?: Event) {
    event?.preventDefault();
    this.authService
      .loginToSubsystem(subsystem)
      .subscribe(() => this.router.navigate([this.routeBySubsystem[subsystem]]));
  }
}
