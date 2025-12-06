import { Component } from '@angular/core';
import { CarouselModule } from 'primeng/carousel';
import { ButtonModule } from 'primeng/button';
import { CommonModule } from '@angular/common';
import { HeroComponent } from "../../components/hero/hero";
import { MovieModalComponent } from "../../components/movie-modal/movie-modal";

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CarouselModule,
    ButtonModule,
    CommonModule,
    HeroComponent,
    MovieModalComponent
  ],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class HomeComponent {

  modalVisible = false;
  selectedMovie: any = null;

  openMovieDetail(movie: any) {
    this.selectedMovie = movie;
    this.modalVisible = true;
  }

  closeMovieDetail() {
    this.modalVisible = false;
  }

  trendingMovies = [
    { title: "Inception", poster: "https://image.tmdb.org/t/p/w500/qmDpIHrmpJINaRKAfWQfftjCdyi.jpg", description: "A thief who steals corporate secrets..." },
    { title: "Interstellar", poster: "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", description: "A team travels through a wormhole..." },
    { title: "The Dark Knight", poster: "https://image.tmdb.org/t/p/w500/1hRoyzDtpgMU7Dz4JF22RANzQO7.jpg", description: "Batman faces the Joker..." }
  ];

  topRatedMovies = [
    { title: "Fight Club", poster: "https://image.tmdb.org/t/p/w500/bptfVGEQuv6vDTIMVCHjJ9Dz8PX.jpg", description: "An insomniac forms a fight club." },
    { title: "The Godfather", poster: "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg", description: "Mafia family epic." },
    { title: "Pulp Fiction", poster: "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg", description: "Nonlinear crime stories." }
  ];

  actionMovies = [
    { title: "John Wick", poster: "https://image.tmdb.org/t/p/w500/fZPSd91yGE9fCcCe6OoQr6E3Bev.jpg", description: "Legendary assassin returns." },
    { title: "Mad Max", poster: "https://image.tmdb.org/t/p/w500/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg", description: "Post-apocalyptic mayhem." },
    { title: "Gladiator", poster: "https://image.tmdb.org/t/p/w500/pRho4REuXkFzfrVN7Od8VY6F4gl.jpg", description: "Roman general becomes gladiator." }
  ];
}
