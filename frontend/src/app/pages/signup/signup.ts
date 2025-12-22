import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';  
import { HttpClient } from '@angular/common/http';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [
    FormsModule,
    RouterModule,        
    InputTextModule,
    ButtonModule
  ],
  templateUrl: './signup.html',
  styleUrl: './signup.css'
})
export class SignupComponent {
  email = "";
  username = "";
  password = "";
  confirmPassword = "";

  constructor(private http: HttpClient, private router: Router) {}

  register() {
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

    this.http.post("http://127.0.0.1:8000/api/auth/register/", payload)
      .subscribe({
        next: (res) => {
          alert("Account created successfully!");
          this.router.navigate(['/']);   
        },
        error: (err) => {
          console.error(err);
          alert("Registration failed.");
        }
      });
  }
  //login() {
  //const payload = {
    //email: this.email,
    //password: this.password
  //};

  //this.http.post("http://127.0.0.1:8000/api/token/", payload)
    //.subscribe({
      //next: (res: any) => {
        //localStorage.setItem("access", res.access);
        //localStorage.setItem("refresh", res.refresh);
        //this.router.navigate(['/']); 
     // },
      //error: () => {
        //alert("Login failed");
      //}
    //});
}

