import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FilmSearch } from './film-search';

describe('FilmSearch', () => {
  let component: FilmSearch;
  let fixture: ComponentFixture<FilmSearch>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FilmSearch]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FilmSearch);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
