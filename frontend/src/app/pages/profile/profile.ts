import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import { ActivatedRoute, RouterModule, Router, NavigationEnd } from '@angular/router';
import { filter, Subscription } from 'rxjs';

import { AvatarModule } from 'primeng/avatar';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { TextareaModule } from 'primeng/textarea';
import { FormsModule } from '@angular/forms';
import { RatingModule } from 'primeng/rating';
import { FileUploadModule } from 'primeng/fileupload';
import { MenuModule } from 'primeng/menu';
import { PopoverModule } from 'primeng/popover';
import { Popover } from 'primeng/popover';
import { MenuItem } from 'primeng/api';
import { FilmService } from '../../services/film.service';
import { API_URL } from '../../config/api.config';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [
    CommonModule,
    HttpClientModule,
    AvatarModule,
    ButtonModule,
    DialogModule,
    TextareaModule,
    FormsModule,
    RatingModule,
    FileUploadModule,
    RouterModule,
    MenuModule,
    PopoverModule
  ],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class ProfileComponent implements OnInit, OnDestroy {

  @ViewChild('profileMenu') profileMenu!: Popover;

  private routerSubscription?: Subscription;

  user: any = { profile: {} };
  username: string = '';
  avatarLabel = "";
  avatarImage: string | null = null;
  navbarAvatarLabel = "";
  navbarAvatarImage: string | null = null;
  navbarUsername: string = "";
  isAdmin = false;

  menuItems: MenuItem[] = [];

  editMode = false;
  bioToEdit = "";

  avatarModalVisible = false;
  selectedAvatar: any = null;
  profilePictureFile: File | null = null;
  uploadedFile: string | null = null; // Base64 data URL
  uploadedFileName: string = '';
  uploadError: string = '';

  // Profile data
  followersCount: number = 0;
  followingCount: number = 0;
  isFollowing: boolean = false;
  watchedFilms: any[] = [];
  userLists: any[] = [];
  userBadges: any[] = [];
  userReviews: any[] = [];
  userRatings: any[] = [];

  // Loading states
  loadingProfile = true;
  loadingWatchedFilms = false;
  loadingLists = false;
  loadingBadges = false;
  loadingReviews = false;

  // Dialogs
  showFollowersDialog = false;
  showFollowingDialog = false;
  followersList: any[] = [];
  followingList: any[] = [];

  availableAvatars = [
    { name: 'Avatar 1', url: 'https://primefaces.org/cdn/primeng/images/demo/avatar/amyelsner.png' },
    { name: 'Avatar 2', url: 'https://primefaces.org/cdn/primeng/images/demo/avatar/onyamalimba.png' },
    { name: 'Avatar 3', url: 'https://primefaces.org/cdn/primeng/images/demo/avatar/walter.jpg' },
    { name: 'Avatar 4', url: 'https://primefaces.org/cdn/primeng/images/demo/avatar/asiyajavayant.png' },
    { name: 'Avatar 5', url: 'https://primefaces.org/cdn/primeng/images/demo/avatar/bernardodominic.png' },
    { name: 'Avatar 6', url: 'https://primefaces.org/cdn/primeng/images/demo/avatar/elwinsharp.png' },
    { name: 'Avatar 7', url: 'https://primefaces.org/cdn/primeng/images/demo/avatar/ionibowcher.png' },
    { name: 'Avatar 8', url: 'https://primefaces.org/cdn/primeng/images/demo/avatar/ivanmagalhaes.png' },
    { name: 'Avatar 9', url: 'https://primefaces.org/cdn/primeng/images/demo/avatar/josephine.png' },
    { name: 'Avatar 10', url: 'https://primefaces.org/cdn/primeng/images/demo/avatar/michaelnovotny.png' },
    { name: 'Avatar 11', url: 'https://primefaces.org/cdn/primeng/images/demo/avatar/stephenshaw.png' },
    { name: 'Avatar 12', url: 'https://primefaces.org/cdn/primeng/images/demo/avatar/xuxuefeng.png' }
  ];

  constructor(
    private http: HttpClient,
    private router: Router,
    private route: ActivatedRoute,
    private filmService: FilmService
  ) { }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.username = params['username'] || 'me';
      this.loadUser();
      this.loadNavbarUser();
      this.setupMenuItems();
    });

    // Reload data when navigating to profile page (e.g., after rating a film or creating a list)
    this.routerSubscription = this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((event: any) => {
        if (event.url.startsWith('/profile')) {
          // Update username from URL if needed
          const urlMatch = event.url.match(/\/profile\/([^\/]+)/);
          if (urlMatch && urlMatch[1] && urlMatch[1] !== 'me') {
            this.username = urlMatch[1];
            // Reload user data when username changes
            this.loadUser();
          } else if (event.url === '/profile' || event.url.startsWith('/profile/me')) {
            // For 'me' or no username, keep current username or set to 'me'
            const newUsername = this.username || 'me';
            if (newUsername !== this.username) {
              this.username = newUsername;
              this.loadUser();
            } else {
              // Same username, just reload lists
              this.loadWatchedFilms();
              this.loadUserLists();
            }
          } else {
            // Reload watched films, ratings, and lists when returning to profile
            this.loadWatchedFilms();
            this.loadUserLists();
          }
        }
      });
  }

  ngOnDestroy() {
    if (this.routerSubscription) {
      this.routerSubscription.unsubscribe();
    }
  }

  // === SETUP MENU ITEMS ====================================================
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

  // === LOAD NAVBAR USER ====================================================
  loadNavbarUser() {
    const cached = localStorage.getItem("user_profile");
    if (cached) {
      try {
        const usr = JSON.parse(cached);
        // Backend returns profile_picture_url directly, not in profile.avatar
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
          // Backend returns profile_picture_url directly in serializer.data
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

  // === LOGOUT ===============================================================
  logout() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user_profile');
    this.router.navigate(['/']);
  }

  // === USER LOAD ========================================================
  loadUser() {
    this.loadingProfile = true;
    const token = localStorage.getItem("access");

    // If no token and not viewing own profile, try to get from cache or show error
    if (!token && this.username !== 'me') {
      // For viewing other users without auth, we'd need a public endpoint
      // For now, require auth
      this.loadingProfile = false;
      return;
    }

    const headers = new HttpHeaders({
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    });

    const profileUrl = this.username === 'me'
      ? `${API_URL}/auth/me/`
      : `${API_URL}/profile/${this.username}/`;

    this.http.get(profileUrl, { headers })
      .subscribe({
        next: (res: any) => {
          console.log('Profile loaded:', res);
          // Backend returns serializer.data directly, so transform to expected format
          // Backend format: { id, user, username, email, bio, profile_picture_url, ... }
          // Frontend expects: { username, profile: { bio, profile_picture_url, ... } }
          this.user = {
            username: res.username || res.user?.username || '',
            email: res.email || res.user?.email || '',
            profile: {
              bio: res.bio || '',
              profile_picture_url: res.profile_picture_url || null,
              display_name: res.display_name || '',
              films_watched_count: res.films_watched_count || 0,
              reviews_count: res.reviews_count || 0,
              lists_count: res.lists_count || 0
            }
          };

          // Extract username from response
          if (res.username) {
            this.username = res.username;
          } else if (res.user?.username) {
            this.username = res.user.username;
          }

          console.log('Username set to:', this.username);

          this.avatarImage = res.profile_picture_url || null;
          this.avatarLabel = (this.username[0] || "U").toUpperCase();
          this.bioToEdit = res.bio || "";
          this.isAdmin = !!(res.is_staff || res.is_superuser);
          this.setupMenuItems();

          // Load all profile data
          this.loadFollowStats();
          this.loadWatchedFilms();
          this.loadUserLists();
          this.loadUserBadges();
          this.loadUserReviews();

          this.loadingProfile = false;
        },
        error: (err) => {
          console.error('Error loading profile:', err);
          console.error('Error status:', err.status);
          console.error('Error details:', err.error);
          this.loadingProfile = false;
        }
      });
  }

  // === LOAD FOLLOW STATS ================================================
  loadFollowStats() {
    const token = localStorage.getItem("access");
    const headers = new HttpHeaders({
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    });

    // Try to get follow status, fallback to counting from followers/following lists
    this.http.get(`${API_URL}/users/${this.username}/follow-status`, { headers })
      .subscribe({
        next: (res: any) => {
          this.followersCount = res.followers_count || 0;
          this.followingCount = res.following_count || 0;
          // Check if current user is following this profile
          if (!this.isOwnProfile() && token) {
            this.isFollowing = res.is_following || false;
          }
        },
        error: () => {
          // Fallback: count from lists
          this.http.get(`${API_URL}/profile/${this.username}/followers/`)
            .subscribe({
              next: (res: any) => {
                this.followersCount = (res.results || res || []).length;
              }
            });
          this.http.get(`${API_URL}/profile/${this.username}/following/`)
            .subscribe({
              next: (res: any) => {
                this.followingCount = (res.results || res || []).length;
              }
            });
        }
      });
  }

  // === LOAD WATCHED FILMS ===============================================
  loadWatchedFilms() {
    this.loadingWatchedFilms = true;
    this.http.get(`${API_URL}/users/${this.username}/watched`)
      .subscribe({
        next: (res: any) => {
          const items = res.results || res || [];
          this.watchedFilms = items.map((film: any) => ({
            ...film,
            film_poster_url:
              film.film_poster_url ||
              film.poster_url ||
              film.poster ||
              film.image ||
              '/assets/default-poster.jpg',
          }));
          // Load ratings for watched films
          this.loadRatingsForWatchedFilms();
          // Load poster URLs from film details if missing
          this.loadMissingPosters();
          this.loadingWatchedFilms = false;
        },
        error: () => {
          this.watchedFilms = [];
          this.loadingWatchedFilms = false;
        }
      });
  }

  // === LOAD MISSING POSTERS FROM FILM DETAILS ==========================
  loadMissingPosters() {
    const token = localStorage.getItem("access");
    const headers = new HttpHeaders({
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    });

    // For films without poster URLs, fetch from film details
    this.watchedFilms.forEach((film: any) => {
      if (!film.film_poster_url || film.film_poster_url === '/assets/default-poster.jpg') {
        const imdbId = film.film_imdb_id;
        if (imdbId) {
          this.http.get(`${API_URL}/films/${imdbId}`, { headers })
            .subscribe({
              next: (filmData: any) => {
                const posterUrl = filmData.metadata?.primaryImage?.url ||
                  filmData.posterUrl ||
                  filmData.poster_url;
                if (posterUrl) {
                  // Update the film in the array
                  const filmIndex = this.watchedFilms.findIndex((f: any) =>
                    f.film_imdb_id === imdbId
                  );
                  if (filmIndex !== -1) {
                    this.watchedFilms[filmIndex].film_poster_url = posterUrl;
                  }
                }
              },
              error: () => {
                // Silently fail - keep default poster
              }
            });
        }
      }
    });
  }

  // === LOAD RATINGS FOR WATCHED FILMS ==================================
  loadRatingsForWatchedFilms() {
    const token = localStorage.getItem("access");
    if (!token) {
      // If no token, just show watched films without ratings
      return;
    }

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    // Get user's ratings - only if viewing own profile or if endpoint allows
    if (this.isOwnProfile()) {
      this.http.get(`${API_URL}/profile/${this.username}/ratings/`, { headers })
        .subscribe({
          next: (res: any) => {
            this.userRatings = res.results || res || [];
            // Match ratings with watched films by film_imdb_id
            this.watchedFilms = this.watchedFilms.map((film: any) => {
              const filmImdbId = String(film.film_imdb_id || '').trim();
              const rating = this.userRatings.find((r: any) => {
                // Try multiple matching strategies
                const ratingImdbId = String(r.film_imdb_id || '').trim();
                if (ratingImdbId && filmImdbId && ratingImdbId === filmImdbId) {
                  return true;
                }
                // Check if film object has imdb_id
                if (r.film && typeof r.film === 'object' && r.film.imdb_id) {
                  return String(r.film.imdb_id).trim() === filmImdbId;
                }
                // Compare UUIDs if both are UUIDs (fallback)
                if (r.film && film.film) {
                  return String(r.film) === String(film.film);
                }
                return false;
              });
              return { ...film, rating: rating || null };
            });
          },
          error: (err) => {
            console.error('Error loading ratings:', err);
            // If ratings endpoint fails, just show films without ratings
          }
        });
    }
  }

  // === LOAD USER LISTS ==================================================
  loadUserLists() {
    if (!this.username) {
      console.warn('Cannot load lists: username not set');
      this.loadingLists = false;
      return;
    }

    this.loadingLists = true;
    const url = this.username === 'me'
      ? `${API_URL}/lists/`
      : `${API_URL}/profile/${this.username}/lists/`;

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('access') || ''}`
    });

    this.http.get(url, { headers })
      .subscribe({
        next: (res: any) => {
          this.userLists = res.results || res || [];
          this.loadingLists = false;
          console.log('Loaded user lists:', this.userLists.length);
        },
        error: (err) => {
          console.error('Error loading user lists:', err);
          this.loadingLists = false;
        }
      });
  }

  // === LOAD USER BADGES ================================================
  loadUserBadges() {
    this.loadingBadges = true;
    this.http.get(`${API_URL}/users/${this.username}/badges`)
      .subscribe({
        next: (res: any) => {
          this.userBadges = res.results || res || [];
          this.loadingBadges = false;
        },
        error: () => {
          this.userBadges = [];
          this.loadingBadges = false;
        }
      });
  }

  // === LOAD USER REVIEWS ===============================================
  loadUserReviews() {
    this.loadingReviews = true;
    this.http.get(`${API_URL}/profile/${this.username}/reviews/`)
      .subscribe({
        next: (res: any) => {
          const items = res.results || res || [];
          this.userReviews = items.map((r: any) => ({
            ...r,
            film_poster_url:
              r.film_poster_url ||
              r.poster_url ||
              r.poster ||
              r.image ||
              '/assets/default-poster.jpg',
            isRevealed: false // Initialize spoiler reveal state
          }));
          // Load missing posters from film details
          this.loadMissingReviewPosters();
          this.loadingReviews = false;
        },
        error: () => {
          this.loadingReviews = false;
        }
      });
  }

  // === LOAD MISSING POSTERS FOR REVIEWS ===============================
  loadMissingReviewPosters() {
    const token = localStorage.getItem("access");
    const headers = new HttpHeaders({
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    });

    // For reviews without poster URLs, fetch from film details
    this.userReviews.forEach((review: any) => {
      if (!review.film_poster_url || review.film_poster_url === '/assets/default-poster.jpg') {
        const imdbId = review.film_imdb_id;
        if (imdbId) {
          this.http.get(`${API_URL}/films/${imdbId}`, { headers })
            .subscribe({
              next: (filmData: any) => {
                const posterUrl = filmData.metadata?.primaryImage?.url ||
                  filmData.posterUrl ||
                  filmData.poster_url;
                if (posterUrl) {
                  // Update the review in the array
                  const reviewIndex = this.userReviews.findIndex((r: any) =>
                    r.film_imdb_id === imdbId && r.id === review.id
                  );
                  if (reviewIndex !== -1) {
                    this.userReviews[reviewIndex].film_poster_url = posterUrl;
                  }
                }
              },
              error: () => {
                // Silently fail - keep default poster
              }
            });
        }
      }
    });
  }

  // === LOAD FOLLOWERS ===================================================
  loadFollowers() {
    this.http.get(`${API_URL}/profile/${this.username}/followers/`)
      .subscribe({
        next: (res: any) => {
          this.followersList = res.results || res || [];
          this.showFollowersDialog = true;
        }
      });
  }

  // === LOAD FOLLOWING ===================================================
  loadFollowing() {
    this.http.get(`${API_URL}/profile/${this.username}/following/`)
      .subscribe({
        next: (res: any) => {
          this.followingList = res.results || res || [];
          this.showFollowingDialog = true;
        }
      });
  }

  // === NAVIGATE TO FILM =================================================
  goToFilm(imdbId: string) {
    this.router.navigate(['/film-details', imdbId]);
  }

  // === TOGGLE SPOILER VISIBILITY =======================================
  toggleSpoiler(review: any) {
    review.isRevealed = !review.isRevealed;
  }

  // === PROFILE PICTURE UPLOAD ===========================================
  onProfilePictureSelect(event: any) {
    const file = event.files?.[0];
    if (file) {
      this.profilePictureFile = file;
      // Create preview
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.avatarImage = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }

  uploadProfilePicture() {
    // Note: Backend currently expects profile_picture_url (URL string), not file upload
    // For now, we'll use the avatar selection with URLs
    // File upload would require backend changes to support multipart/form-data
    this.avatarModalVisible = false;
    this.profilePictureFile = null;

    // If you want to implement file upload, you'd need:
    // 1. Backend endpoint that accepts multipart/form-data
    // 2. Upload file to storage service (S3, etc.)
    // 3. Get URL back and update profile_picture_url
  }

  // === EDIT MODE ========================================================
  enableEditMode() {
    this.editMode = true;
    this.bioToEdit = this.user.profile?.bio || "";
  }

  cancelEdit() {
    this.editMode = false;
    this.bioToEdit = this.user.profile?.bio || "";
  }

  // === SAVE PROFILE (BIO) ================================================
  async saveProfile() {
    console.log('saveProfile called');
    let token = localStorage.getItem("access");
    if (!token) {
      alert("Please log in to save your profile");
      return;
    }

    // Get actual username - use the username from user object if available
    let profileUsername = this.user?.username || this.username;
    if (profileUsername === 'me' || !profileUsername) {
      const cached = localStorage.getItem("user_profile");
      if (cached) {
        try {
          const usr = JSON.parse(cached);
          profileUsername = usr.username || usr.user?.username || 'me';
        } catch { }
      }
    }

    console.log('Saving profile for username:', profileUsername);
    console.log('Bio to save:', this.bioToEdit);

    const payload = {
      profile_picture_url: this.user.profile?.profile_picture_url || "",
      bio: this.bioToEdit
    };

    console.log('Payload:', payload);

    // Always use profile endpoint for PATCH (auth/me only supports GET)
    const url = `${API_URL}/profile/${profileUsername}/`;
    console.log('URL:', url);

    // Try to save with current token
    let headers = new HttpHeaders({
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json"
    });

    this.http.patch(url, payload, { headers })
      .subscribe({
        next: (res: any) => {
          console.log('Profile saved successfully:', res);
          // Backend returns serializer.data directly, so update from response
          if (res.bio !== undefined) {
            this.user.profile.bio = res.bio;
          }
          if (res.profile_picture_url !== undefined) {
            this.user.profile.profile_picture_url = res.profile_picture_url;
          }
          // Update localStorage cache so other pages see the updated profile
          const cached = localStorage.getItem("user_profile");
          if (cached) {
            try {
              const cachedUser = JSON.parse(cached);
              if (res.bio !== undefined) {
                cachedUser.bio = res.bio;
                if (cachedUser.profile) {
                  cachedUser.profile.bio = res.bio;
                }
              }
              if (res.profile_picture_url !== undefined) {
                cachedUser.profile_picture_url = res.profile_picture_url;
                if (cachedUser.profile) {
                  cachedUser.profile.profile_picture_url = res.profile_picture_url;
                }
              }
              localStorage.setItem("user_profile", JSON.stringify(cachedUser));
            } catch (e) {
              console.error('Error updating cache:', e);
            }
          }
          this.editMode = false;
          // Reload user data to get updated profile
          this.loadUser();
        },
        error: async (err) => {
          console.error('Error saving profile:', err);
          console.error('Error status:', err.status);
          console.error('Error details:', err.error);

          // If token expired, try to refresh and retry
          if (err.status === 401 || (err.error?.detail && err.error.detail.includes("token"))) {
            console.log('Token expired, refreshing...');
            const newToken = await this.refreshToken();
            if (newToken) {
              console.log('Token refreshed, retrying...');
              // Retry with new token
              headers = new HttpHeaders({
                Authorization: `Bearer ${newToken}`,
                "Content-Type": "application/json"
              });

              this.http.patch(url, payload, { headers })
                .subscribe({
                  next: (res: any) => {
                    console.log('Profile saved after refresh:', res);
                    // Backend returns serializer.data directly, so update from response
                    if (res.bio !== undefined) {
                      this.user.profile.bio = res.bio;
                    }
                    if (res.profile_picture_url !== undefined) {
                      this.user.profile.profile_picture_url = res.profile_picture_url;
                    }
                    // Update localStorage cache so other pages see the updated profile
                    const cached = localStorage.getItem("user_profile");
                    if (cached) {
                      try {
                        const cachedUser = JSON.parse(cached);
                        if (res.bio !== undefined) {
                          cachedUser.bio = res.bio;
                          if (cachedUser.profile) {
                            cachedUser.profile.bio = res.bio;
                          }
                        }
                        if (res.profile_picture_url !== undefined) {
                          cachedUser.profile_picture_url = res.profile_picture_url;
                          if (cachedUser.profile) {
                            cachedUser.profile.profile_picture_url = res.profile_picture_url;
                          }
                        }
                        localStorage.setItem("user_profile", JSON.stringify(cachedUser));
                      } catch (e) {
                        console.error('Error updating cache:', e);
                      }
                    }
                    this.editMode = false;
                    this.loadUser();
                  },
                  error: (retryErr) => {
                    console.error('Error saving profile after refresh:', retryErr);
                    const errorMsg = retryErr.error?.detail || retryErr.message || "Failed to save biography";
                    alert(`Error: ${errorMsg}. Please try logging in again.`);
                  }
                });
            } else {
              alert("Your session has expired. Please log in again.");
              this.router.navigate(['/']);
            }
          } else {
            const errorMsg = err.error?.detail || err.error?.message || err.message || "Failed to save biography";
            alert(`Error: ${errorMsg}. Status: ${err.status || 'Unknown'}`);
          }
        }
      });
  }

  // === AVATAR SELECT ======================================================
  openAvatarSelection() {
    // Check if current avatar URL matches any available avatar
    this.selectedAvatar = this.availableAvatars.find(av => av.url === this.avatarImage) || null;
    // Keep the current avatarImage value (might be a custom URL)
    this.avatarModalVisible = true;
    // Reset upload state
    this.uploadedFile = null;
    this.uploadedFileName = '';
    this.uploadError = '';
  }

  // === SELECT AVATAR ======================================================
  selectAvatar(avatar: any) {
    this.selectedAvatar = avatar;
    // Clear uploaded file when selecting an avatar
    this.uploadedFile = null;
    this.uploadedFileName = '';
    this.uploadError = '';
  }

  // === FILE UPLOAD ========================================================
  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (!file) {
      return;
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      this.uploadError = 'Please select an image file (JPG, PNG, GIF)';
      return;
    }

    // Validate file size (2MB max)
    const maxSize = 2 * 1024 * 1024; // 2MB in bytes
    if (file.size > maxSize) {
      this.uploadError = 'File size must be less than 2MB';
      return;
    }

    this.uploadError = '';
    this.uploadedFileName = file.name;
    this.profilePictureFile = file;

    // Compress and resize image before converting to base64
    this.compressImage(file);
  }

  // === COMPRESS IMAGE =====================================================
  compressImage(file: File) {
    const reader = new FileReader();
    reader.onload = (e: any) => {
      const img = new Image();
      img.onload = () => {
        // Create canvas to resize and compress
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        if (!ctx) {
          this.uploadError = 'Error processing image. Please try again.';
          return;
        }

        // Calculate new dimensions (max 800x800, maintain aspect ratio)
        const maxWidth = 800;
        const maxHeight = 800;
        let width = img.width;
        let height = img.height;

        if (width > height) {
          if (width > maxWidth) {
            height = (height * maxWidth) / width;
            width = maxWidth;
          }
        } else {
          if (height > maxHeight) {
            width = (width * maxHeight) / height;
            height = maxHeight;
          }
        }

        canvas.width = width;
        canvas.height = height;

        // Draw and compress
        ctx.drawImage(img, 0, 0, width, height);

        // Convert to base64 with compression (0.85 quality for JPEG)
        const quality = 0.85;
        const dataUrl = canvas.toDataURL('image/jpeg', quality);

        this.uploadedFile = dataUrl;
        // Clear selected avatar and URL input when file is uploaded
        this.selectedAvatar = null;
        this.avatarImage = '';
      };
      img.onerror = () => {
        this.uploadError = 'Error loading image. Please try again.';
        this.uploadedFile = null;
        this.uploadedFileName = '';
      };
      img.src = e.target.result;
    };
    reader.onerror = () => {
      this.uploadError = 'Error reading file. Please try again.';
      this.uploadedFile = null;
      this.uploadedFileName = '';
    };
    reader.readAsDataURL(file);
  }

  // === CANCEL AVATAR SELECTION ===========================================
  cancelAvatarSelection() {
    this.avatarModalVisible = false;
    // Reset all states
    this.uploadedFile = null;
    this.uploadedFileName = '';
    this.uploadError = '';
    // Don't clear selectedAvatar or avatarImage - user might want to try again
  }

  // === REFRESH TOKEN ======================================================
  refreshToken(): Promise<string | null> {
    return new Promise((resolve) => {
      const refreshToken = localStorage.getItem("refresh");
      if (!refreshToken) {
        resolve(null);
        return;
      }

      this.http.post(`${API_URL}/auth/token/refresh/`, {
        refresh: refreshToken
      }).subscribe({
        next: (res: any) => {
          if (res.access) {
            localStorage.setItem("access", res.access);
            resolve(res.access);
          } else {
            resolve(null);
          }
        },
        error: () => {
          // Refresh token also expired, need to login again
          resolve(null);
        }
      });
    });
  }

  // === SAVE AVATAR ========================================================
  async saveAvatar() {
    console.log('saveAvatar called');
    let token = localStorage.getItem("access");
    if (!token) {
      alert("Please log in to save your profile picture");
      return;
    }

    // Get actual username - use the username from user object if available
    let profileUsername = this.user?.username || this.username;
    if (profileUsername === 'me' || !profileUsername) {
      const cached = localStorage.getItem("user_profile");
      if (cached) {
        try {
          const usr = JSON.parse(cached);
          profileUsername = usr.username || usr.user?.username || 'me';
        } catch { }
      }
    }

    console.log('Saving avatar for username:', profileUsername);

    // Priority: uploaded file > selected avatar > URL input
    const newAvatarUrl = this.uploadedFile || this.selectedAvatar?.url || this.avatarImage || "";

    if (!newAvatarUrl) {
      alert("Please upload an image, select an avatar, or enter an image URL");
      return;
    }

    console.log('New avatar URL:', newAvatarUrl);

    const payload = {
      profile_picture_url: newAvatarUrl,
      bio: this.user.profile?.bio || ""
    };

    console.log('Payload:', payload);

    // Always use profile endpoint for PATCH (auth/me only supports GET)
    const url = `${API_URL}/profile/${profileUsername}/`;
    console.log('URL:', url);

    // Try to save with current token
    let headers = new HttpHeaders({
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json"
    });

    this.http.patch(url, payload, { headers })
      .subscribe({
        next: (res: any) => {
          console.log('Avatar saved successfully:', res);
          // Backend returns serializer.data directly, so update from response
          const updatedUrl = res.profile_picture_url !== undefined ? res.profile_picture_url : newAvatarUrl;
          this.user.profile.profile_picture_url = updatedUrl;
          this.avatarImage = updatedUrl;
          // Only update navbar if this is the current user's own profile
          if (this.isOwnProfile()) {
            this.navbarAvatarImage = updatedUrl;
          }

          // Update localStorage cache so other pages see the updated profile picture
          const cached = localStorage.getItem("user_profile");
          if (cached) {
            try {
              const cachedUser = JSON.parse(cached);
              cachedUser.profile_picture_url = updatedUrl;
              if (cachedUser.profile) {
                cachedUser.profile.profile_picture_url = updatedUrl;
              }
              localStorage.setItem("user_profile", JSON.stringify(cachedUser));
            } catch (e) {
              console.error('Error updating cache:', e);
            }
          }

          this.avatarModalVisible = false;
          // Clear upload state after successful save
          this.uploadedFile = null;
          this.uploadedFileName = '';
          this.uploadError = '';
          // Keep selectedAvatar if it was selected, otherwise clear it
          if (!this.selectedAvatar) {
            this.selectedAvatar = null;
          }
          // Reload user data to get updated profile
          this.loadUser();
          // Also reload navbar user to update navbar avatar
          this.loadNavbarUser();
        },
        error: async (err) => {
          console.error('Error saving avatar:', err);
          console.error('Error status:', err.status);
          console.error('Error details:', err.error);

          // If token expired, try to refresh and retry
          if (err.status === 401 || (err.error?.detail && err.error.detail.includes("token"))) {
            console.log('Token expired, refreshing...');
            const newToken = await this.refreshToken();
            if (newToken) {
              console.log('Token refreshed, retrying...');
              // Retry with new token
              headers = new HttpHeaders({
                Authorization: `Bearer ${newToken}`,
                "Content-Type": "application/json"
              });

              this.http.patch(url, payload, { headers })
                .subscribe({
                  next: (res: any) => {
                    console.log('Avatar saved after refresh:', res);
                    // Backend returns serializer.data directly, so update from response
                    const updatedUrl = res.profile_picture_url !== undefined ? res.profile_picture_url : newAvatarUrl;
                    this.user.profile.profile_picture_url = updatedUrl;
                    this.avatarImage = updatedUrl;
                    // Only update navbar if this is the current user's own profile
                    if (this.isOwnProfile()) {
                      this.navbarAvatarImage = updatedUrl;
                    }

                    // Update localStorage cache so other pages see the updated profile picture
                    const cached = localStorage.getItem("user_profile");
                    if (cached) {
                      try {
                        const cachedUser = JSON.parse(cached);
                        cachedUser.profile_picture_url = updatedUrl;
                        if (cachedUser.profile) {
                          cachedUser.profile.profile_picture_url = updatedUrl;
                        }
                        localStorage.setItem("user_profile", JSON.stringify(cachedUser));
                      } catch (e) {
                        console.error('Error updating cache:', e);
                      }
                    }

                    this.avatarModalVisible = false;
                    // Clear upload state after successful save
                    this.uploadedFile = null;
                    this.uploadedFileName = '';
                    this.uploadError = '';
                    if (!this.selectedAvatar) {
                      this.selectedAvatar = null;
                    }
                    this.loadUser();
                    // Also reload navbar user to update navbar avatar
                    this.loadNavbarUser();
                  },
                  error: (retryErr) => {
                    console.error('Error saving avatar after refresh:', retryErr);
                    const errorMsg = retryErr.error?.detail || retryErr.message || "Failed to save profile picture";
                    alert(`Error: ${errorMsg}. Please try logging in again.`);
                  }
                });
            } else {
              alert("Your session has expired. Please log in again.");
              this.router.navigate(['/']);
            }
          } else {
            console.error('Full error response:', err);
            let errorMsg = "Failed to save profile picture";
            if (err.error) {
              if (err.error.detail) {
                errorMsg = err.error.detail;
              } else if (typeof err.error === 'string') {
                errorMsg = err.error;
              } else if (err.error.message) {
                errorMsg = err.error.message;
              } else if (err.error.profile_picture_url) {
                // Django validation error
                errorMsg = Array.isArray(err.error.profile_picture_url)
                  ? err.error.profile_picture_url.join(', ')
                  : err.error.profile_picture_url;
              }
            } else if (err.message) {
              errorMsg = err.message;
            }
            alert(`Error: ${errorMsg}. Status: ${err.status || 'Unknown'}`);
          }
        }
      });
  }

  // === NAVIGATION ==========================================================
  goHome() {
    this.router.navigate(['/home']);
  }

  goToFilmSearch() {
    this.router.navigate(['/film-search']);
  }

  goToProfile(username: string) {
    this.router.navigate(['/profile', username]);
  }

  goToProfileFromDialog(username: string) {
    // Close dialogs before navigating
    this.showFollowersDialog = false;
    this.showFollowingDialog = false;
    // Navigate to profile
    this.router.navigate(['/profile', username]);
  }

  goToLists() {
    this.router.navigate(['/lists']);
  }

  goToListDetail(listId: number) {
    this.router.navigate(['/lists', listId]);
  }

  // === TOGGLE FOLLOW ======================================================
  toggleFollow() {
    const token = localStorage.getItem("access");
    if (!token) {
      alert("Please log in to follow users");
      return;
    }

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    if (this.isFollowing) {
      // Unfollow
      this.http.delete(`${API_URL}/users/${this.username}/follow`, { headers })
        .subscribe({
          next: () => {
            this.isFollowing = false;
            this.followersCount = Math.max(0, this.followersCount - 1);
          },
          error: async (err) => {
            if (err.status === 401 || (err.error?.detail && err.error.detail.includes("token"))) {
              const newToken = await this.refreshToken();
              if (newToken) {
                const newHeaders = new HttpHeaders({
                  Authorization: `Bearer ${newToken}`
                });
                this.http.delete(`${API_URL}/users/${this.username}/follow`, { headers: newHeaders })
                  .subscribe({
                    next: () => {
                      this.isFollowing = false;
                      this.followersCount = Math.max(0, this.followersCount - 1);
                    },
                    error: (retryErr) => {
                      console.error('Error unfollowing user after refresh:', retryErr);
                      alert('Error unfollowing user. Please try again.');
                    }
                  });
              } else {
                alert("Your session has expired. Please log in again.");
                this.router.navigate(['/']);
              }
            } else {
              console.error('Error unfollowing user:', err);
              alert('Error unfollowing user. Please try again.');
            }
          }
        });
    } else {
      // Follow
      this.http.post(`${API_URL}/users/${this.username}/follow`, {}, { headers })
        .subscribe({
          next: () => {
            this.isFollowing = true;
            this.followersCount += 1;
          },
          error: async (err) => {
            if (err.status === 401 || (err.error?.detail && err.error.detail.includes("token"))) {
              const newToken = await this.refreshToken();
              if (newToken) {
                const newHeaders = new HttpHeaders({
                  Authorization: `Bearer ${newToken}`
                });
                this.http.post(`${API_URL}/users/${this.username}/follow`, {}, { headers: newHeaders })
                  .subscribe({
                    next: () => {
                      this.isFollowing = true;
                      this.followersCount += 1;
                    },
                    error: (retryErr) => {
                      console.error('Error following user after refresh:', retryErr);
                      alert('Error following user. Please try again.');
                    }
                  });
              } else {
                alert("Your session has expired. Please log in again.");
                this.router.navigate(['/']);
              }
            } else {
              console.error('Error following user:', err);
              alert('Error following user. Please try again.');
            }
          }
        });
    }
  }

  // === CHECK IF OWN PROFILE ===============================================
  isOwnProfile(): boolean {
    const currentUser = localStorage.getItem("user_profile");
    if (!currentUser) return false;
    try {
      const user = JSON.parse(currentUser);
      return user.username === this.username || this.username === 'me';
    } catch {
      return false;
    }
  }

  // === GET EMPTY BADGE SLOTS ==============================================
  getEmptyBadgeSlots(): number[] {
    const filled = Math.min(this.userBadges.length, 9);
    const empty = 9 - filled;
    return Array(empty).fill(0);
  }

  // === HELPER: GET FILM TITLE =============================================
  getFilmTitle(film: any): string {
    const title = film?.film_title || film?.title;
    if (title && typeof title === 'string' && title.trim()) {
      return title.trim();
    }
    return 'Unknown Film';
  }

  // === REVIEW EDIT & DELETE ===============================================
  editingReview: any = null;
  editReviewTitle: string = '';
  editReviewContent: string = '';
  editReviewRating: number = 0;

  openEditReview(review: any) {
    this.editingReview = review;
    this.editReviewTitle = review.title || '';
    this.editReviewContent = review.content || '';
    this.editReviewRating = review.rating || 0;
  }

  cancelEditReview() {
    this.editingReview = null;
    this.editReviewTitle = '';
    this.editReviewContent = '';
    this.editReviewRating = 0;
  }

  saveEditReview() {
    if (!this.editingReview) return;

    const payload: any = {
      title: this.editReviewTitle.trim(),
      content: this.editReviewContent.trim(),
    };

    if (this.editReviewRating && this.editReviewRating >= 1 && this.editReviewRating <= 5) {
      payload.rating = this.editReviewRating;
    }

    this.filmService.updateReview(this.editingReview.id, payload).subscribe({
      next: (res: any) => {
        // Reload reviews to get updated data
        this.loadUserReviews();
        this.cancelEditReview();
      },
      error: (err) => {
        console.error('Error updating review:', err);
        console.error('Full error:', JSON.stringify(err, null, 2));
        const errorMsg = err.error?.detail || err.error?.message || err.message || 'Failed to update review. Please try again.';
        alert(`Error: ${errorMsg}`);
      }
    });
  }

  deleteReview(review: any) {
    if (!confirm('Are you sure you want to delete this review?')) {
      return;
    }

    this.filmService.deleteReview(review.id).subscribe({
      next: () => {
        // Reload reviews to get updated list
        this.loadUserReviews();
      },
      error: (err) => {
        console.error('Error deleting review:', err);
        console.error('Full error:', JSON.stringify(err, null, 2));
        const errorMsg = err.error?.detail || err.error?.message || err.message || 'Failed to delete review. Please try again.';
        alert(`Error: ${errorMsg}`);
      }
    });
  }

  isReviewOwner(review: any): boolean {
    const currentUser = localStorage.getItem("user_profile");
    if (!currentUser) return false;
    try {
      const user = JSON.parse(currentUser);
      return user.username === review.username || user.id === review.user;
    } catch {
      return false;
    }
  }
}

