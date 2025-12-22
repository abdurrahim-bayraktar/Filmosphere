import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { FilmDetail, UserRating, WatchedStatus, UserMood, ReviewRequest } from '../models/film.model';

@Injectable({
  providedIn: 'root'
})
export class FilmService {
  private apiUrl = 'http://localhost:8000/api'; // Adjust to your Django URL

  constructor(private http: HttpClient) {}

private getAuthHeaders(): HttpHeaders {
  const token = localStorage.getItem('access_token');
  
  // CRITICAL FIX: Only add the header if the token actually exists
  if (token) {
    return new HttpHeaders({ 'Authorization': `Bearer ${token}` });
  }
  return new HttpHeaders();
}

// Add a helper to check if user is logged in
isLoggedIn(): boolean {
  return !!localStorage.getItem('access_token');
}

  // --- 2. Film Details ---
  getFilmDetails(imdbId: string): Observable<FilmDetail> {
    // Optional Auth headers included for user_rating
    return this.http.get<FilmDetail>(`${this.apiUrl}/films/${imdbId}`, { headers: this.getAuthHeaders() });
  }

  // --- 3. Rating ---
  rateFilm(imdbId: string, ratings: UserRating): Observable<any> {
    return this.http.post(`${this.apiUrl}/films/${imdbId}/rate`, ratings, { headers: this.getAuthHeaders() });
  }

  getUserRating(imdbId: string): Observable<UserRating> {
    return this.http.get<UserRating>(`${this.apiUrl}/films/${imdbId}/rate`, { headers: this.getAuthHeaders() });
  }

  deleteRating(imdbId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/films/${imdbId}/rate`, { headers: this.getAuthHeaders() });
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
}