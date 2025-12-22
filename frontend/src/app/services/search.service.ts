import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SearchService {

  private apiUrl = 'http://127.0.0.1:8000/api';

  constructor(private http: HttpClient) {}


/** 1) Page Opening – Trending Films */
getAllFilms(): Observable<any[]> {
  return this.http
    .get<any>(`${this.apiUrl}/kinocheck/trailers/trending`)
    .pipe(
      map(res => {
        const dataArray = Array.isArray(res) 
          ? res 
          : Object.values(res).filter(item => item && typeof item === 'object');

        return dataArray.map((item: any) => ({
          title: item.title,
          poster: item.thumbnail,
          genres: item.genres || [],
          imdb_id: item.resource?.imdb_id
        }));
      })
    );
}

  /** 2) Genre Filter */
  filterByGenre(genre: string): Observable<any[]> {
    return this.http
      .get<any>(`${this.apiUrl}/kinocheck/trailers/?genres=${genre}`)
      .pipe(
        map(res => {
          const data = Array.isArray(res)
            ? res
            : Object.values(res).filter(v => v && typeof v === 'object');

          return data.map((item: any) => ({
            title: item.title,
            poster: item.thumbnail || item.poster,
            genres: item.genres || [],
            imdb_id: item.resource?.imdb_id
          }));
        })
      );
  }

  /** 3) IMDb Search */
  searchIMDB(query: string): Observable<any[]> {
  return this.http
    .get<any>(`${this.apiUrl}/search/imdb/?q=${query}`)
    .pipe(map(res => res.results || []));
}
}
