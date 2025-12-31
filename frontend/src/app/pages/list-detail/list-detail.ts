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
import { API_URL } from '../../config/api.config';

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
  isAdmin = false;
  menuItems: MenuItem[] = [];

  constructor(
    private route: ActivatedRoute,
    private filmService: FilmService,
    private router: Router,
    private http: HttpClient
  ) { }

  ngOnInit() {
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
    const items: MenuItem[] = [
      { label: 'Home', icon: 'pi pi-home', routerLink: ['/home'] } as MenuItem,
      { label: 'My Profile', icon: 'pi pi-user', routerLink: ['/profile'] } as MenuItem,
    ];

    if (this.isAdmin) {
      items.push({ label: 'Admin', icon: 'pi pi-cog', routerLink: ['/admin'] } as MenuItem);
    }

    items.push({ separator: true } as MenuItem);
    items.push({ label: 'Logout', icon: 'pi pi-sign-out', command: () => this.logout() } as MenuItem);

    this.menuItems = items;
  }

  loadNavbarUser() {
    const cached = localStorage.getItem("user_profile");
    if (cached) {
      try {
        const usr = JSON.parse(cached);
        this.navbarAvatarImage = usr.profile_picture_url || usr.profile?.profile_picture_url || null;
        this.navbarAvatarLabel = (usr.username || usr.user?.username || "U")[0]?.toUpperCase() || "U";
        this.navbarUsername = usr.username || usr.user?.username || "Guest";
        this.isAdmin = !!(usr.is_staff || usr.is_superuser);
        this.setupMenuItems();
      } catch { }
    }

    const token = localStorage.getItem("access");
    if (!token) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    this.http.get(`${API_URL}/auth/me/`, { headers })
      .subscribe({
        next: (res: any) => {
          this.navbarAvatarImage = res.profile_picture_url || res.profile?.profile_picture_url || null;
          this.navbarAvatarLabel = (res.username || res.user?.username || "U")[0]?.toUpperCase() || "U";
          this.navbarUsername = res.username || res.user?.username || "Guest";
          this.isAdmin = !!(res.is_staff || res.is_superuser);
          this.setupMenuItems();
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


