import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';  
import { HttpClient } from '@angular/common/http';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { CommonModule } from '@angular/common';
import { API_URL } from '../../config/api.config';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [
    FormsModule,
    RouterModule,        
    InputTextModule,
    ButtonModule,
    CommonModule
  ],
  templateUrl: './signup.html',
  styleUrl: './signup.css'
})
export class SignupComponent {
  email = "";
  username = "";
  password = "";
  confirmPassword = "";
  passwordErrors: string[] = [];
  showPasswordErrors = false;
  successMessage = "";
  showSuccessMessage = false;

  constructor(private http: HttpClient, private router: Router) {}

  register() {
    this.passwordErrors = [];
    this.showPasswordErrors = false;
    this.showSuccessMessage = false;
    this.successMessage = "";

    if (this.password !== this.confirmPassword) {
      alert("Passwords do not match.");
      return;
    }

    const payload = {
      username: this.username,
      email: this.email,
      password: this.password,
      password_confirm: this.confirmPassword
    };

    this.http.post(`${API_URL}/auth/register/`, payload)
      .subscribe({
        next: (res) => {
          this.successMessage = "Account has been created successfully!";
          this.showSuccessMessage = true;
          // Clear sensitive fields after success
          this.password = "";
          this.confirmPassword = "";
          this.passwordErrors = [];
          this.showPasswordErrors = false;
          // Optionally navigate after short delay to let user read message
          setTimeout(() => this.router.navigate(['/']), 900);
        },
        error: (err) => {
          console.error(err);
          
          // Extract password validation errors from backend
          if (err.error && err.error.password) {
            this.passwordErrors = Array.isArray(err.error.password) 
              ? err.error.password 
              : [err.error.password];
            this.showPasswordErrors = true;
          } else if (err.error && err.error.non_field_errors) {
            const errors = Array.isArray(err.error.non_field_errors)
              ? err.error.non_field_errors
              : [err.error.non_field_errors];
            alert(errors.join('\n'));
          } else {
            alert("Registration failed. Please check your inputs and try again.");
          }
        }
      });
  }
}

