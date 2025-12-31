import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import { Router, RouterModule } from '@angular/router';
import { AvatarModule } from 'primeng/avatar';
import { MenuItem } from 'primeng/api';
import { MenuModule } from 'primeng/menu';
import { PopoverModule } from 'primeng/popover';
import { Popover } from 'primeng/popover';
import { API_URL } from '../../config/api.config';

type ChatMessage = {
  role: 'user' | 'assistant';
  text: string;
  blocked?: boolean;
  flags?: string[];
};

type RecommendationItem = {
  title: string;
  year?: number;
  imdb_id?: string;
  reason?: string;
};

type ChatApiResponse = {
  blocked: boolean;
  message?: string;       // blocked ise backend bunu döndürüyor
  flags?: string[];
  reason?: string;
  items?: RecommendationItem[]; // blocked değilse öneriler
  // demo mod vs. için bazen debug alanları gelebilir, sorun değil
};

@Component({
  selector: 'app-recommendation-chat',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    HttpClientModule,
    RouterModule,
    AvatarModule,
    PopoverModule,
    MenuModule
  ],
  templateUrl: './recommendation-chat.html',
  styleUrls: ['./recommendation-chat.css']
})
export class RecommendationChatComponent implements OnInit {
  @ViewChild('profileMenu') profileMenu!: Popover;

  messages: ChatMessage[] = [];
  input = '';
  loading = false;

  user: any = null;
  avatarLabel: string = "";
  avatarImage: string | null = null;
  isAdmin = false;
  menuItems: MenuItem[] = [];

  private API_URL = `${API_URL}/recommendations/chat/`;

  constructor(
    private http: HttpClient,
    private router: Router
  ) { }

  ngOnInit() {
    this.loadUser();
  }

  setupMenuItems() {
    const items: MenuItem[] = [
      { label: 'My Profile', icon: 'pi pi-user', routerLink: ['/profile'] } as MenuItem,
    ];

    if (this.isAdmin) {
      items.push({ label: 'Admin', icon: 'pi pi-cog', routerLink: ['/admin'] } as MenuItem);
    }

    items.push({ separator: true } as MenuItem);
    items.push({ label: 'Logout', icon: 'pi pi-sign-out', command: () => this.logout() } as MenuItem);

    this.menuItems = items;
  }

  loadUser() {
    const cached = localStorage.getItem("user_profile");

    if (cached) {
      try {
        const usr = JSON.parse(cached);
        this.user = usr;
        this.isAdmin = !!(usr.is_staff || usr.is_superuser);
        // Backend returns profile_picture_url directly, not in profile.avatar
        this.avatarImage = usr.profile_picture_url || usr.profile?.profile_picture_url || usr.profile?.avatar || null;
        this.avatarLabel = (usr.username || usr.user?.username || "U")[0]?.toUpperCase() || "U";
        this.setupMenuItems();
      } catch (e) {
        console.error('Error parsing cached user:', e);
      }
    }

    const token = localStorage.getItem("access");
    if (!token) return;

    this.http.get(`${API_URL}/auth/me/`, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (res: any) => {
        this.user = res;
        this.isAdmin = !!(res.is_staff || res.is_superuser);
        // Backend returns profile_picture_url directly in serializer.data
        this.avatarImage = res.profile_picture_url || res.profile?.profile_picture_url || null;
        this.avatarLabel = (res.username || res.user?.username || "U")[0]?.toUpperCase() || "U";
        localStorage.setItem("user_profile", JSON.stringify(res));
        this.setupMenuItems();
      },
      error: (err) => {
        console.error('Error loading user:', err);
      }
    });
  }

  logout() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    this.user = { username: "Guest" };
    this.avatarLabel = "G";
    this.router.navigate(['/']);
  }

  goToFilmSearch() {
    this.router.navigate(['/film-search']);
  }

  // 🔑 Login sonrası token
  private getToken(): string | null {
    return localStorage.getItem('access') || localStorage.getItem('access_token');
  }

  // 🧪 Örnek mesaj bas
  useExample(text: string) {
    this.input = text;
  }

  // 🧹 Sohbeti temizle
  clearChat() {
    this.messages = [];
    this.input = '';
  }

  private formatItems(items: RecommendationItem[]): string {
    if (!items || items.length === 0) return '(No recommendations)';

    return items
      .map((x) => {
        const year = x.year ? ` (${x.year})` : '';
        const reason = x.reason ? ` — ${x.reason}` : '';
        return `• ${x.title}${year}${reason}`;
      })
      .join('\n');
  }

  send() {
    const text = this.input.trim();
    if (!text || this.loading) return;

    // Kullanıcı mesajı
    this.messages.push({ role: 'user', text });
    this.input = '';
    this.loading = true;

    const token = this.getToken();
    if (!token) {
      this.messages.push({
        role: 'assistant',
        text: '❌ You cannot get recommendations without logging in.'
      });
      this.loading = false;
      return;
    }

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    this.http
      .post<ChatApiResponse>(
        this.API_URL,
        { user_message: text },
        { headers }
      )
      .subscribe({
        next: (res) => {
          // 🚫 ENGELLENDİ
          if (res?.blocked) {
            this.messages.push({
              role: 'assistant',
              text:
                (res?.message ?? '🚫 This request/response cannot be displayed due to security policies.') +
                (res?.reason ? `\n\nReason: ${res.reason}` : '') +
                (res?.flags?.length ? `\nFlags: ${res.flags.join(', ')}` : ''),
              blocked: true,
              flags: res.flags || []
            });
            this.loading = false;
            return;
          }

          // ✅ NORMAL: message veya items döner
          const message = res?.message;
          const items = res?.items ?? [];

          let displayText: string;
          if (message) {
            displayText = message;
          } else if (items.length > 0) {
            displayText = this.formatItems(items);
          } else {
            displayText = 'No recommendations available.';
          }

          this.messages.push({
            role: 'assistant',
            text: displayText
          });

          this.loading = false;
        },
        error: (err) => {
          const msg =
            err?.error?.detail ||
            err?.error?.error ||
            err?.message ||
            JSON.stringify(err);

          this.messages.push({
            role: 'assistant',
            text: `❌ Error: ${err?.status ?? ''} ${msg}`
          });

          this.loading = false;
        }
      });
  }
}

