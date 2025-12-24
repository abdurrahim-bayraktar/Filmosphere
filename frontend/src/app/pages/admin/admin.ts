import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { AvatarModule } from 'primeng/avatar';
import { PopoverModule } from 'primeng/popover';
import { Popover } from 'primeng/popover';
import { MenuModule } from 'primeng/menu';
import { MenuItem } from 'primeng/api';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { TextareaModule } from 'primeng/textarea';
import { TagModule } from 'primeng/tag';
import { BadgeModule } from 'primeng/badge';
import { ProgressBarModule } from 'primeng/progressbar';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ButtonModule,
    CardModule,
    TableModule,
    AvatarModule,
    PopoverModule,
    MenuModule,
    RouterLink,
    DialogModule,
    InputTextModule,
    TextareaModule,
    TagModule,
    BadgeModule,
    ProgressBarModule
  ],
  templateUrl: './admin.html',
  styleUrl: './admin.css'
})
export class AdminComponent implements OnInit {
  
  @ViewChild('profileMenu') profileMenu!: Popover;

  user: any = null;
  isAdmin: boolean = false;
  avatarLabel: string = "";
  avatarImage: string | null = null;
  menuItems: MenuItem[] = [];
  
  adminStats: any = {
    totalUsers: 0,
    totalFilms: 0,
    totalReviews: 0
  };

  // User Management
  users: any[] = [];
  selectedUser: any = null;
  userDialogVisible = false;
  userSearchTerm = '';
  private searchTimeout: any = null;

  // Recent Comments
  recentComments: any[] = [];

  // Mood Tracking
  moodData: any = {
    happy: 0,
    sad: 0,
    excited: 0,
    calm: 0,
    anxious: 0,
    bored: 0,
    energetic: 0,
    relaxed: 0,
    stressed: 0,
    neutral: 0
  };
  moodType: 'before' | 'after' = 'before';

  // Film Management
  films: any[] = [];
  filmDialogVisible = false;
  editingFilm: any = null;
  newFilm = {
    title: '',
    imdb_id: '',
    year: '',
    description: ''
  };

  // Badge Management
  badgeStats: any = {
    totalBadges: 0,
    activeBadges: 0,
    customBadges: 0
  };
  badges: any[] = [];
  badgesDialogVisible = false;

  // Flagged Content
  flaggedContent: any[] = [];

  // Recommendation Engine
  engineStatus = {
    status: 'running', // running, stopped, error
    lastRun: '2025-12-12 10:30:00',
    nextRun: '2025-12-12 14:30:00',
    processedUsers: 1250,
    recommendationsGenerated: 3420
  };

  // System Logs
  systemLogs: any[] = [];

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    // TEMPORARILY COMMENTED OUT FOR PREVIEW - REMOVE COMMENTS TO ENABLE AUTH CHECK
    // this.checkAuth();
    this.setupMenuItems();
    
    // Mock data for preview
    this.isAdmin = true;
    this.user = {
      username: "admin",
      email: "admin@filmosphere.com",
      id: 1,
      profile: {
        avatar: null
      }
    };
    this.avatarLabel = "A";
    this.loadAdminStats();
    this.loadUsers();
    this.loadRecentReviews();
    this.loadFilms();
    this.loadBadgeStats();
    this.loadMoodStats();
    this.loadSystemLogs();
    this.loadMockData();
  }

  loadUsers() {
    const token = localStorage.getItem("access");
    const headers = token ? new HttpHeaders({
      Authorization: `Bearer ${token}`
    }) : new HttpHeaders();

    // Build search query if search term exists
    let url = "http://127.0.0.1:8000/api/admin/users/";
    if (this.userSearchTerm) {
      url += `?search=${encodeURIComponent(this.userSearchTerm)}`;
    }

    console.log('[ADMIN] Loading users from:', url);
    this.http.get(url, { headers })
      .subscribe({
        next: (users: any) => {
          console.log('[ADMIN] Users loaded successfully:', users);
          // Handle both array and paginated response
          if (Array.isArray(users)) {
            this.users = users;
            console.log(`[ADMIN] Loaded ${users.length} users`);
          } else if (users.results) {
            this.users = users.results;
            console.log(`[ADMIN] Loaded ${users.results.length} users from paginated response`);
          } else {
            this.users = [];
            console.log('[ADMIN] No users found in response');
          }
        },
        error: (err) => {
          console.error("[ADMIN] Failed to load users:", err);
          this.users = [];
        }
      });
  }

  onUserSearch() {
    // Debounce search to avoid too many API calls
    if (this.searchTimeout) {
      clearTimeout(this.searchTimeout);
    }
    this.searchTimeout = setTimeout(() => {
      this.loadUsers();
    }, 300); // Wait 300ms after user stops typing
  }

  loadRecentReviews() {
    console.log('[ADMIN] Loading recent reviews...');
    this.http.get("http://127.0.0.1:8000/api/admin/reviews/recent")
      .subscribe({
        next: (reviews: any) => {
          console.log('[ADMIN] Recent reviews loaded:', reviews);
          // Handle both array and paginated response
          if (Array.isArray(reviews)) {
            this.recentComments = reviews.map((review: any) => ({
              id: review.id,
              user: review.username,
              film: review.film_title,
              comment: review.content,
              date: review.created_at
            }));
            console.log(`[ADMIN] Loaded ${reviews.length} recent reviews`);
          } else if (reviews.results) {
            this.recentComments = reviews.results.map((review: any) => ({
              id: review.id,
              user: review.username,
              film: review.film_title,
              comment: review.content,
              date: review.created_at
            }));
            console.log(`[ADMIN] Loaded ${reviews.results.length} recent reviews from paginated response`);
          } else {
            this.recentComments = [];
            console.log('[ADMIN] No reviews found in response');
          }
        },
        error: (err) => {
          console.error("[ADMIN] Failed to load recent reviews:", err);
          this.recentComments = [];
        }
      });
  }

  loadFilms() {
    console.log('[ADMIN] Loading films...');
    this.http.get("http://127.0.0.1:8000/api/admin/films/")
      .subscribe({
        next: (films: any) => {
          console.log('[ADMIN] Films loaded:', films);
          // Handle both array and paginated response
          if (Array.isArray(films)) {
            this.films = films;
            console.log(`[ADMIN] Loaded ${films.length} films`);
          } else if (films.results) {
            this.films = films.results;
            console.log(`[ADMIN] Loaded ${films.results.length} films from paginated response`);
          } else {
            this.films = [];
            console.log('[ADMIN] No films found in response');
          }
        },
        error: (err) => {
          console.error("[ADMIN] Failed to load films:", err);
          this.films = [];
        }
      });
  }

  loadBadgeStats() {
    console.log('[ADMIN] Loading badge stats...');
    this.http.get("http://127.0.0.1:8000/api/admin/badges/stats")
      .subscribe({
        next: (stats: any) => {
          console.log('[ADMIN] Badge stats loaded:', stats);
          this.badgeStats = {
            totalBadges: stats.total_badges || 0,
            activeBadges: stats.active_badges || 0,
            customBadges: stats.custom_badges || 0
          };
          console.log(`[ADMIN] Total: ${this.badgeStats.totalBadges}, Active: ${this.badgeStats.activeBadges}, Custom: ${this.badgeStats.customBadges}`);
        },
        error: (err) => {
          console.error("[ADMIN] Failed to load badge stats:", err);
          this.badgeStats = {
            totalBadges: 0,
            activeBadges: 0,
            customBadges: 0
          };
        }
      });
  }

  loadMoodStats() {
    console.log(`[ADMIN] Loading mood stats (${this.moodType})...`);
    this.http.get("http://127.0.0.1:8000/api/admin/moods/stats")
      .subscribe({
        next: (stats: any) => {
          console.log('[ADMIN] Mood stats loaded:', stats);
          
          // Get the appropriate data based on selected type
          const selectedData = this.moodType === 'before' ? stats.before : stats.after;
          
          if (selectedData && selectedData.percentages) {
            this.moodData = {
              happy: selectedData.percentages.happy || 0,
              sad: selectedData.percentages.sad || 0,
              excited: selectedData.percentages.excited || 0,
              calm: selectedData.percentages.calm || 0,
              anxious: selectedData.percentages.anxious || 0,
              bored: selectedData.percentages.bored || 0,
              energetic: selectedData.percentages.energetic || 0,
              relaxed: selectedData.percentages.relaxed || 0,
              stressed: selectedData.percentages.stressed || 0,
              neutral: selectedData.percentages.neutral || 0
            };
            console.log(`[ADMIN] Mood data updated for ${this.moodType}:`, this.moodData);
          }
        },
        error: (err) => {
          console.error("[ADMIN] Failed to load mood stats:", err);
        }
      });
  }

  onMoodTypeChange() {
    console.log(`[ADMIN] Mood type changed to: ${this.moodType}`);
    this.loadMoodStats();
  }

  openBadgesDialog() {
    console.log('[ADMIN] Opening badges dialog...');
    this.badgesDialogVisible = true;
    this.loadAllBadges();
  }

  loadAllBadges() {
    console.log('[ADMIN] Loading all badges...');
    this.http.get("http://127.0.0.1:8000/api/badges/")
      .subscribe({
        next: (badges: any) => {
          console.log('[ADMIN] All badges loaded:', badges);
          if (Array.isArray(badges)) {
            this.badges = badges;
          } else if (badges.results) {
            this.badges = badges.results;
          } else {
            this.badges = [];
          }
          console.log(`[ADMIN] Loaded ${this.badges.length} badges`);
        },
        error: (err) => {
          console.error("[ADMIN] Failed to load badges:", err);
          this.badges = [];
        }
      });
  }

  loadSystemLogs() {
    console.log('[ADMIN] Loading system logs...');
    this.http.get("http://127.0.0.1:8000/api/admin/logs")
      .subscribe({
        next: (logs: any) => {
          console.log('[ADMIN] System logs loaded:', logs);
          // Handle both array and paginated response
          if (Array.isArray(logs)) {
            this.systemLogs = logs.map((log: any, index: number) => ({
              id: index,
              level: log.level || 'INFO',
              message: log.message || '',
              timestamp: log.timestamp || new Date().toISOString()
            }));
            console.log(`[ADMIN] Loaded ${logs.length} system logs`);
          } else if (logs.results) {
            this.systemLogs = logs.results.map((log: any, index: number) => ({
              id: index,
              level: log.level || 'INFO',
              message: log.message || '',
              timestamp: log.timestamp || new Date().toISOString()
            }));
            console.log(`[ADMIN] Loaded ${logs.results.length} system logs from paginated response`);
          } else {
            this.systemLogs = [];
            console.log('[ADMIN] No logs found in response');
          }
        },
        error: (err) => {
          console.error("[ADMIN] Failed to load system logs:", err);
          this.systemLogs = [];
        }
      });
  }

  loadMockData() {
    // Mock data for other sections (comments, films, etc.)
    // Most data is now loaded from API, so this is minimal

    this.flaggedContent = [
      { id: 1, type: 'Review', content: 'Inappropriate language detected', user: 'user123', date: '2025-12-12 10:00:00', status: 'pending' },
      { id: 2, type: 'Comment', content: 'Spam detected', user: 'spammer', date: '2025-12-11 15:30:00', status: 'reviewed' }
    ];
  }

  // User Management Methods
  banUser(user: any) {
    const action = user.is_active ? 'ban' : 'unban';
    if (confirm(`Are you sure you want to ${action} ${user.username}?`)) {
      const token = localStorage.getItem("access");
      const headers = token ? new HttpHeaders({
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      }) : new HttpHeaders({
        'Content-Type': 'application/json'
      });

      console.log(`[ADMIN] Attempting to ${action} user ${user.id} (${user.username})...`);
      this.http.post(`http://127.0.0.1:8000/api/admin/users/${user.id}/ban`, {}, { headers })
        .subscribe({
          next: (response: any) => {
            console.log(`[ADMIN] ${action} successful:`, response);
            // Reload users to update the list
            this.loadUsers();
          },
          error: (err) => {
            console.error(`[ADMIN] Failed to ${action} user:`, err);
            alert(`Failed to ${action} user: ${err.error?.detail || err.message}`);
          }
        });
    }
  }

  deleteUser(user: any) {
    if (confirm(`Are you sure you want to delete ${user.username}? This action cannot be undone.`)) {
      const token = localStorage.getItem("access");
      const headers = token ? new HttpHeaders({
        Authorization: `Bearer ${token}`
      }) : new HttpHeaders();

      console.log(`[ADMIN] Attempting to delete user ${user.id} (${user.username})...`);
      this.http.delete(`http://127.0.0.1:8000/api/admin/users/${user.id}/delete`, { headers })
        .subscribe({
          next: (response: any) => {
            console.log('[ADMIN] Delete successful:', response);
            // Reload users to update the list
            this.loadUsers();
          },
          error: (err) => {
            console.error('[ADMIN] Failed to delete user:', err);
            alert(`Failed to delete user: ${err.error?.detail || err.message}`);
          }
        });
    }
  }

  // Film Management Methods
  openFilmDialog(film?: any) {
    if (film) {
      this.editingFilm = film;
      this.newFilm = { 
        title: film.title || '', 
        imdb_id: film.imdb_id || '', 
        year: film.year || '', 
        description: '' 
      };
    } else {
      this.editingFilm = null;
      this.newFilm = { title: '', imdb_id: '', year: '', description: '' };
    }
    this.filmDialogVisible = true;
  }

  saveFilm() {
    if (this.editingFilm) {
      // Update existing film
      console.log(`[ADMIN] Updating film ${this.editingFilm.id}...`, this.newFilm);
      this.http.put(`http://127.0.0.1:8000/api/admin/films/${this.editingFilm.id}/update`, {
        title: this.newFilm.title,
        year: this.newFilm.year ? parseInt(this.newFilm.year) : null
      })
        .subscribe({
          next: (response: any) => {
            console.log('[ADMIN] Film updated successfully:', response);
            this.loadFilms();
            this.filmDialogVisible = false;
          },
          error: (err) => {
            console.error('[ADMIN] Failed to update film:', err);
            alert(`Failed to update film: ${err.error?.detail || err.message}`);
          }
        });
    } else {
      // Create new film
      if (!this.newFilm.imdb_id) {
        alert('IMDb ID is required');
        return;
      }

      console.log(`[ADMIN] Creating film with IMDb ID: ${this.newFilm.imdb_id}...`);
      this.http.post("http://127.0.0.1:8000/api/admin/films/create", {
        imdb_id: this.newFilm.imdb_id.trim()
      })
        .subscribe({
          next: (response: any) => {
            console.log('[ADMIN] Film created successfully:', response);
            if (response.film) {
              console.log(`[ADMIN] Film details: ${response.film.title} (${response.film.year}) - ${response.film.imdb_id}`);
              if (response.film.description) {
                console.log(`[ADMIN] Description: ${response.film.description.substring(0, 100)}...`);
              }
            }
            this.loadFilms();
            this.filmDialogVisible = false;
          },
          error: (err) => {
            console.error('[ADMIN] Failed to create film:', err);
            alert(`Failed to create film: ${err.error?.detail || err.message}`);
          }
        });
    }
  }

  deleteFilm(film: any) {
    if (confirm(`Delete ${film.title}?`)) {
      console.log(`[ADMIN] Deleting film ${film.id} (${film.title})...`);
      this.http.delete(`http://127.0.0.1:8000/api/admin/films/${film.id}/delete`)
        .subscribe({
          next: (response: any) => {
            console.log('[ADMIN] Film deleted successfully:', response);
            this.loadFilms();
          },
          error: (err) => {
            console.error('[ADMIN] Failed to delete film:', err);
            alert(`Failed to delete film: ${err.error?.detail || err.message}`);
          }
        });
    }
  }

  // Flagged Content Methods
  approveContent(item: any) {
    console.log('Approving content:', item);
    // API call here
  }

  rejectContent(item: any) {
    if (confirm('Reject this flagged content?')) {
      console.log('Rejecting content:', item);
      // API call here
    }
  }

  // Recommendation Engine Methods
  startEngine() {
    console.log('Starting recommendation engine');
    this.engineStatus.status = 'running';
    // API call here
  }

  stopEngine() {
    if (confirm('Stop the recommendation engine?')) {
      console.log('Stopping recommendation engine');
      this.engineStatus.status = 'stopped';
      // API call here
    }
  }

  setupMenuItems() {
    this.menuItems = [
      { label: 'My Profile', icon: 'pi pi-user', routerLink: ['/profile'] },
      { label: 'Home', icon: 'pi pi-home', routerLink: ['/home'] },
      { separator: true },
      { label: 'Logout', icon: 'pi pi-sign-out', command: () => this.logout() }
    ];
  }

  // TEMPORARILY COMMENTED OUT FOR PREVIEW - REMOVE COMMENTS TO ENABLE AUTH CHECK
  /*
  checkAuth() {
    const token = localStorage.getItem("access");
    
    if (!token) {
      // Redirect to login if not authenticated
      this.router.navigate(['/']);
      return;
    }

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    // Check if user is authenticated and get user info
    this.http.get("http://127.0.0.1:8000/api/auth/me/", { headers })
      .subscribe({
        next: (res: any) => {
          this.user = res;
          this.avatarImage = res.profile?.avatar || null;
          this.avatarLabel = res.username[0]?.toUpperCase() || "U";
          // Check if user is admin (you may need to adjust this based on your backend)
          this.isAdmin = res.is_staff || res.is_superuser || false;
          
          if (this.isAdmin) {
            this.loadAdminStats();
          } else {
            // Redirect non-admin users
            alert("Access denied. Admin privileges required.");
            this.router.navigate(['/home']);
          }
        },
        error: (err) => {
          console.error("Auth error:", err);
          this.router.navigate(['/']);
        }
      });
  }
  */

  loadAdminStats() {
    // Temporarily allow access without authentication for testing
    console.log("Calling API without auth: http://127.0.0.1:8000/api/admin/stats/");
    this.http.get("http://127.0.0.1:8000/api/admin/stats/")
      .subscribe({
        next: (stats: any) => {
          console.log("API response:", stats);
          this.adminStats = {
            totalUsers: stats.total_users,
            totalFilms: stats.total_films,
            totalReviews: stats.total_reviews
          };
        },
        error: (err) => {
          console.error("Failed to load admin stats:", err);
          // Fallback to mock data if API fails
          this.adminStats = {
            totalUsers: 0,
            totalFilms: 0,
            totalReviews: 0
          };
        }
      });
  }

  logout() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user_profile');
    this.router.navigate(['/']);
  }

  goHome() {
    this.router.navigate(['/home']);
  }
}
