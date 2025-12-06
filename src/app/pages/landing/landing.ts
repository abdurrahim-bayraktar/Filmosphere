import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';

@Component({
  selector: 'app-landing',
  standalone: true,
  templateUrl: './landing.html',
  styleUrl: './landing.css',
  imports: [FormsModule, RouterModule, ButtonModule, InputTextModule]
})
export class LandingComponent {
  email: string = '';
  password: string = '';
}
