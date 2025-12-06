# Filmosphere – Movie Streaming Platform (Frontend)

This repository contains the frontend implementation of Filmosphere, a movie streaming platform developed using **Angular**. The project currently focuses on the user interface, component structure, and overall layout of the application. Backend services are still under development; therefore, the frontend uses mock data for demonstration purposes.

## Overview

Filmosphere aims to provide a modern streaming experience similar to leading platforms. The interface includes a landing page, authentication screens, a home dashboard, a hero section, carousel-based movie rows, and a modal structure for detailed movie information.

The project is designed to be **modular** and fully compatible with upcoming backend integration.

## Implemented Frontend Features

### Landing and Authentication Pages
* Sign In page with styled inputs and interactive elements
* Forgot Password workflow UI
* Sign Up page with validation-ready layout
* Dark theme and responsive layout consistent across pages

### Home Page
* Navigation bar with user section
* **Hero component** for featured film display
* Multiple movie carousel sections (Trending, Top Rated, Action)
* Hover animations and card scaling effects
* Fully reusable movie card component structure

### Movie Modal Component
* Opens when selecting a movie card
* Structured to display poster, title, summary and available actions
* Buttons prepared for trailer playback and full movie launch
* Designed to integrate with external APIs (IMDb, Kinocheck) once backend is ready

## Technology Stack

* **Angular 17** (standalone component structure)
* **PrimeNG** component library
* TypeScript
* CSS styling with custom theme adjustments
* npm package manager

## Project Structure
```text
frontend/
├── src/app/
│    ├── components/
│    │     ├── hero/
│    │     └── movie-modal/
│    ├── pages/
│    │     ├── landing/
│    │     ├── signup/
│    │     ├── forgot-password/
│    │     └── home/
│    ├── app.routes.ts
│    └── app.config.ts
├── assets/
└── README.md