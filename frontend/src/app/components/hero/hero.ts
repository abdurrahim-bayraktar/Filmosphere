import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';   // Required for directives like *ngIf

@Component({
  selector: 'app-hero',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './hero.html',
  styleUrls: ['./hero.css']
})
export class HeroComponent implements OnInit {

  heroMovie: any = null; // Object to store the featured movie data

  ngOnInit(): void {
    this.loadDummyHeroMovie();  // Initializes with dummy data
  }


  //  DUMMY HERO MOVIE - Method to load static data
  loadDummyHeroMovie() {
    this.heroMovie = {
      title: "Interstellar",
      overview: "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
      backdrop: "https://image.tmdb.org/t/p/original/rAiYTfKGqDCRIIqo664sY9XZIvQ.jpg"
    };
  }
}