import { Component } from '@angular/core';
import { Router } from '@angular/router';
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

  email: string = '';

  constructor(private router: Router) { }

  goLogin() {
    this.router.navigate(['/']);
  }

}
