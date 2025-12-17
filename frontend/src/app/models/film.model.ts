export interface FilmDetail {
  imdb_id: string;
  title: string;
  year: number;
  metadata: any;       // Keeps the raw metadata if you need it later
  
  // UI-Mapped Fields
  posterUrl?: string;
  backdropUrl?: string;
  description?: string; // <--- Added this
  director?: string;    // <--- Added this
  duration?: string;    // <--- Added this
  genres?: string[];    // <--- Added this
  
  rating_statistics: {
    overall: number;
    plot: number;
    acting: number;
    total_ratings: number;
  };

  user_rating?: UserRating; 
  
  cast?: Actor[];       // <--- Added this
  reviews?: Review[];   // <--- Added this
}

export interface Actor {
  name: string;
  role: string;
  profileUrl?: string;
}

export interface Review {
  user: string;
  rating: number;
  comment: string;
}

export interface UserRating {
  overall_rating?: number;
  plot_rating?: number;
  acting_rating?: number;
  cinematography_rating?: number;
  soundtrack_rating?: number;
  originality_rating?: number;
  direction_rating?: number;
}

export interface WatchedStatus {
  is_watched: boolean;
  watched_at?: string;
}

export interface UserMood {
  mood_before?: string;
  mood_after?: string;
}

export interface ReviewRequest {
  title: string;
  content: string;
  rating?: number;
}