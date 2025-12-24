import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { FilmDetail, UserRating, WatchedStatus, UserMood, Review, ReviewRequest } from '../models/film.model';

@Injectable({
  providedIn: 'root'
})
export class FilmService {
  private apiUrl = 'http://127.0.0.1:8000/api'; // Adjust to your Django URL

  constructor(private http: HttpClient) {}

private getAuthHeaders(): HttpHeaders {
  const token = localStorage.getItem('access');
  
  // CRITICAL FIX: Only add the header if the token actually exists
  if (token) {
    return new HttpHeaders({ 'Authorization': `Bearer ${token}` });
  }
  return new HttpHeaders();
}

// Add a helper to check if user is logged in
isLoggedIn(): boolean {
  // Tokens are saved under "access" in the login flow
  return !!localStorage.getItem('access');
}

  // --- 2. Film Details ---
  getFilmDetails(imdbId: string): Observable<FilmDetail> {
    // Optional Auth headers included for user_rating
    return this.http.get<FilmDetail>(`${this.apiUrl}/films/${imdbId}`, { headers: this.getAuthHeaders() });
  }

  // --- 4. Watched ---
  markAsWatched(imdbId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/films/${imdbId}/watched`, {}, { headers: this.getAuthHeaders() });
  }

  markAsUnwatched(imdbId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/films/${imdbId}/unwatched`, { headers: this.getAuthHeaders() });
  }

  getWatchedStatus(imdbId: string): Observable<WatchedStatus> {
    return this.http.get<WatchedStatus>(`${this.apiUrl}/films/${imdbId}/watched-status`, { headers: this.getAuthHeaders() });
  }

  // --- 5. Mood ---
  logMood(imdbId: string, moodData: UserMood): Observable<any> {
    return this.http.post(`${this.apiUrl}/films/${imdbId}/mood`, moodData, { headers: this.getAuthHeaders() });
  }

  getUserMood(imdbId: string): Observable<UserMood> {
    return this.http.get<UserMood>(`${this.apiUrl}/films/${imdbId}/mood`, { headers: this.getAuthHeaders() });
  }

  // --- 6. Reviews ---
  createReview(imdbId: string, review: ReviewRequest): Observable<any> {
    return this.http.post(`${this.apiUrl}/films/${imdbId}/reviews/create`, review, { headers: this.getAuthHeaders() });
  }

  /**
   * Rate a film. Supports partial updates (e.g., just overall, or just specific aspects).
   */
  rateFilm(imdbId: string, ratingPayload: UserRating): Observable<any> {
    return this.http.post(`${this.apiUrl}/films/${imdbId}/rate`, ratingPayload, { headers: this.getAuthHeaders() });
  }

  /**
   * Delete the user's rating for a film.
   */
  deleteRating(imdbId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/films/${imdbId}/rate`, { headers: this.getAuthHeaders() });
  }
  
  /**
   * (Optional) Fetch just the user's rating if you need to refresh it separately
   */
  getUserRating(imdbId: string): Observable<UserRating> {
    return this.http.get<UserRating>(`${this.apiUrl}/films/${imdbId}/rate`);
  }

  getFilmReviews(imdbId: string): Observable<any> {
    // DRF paginates: returns { count, next, previous, results: [...] }
    return this.http.get(`${this.apiUrl}/films/${imdbId}/reviews`);
  }

  // --- Review Update & Delete ---
  updateReview(reviewId: number, review: ReviewRequest): Observable<any> {
    return this.http.put(`${this.apiUrl}/reviews/${reviewId}`, review, { headers: this.getAuthHeaders() });
  }

  deleteReview(reviewId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/reviews/${reviewId}`, { headers: this.getAuthHeaders() });
  }

  // --- Lists ---
  getLists(): Observable<any> {
    return this.http.get(`${this.apiUrl}/lists/`, { headers: this.getAuthHeaders() });
  }

  createList(listData: { title: string; description?: string; is_public?: boolean }): Observable<any> {
    return this.http.post(`${this.apiUrl}/lists/create/`, listData, { headers: this.getAuthHeaders() });
  }

  getList(listId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/lists/${listId}`, { headers: this.getAuthHeaders() });
  }

  updateList(listId: number, listData: { title?: string; description?: string; is_public?: boolean }): Observable<any> {
    return this.http.put(`${this.apiUrl}/lists/${listId}`, listData, { headers: this.getAuthHeaders() });
  }

  deleteList(listId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/lists/${listId}`, { headers: this.getAuthHeaders() });
  }

  addFilmToList(listId: number, imdbId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/lists/${listId}/films`, { imdb_id: imdbId }, { headers: this.getAuthHeaders() });
  }

  removeFilmFromList(listId: number, imdbId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/lists/${listId}/films/${imdbId}`, { headers: this.getAuthHeaders() });
  }
}