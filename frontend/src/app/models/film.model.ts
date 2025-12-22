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
    plot?: number;
    acting?: number;
    total_ratings: number;
  };

  user_rating?: UserRating;
  
  cast?: Actor[];       // <--- Added this
  reviews?: Review[];   // <--- Added this
}

export interface UserRating {
  overall_rating?: number;
  plot_rating?: number;
  acting_rating?: number;
  cinematography_rating?: number;
  soundtrack_rating?: number;
  originality_rating?: number;
  direction_rating?: number;

  // ✅ FIX: Allow dynamic access by string key
  [key: string]: number | undefined;
}

// Helper to easily iterate in the HTML
export const RATING_ASPECTS = [
  { label: 'Plot', key: 'plot_rating' },
  { label: 'Acting', key: 'acting_rating' },
  { label: 'Cinematography', key: 'cinematography_rating' },
  { label: 'Soundtrack', key: 'soundtrack_rating' },
  { label: 'Originality', key: 'originality_rating' },
  { label: 'Direction', key: 'direction_rating' }
];

export interface Actor {
  name: string;
  role: string;
  profileUrl?: string;
}

export interface Review {
id: number;
  user: number;
  username: string; // The backend provides this directly now
  title: string;
  content: string;  // mapped from 'comment' in old model
  rating: number;
  likes_count: number;
  is_liked: boolean;
  
  // Spoiler flags
  contains_spoiler: boolean; 
  is_spoiler: boolean;
  is_auto_detected_spoiler: boolean;
  
  created_at: string;
  
  // UI State (Not from API)
  isRevealed?: boolean;
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