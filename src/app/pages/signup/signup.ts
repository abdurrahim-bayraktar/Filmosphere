import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [FormsModule, RouterModule, InputTextModule, ButtonModule],
  templateUrl: './signup.html',
  styleUrl: './signup.css'
})
export class SignupComponent {
  email: string = '';
  password: string = '';
  confirmPassword: string = '';
}
