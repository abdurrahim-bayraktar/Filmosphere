import { Component, OnInit, ViewChild } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { CarouselModule } from 'primeng/carousel';
import { ButtonModule } from 'primeng/button';
import { CommonModule } from '@angular/common';
import { HeroComponent } from "../../components/hero/hero";
import { MovieModalComponent } from "../../components/movie-modal/movie-modal";
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { AvatarModule } from 'primeng/avatar';
import { MenuItem } from 'primeng/api';
import { MenuModule } from 'primeng/menu';
import { PopoverModule } from 'primeng/popover';
import { Popover } from 'primeng/popover';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    RouterModule,
    CarouselModule,
    ButtonModule,
    CommonModule,
    HeroComponent,
    MovieModalComponent,
    HttpClientModule,
    AvatarModule,
    PopoverModule,
    MenuModule
  ],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class HomeComponent implements OnInit {

  @ViewChild('profileMenu') profileMenu!: Popover;

  user: any = null;
  avatarLabel: string = "";
  avatarImage: string | null = null;

  menuItems: MenuItem[] = [];

  modalVisible = false;
  selectedMovie: any = null;

  trendingMovies: any[] = [];
  topRatedMovies: any[] = [];
  actionMovies: any[] = [];

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadUser();
    this.setupMenuItems();
  }

  setupMenuItems() {
    this.menuItems = [
      { label: 'My Profile', icon: 'pi pi-user', routerLink: ['/profile'] },
      { label: 'Settings', icon: 'pi pi-cog', routerLink: ['/settings'] },
      { separator: true },
      { label: 'Logout', icon: 'pi pi-sign-out', command: () => this.logout() }
    ];
  }

  loadUser() {
    const cached = localStorage.getItem("user_profile");

    if (cached) {
      const usr = JSON.parse(cached);
      this.user = usr;
      this.avatarImage = usr.profile?.avatar || null;
      this.avatarLabel = usr.username?.[0]?.toUpperCase() || "U";
    }

    const token = localStorage.getItem("access");
    if (!token) return;

    this.http.get("http://127.0.0.1:8000/api/auth/me/", {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (res: any) => {
        this.user = res;
        this.avatarImage = res.profile?.avatar || null;
        this.avatarLabel = res.username?.[0]?.toUpperCase() || "U";
        localStorage.setItem("user_profile", JSON.stringify(res));
      }
    });
  }

  logout() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    this.user = { username: "Guest" };
    this.avatarLabel = "G";
    this.router.navigate(['/']);
  }

  openMovieDetail(movie: any) {
    this.selectedMovie = movie;
    this.modalVisible = true;
  }

  closeMovieDetail() {
    this.modalVisible = false;
  }

  goToFilmSearch() {
    this.router.navigate(['/film-search']);
  }
}
