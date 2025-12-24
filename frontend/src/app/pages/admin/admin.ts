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
    lastRun: '',
    nextRun: '',
    processedUsers: 0,
    recommendationsGenerated: 0
  };

  // System Logs
  systemLogs: any[] = [];

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    this.setupMenuItems();
    this.checkAuth();
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
    const token = localStorage.getItem("access");
    if (!token) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    console.log('[ADMIN] Loading recent reviews...');
    this.http.get("http://127.0.0.1:8000/api/admin/reviews/recent", { headers })
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
    const token = localStorage.getItem("access");
    if (!token) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    console.log('[ADMIN] Loading films...');
    this.http.get("http://127.0.0.1:8000/api/admin/films/", { headers })
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
    const token = localStorage.getItem("access");
    if (!token) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    console.log('[ADMIN] Loading badge stats...');
    this.http.get("http://127.0.0.1:8000/api/admin/badges/stats", { headers })
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
    const token = localStorage.getItem("access");
    if (!token) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    console.log(`[ADMIN] Loading mood stats (${this.moodType})...`);
    this.http.get("http://127.0.0.1:8000/api/admin/moods/stats", { headers })
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
    const token = localStorage.getItem("access");
    if (!token) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    console.log('[ADMIN] Loading all badges...');
    this.http.get("http://127.0.0.1:8000/api/badges/", { headers })
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
    const token = localStorage.getItem("access");
    if (!token) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    console.log('[ADMIN] Loading system logs...');
    this.http.get("http://127.0.0.1:8000/api/admin/logs", { headers })
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
    // All data is now loaded from API - no mock data needed
    this.flaggedContent = [];
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
      const token = localStorage.getItem("access");
      if (!token) {
        alert("Authentication required");
        return;
      }

      const headers = new HttpHeaders({
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      });

      // Update existing film
      console.log(`[ADMIN] Updating film ${this.editingFilm.id}...`, this.newFilm);
      this.http.put(`http://127.0.0.1:8000/api/admin/films/${this.editingFilm.id}/update`, {
        title: this.newFilm.title,
        year: this.newFilm.year ? parseInt(this.newFilm.year) : null
      }, { headers })
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

      const token = localStorage.getItem("access");
      if (!token) {
        alert("Authentication required");
        return;
      }

      const headers = new HttpHeaders({
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      });

      console.log(`[ADMIN] Creating film with IMDb ID: ${this.newFilm.imdb_id}...`);
      this.http.post("http://127.0.0.1:8000/api/admin/films/create", {
        imdb_id: this.newFilm.imdb_id.trim()
      }, { headers })
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
      const token = localStorage.getItem("access");
      if (!token) {
        alert("Authentication required");
        return;
      }

      const headers = new HttpHeaders({
        Authorization: `Bearer ${token}`
      });

      console.log(`[ADMIN] Deleting film ${film.id} (${film.title})...`);
      this.http.delete(`http://127.0.0.1:8000/api/admin/films/${film.id}/delete`, { headers })
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
    const token = localStorage.getItem("access");
    if (!token) {
      alert("Authentication required");
      return;
    }

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    console.log('[ADMIN] Approving content:', item);
    this.http.post(`http://127.0.0.1:8000/api/admin/reviews/${item.id}/moderate`, {
      action: "approve",
      reason: "Approved by admin"
    }, { headers })
      .subscribe({
        next: (response: any) => {
          console.log('[ADMIN] Content approved:', response);
          this.loadFlaggedContent();
          this.loadRecentReviews();
        },
        error: (err) => {
          console.error('[ADMIN] Failed to approve content:', err);
          alert(`Failed to approve: ${err.error?.detail || err.message}`);
        }
      });
  }

  rejectContent(item: any) {
    if (confirm('Reject this flagged content? It will be permanently deleted.')) {
      const token = localStorage.getItem("access");
      if (!token) {
        alert("Authentication required");
        return;
      }

      const headers = new HttpHeaders({
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      });

      console.log('[ADMIN] Rejecting content:', item);
      this.http.post(`http://127.0.0.1:8000/api/admin/reviews/${item.id}/moderate`, {
        action: "reject",
        reason: "Rejected by admin"
      }, { headers })
        .subscribe({
          next: (response: any) => {
            console.log('[ADMIN] Content rejected:', response);
            this.loadFlaggedContent();
            this.loadRecentReviews();
          },
          error: (err) => {
            console.error('[ADMIN] Failed to reject content:', err);
            alert(`Failed to reject: ${err.error?.detail || err.message}`);
          }
        });
    }
  }

  loadFlaggedContent() {
    const token = localStorage.getItem("access");
    if (!token) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    console.log('[ADMIN] Loading flagged content...');
    // Get pending reviews (flagged by DeepSeek or users)
    this.http.get("http://127.0.0.1:8000/api/admin/reviews/flagged?status=pending", { headers })
      .subscribe({
        next: (reviews: any) => {
          console.log('[ADMIN] Flagged content loaded:', reviews);
          if (Array.isArray(reviews)) {
            this.flaggedContent = reviews.map((review: any) => ({
              id: review.id,
              type: 'Review',
              content: (review.content || review.title || 'No content').substring(0, 200),
              user: review.username || review.user?.username || 'Unknown',
              date: review.created_at,
              status: review.moderation_status || 'pending',
              reason: review.moderation_reason || review.flagged_count > 0 ? `Flagged by ${review.flagged_count} user(s)` : 'Pending moderation'
            }));
          } else if (reviews.results) {
            this.flaggedContent = reviews.results.map((review: any) => ({
              id: review.id,
              type: 'Review',
              content: (review.content || review.title || 'No content').substring(0, 200),
              user: review.username || review.user?.username || 'Unknown',
              date: review.created_at,
              status: review.moderation_status || 'pending',
              reason: review.moderation_reason || review.flagged_count > 0 ? `Flagged by ${review.flagged_count} user(s)` : 'Pending moderation'
            }));
          } else {
            this.flaggedContent = [];
          }
          console.log(`[ADMIN] Loaded ${this.flaggedContent.length} flagged items`);
        },
        error: (err) => {
          console.error("[ADMIN] Failed to load flagged content:", err);
          this.flaggedContent = [];
        }
      });
  }

  loadRecommendationEngineStats() {
    const token = localStorage.getItem("access");
    if (!token) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    console.log('[ADMIN] Loading recommendation engine stats...');
    // Get all recommendation logs for stats
    this.http.get("http://127.0.0.1:8000/api/admin/logs?type=recommendation&limit=1000", { headers })
      .subscribe({
        next: (allLogs: any) => {
          console.log('[ADMIN] Recommendation logs loaded:', allLogs);
          
          const recommendationLogs = Array.isArray(allLogs) ? allLogs : (allLogs.results || []);
          
          // Calculate stats
          const uniqueUsers = new Set(recommendationLogs.map((log: any) => log.user || log.user_id).filter(Boolean));
          const recommendationsGenerated = recommendationLogs.filter((log: any) => !log.blocked && (log.type === 'recommendation' || log.message?.includes('Recommendation'))).length;
          
          // Get last run time (most recent log)
          const lastLog = recommendationLogs.length > 0 ? recommendationLogs[0] : null;
          const lastRun = lastLog?.timestamp || lastLog?.created_at || '';
          
          // Format last run date
          let formattedLastRun = 'Never';
          if (lastRun) {
            try {
              const lastRunDate = new Date(lastRun);
              formattedLastRun = lastRunDate.toLocaleString('en-US', { 
                year: 'numeric', 
                month: '2-digit', 
                day: '2-digit', 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit',
                hour12: false
              }).replace(',', '');
            } catch (e) {
              formattedLastRun = lastRun;
            }
          }
          
          // Calculate next run (assuming daily runs, add 24 hours)
          let formattedNextRun = 'Not scheduled';
          if (lastRun) {
            try {
              const lastRunDate = new Date(lastRun);
              lastRunDate.setHours(lastRunDate.getHours() + 24);
              formattedNextRun = lastRunDate.toLocaleString('en-US', { 
                year: 'numeric', 
                month: '2-digit', 
                day: '2-digit', 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit',
                hour12: false
              }).replace(',', '');
            } catch (e) {
              formattedNextRun = 'Not scheduled';
            }
          }
          
          this.engineStatus = {
            status: 'running',
            lastRun: formattedLastRun,
            nextRun: formattedNextRun,
            processedUsers: uniqueUsers.size,
            recommendationsGenerated: recommendationsGenerated
          };
          
          console.log('[ADMIN] Recommendation engine stats:', this.engineStatus);
        },
        error: (err) => {
          console.error('[ADMIN] Failed to load recommendation stats:', err);
          // Set default values on error
          this.engineStatus = {
            status: 'error',
            lastRun: 'Error loading',
            nextRun: 'Error loading',
            processedUsers: 0,
            recommendationsGenerated: 0
          };
        }
      });
  }

  // Recommendation Engine Methods
  startEngine() {
    console.log('Starting recommendation engine');
    this.engineStatus.status = 'running';
    // API call here (if you implement engine control endpoint)
  }

  stopEngine() {
    if (confirm('Stop the recommendation engine?')) {
      console.log('Stopping recommendation engine');
      this.engineStatus.status = 'stopped';
      // API call here (if you implement engine control endpoint)
    }
  }

  setupMenuItems() {
    const items: MenuItem[] = [
      { label: 'My Profile', icon: 'pi pi-user', routerLink: ['/profile'] } as MenuItem,
      { label: 'Home', icon: 'pi pi-home', routerLink: ['/home'] } as MenuItem,
      { label: 'Admin', icon: 'pi pi-cog', routerLink: ['/admin'] } as MenuItem,
      { separator: true } as MenuItem,
      { label: 'Logout', icon: 'pi pi-sign-out', command: () => this.logout() } as MenuItem
    ];

    this.menuItems = items;
  }

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
          console.log("[ADMIN] User data received:", res);
          this.user = res;
          this.avatarImage = res.profile_picture_url || res.profile?.profile_picture_url || res.profile?.avatar || null;
          this.avatarLabel = (res.username || res.user?.username || "U")[0]?.toUpperCase() || "U";
          
          // Check if user is admin - check both direct fields and nested user object
          const isStaff = res.is_staff || res.user?.is_staff || false;
          const isSuperuser = res.is_superuser || res.user?.is_superuser || false;
          this.isAdmin = isStaff || isSuperuser;
          this.setupMenuItems();
          
          console.log("[ADMIN] Admin check:", { isStaff, isSuperuser, isAdmin: this.isAdmin });
          
          if (this.isAdmin) {
            // Load all admin data
            this.loadAdminStats();
            this.loadUsers();
            this.loadRecentReviews();
            this.loadFilms();
            this.loadBadgeStats();
            this.loadMoodStats();
            this.loadSystemLogs();
            this.loadFlaggedContent();
            this.loadRecommendationEngineStats();
          } else {
            // Redirect non-admin users
            alert("Access denied. Admin privileges required. Please contact an administrator.");
            this.router.navigate(['/home']);
          }
        },
        error: (err) => {
          console.error("Auth error:", err);
          alert("Authentication failed. Please login again.");
          this.router.navigate(['/']);
        }
      });
  }

  loadAdminStats() {
    const token = localStorage.getItem("access");
    if (!token) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    console.log("[ADMIN] Loading admin stats...");
    this.http.get("http://127.0.0.1:8000/api/admin/stats/", { headers })
      .subscribe({
        next: (stats: any) => {
          console.log("[ADMIN] Stats loaded:", stats);
          this.adminStats = {
            totalUsers: stats.total_users || 0,
            totalFilms: stats.total_films || 0,
            totalReviews: stats.total_reviews || 0
          };
        },
        error: (err) => {
          console.error("[ADMIN] Failed to load admin stats:", err);
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
