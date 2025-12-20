import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, map, of } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SearchService {

  private kinoKey = "fCxG8kroiDIHzQZWXnhJ0NVdqwqtmahDz0OSnCieTMEwTlj6vj37Bs4KFbcaYmlv";

  constructor(private http: HttpClient) {}

searchIMDB(query: string): Observable<any[]> {
  return this.http.get<any>(`http://127.0.0.1:8000/api/search/imdb/?q=${query}`)
    .pipe(map(res => res.results || []));
}


}
