import { Routes } from '@angular/router';
import { SignupComponent } from './pages/signup/signup';
import { ForgotPasswordComponent } from './pages/forgot-password/forgot-password';
import { HomeComponent } from './pages/home/home';
import { LandingComponent } from './pages/landing/landing';
import { ProfileComponent } from './pages/profile/profile';
import { AdminComponent } from './pages/admin/admin';
import { FilmDetailComponent } from './pages/film-details/film-details';
import { FilmSearch } from './pages/film-search/film-search';
import { UserSearchComponent } from './pages/user-search/user-search';
import { ListManagementComponent } from './pages/list-management/list-management';
import { ListDetailComponent } from './pages/list-detail/list-detail';

export const routes: Routes = [
  { path: '', component: LandingComponent },
  { path: 'signup', component: SignupComponent },
  { path: 'forgot-password', component: ForgotPasswordComponent },
  { path: 'home', component: HomeComponent },
  { path: 'profile', component: ProfileComponent },
  { path: 'profile/:username', component: ProfileComponent },
  { path: 'admin', component: AdminComponent },
  { path: 'film-details/:id', component: FilmDetailComponent },
  { path: 'film-search', component: FilmSearch },
  { path: 'user-search', component: UserSearchComponent },
  { path: 'lists', component: ListManagementComponent },
  { path: 'lists/:id', component: ListDetailComponent },

  // ✅ RECOMMENDATION CHAT (standalone component)
  {
    path: 'recommendation-chat',
    loadComponent: () =>
      import('./pages/recommendation-chat/recommendation-chat')
        .then(m => m.RecommendationChatComponent),
  },
];

