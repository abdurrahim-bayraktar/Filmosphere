import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MovieModal } from './movie-modal';

describe('MovieModal', () => {
  let component: MovieModal;
  let fixture: ComponentFixture<MovieModal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MovieModal]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MovieModal);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
