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

  // Recent Comments
  recentComments: any[] = [];

  // Mood Tracking
  moodData: any = {
    happy: 45,
    sad: 20,
    excited: 25,
    neutral: 10
  };

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
    this.loadMockData();
  }

  loadMockData() {
    // Mock data for preview
    this.users = [
      { id: 1, username: 'john_doe', email: 'john@example.com', joined: '2025-01-15', status: 'active' },
      { id: 2, username: 'jane_smith', email: 'jane@example.com', joined: '2025-02-20', status: 'active' },
      { id: 3, username: 'banned_user', email: 'banned@example.com', joined: '2024-12-10', status: 'banned' }
    ];

    this.recentComments = [
      { id: 1, user: 'john_doe', film: 'Inception', comment: 'Amazing movie!', date: '2025-12-12 09:15:00' },
      { id: 2, user: 'jane_smith', film: 'The Matrix', comment: 'Mind-blowing!', date: '2025-12-12 08:30:00' },
      { id: 3, user: 'user123', film: 'Interstellar', comment: 'Great visuals', date: '2025-12-11 22:45:00' }
    ];

    this.films = [
      { id: 1, title: 'Inception', imdb_id: 'tt1375666', year: 2010 },
      { id: 2, title: 'The Matrix', imdb_id: 'tt0133093', year: 1999 }
    ];

    this.badgeStats = {
      totalBadges: 15,
      activeBadges: 12,
      customBadges: 3
    };

    this.flaggedContent = [
      { id: 1, type: 'Review', content: 'Inappropriate language detected', user: 'user123', date: '2025-12-12 10:00:00', status: 'pending' },
      { id: 2, type: 'Comment', content: 'Spam detected', user: 'spammer', date: '2025-12-11 15:30:00', status: 'reviewed' }
    ];

    this.systemLogs = [
      { id: 1, level: 'INFO', message: 'User registration successful', timestamp: '2025-12-12 11:00:00' },
      { id: 2, level: 'WARNING', message: 'API rate limit approaching', timestamp: '2025-12-12 10:45:00' },
      { id: 3, level: 'ERROR', message: 'Database connection timeout', timestamp: '2025-12-12 10:30:00' }
    ];
  }

  // User Management Methods
  banUser(user: any) {
    if (confirm(`Are you sure you want to ban ${user.username}?`)) {
      console.log('Banning user:', user);
      // API call here
    }
  }

  deleteUser(user: any) {
    if (confirm(`Are you sure you want to delete ${user.username}? This action cannot be undone.`)) {
      console.log('Deleting user:', user);
      // API call here
    }
  }

  // Film Management Methods
  openFilmDialog(film?: any) {
    if (film) {
      this.editingFilm = film;
      this.newFilm = { ...film };
    } else {
      this.editingFilm = null;
      this.newFilm = { title: '', imdb_id: '', year: '', description: '' };
    }
    this.filmDialogVisible = true;
  }

  saveFilm() {
    console.log('Saving film:', this.newFilm);
    // API call here
    this.filmDialogVisible = false;
  }

  deleteFilm(film: any) {
    if (confirm(`Delete ${film.title}?`)) {
      console.log('Deleting film:', film);
      // API call here
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
    const token = localStorage.getItem("access");
    if (!token) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    // Example: Load admin statistics
    // You'll need to create these endpoints in your backend
    // For now, this is a placeholder structure
    
    // Example API calls (adjust endpoints based on your backend):
    // this.http.get("http://127.0.0.1:8000/api/admin/stats/", { headers })
    //   .subscribe({
    //     next: (stats: any) => {
    //       this.adminStats = stats;
    //     }
    //   });
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
