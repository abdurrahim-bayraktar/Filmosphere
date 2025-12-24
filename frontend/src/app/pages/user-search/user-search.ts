import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { NgFor, NgIf, CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AvatarModule } from 'primeng/avatar';
import { MenuItem } from 'primeng/api';
import { MenuModule } from 'primeng/menu';
import { PopoverModule } from 'primeng/popover';
import { Popover } from 'primeng/popover';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import { InputTextModule } from 'primeng/inputtext';
import { Subject, debounceTime, distinctUntilChanged } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-user-search',
  standalone: true,
  imports: [
    FormsModule,
    ButtonModule,
    NgFor,
    NgIf,
    CommonModule,
    RouterModule,
    AvatarModule,
    PopoverModule,
    MenuModule,
    HttpClientModule,
    InputTextModule
  ],
  templateUrl: 'user-search.html',
  styleUrls: ['user-search.css']
})
export class UserSearchComponent implements OnInit, OnDestroy {
  @ViewChild('profileMenu') profileMenu!: Popover;

  users: any[] = [];
  searchQuery: string = '';
  loading: boolean = false;
  followStatuses: { [username: string]: boolean } = {};

  user: any = null;
  avatarLabel: string = "";
  avatarImage: string | null = null;
  isAdmin = false;
  menuItems: MenuItem[] = [];

  private searchSubject = new Subject<string>();
  private destroy$ = new Subject<void>();

  constructor(
    private router: Router,
    private http: HttpClient
  ) { }

  ngOnInit() {
    this.loadUser();
    
    // Setup debounced search
    this.searchSubject.pipe(
      debounceTime(300), // Wait 300ms after user stops typing
      distinctUntilChanged(), // Only search if query changed
      takeUntil(this.destroy$)
    ).subscribe(query => {
      if (query.trim()) {
        this.performSearch(query);
      } else {
        this.users = [];
      }
    });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onSearchInputChange() {
    this.searchSubject.next(this.searchQuery);
  }

  setupMenuItems() {
    const items: MenuItem[] = [
      { label: 'My Profile', icon: 'pi pi-user', routerLink: ['/profile'] } as MenuItem,
      { label: 'Home', icon: 'pi pi-home', routerLink: ['/home'] } as MenuItem,
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
        this.avatarImage = usr.profile_picture_url || usr.profile?.profile_picture_url || usr.profile?.avatar || null;
        this.avatarLabel = (usr.username || usr.user?.username || "U")[0]?.toUpperCase() || "U";
        this.setupMenuItems();
      } catch (e) {
        console.error('Error parsing cached user:', e);
      }
    }

    const token = localStorage.getItem("access");
    if (!token) return;

    this.http.get("http://127.0.0.1:8000/api/auth/me/", {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (res: any) => {
        this.user = res;
        this.isAdmin = !!(res.is_staff || res.is_superuser);
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
    localStorage.removeItem('user_profile');
    this.user = { username: "Guest" };
    this.avatarLabel = "G";
    this.router.navigate(['/']);
  }

  searchUsers() {
    if (!this.searchQuery.trim()) {
      this.users = [];
      return;
    }
    this.performSearch(this.searchQuery);
  }

  performSearch(query: string) {
    this.loading = true;
    this.http.get(`http://127.0.0.1:8000/api/users/search/?q=${encodeURIComponent(query)}`)
      .subscribe({
        next: (res: any) => {
          this.users = res.results || [];
          // Load follow statuses for each user
          this.loadFollowStatuses();
          this.loading = false;
        },
        error: (err) => {
          console.error('Error searching users:', err);
          this.users = [];
          this.loading = false;
        }
      });
  }

  loadFollowStatuses() {
    const token = localStorage.getItem("access");
    if (!token) return;

    const currentUsername = this.user?.username || this.user?.user?.username;
    if (!currentUsername) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    // Check follow status for each user (skip current user)
    this.users.forEach((user) => {
      const username = user.username || user.user?.username;
      if (!username || username === currentUsername) {
        // Don't check follow status for current user
        return;
      }

      this.http.get(`http://127.0.0.1:8000/api/users/${username}/follow-status`, { headers })
        .subscribe({
          next: (res: any) => {
            this.followStatuses[username] = res.is_following || false;
          },
          error: () => {
            this.followStatuses[username] = false;
          }
        });
    });
  }

  toggleFollow(username: string) {
    const token = localStorage.getItem("access");
    if (!token) {
      alert("Please log in to follow users");
      return;
    }

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    const isFollowing = this.followStatuses[username];

    if (isFollowing) {
      // Unfollow
      this.http.delete(`http://127.0.0.1:8000/api/users/${username}/follow`, { headers })
        .subscribe({
          next: () => {
            this.followStatuses[username] = false;
          },
          error: (err) => {
            console.error('Error unfollowing user:', err);
            alert('Error unfollowing user. Please try again.');
          }
        });
    } else {
      // Follow
      this.http.post(`http://127.0.0.1:8000/api/users/${username}/follow`, {}, { headers })
        .subscribe({
          next: () => {
            this.followStatuses[username] = true;
          },
          error: (err) => {
            console.error('Error following user:', err);
            alert('Error following user. Please try again.');
          }
        });
    }
  }

  goToProfile(username: string) {
    this.router.navigate(['/profile', username]);
  }

  goToFilmSearch() {
    this.router.navigate(['/film-search']);
  }
}

