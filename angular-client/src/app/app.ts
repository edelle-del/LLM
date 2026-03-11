import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  imports: [FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  prompt = '';
  result = '';
  loading = false;
  error = '';
  apiUrl = 'http://localhost:8081/llm/generate';

  constructor(private readonly http: HttpClient) {}

  generate(): void {
    const prompt = this.prompt.trim();
    if (!prompt || this.loading) {
      return;
    }

    this.loading = true;
    this.error = '';

    this.http.post<{ result: string }>(this.apiUrl, { prompt }).subscribe({
      next: (res) => {
        this.result = res.result ?? '';
        this.loading = false;
      },
      error: (err) => {
        this.error = err?.error?.detail ?? 'Failed to call Spring Boot API.';
        this.loading = false;
      },
    });
  }
}
