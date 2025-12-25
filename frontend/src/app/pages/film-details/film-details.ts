import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { RatingModule } from 'primeng/rating';
import { TagModule } from 'primeng/tag';
import { TabsModule } from 'primeng/tabs'; // v18
import { DialogModule } from 'primeng/dialog';
import { TextareaModule } from 'primeng/textarea';
import { SelectModule } from 'primeng/select';
import { InputTextModule } from 'primeng/inputtext';
import { CheckboxModule } from 'primeng/checkbox';
import { AvatarModule } from 'primeng/avatar';
import { PopoverModule } from 'primeng/popover';
import { MenuModule } from 'primeng/menu';
import { MenuItem } from 'primeng/api';
import { Popover } from 'primeng/popover';
import { HttpClient } from '@angular/common/http';
import { FilmService } from '../../services/film.service';
import { FilmDetail, UserRating, UserMood, RATING_ASPECTS, Review } from '../../models/film.model';

@Component({
  selector: 'app-film-detail',
  standalone: true,
  imports: [
    CommonModule, ButtonModule, RatingModule, TagModule, TabsModule,
    FormsModule, DialogModule, TextareaModule, SelectModule, InputTextModule,
    RouterModule, AvatarModule, PopoverModule, MenuModule, CheckboxModule
  ],
  templateUrl: './film-details.html',
  styleUrls: ['./film-details.css']
})

export class FilmDetailComponent implements OnInit {
  @ViewChild('profileMenu') profileMenu!: Popover;

  imdbId: string = '';
  film: FilmDetail | null = null;
  
  // User Interaction State
  isWatched: boolean = false;
  userRating: UserRating = {}; // Stores partial updates
  overallRating: number = 0;   // Helper for the main star UI
  userMood: UserMood = {};

  reviews: Review[] = []; // Store reviews here specifically

  // UI State
  showReviewDialog: boolean = false;
  newReview = { title: '', content: '' };

  // Rating Dialog State
  showRatingDialog: boolean = false;
  tempRating: UserRating = {}; // Holds changes inside the dialog
  ratingAspects = RATING_ASPECTS; // For the *ngFor loop
  
  // Static Options
  moodOptions = [
    { label: 'Happy', value: 'happy' },
    { label: 'Sad', value: 'sad' },
    { label: 'Excited', value: 'excited' },
    { label: 'Calm', value: 'calm' },
    { label: 'Anxious', value: 'anxious' },
    { label: 'Bored', value: 'bored' },
    { label: 'Energetic', value: 'energetic' },
    { label: 'Relaxed', value: 'relaxed' },
    { label: 'Stressed', value: 'stressed' },
    { label: 'Neutral', value: 'neutral' }
  ];

  // Navbar state
  user: any = null;
  avatarLabel: string = '';
  avatarImage: string | null = null;
  isAdmin = false;
  menuItems: MenuItem[] = [];

  // Lists state
  userLists: any[] = [];
  showListDialog: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private filmService: FilmService,
    private router: Router,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.loadUser();
    this.route.paramMap.subscribe(params => {
      this.imdbId = params.get('id') || 'tt1375666'; 
      this.loadFilmData();
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

  loadUser() {
    const cached = localStorage.getItem('user_profile');
    if (cached) {
      try {
        const usr = JSON.parse(cached);
        this.user = usr;
        this.isAdmin = !!(usr.is_staff || usr.is_superuser);
        this.avatarImage = usr.profile_picture_url || usr.profile?.profile_picture_url || null;
        this.avatarLabel = (usr.username || usr.user?.username || 'U')[0]?.toUpperCase() || 'U';
        this.setupMenuItems();
      } catch (e) {
        console.error('Error parsing cached user:', e);
      }
    }

    const token = localStorage.getItem('access');
    if (!token) return;

    this.http.get('http://127.0.0.1:8000/api/auth/me/', {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (res: any) => {
        this.user = res;
        this.isAdmin = !!(res.is_staff || res.is_superuser);
        this.avatarImage = res.profile_picture_url || res.profile?.profile_picture_url || null;
        this.avatarLabel = (res.username || res.user?.username || 'U')[0]?.toUpperCase() || 'U';
        localStorage.setItem('user_profile', JSON.stringify(res));
        this.setupMenuItems();
      },
      error: (err) => console.error('Error loading user:', err)
    });
  }

  logout() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user_profile');
    this.user = { username: 'Guest' };
    this.avatarLabel = 'G';
    this.avatarImage = null;
    this.router.navigate(['/']);
  }

  // src/app/pages/film-details/film-detail.component.ts

  loadFilmData() {
    this.loadUserLists();
    // 1. Get Details
    this.filmService.getFilmDetails(this.imdbId).subscribe({
      next: (data: any) => {
        console.log('Raw API Response:', data);
        const directorCredit = data.credits?.credits?.find((c: any) => c.category === 'director');
        const directorName = directorCredit?.name?.displayName || data.metadata?.directors?.[0]?.name || 'Unknown';

        // MAP the nested data to the flat structure your Template expects
        this.film = {
          metadata: data.metadata,
          imdb_id: data.imdb_id,
          // Title is inside metadata
          title: data.metadata?.primaryTitle || data.title || 'Untitled',
          // Year is inside metadata
          year: data.metadata?.startYear || 0,
          // Image is inside metadata.primaryImage.url
          posterUrl: data.metadata?.primaryImage?.url || 'https://via.placeholder.com/300x450',
          // Plot/Description is inside metadata
          description: data.metadata?.plot || 'No description available.',
          // Director (safe check if directors array exists)
          director: directorName,
          // Genres
          genres: data.metadata?.genres || [],
          // Convert runtimeSeconds (e.g. 5820) to string "1h 37m"
          duration: this.formatDuration(data.metadata?.runtimeSeconds),
          // Pass through ratings
          rating_statistics: data.rating_statistics || { overall: 0, total_ratings: 0 },
          // Use a high-res image for backdrop if available, else poster
          backdropUrl: data.metadata?.primaryImage?.url, 
          // Cast mapping (safe check)
          cast: data.credits?.credits
      // 1. FILTER: Only keep entries where category is 'actor' or 'actress'
      ?.filter((c: any) => c.category === 'actor' || c.category === 'actress')
      
      // 2. SLICE: Get the top 6 actors (matches your 6-column grid)
      .slice(0, 6)
      
      // 3. MAP: Map to your model (keeping the image logic working)
      .map((c: any) => ({
          name: c.name?.displayName || 'Unknown',
          role: c.characters?.[0] || 'Actor',
          profileUrl: c.name?.primaryImage?.url || null
      })) || [],
          reviews: [] // Initialize empty if not provided
        };

        // Handle User Rating if present
        if (data.user_rating) {
          this.userRating = data.user_rating;
          this.overallRating = data.user_rating.overall_rating || 0;
        }
      },
      error: (err) => {
        console.error('Error loading film details:', err);
      }
    });

    this.loadReviews();
    // 2. ONLY load private data if logged in (Prevents 401 Error)
    if (this.filmService.isLoggedIn()) {
      this.filmService.getWatchedStatus(this.imdbId).subscribe({
        next: (status) => this.isWatched = status.is_watched,
        error: (e) => console.log('Could not fetch watched status (likely 401)', e)
      });

      this.filmService.getUserMood(this.imdbId).subscribe({
        next: (mood) => {
          this.userMood = mood || {};
        },
        error: (e) => {
          // 404 is normal if user hasn't logged a mood yet
          if (e.status === 404) {
            this.userMood = {};
          } else {
            console.log('Could not fetch mood:', e);
          }
        }
      });
    }
  }
  watchTrailer() {
    if (!this.imdbId) {
      console.warn('No IMDB ID available to fetch trailer.');
      return;
    }

    const url = `http://127.0.0.1:8000/api/kinocheck-url/${this.imdbId}/`;

    // Optional: Add a loading state here if you want to show a spinner
    // this.isLoadingTrailer = true;

    this.http.get<{ kinocheck_url: string }>(url).subscribe({
      next: (response) => {
        if (response && response.kinocheck_url) {
          // Open in a new tab
          window.open(response.kinocheck_url, '_blank');
        } else {
          alert('Trailer not available for this film.');
        }
      },
      error: (err) => {
        console.error('Error fetching trailer:', err);
        alert('Could not fetch trailer link.');
      }
    });
  }
  loadReviews() {
    this.filmService.getFilmReviews(this.imdbId).subscribe({
      next: (data: any) => {
        console.log('=== REVIEWS DEBUG ===');
        console.log('Raw data:', data);
        console.log('Is array?', Array.isArray(data));
        console.log('data.results?', data?.results);
        
        // DRF may return a paginated object; normalize to array
        const items = Array.isArray(data) ? data : data?.results || [];
        console.log('Items array:', items);
        console.log('Items length:', items.length);

        this.reviews = items.map((r: any) => ({
          ...r,
          isRevealed: false,
        }));
        console.log('Final this.reviews:', this.reviews);
        console.log('Final this.reviews.length:', this.reviews.length);
        console.log('====================');
      },
      error: (err) => {
        console.error('=== ERROR LOADING REVIEWS ===');
        console.error('Error:', err);
        console.error('Status:', err.status);
        console.error('Message:', err.message);
        console.error('Error details:', err.error);
        console.error('============================');
      }
    });
  }

  toggleSpoiler(review: Review) {
    review.isRevealed = !review.isRevealed;
  }

  toggleLike(review: Review) {
    if (!this.isLoggedIn()) {
      return;
    }

    const token = localStorage.getItem('access');
    if (!token) return;

    const headers = { 'Authorization': `Bearer ${token}` };

    this.http.post(`http://127.0.0.1:8000/api/reviews/${review.id}/like`, {}, { headers })
      .subscribe({
        next: (response: any) => {
          // Update the review with the new data from the server
          review.is_liked = response.review.is_liked;
          review.likes_count = response.review.likes_count;
        },
        error: (err) => {
          console.error('Error toggling like:', err);
        }
      });
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('access');
  }


  getActorName(nameData: any): string {
      if (!nameData) return 'Unknown';
      if (typeof nameData === 'string') return nameData;
      
      // Check common API locations for the name string
      return nameData.text || nameData.name || nameData.nameText?.text || 'Unknown';
  }
  // Add this helper function to your class to convert seconds to "Xh Ym"
  // Lists methods
  loadUserLists() {
    this.filmService.getLists().subscribe({
      next: (res: any) => {
        this.userLists = (res.results || res || []).map((list: any) => {
          // Check if film is in this list by comparing imdb_id
          const hasFilm = list.items?.some((item: any) => {
            const itemImdbId = item.film_imdb_id || item.film?.imdb_id || item.film;
            return itemImdbId && itemImdbId.trim() === this.imdbId.trim();
          }) || false;
          
          return {
            ...list,
            hasFilm: hasFilm
          };
        });
      },
      error: (err) => {
        console.error('Error loading lists:', err);
      }
    });
  }

  openListDialog() {
    this.showListDialog = true;
  }

  closeListDialog() {
    this.showListDialog = false;
  }

  toggleFilmInList(list: any, event?: Event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    
    const currentState = list.hasFilm;
    const newState = !currentState;
    
    if (currentState) {
      // Remove from list
      this.filmService.removeFilmFromList(list.id, this.imdbId).subscribe({
        next: () => {
          list.hasFilm = false;
          if (list.items) {
            list.items = list.items.filter((item: any) => item.film_imdb_id !== this.imdbId);
            list.films_count = (list.films_count || 0) - 1;
          }
        },
        error: (err) => {
          console.error('Error removing film from list:', err);
          const errorMsg = err.error?.detail || err.error?.message || err.message || 'Failed to remove film from list';
          alert(`Error: ${errorMsg}`);
          // Revert checkbox state on error
          list.hasFilm = currentState;
        }
      });
    } else {
      // Add to list
      this.filmService.addFilmToList(list.id, this.imdbId).subscribe({
        next: (res: any) => {
          list.hasFilm = true;
          if (!list.items) {
            list.items = [];
          }
          list.items.push({
            film_imdb_id: this.imdbId,
            film_title: this.film?.title || 'Unknown Film',
            film_poster_url: this.film?.posterUrl || this.film?.metadata?.primaryImage?.url,
            film_year: this.film?.year || this.film?.metadata?.releaseDate?.year
          });
          list.films_count = (list.films_count || 0) + 1;
        },
        error: (err) => {
          console.error('Error adding film to list:', err);
          const errorMsg = err.error?.detail || err.error?.message || err.message || 'Failed to add film to list';
          alert(`Error: ${errorMsg}`);
          // Revert checkbox state on error
          list.hasFilm = currentState;
        }
      });
    }
  }

  goToLists() {
    this.router.navigate(['/lists']);
  }

  formatDuration(seconds: number): string {
    if (!seconds) return 'N/A';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return `${h}h ${m}m`;
  }

  // --- Actions ---

  toggleWatched() {
    if (this.isWatched) {
      this.filmService.markAsUnwatched(this.imdbId).subscribe(() => this.isWatched = false);
    } else {
      this.filmService.markAsWatched(this.imdbId).subscribe(() => this.isWatched = true);
    }
  }

  openRatingDialog(initialValue?: number) {
      // 1. Clone existing rating or start fresh
      this.tempRating = { ...this.userRating };
      
      // 2. If triggered by clicking the sidebar stars, capture that value immediately
      if (initialValue) {
        this.tempRating.overall_rating = initialValue;
      }

      this.showRatingDialog = true;

  }

  updateCalculatedAverage() {
      let sum = 0;
      let count = 0;

      this.ratingAspects.forEach(aspect => {
        // @ts-ignore - access by key dynamically
        const val = this.tempRating[aspect.key];
        if (val && val > 0) {
          sum += val;
          count++;
        }
      });

      if (count > 0) {
        // Round to nearest 0.5 or 1 depending on preference. 
        // Math.round(num) for integer, or (Math.round(num * 2) / 2) for half-stars
        this.tempRating.overall_rating = Math.round(sum / count);
      }
  }

  submitRating() {
      // 1. Construct Payload based on what is filled
      const payload: UserRating = {};

      // If we have aspects, send them. The backend calculates average, 
      // but we can send overall_rating too if we want to enforce the UI value.
      let hasAspects = false;
      this.ratingAspects.forEach(aspect => {
        // @ts-ignore
        const val = this.tempRating[aspect.key];
        if (val) {
          // @ts-ignore
          payload[aspect.key] = val;
          hasAspects = true;
        }
      });

      // Always send overall_rating (either user defined or auto-calculated)
      if (this.tempRating.overall_rating) {
        payload.overall_rating = this.tempRating.overall_rating;
      }

      // 2. Call API
      this.filmService.rateFilm(this.imdbId, payload).subscribe({
        next: () => {
          this.userRating = { ...this.tempRating }; // Update local state
          this.overallRating = this.tempRating.overall_rating || 0; // Update sidebar stars
          this.showRatingDialog = false;
          console.log('Rating saved successfully');
        },
        error: (err) => console.error('Error saving rating', err)
      });
    }

  deleteRating() {
    this.filmService.deleteRating(this.imdbId).subscribe({
      next: () => {
        this.userRating = {};
        this.overallRating = 0;
        this.showRatingDialog = false;
        console.log('Rating removed');
      },
      error: (err) => console.error('Error removing rating', err)
    });
  }


  saveMood() {
    // Only save if at least one mood is selected
    if (this.userMood.mood_before || this.userMood.mood_after) {
      this.filmService.logMood(this.imdbId, this.userMood).subscribe({
        next: () => {
          console.log('Mood updated');
        },
        error: (err) => {
          console.error('Error saving mood:', err);
        }
      });
    }
  }

  getMoodIcon(moodValue: string): string {
    const iconMap: { [key: string]: string } = {
      'happy': 'pi pi-smile',
      'sad': 'pi pi-frown',
      'excited': 'pi pi-star-fill',
      'calm': 'pi pi-heart',
      'anxious': 'pi pi-exclamation-triangle',
      'bored': 'pi pi-minus-circle',
      'energetic': 'pi pi-bolt',
      'relaxed': 'pi pi-check-circle',
      'stressed': 'pi pi-times-circle',
      'neutral': 'pi pi-circle'
    };
    return iconMap[moodValue] || 'pi pi-circle';
  }

  openReviewDialog() {
    this.showReviewDialog = true;
  }

  submitReview() {
    // Check if user is logged in
    if (!this.filmService.isLoggedIn()) {
      alert('Please log in to post a review');
      return;
    }

    // Validate required fields
    if (!this.newReview.title?.trim() || !this.newReview.content?.trim()) {
      alert('Please fill in both title and content');
      return;
    }

    const payload: any = {
      title: this.newReview.title.trim(),
      content: this.newReview.content.trim(),
    };

    // Only include rating if it's valid (1-5)
    if (this.overallRating && this.overallRating >= 1 && this.overallRating <= 5) {
      payload.rating = this.overallRating;
    }
    
    this.filmService.createReview(this.imdbId, payload).subscribe({
      next: (response: any) => {
        this.showReviewDialog = false;
        this.newReview = { title: '', content: '' }; // Reset
        this.loadReviews(); // refresh list
        
        // Check if review was flagged for moderation
        if (response.moderation_message) {
          alert(response.moderation_message);
          console.log('Review submitted for moderation:', response.moderation_message);
        } else {
          alert('Review posted successfully!');
          console.log('Review posted successfully');
        }
      },
      error: (err) => {
        console.error('Error creating review:', err);
        // Show user-friendly error message
        let errorMsg = 'Failed to post review. Please try again.';
        if (err.error?.detail) {
          errorMsg = err.error.detail;
        } else if (err.error?.rating) {
          errorMsg = `Rating error: ${err.error.rating[0]}`;
        } else if (err.error?.title) {
          errorMsg = `Title error: ${err.error.title[0]}`;
        } else if (err.error?.content) {
          errorMsg = `Content error: ${err.error.content[0]}`;
        } else if (err.status === 401) {
          errorMsg = 'Please log in to post a review';
        }
        alert(errorMsg);
      }
    });
  }

}