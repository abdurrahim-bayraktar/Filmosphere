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
import { FilmDetail, UserRating, UserMood } from '../../models/film.model';

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
  
  // UI State
  showReviewDialog: boolean = false;
  newReview = { title: '', content: '' };
  
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

  onRate(event: any) {
    // Basic rate with overall only
    const ratingValue = event.value;
    const payload: UserRating = { overall_rating: ratingValue };
    
    this.filmService.rateFilm(this.imdbId, payload).subscribe(response => {
       console.log('Rated successfully', response);
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