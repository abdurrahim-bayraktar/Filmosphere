import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  templateUrl: './forgot-password.html',
  styleUrl: './forgot-password.css',
  imports: [ButtonModule, InputTextModule, FormsModule]
})
export class ForgotPasswordComponent {

  email: string = "";
  sentCode: string | null = null;

  constructor(private router: Router, private http: HttpClient) {}

  sendResetCode() {
    this.http.post("http://127.0.0.1:8000/api/auth/forgot-password/", {
      email: this.email
    }).subscribe({
      next: (res: any) => {
        this.sentCode = res.reset_code;
        alert("A reset code has been generated.");
      },
      error: () => {
        alert("Email not found.");
      }
    });
  }

  goLogin() {
    this.router.navigate(['/']);
  }
}
