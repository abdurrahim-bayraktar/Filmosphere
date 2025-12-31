import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { TextareaModule } from 'primeng/textarea';
import { AvatarModule } from 'primeng/avatar';
import { PopoverModule } from 'primeng/popover';
import { MenuModule } from 'primeng/menu';
import { Popover } from 'primeng/popover';
import { MenuItem } from 'primeng/api';

import { FilmService } from '../../services/film.service';
import { API_URL } from '../../config/api.config';

@Component({
  selector: 'app-list-management',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    ButtonModule,
    DialogModule,
    InputTextModule,
    TextareaModule,
    AvatarModule,
    PopoverModule,
    MenuModule
  ],
  templateUrl: './list-management.html',
  styleUrl: './list-management.css'
})
export class ListManagementComponent implements OnInit {
  @ViewChild('profileMenu') profileMenu!: Popover;

  lists: any[] = [];
  loading = true;

  // Create/Edit Dialog
  showListDialog = false;
  editingList: any = null;
  listTitle = '';
  listDescription = '';
  listIsPublic = false;

  // Navbar state
  navbarAvatarLabel = '';
  navbarAvatarImage: string | null = null;
  navbarUsername: string = '';
  isAdmin = false;
  menuItems: MenuItem[] = [];

  constructor(
    private filmService: FilmService,
    private http: HttpClient,
    private router: Router
  ) { }

  ngOnInit() {
    this.loadNavbarUser();
    this.loadLists();
  }

  setupMenuItems() {
    const items: MenuItem[] = [
      { label: 'Home', icon: 'pi pi-home', routerLink: ['/home'] } as MenuItem,
      { label: 'My Profile', icon: 'pi pi-user', routerLink: ['/profile'] } as MenuItem,
    ];

    if (this.isAdmin) {
      items.push({ label: 'Admin', icon: 'pi pi-cog', routerLink: ['/admin'] } as MenuItem);
    }

    items.push({ separator: true } as MenuItem);
    items.push({ label: 'Logout', icon: 'pi pi-sign-out', command: () => this.logout() } as MenuItem);

    this.menuItems = items;
  }

  loadNavbarUser() {
    const cached = localStorage.getItem("user_profile");
    if (cached) {
      try {
        const usr = JSON.parse(cached);
        this.navbarAvatarImage = usr.profile_picture_url || usr.profile?.profile_picture_url || null;
        this.navbarAvatarLabel = (usr.username || usr.user?.username || "U")[0]?.toUpperCase() || "U";
        this.navbarUsername = usr.username || usr.user?.username || "Guest";
        this.isAdmin = !!(usr.is_staff || usr.is_superuser);
        this.setupMenuItems();
      } catch { }
    }

    const token = localStorage.getItem("access");
    if (!token) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    this.http.get(`${API_URL}/auth/me/`, { headers })
      .subscribe({
        next: (res: any) => {
          this.navbarAvatarImage = res.profile_picture_url || res.profile?.profile_picture_url || null;
          this.navbarAvatarLabel = (res.username || res.user?.username || "U")[0]?.toUpperCase() || "U";
          this.navbarUsername = res.username || res.user?.username || "Guest";
          this.isAdmin = !!(res.is_staff || res.is_superuser);
          this.setupMenuItems();
        },
        error: (err) => {
          console.error('Error loading navbar user:', err);
        }
      });
  }

  logout() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user_profile');
    this.router.navigate(['/']);
  }

  loadLists() {
    this.loading = true;
    this.filmService.getLists().subscribe({
      next: (res: any) => {
        this.lists = res.results || res || [];
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading lists:', err);
        this.loading = false;
      }
    });
  }

  openCreateListDialog() {
    this.editingList = null;
    this.listTitle = '';
    this.listDescription = '';
    this.showListDialog = true;
  }

  openEditListDialog(list: any) {
    this.editingList = list;
    this.listTitle = list.title || '';
    this.listDescription = list.description || '';
    this.showListDialog = true;
  }

  closeListDialog() {
    this.showListDialog = false;
    this.editingList = null;
    this.listTitle = '';
    this.listDescription = '';
  }

  saveList() {
    if (!this.listTitle.trim()) {
      alert('Please enter a list title');
      return;
    }

    const payload = {
      title: this.listTitle.trim(),
      description: this.listDescription.trim()
    };

    if (this.editingList) {
      // Update existing list
      this.filmService.updateList(this.editingList.id, payload).subscribe({
        next: () => {
          this.loadLists();
          this.closeListDialog();
        },
        error: (err) => {
          console.error('Error updating list:', err);
          const errorMsg = err.error?.detail || err.error?.message || err.message || 'Failed to update list';
          alert(`Error: ${errorMsg}`);
        }
      });
    } else {
      // Create new list
      this.filmService.createList(payload).subscribe({
        next: () => {
          this.loadLists();
          this.closeListDialog();
          // Navigate to profile to see the new list immediately
          this.router.navigate(['/profile']);
        },
        error: (err) => {
          console.error('Error creating list:', err);
          const errorMsg = err.error?.detail || err.error?.message || err.message || 'Failed to create list';
          alert(`Error: ${errorMsg}`);
        }
      });
    }
  }

  deleteList(list: any) {
    if (!confirm(`Are you sure you want to delete "${list.title}"?`)) {
      return;
    }

    this.filmService.deleteList(list.id).subscribe({
      next: () => {
        this.loadLists();
      },
      error: (err) => {
        console.error('Error deleting list:', err);
        const errorMsg = err.error?.detail || err.error?.message || err.message || 'Failed to delete list';
        alert(`Error: ${errorMsg}`);
      }
    });
  }

  goToFilm(imdbId: string) {
    this.router.navigate(['/film-details', imdbId]);
  }

  goToListDetail(listId: number) {
    this.router.navigate(['/lists', listId]);
  }

  goHome() {
    this.router.navigate(['/home']);
  }
}


