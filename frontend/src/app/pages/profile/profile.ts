import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';

import { AvatarModule } from 'primeng/avatar';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { TextareaModule } from 'primeng/textarea';
import { FormsModule } from '@angular/forms';
import { Select } from 'primeng/select';

import { Router } from '@angular/router';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [
    CommonModule,
    HttpClientModule,
    AvatarModule,
    ButtonModule,
    DialogModule,
    TextareaModule,
    FormsModule,
    Select
  ],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class ProfileComponent implements OnInit {

  user: any = { profile: {} };
  avatarLabel = "";
  avatarImage: string | null = null;

  editMode = false;
  bioToEdit = "";

  avatarModalVisible = false;
  selectedAvatar: any = null;

  availableAvatars = [
    { name: 'Avatar 1', url: 'https://primefaces.org/cdn/primeng/images/demo/avatar/amyelsner.png' },
    { name: 'Avatar 2', url: 'https://primefaces.org/cdn/primeng/images/demo/avatar/onyamalimba.png' },
    { name: 'Avatar 3', url: 'https://primefaces.org/cdn/primeng/images/demo/avatar/walter.jpg' }
  ];

  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit() {
    this.loadUser();
  }

  // === USER LOAD ========================================================
  loadUser() {
    const token = localStorage.getItem("access");
    const cachedUser = localStorage.getItem("user_profile");

    if (cachedUser) {
      try {
        this.user = JSON.parse(cachedUser);
        this.avatarImage = this.user.profile?.avatar || null;
        this.avatarLabel = this.user.username[0].toUpperCase();
        this.bioToEdit = this.user.profile?.bio || "";
      } catch {}
    }

    if (!token) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    this.http.get("http://127.0.0.1:8000/api/auth/me/", { headers })
      .subscribe({
        next: (res: any) => {
          this.user = res;

          this.avatarImage = res.profile?.avatar || null;
          this.avatarLabel = res.username[0]?.toUpperCase() || "U";
          this.bioToEdit = res.profile?.bio || "";

          this.selectedAvatar =
            this.availableAvatars.find(av => av.url === this.avatarImage) ||
            this.availableAvatars[0];

          localStorage.setItem("user_profile", JSON.stringify(res));
        }
      });
  }

  // === EDIT MODE ========================================================
  enableEditMode() {
    this.editMode = true;
    this.bioToEdit = this.user.profile?.bio || "";
  }

  cancelEdit() {
    this.editMode = false;
    this.bioToEdit = this.user.profile?.bio || "";
  }

  // === SAVE PROFILE (BIO) ================================================
  saveProfile() {
    const token = localStorage.getItem("access");
    if (!token) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json"
    });

    const payload = {
      avatar: this.user.profile.avatar || "",
      bio: this.bioToEdit,
      favorite_movie_1: this.user.profile.favorite_movie_1,
      favorite_movie_2: this.user.profile.favorite_movie_2,
      favorite_movie_3: this.user.profile.favorite_movie_3
    };

    this.http.patch(
      "http://127.0.0.1:8000/api/auth/profile/update/",
      payload,
      { headers }
    )
    .subscribe({
      next: () => {
        this.user.profile.bio = this.bioToEdit;
        this.editMode = false;

        localStorage.setItem("user_profile", JSON.stringify(this.user));
      }
    });
  }

  // === AVATAR SELECT ======================================================
  openAvatarSelection() {
    this.avatarModalVisible = true;
  }

  // === SAVE AVATAR ========================================================
  saveAvatar() {
    const token = localStorage.getItem("access");
    if (!token || !this.selectedAvatar) return;

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json"
    });

    const newAvatar = this.selectedAvatar.url;

    const payload = {
      avatar: newAvatar,
      bio: this.user.profile.bio,
      favorite_movie_1: this.user.profile.favorite_movie_1,
      favorite_movie_2: this.user.profile.favorite_movie_2,
      favorite_movie_3: this.user.profile.favorite_movie_3
    };

    this.http.patch(
      "http://127.0.0.1:8000/api/auth/profile/update/",
      payload,
      { headers }
    )
    .subscribe({
      next: () => {
        this.user.profile.avatar = newAvatar;
        this.avatarImage = newAvatar;

        localStorage.setItem("user_profile", JSON.stringify(this.user));

        this.avatarModalVisible = false;
      }
    });
  }

  // === NAVIGATION ==========================================================
  goHome() {
    this.router.navigate(['/home']);
  }
}
