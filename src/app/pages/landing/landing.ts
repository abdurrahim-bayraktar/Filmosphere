import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';

@Component({
  selector: 'app-landing',
  standalone: true,
  templateUrl: './landing.html',
  styleUrl: './landing.css',
  imports: [
    FormsModule,
    RouterModule,
    ButtonModule,
    InputTextModule
  ]
})
export class LandingComponent {
  email: string = '';
  password: string = '';

  constructor(private http: HttpClient, private router: Router) {}

  login() {
    const payload = {
      username: this.email,   // email OR username field
      password: this.password
    };

    this.http.post("http://127.0.0.1:8000/api/auth/login/", payload)
      .subscribe({
        next: (res: any) => {

          // ------------------------------
          // SAVE TOKENS
          // ------------------------------
          localStorage.setItem("access", res.access);
          localStorage.setItem("refresh", res.refresh);

          // ------------------------------
          // SAVE USER INFO
          // backend now returns: res.user = { id, username, email }
          // ------------------------------
          if (res.user) {
            localStorage.setItem("username", res.user.username);
            localStorage.setItem("email", res.user.email);
            localStorage.setItem("user_id", res.user.id);
          }

          this.router.navigate(['/home']);
        },
        error: (err) => {
          console.error(err);
          alert("Invalid login credentials");
        }
      });
  }
}
