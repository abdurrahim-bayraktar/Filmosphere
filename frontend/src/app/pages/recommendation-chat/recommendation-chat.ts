import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';

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
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './recommendation-chat.html',
  styleUrls: ['./recommendation-chat.css']
})
export class RecommendationChatComponent {
  messages: ChatMessage[] = [];
  input = '';
  loading = false;

  private API_URL = 'http://127.0.0.1:8000/api/recommendations/chat/';

  constructor(private http: HttpClient) {}

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
    if (!items || items.length === 0) return '(Öneri gelmedi)';

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
        text: '❌ Giriş yapmadan öneri alamazsın.'
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
                (res?.message ?? '🚫 Bu istek/yanıt güvenlik politikaları nedeniyle gösterilemiyor.') +
                (res?.reason ? `\n\nSebep: ${res.reason}` : '') +
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
            text: `❌ Hata: ${err?.status ?? ''} ${msg}`
          });

          this.loading = false;
        }
      });
  }
}
