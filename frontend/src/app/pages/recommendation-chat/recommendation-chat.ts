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
  menuItems: MenuItem[] = [];

  private API_URL = 'http://127.0.0.1:8000/api/recommendations/chat/';

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadUser();
    this.setupMenuItems();
  }

  setupMenuItems() {
    this.menuItems = [
      { label: 'My Profile', icon: 'pi pi-user', routerLink: ['/profile'] },
      { label: 'Settings', icon: 'pi pi-cog', routerLink: ['/settings'] },
      { separator: true },
      { label: 'Logout', icon: 'pi pi-sign-out', command: () => this.logout() }
    ];
  }

  loadUser() {
    const cached = localStorage.getItem("user_profile");

    if (cached) {
      const usr = JSON.parse(cached);
      this.user = usr;
      this.avatarImage = usr.profile?.avatar || null;
      this.avatarLabel = usr.username?.[0]?.toUpperCase() || "U";
    }

    const token = localStorage.getItem("access");
    if (!token) return;

    this.http.get("http://127.0.0.1:8000/api/auth/me/", {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (res: any) => {
        this.user = res;
        this.avatarImage = res.profile?.avatar || null;
        this.avatarLabel = res.username?.[0]?.toUpperCase() || "U";
        localStorage.setItem("user_profile", JSON.stringify(res));
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

          // ✅ NORMAL: items döner
          const items = res?.items ?? [];
          const formatted = this.formatItems(items);

          this.messages.push({
            role: 'assistant',
            text: formatted
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
