import { Component } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Registration, RoleType } from '../model/registration.model';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-registration',
  templateUrl: './registration.component.html',
  styleUrls: ['./registration.component.css'],
})
export class RegistrationComponent {
  subsystems = ['WA'] as const;

  registrationForm = new FormGroup({
    name: new FormControl('', [Validators.required]),
    surname: new FormControl('', [Validators.required]),
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', [Validators.required]),

    WA: new FormControl<RoleType>('EMPLOYEE', [Validators.required]),
  });

  constructor(private authService: AuthService, private snackBar: MatSnackBar) {}

  register(): void {
    if (this.registrationForm.invalid) return;

    const formValue = this.registrationForm.value;

    const registration: Registration = {
      name: formValue.name || '',
      surname: formValue.surname || '',
      email: formValue.email || '',
      password: formValue.password || '',
      roles: this.subsystems.map((subsystem) => ({
        subsystem,
        role: (formValue[subsystem] as RoleType) ?? 'EMPLOYEE',
      })),
    };

    this.authService.register(registration).subscribe({
      next: () => {
        this.snackBar.open('Korisnik je napravljen', 'Zatvori', { duration: 5000 });

        this.registrationForm.reset({
          name: '',
          surname: '',
          email: '',
          password: '',
          WA: 'EMPLOYEE',
        });
        this.registrationForm.markAsPristine();
        this.registrationForm.markAsUntouched();
      },
    });
  }

  goBack() {
    window.history.back();
  }
}
