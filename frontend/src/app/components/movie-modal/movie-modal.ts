import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'app-movie-modal',
  standalone: true,
  templateUrl: './movie-modal.html',
  styleUrls: ['./movie-modal.css'],
  imports: [CommonModule, ButtonModule]
})
export class MovieModalComponent {

  @Input() visible: boolean = false;      // Input property: controls modal visibility
  @Input() movie: any = null;             // Input property: data object for the movie to display

  @Output() close = new EventEmitter<void>(); // Output event: emitted when modal close action is triggered

  onClose() {
    this.close.emit(); // Emits the close event to the parent component
  }
}