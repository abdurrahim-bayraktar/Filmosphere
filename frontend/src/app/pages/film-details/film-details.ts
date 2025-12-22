import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { RatingModule } from 'primeng/rating';
import { TagModule } from 'primeng/tag';
import { TabsModule } from 'primeng/tabs'; // v18
import { DialogModule } from 'primeng/dialog';
import { TextareaModule } from 'primeng/textarea';
import { SelectModule } from 'primeng/select';
import { FilmService } from '../../services/film.service';
import { FilmDetail, UserRating, UserMood, RATING_ASPECTS, Review } from '../../models/film.model';

@Component({
  selector: 'app-film-detail',
  standalone: true,
  imports: [
    CommonModule, ButtonModule, RatingModule, TagModule, TabsModule, 
    FormsModule, DialogModule, TextareaModule, SelectModule
  ],
  templateUrl: './film-details.html',
  styleUrls: ['./film-details.css']
})

export class FilmDetailComponent implements OnInit {
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

  constructor(
    private route: ActivatedRoute,
    private filmService: FilmService
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.imdbId = params.get('id') || 'tt1375666'; 
      this.loadFilmData();
    });
  }

  // src/app/pages/film-details/film-detail.component.ts

  loadFilmData() {
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
        next: (mood) => this.userMood = mood,
        error: (e) => console.log('Could not fetch mood (likely 401)', e)
      });
    }
  }

  loadReviews() {
    this.filmService.getFilmReviews(this.imdbId).subscribe({
      next: (data) => {
        // Map the API data and initialize isRevealed to false
        this.reviews = data.map(r => ({
          ...r,
          isRevealed: false 
        }));
      },
      error: (err) => console.error('Error loading reviews:', err)
    });
  }

  toggleSpoiler(review: Review) {
    review.isRevealed = !review.isRevealed;
  }

  getActorName(nameData: any): string {
      if (!nameData) return 'Unknown';
      if (typeof nameData === 'string') return nameData;
      
      // Check common API locations for the name string
      return nameData.text || nameData.name || nameData.nameText?.text || 'Unknown';
  }
  // Add this helper function to your class to convert seconds to "Xh Ym"
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
    this.filmService.logMood(this.imdbId, this.userMood).subscribe(() => {
      console.log('Mood updated');
    });
  }

  openReviewDialog() {
    this.showReviewDialog = true;
  }

  submitReview() {
    const payload = {
      ...this.newReview,
      rating: this.overallRating // Attach current star rating
    };
    
    this.filmService.createReview(this.imdbId, payload).subscribe(() => {
      this.showReviewDialog = false;
      this.newReview = { title: '', content: '' }; // Reset
      // Optionally reload reviews here
    });
  }

}