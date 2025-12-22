import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RecommendationChat } from './recommendation-chat';

describe('RecommendationChat', () => {
  let component: RecommendationChat;
  let fixture: ComponentFixture<RecommendationChat>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RecommendationChat]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RecommendationChat);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
