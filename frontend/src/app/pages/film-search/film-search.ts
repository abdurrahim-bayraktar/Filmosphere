import { Component, OnInit, OnDestroy, ViewChild, HostListener } from '@angular/core';
import { SearchService } from '../../services/search.service';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { NgFor, NgIf } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AvatarModule } from 'primeng/avatar';
import { MenuItem } from 'primeng/api';
import { MenuModule } from 'primeng/menu';
import { PopoverModule } from 'primeng/popover';
import { Popover } from 'primeng/popover';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { API_URL } from '../../config/api.config';

@Component({
  selector: 'app-film-search',
  standalone: true,
  imports: [
    FormsModule,
    ButtonModule,
    NgFor,
    NgIf,
    RouterModule,
    AvatarModule,
    PopoverModule,
    MenuModule,
    HttpClientModule
  ],
  templateUrl: 'film-search.html',
  styleUrls: ['film-search.css']
})
export class FilmSearch implements OnInit, OnDestroy {
  @ViewChild('profileMenu') profileMenu!: Popover;

  films: any[] = [];
  searchQuery: string = '';
  filterMenuOpen = false;

  user: any = null;
  avatarLabel: string = "";
  avatarImage: string | null = null;
  isAdmin = false;
  menuItems: MenuItem[] = [];

  // Users will see these English labels in the UI
  genres: string[] = [
    'Action', 'Adventure', 'Animation', 'Comedy',
    'Crime', 'Drama', 'Fantasy', 'Horror',
    'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'Family'
  ];

  // Map English UI labels to the specific strings expected by KinoCheck API (observed in terminal)
  private genreMapping: { [key: string]: string } = {
    'Action': 'Action',
    'Adventure': 'Abenteuer',
    'Animation': 'Animation',
    'Comedy': 'Komödie',
    'Crime': 'Krimi',
    'Drama': 'Drama',
    'Fantasy': 'Fantasy',
    'Horror': 'Horror',
    'Mystery': 'Mystery',
    'Romance': 'Lovestory',
    'Sci-Fi': 'Science Fiction',
    'Thriller': 'Thriller',
    'Family': 'Familie'
  };

  constructor(
    private api: SearchService,
    private router: Router,
    private http: HttpClient
  ) { }

  ngOnInit() {
    this.loadAllFilms();
    this.loadUser();
  }

  setupMenuItems() {
    const items: MenuItem[] = [
      { label: 'My Profile', icon: 'pi pi-user', routerLink: ['/profile'] } as MenuItem,
    ];

    if (this.isAdmin) {
      items.push({ label: 'Admin', icon: 'pi pi-cog', routerLink: ['/admin'] } as MenuItem);
    }

    items.push({ separator: true } as MenuItem);
    items.push({ label: 'Logout', icon: 'pi pi-sign-out', command: () => this.logout() } as MenuItem);

    this.menuItems = items;
  }

  loadUser() {
    const cached = localStorage.getItem("user_profile");

    if (cached) {
      try {
        const usr = JSON.parse(cached);
        this.user = usr;
        this.isAdmin = !!(usr.is_staff || usr.is_superuser);
        // Backend returns profile_picture_url directly, not in profile.avatar
        this.avatarImage = usr.profile_picture_url || usr.profile?.profile_picture_url || usr.profile?.avatar || null;
        this.avatarLabel = (usr.username || usr.user?.username || "U")[0]?.toUpperCase() || "U";
        this.setupMenuItems();
      } catch (e) {
        console.error('Error parsing cached user:', e);
      }
    }

    const token = localStorage.getItem("access");
    if (!token) return;

    this.http.get("${API_URL}/auth/me/", {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (res: any) => {
        this.user = res;
        this.isAdmin = !!(res.is_staff || res.is_superuser);
        // Backend returns profile_picture_url directly in serializer.data
        this.avatarImage = res.profile_picture_url || res.profile?.profile_picture_url || null;
        this.avatarLabel = (res.username || res.user?.username || "U")[0]?.toUpperCase() || "U";
        localStorage.setItem("user_profile", JSON.stringify(res));
        this.setupMenuItems();
      },
      error: (err) => {
        console.error('Error loading user:', err);
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

  goToFilmSearch() {
    this.router.navigate(['/film-search']);
  }

  loadAllFilms() {
    this.api.getAllFilms().subscribe((data: any) => {
      this.films = data || [];
    });
  }

  onSearch() {
  const query = this.searchQuery.trim();
  if (!query) {
    this.loadAllFilms();
    return;
  }

  this.api.searchIMDB(query).subscribe((results: any[]) => {
    this.films = results.map(item => ({
      title: item.title,
      // API'den gelen görseli güvenli bir şekilde alalım
      poster: item.image?.url || item.image || item.poster || 'assets/no-image.png',
      genres: [],
      imdb_id: item.imdb_id
    }));
  });
}

  onSearchChange() {
    if (!this.searchQuery.trim()) {
      this.loadAllFilms();
    }
  }

  clearSearch() {
    this.searchQuery = '';
    this.loadAllFilms();
  }

  toggleFilterMenu() {
    this.filterMenuOpen = !this.filterMenuOpen;
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    const filterWrapper = target.closest('.filter-wrapper');
    if (!filterWrapper && this.filterMenuOpen) {
      this.filterMenuOpen = false;
    }
  }

  ngOnDestroy() {
    // Cleanup if needed
  }

  filterByGenre(genre: string) {
    // Convert the English UI label to the API-compatible genre string
    const apiGenre = this.genreMapping[genre] || genre;

    this.api.filterByGenre(apiGenre).subscribe((data: any[]) => {
      // Create a new reference to ensure Angular change detection triggers UI update
      this.films = [...data];
      this.filterMenuOpen = false;
    });
  }
}

