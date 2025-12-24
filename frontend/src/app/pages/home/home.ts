import { Component, OnInit,OnDestroy, ViewChild, inject} from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { CarouselModule } from 'primeng/carousel';
import { ButtonModule } from 'primeng/button';
import { CommonModule } from '@angular/common';
import { HeroComponent } from "../../components/hero/hero";
import { MovieModalComponent } from "../../components/movie-modal/movie-modal";
import { HttpClient, HttpClientModule,HttpHeaders } from '@angular/common/http';
import { AvatarModule } from 'primeng/avatar';
import { MenuItem } from 'primeng/api';
import { MenuModule } from 'primeng/menu';
import { PopoverModule } from 'primeng/popover';
import { Popover } from 'primeng/popover';
import { forkJoin } from 'rxjs';
import { SearchService } from '../../services/search.service';


interface FilmSearchResult {
  title?: string;
  primaryTitle?: string;
  image?: string;
  primaryImage?: { url?: string };
  imdb_id?: string;
  id?: string;
  year?: number;
  startYear?: number;
}

interface Film {
  title: string;
  poster: string | null;
  id: string;
  year?: number;
  imdb_id: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    RouterModule,
    CarouselModule,
    ButtonModule,
    CommonModule,
    MovieModalComponent,
    HttpClientModule,
    AvatarModule,
    PopoverModule,
    MenuModule
  ],
  templateUrl: './home.html',
  styleUrl: './home.css'
})

export class HomeComponent implements OnInit, OnDestroy {
  private http: HttpClient;
  private router: Router;
  private searchService: SearchService;

  @ViewChild('profileMenu') profileMenu!: Popover;
  

  user: any = null;
  avatarLabel: string = "";
  avatarImage: string | null = null;

  menuItems: MenuItem[] = [];

  modalVisible = false;
  selectedMovie: any = null;

  films: Film[] = [];
  topComments: any[] = [];

  heroBackgrounds: string[] = ['assets/img/hero/WelcomePhoto2.jpg',
    'assets/img/hero/WelcomePhoto20.jpg',
    'assets/img/hero/WelcomePhoto10.jpg',
    'assets/img/hero/WelcomePhoto8.jpg',
    'assets/img/hero/WelcomePhoto6.jpg',
   ];

   currentHeroIndex = 0;
   heroInterval: any;


  constructor(){
     this.http = inject(HttpClient);
    this.router = inject(Router);
    this.searchService = inject(SearchService);
  }

  ngOnInit() {
    this.loadUser();
    this.startHeroRotation();
    // Clear films array first to show loading state
    //this.films = [];
    this.loadFilms();
    this.loadTopComments();
    this.setupMenuItems();
  }
     startHeroRotation() {
  this.heroInterval = setInterval(() => {
    this.currentHeroIndex =
      (this.currentHeroIndex + 1) % this.heroBackgrounds.length;
  },5000);
}
  ngOnDestroy() {
  if (this.heroInterval) {
    clearInterval(this.heroInterval);
  };
}
  

  setupMenuItems() {
    this.menuItems = [
      { label: 'My Profile', icon: 'pi pi-user', routerLink: ['/profile'] },
      { separator: true },
      { label: 'Logout', icon: 'pi pi-sign-out', command: () => this.logout() }
    ];
  }

 loadUser() {
    const cached = localStorage.getItem("user_profile");

    if (cached) {
      try {
        const usr = JSON.parse(cached);
        this.user = usr;
        // Backend returns profile_picture_url directly, not in profile.avatar
        this.avatarImage = usr.profile_picture_url || usr.profile?.profile_picture_url || usr.profile?.avatar || null;
        this.avatarLabel = (usr.username || usr.user?.username || "U")[0]?.toUpperCase() || "U";
      } catch (e) {
        console.error('Error parsing cached user:', e);
      }
    }

    const token = localStorage.getItem("access");
    if (!token) return;

    this.http.get("http://127.0.0.1:8000/api/auth/me/", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .subscribe({
        next: (res: any) => {
          this.user = res;
          // Backend returns profile_picture_url directly in serializer.data
          this.avatarImage = res.profile_picture_url || res.profile?.profile_picture_url || res.profile?.avatar || null;
          this.avatarLabel = (res.username || res.user?.username || "U")[0]?.toUpperCase() || "U";
          localStorage.setItem("user_profile", JSON.stringify(res));
        }
      });
  }

  logout() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user_profile');
    this.user = { username: "Guest" };
    this.avatarLabel = "G";
    this.router.navigate(['/']);
  }
   navigateToProfile() {
    this.router.navigate(['/profile']);
  }
  reloadFilms() {
    // Reload films with new random selection when logo is clicked
    this.films = []; // Clear current films to show loading state
    // Small delay to ensure fresh randomization seed
    setTimeout(() => {
      this.loadFilms();
    }, 50);
  }

  
  navigateToChatbot() {
    // Navigate to recommendations page or chatbot page
    // For now, we'll use the recommendations endpoint
    this.router.navigate(['/recommendation-chat']);
  }

  navigateToSearch() {
    // Navigate to search page - we can create a dedicated search page or use current search
    // For now, we'll navigate to a search route or show search modal
    this.router.navigate(['/film-search']);
  }
  private shuffleArray<T>(array: T[]): T[] {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  loadFilms() {
  const popularQueries = [
    'inception', 'the dark knight', 'pulp fiction', 'fight club', 'matrix', 'interstellar',
    'the godfather', 'shawshank redemption', 'forrest gump', 'titanic', 'avatar', 'avengers',
    'the godfather part ii', 'the dark knight rises', '12 angry men',
    'schindler list', 'the lord of the rings', 'the good the bad and the ugly',
    'the lord of the rings the return of the king', 'star wars', 'goodfellas',
    'one flew over the cuckoo nest', 'se7en', 'the silence of the lambs', 'city of god',
    'saving private ryan', 'the green mile', 'life is beautiful', 'leon the professional',
    'the departed', 'the prestige', 'gladiator', 'american history x', 'the pianist',
    'casablanca', 'raiders of the lost ark', 'rear window', 'whiplash', 'memento',
    'the usual suspects', 'psycho', 'sunset boulevard', 'apocalypse now', 'alien',
    'terminator', 'blade runner', 'the thing', 'back to the future', 'et',
    'jurassic park', 'jaws', 'the exorcist', 'parasite',
    'spirited away', 'the lion king', 'toy story', 'finding nemo', 'wall-e',
    'up', 'ratatouille', 'monsters inc', 'coco', 'inside out'
  ];

  const shuffled = this.shuffleArray(popularQueries);
  const selectedQueries = shuffled.slice(0, 15);

  const searchObservables = selectedQueries.map(query =>
    this.searchService.searchIMDB(query)
  );

  forkJoin(searchObservables).subscribe({
    next: (results: FilmSearchResult[][]) => {
      const allFilms: Film[] = [];

      results.forEach((result) => {
        if (result && result.length > 0) {
          const film = this.shuffleArray(result)[0];

          const exists = allFilms.some(f =>
            f.imdb_id === film.imdb_id ||
            f.title.toLowerCase() === (film.title || film.primaryTitle || '').toLowerCase()
          );

          if (!exists && (film.imdb_id || film.id)) {
            allFilms.push({
              title: film.title || film.primaryTitle || 'Unknown',
              poster: film.image || film.primaryImage?.url || null,
              id: film.imdb_id || film.id || '',
              year: film.year || film.startYear,
              imdb_id: film.imdb_id || film.id || ''
            });
          }
        }
      });

      this.films = this.shuffleArray(allFilms).slice(0, 12);
    },
    error: (err) => {
      console.error('Error loading films:', err);
      this.fetchFilmsFallback();
    }
  });
}


  fetchFilmsFallback() {
    // Fallback method to fetch films
    const token = localStorage.getItem("access");
    let headers: HttpHeaders | { [key: string]: string } = {};
    if (token) {
      headers = new HttpHeaders({
        'Authorization': `Bearer ${token}`
      });
    }

    // Try to fetch from a popular films endpoint or use search
    this.http.get<{ results?: FilmSearchResult[] }>("http://127.0.0.1:8000/api/search/?q=popular", { headers })
      .subscribe({
        next: (res) => {
          if (res.results && res.results.length > 0) {
            this.films = res.results.slice(0, 12).map((film: FilmSearchResult): Film => ({
              title: film.title || film.primaryTitle || 'Unknown',
              poster: film.image || film.primaryImage?.url || null,
              id: film.imdb_id || film.id || '',
              year: film.year || film.startYear,
              imdb_id: film.imdb_id || film.id || ''
            })).filter((film: Film) => film.id !== ''); // Filter out invalid films
          }
        },
        error: (err) => {
          console.error('Error fetching films:', err);
        }
      });
  }

  loadTopComments() {
    // Fetch reviews from multiple popular films and get most liked ones
    // We'll fetch reviews from a few popular films and sort by likes
    const popularFilmIds = ['tt1375666', 'tt0468569', 'tt0111161', 'tt0137523', 'tt0816692']; // Inception, Dark Knight, Shawshank, Fight Club, Interstellar
    
    const token = localStorage.getItem("access");
    let headers: HttpHeaders | { [key: string]: string } = {};
    if (token) {
      headers = new HttpHeaders({
        'Authorization': `Bearer ${token}`
      });
    }

    const reviewObservables = popularFilmIds.map(imdbId =>
      this.http.get(`http://127.0.0.1:8000/api/films/${imdbId}/reviews`, { headers })
    );

    forkJoin(reviewObservables).subscribe({
      next: (results: any[]) => {
        const allComments: any[] = [];
        results.forEach((reviews: any) => {
          if (reviews && Array.isArray(reviews)) {
            allComments.push(...reviews);
          } else if (reviews && reviews.results && Array.isArray(reviews.results)) {
            allComments.push(...reviews.results);
          }
        });

        // Sort by likes_count descending and take top 10
        this.topComments = allComments
          .filter(comment => comment.moderation_status !== 'rejected')
          .sort((a, b) => (b.likes_count || 0) - (a.likes_count || 0))
          .slice(0, 10);
      },
      error: (err) => {
        console.error('Error loading comments:', err);
      }
    });
  }
  scrollToFilms() {
  const element = document.querySelector('.films-section');
  element?.scrollIntoView({ behavior: 'smooth' });
}


  openMovieDetail(movie: any) {
    if (movie.imdb_id || movie.id) {
      this.selectedMovie = movie;
      this.modalVisible = true;
    } else {
      // Navigate to film detail page
      this.router.navigate(['/film-details', movie.id || movie.imdb_id]);
    }
  }

  closeMovieDetail() {
    this.modalVisible = false;
  }

  formatDate(dateString: string): string {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  }
}
