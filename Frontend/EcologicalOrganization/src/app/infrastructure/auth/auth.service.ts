import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap, throwError } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { TokenStorage } from './jwt/token.service';
import { environment } from 'src/env/environment';
import { JwtHelperService } from '@auth0/angular-jwt';
import { Login } from './model/login.model';
import { AuthenticationResponse } from './model/authentication-response.model';
import { User } from './model/user.model';
import { Registration, RoleType } from './model/registration.model';

export type Subsystem = 'WA';

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

interface AccessTokenPayload {
  sub: string;
  id: number;
  role: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  user$ = new BehaviorSubject<User>({ email: '', id: 0, role: '' });

  constructor(
    private http: HttpClient,
    private tokenStorage: TokenStorage,
    private router: Router
  ) {}

  login(login: Login): Observable<AuthenticationResponse> {
    const body = new URLSearchParams();
    body.set('username', login.username);
    body.set('password', login.password);

    return this.http
      .post<AuthenticationResponse>(
        `${environment.apiHost}auth/login`,
        body.toString(),
        {
          headers: new HttpHeaders({
            'Content-Type': 'application/x-www-form-urlencoded',
          }),
        }
      )
      .pipe(
        tap((tokenResponse) => {
          this.tokenStorage.saveAccessToken(tokenResponse.access_token);
          this.publishUserFromStoredToken();
        })
      );
  }

  loginToSubsystem(subsystem: Subsystem): Observable<TokenResponse> {
    const token = this.tokenStorage.getAccessToken();
    if (!token) {
      return throwError(() => new Error('Not logged in'));
    }
    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`,
    });

    return this.http
      .get<TokenResponse>(
        `${environment.apiHost}auth/login_to_subsystem/${subsystem}`,
        { headers }
      )
      .pipe(
        tap((tokenResponse) => {
          this.tokenStorage.saveAccessToken(tokenResponse.access_token);
          this.publishUserFromStoredToken();
        })
      );
  }

  register(
    registration: Registration
  ): Observable<unknown> {
    const roleBySubsystem: Record<Subsystem, RoleType | 'ADMIN'> = {
      WA: 'EMPLOYEE',
    };
    for (const subsystemRole of registration.roles) {
      if (['WA'].includes(subsystemRole.subsystem)) {
        roleBySubsystem[subsystemRole.subsystem as Subsystem] = subsystemRole.role;
      }
    }

    const payload = {
      email: registration.email,
      first_name: registration.name,
      last_name: registration.surname,
      password: registration.password,
      roles: roleBySubsystem,
    };

    return this.http.post<unknown>(
      `${environment.apiHost}auth/register-account`,
      payload
    );
  }

  logout(): void {
    this.tokenStorage.clear();
    this.user$.next({ email: '', id: 0, role: '' });
    this.router.navigate(['/login']);
  }

  restoreUserFromStoredToken(): void {
    const accessToken = this.tokenStorage.getAccessToken();
    if (!accessToken) return;
    this.publishUserFromStoredToken();
  }

  private publishUserFromStoredToken(): void {
    const jwtHelperService = new JwtHelperService();
    const accessToken = this.tokenStorage.getAccessToken() || '';
    try {
      const tokenPayload = jwtHelperService.decodeToken<AccessTokenPayload>(accessToken);
      if (!tokenPayload) throw new Error('Empty access token');
      this.user$.next({ id: tokenPayload.id, email: tokenPayload.sub, role: tokenPayload.role });
    } catch {
      this.user$.next({ email: '', id: 0, role: '' });
    }
  }

  isAuthenticated(): boolean {
    const token = this.tokenStorage.getAccessToken();
    if (!token) return false;
    const helper = new JwtHelperService();
    return !helper.isTokenExpired(token);
  }
}
