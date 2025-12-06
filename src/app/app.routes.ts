import { Routes } from '@angular/router';
import { SignupComponent } from './pages/signup/signup';
import { ForgotPasswordComponent } from './pages/forgot-password/forgot-password';
import { HomeComponent } from './pages/home/home';
import { LandingComponent } from './pages/landing/landing';

export const routes: Routes = [
  { path: '', component: LandingComponent },
  { path: 'signup', component: SignupComponent },
  { path: 'forgot-password', component: ForgotPasswordComponent },

  { path: 'home', component: HomeComponent },
];
