import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule, Router } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { ButtonModule } from 'primeng/button';
import { AvatarModule } from 'primeng/avatar';
import { PopoverModule } from 'primeng/popover';
import { MenuModule } from 'primeng/menu';
import { Popover } from 'primeng/popover';
import { MenuItem } from 'primeng/api';

import { FilmService } from '../../services/film.service';

@Component({
  selector: 'app-list-detail',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    ButtonModule,
    AvatarModule,
    PopoverModule,
    MenuModule
  ],
  templateUrl: './list-detail.html',
  styleUrl: './list-detail.css'
})
export class ListDetailComponent implements OnInit {
  @ViewChild('profileMenu') profileMenu!: Popover;

  listId: number | null = null;
  list: any = null;
  loading = true;

  // Navbar state
  navbarAvatarLabel = '';
  navbarAvatarImage: string | null = null;
  navbarUsername: string = '';
  menuItems: MenuItem[] = [];

  constructor(
    private route: ActivatedRoute,
    private filmService: FilmService,
    private router: Router,
    private http: HttpClient
  ) {}

  ngOnInit() {
    this.setupMenuItems();
    this.loadNavbarUser();
    
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.listId = parseInt(id, 10);
        this.loadList();
      }
    });
  }

  setupMenuItems() {
    this.menuItems = [
      { label: 'Home', icon: 'pi pi-home', routerLink: ['/home'] },
      { label: 'My Profile', icon: 'pi pi-user', routerLink: ['/profile'] },
      { separator: true },
      { label: 'Logout', icon: 'pi pi-sign-out', command: () => this.logout() }
    ];
  }

  loadNavbarUser() {
    const cached = localStorage.getItem("user_profile");
    if (cached) {
      try {
        const usr = JSON.parse(cached);
        this.navbarAvatarImage = usr.profile_picture_url || usr.profile?.profile_picture_url || null;
        this.navbarAvatarLabel = (usr.username || usr.user?.username || "U")[0]?.toUpperCase() || "U";
        this.navbarUsername = usr.username || usr.user?.username || "Guest";
      } catch {}
    }

    const token = localStorage.getItem("access");
    if (!token) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    this.http.get("http://127.0.0.1:8000/api/auth/me/", { headers })
      .subscribe({
        next: (res: any) => {
          this.navbarAvatarImage = res.profile_picture_url || res.profile?.profile_picture_url || null;
          this.navbarAvatarLabel = (res.username || res.user?.username || "U")[0]?.toUpperCase() || "U";
          this.navbarUsername = res.username || res.user?.username || "Guest";
        },
        error: (err) => {
          console.error('Error loading navbar user:', err);
        }
      });
  }

  logout() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user_profile');
    this.router.navigate(['/']);
  }

  loadList() {
    if (!this.listId) return;
    
    this.loading = true;
    this.filmService.getList(this.listId).subscribe({
      next: (res: any) => {
        console.log('List loaded:', res);
        this.list = res;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading list:', err);
        console.error('Error details:', err.error);
        console.error('Status:', err.status);
        this.loading = false;
        // If 404, list might not exist or user doesn't have access
        if (err.status === 404) {
          this.list = null;
        }
      }
    });
  }

  goToFilm(imdbId: string) {
    this.router.navigate(['/film-details', imdbId]);
  }

  goHome() {
    this.router.navigate(['/home']);
  }

  goToProfile() {
    this.router.navigate(['/profile']);
  }
}

