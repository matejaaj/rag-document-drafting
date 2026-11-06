import { Injectable } from '@angular/core';
import { ACCESS_TOKEN_STORAGE_KEY , USER_STORAGE_KEY } from '../../../shared/constants';

@Injectable({
    providedIn: 'root',
  })
  export class TokenStorage {
    constructor() {}

    saveAccessToken(token: string): void {
      localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
      localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, token);
    }

    getAccessToken() {
      return localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);
    }

    clear() {
      localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
      localStorage.removeItem(USER_STORAGE_KEY);
    }
  }
