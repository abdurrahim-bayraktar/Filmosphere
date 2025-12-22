import { Component, OnInit } from '@angular/core';
import { SearchService } from '../../services/search.service';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { NgFor, NgIf } from '@angular/common';

@Component({
  selector: 'app-film-search',
  standalone: true,
  imports: [
    FormsModule,
    ButtonModule,
    NgFor,
    NgIf
  ],
  templateUrl: 'film-search.html',
  styleUrls: ['film-search.css']
})
export class FilmSearch implements OnInit {

  films: any[] = [];
  searchQuery: string = '';
  filterMenuOpen = false;

  // Users will see these English labels in the UI
  genres: string[] = [
    'Action', 'Adventure', 'Animation', 'Comedy',
    'Crime', 'Drama', 'Fantasy', 'Horror',
    'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'Family'
  ];

  // Map English UI labels to the specific strings expected by KinoCheck API (observed in terminal)
  private genreMapping: { [key: string]: string } = {
    'Action': 'Action',
    'Adventure': 'Abenteuer',
    'Animation': 'Animation',
    'Comedy': 'Komödie',
    'Crime': 'Krimi',
    'Drama': 'Drama',
    'Fantasy': 'Fantasy',
    'Horror': 'Horror',
    'Mystery': 'Mystery',
    'Romance': 'Lovestory',
    'Sci-Fi': 'Science Fiction',
    'Thriller': 'Thriller',
    'Family': 'Familie'
  };

  constructor(private api: SearchService) { }

  ngOnInit() {
    this.loadAllFilms();
  }

  loadAllFilms() {
    this.api.getAllFilms().subscribe((data: any) => {
      this.films = data || [];
    });
  }

  onSearch() {
  const query = this.searchQuery.trim();
  if (!query) {
    this.loadAllFilms();
    return;
  }

  this.api.searchIMDB(query).subscribe((results: any[]) => {
    this.films = results.map(item => ({
      title: item.title,
      // API'den gelen görseli güvenli bir şekilde alalım
      poster: item.image?.url || item.image || item.poster || 'assets/no-image.png',
      genres: [],
      imdb_id: item.imdb_id
    }));
  });
}

  onSearchChange() {
    if (!this.searchQuery.trim()) {
      this.loadAllFilms();
    }
  }

  clearSearch() {
    this.searchQuery = '';
    this.loadAllFilms();
  }

  toggleFilterMenu() {
    this.filterMenuOpen = !this.filterMenuOpen;
  }

  filterByGenre(genre: string) {
    // Convert the English UI label to the API-compatible genre string
    const apiGenre = this.genreMapping[genre] || genre;

    this.api.filterByGenre(apiGenre).subscribe((data: any[]) => {
      // Create a new reference to ensure Angular change detection triggers UI update
      this.films = [...data];
      this.filterMenuOpen = false;
    });
  }
}