
# Filmosphere

## General Information

**Project Title**: Filmosphere  
**Team Name**: Mühendisler  
**Team Members**:  
- **Ahsen Beyza Özkul** | [ahsenozkul](https://github.com/ahsenbeyza) | API Integration, Documentation  
- **Abdurrahim Bayraktar** | [abdurrahim-bayraktar](https://github.com/abdurrahim-bayraktar) | Database Management, Backend Development  
- **Alp Emre Zaimoğlu** | [alpemrezaimoglu](https://github.com/alpemrezaimoglu) | Frontend Development, Testing, Performance Optimization  
- **Bartu Sadıkoğlu** |[itu-itis-sadikoglu22](https://github.com/itu-itis-sadikoglu22)| User Management, Authentication System  
- **Batuhan Berk Balcı** | [batuhanberkbalci](https://github.com/batuhanberkbalci) | Backend Support, Project Configuration  
- **Emir Köse** |[Em1rK0se](https://github.com/Em1rK0se)| Movie Metadata Integration, API Data Handling  
- **Yasin Günay** |[itu-itis22-gunayy21](https://github.com/itu-itis22-gunayy21)| Frontend Components, Security  

## Technology Stack

### Project/Configuration Management
- **Version Control**: Git & GitHub  
- **Task Management**: GitHub Projects / Issues  
- **Documentation**: Markdown pages  
- **Collaboration Tools**: WhatsApp for communication  

### Backend Stack
- **Framework**: Django  
- **Database**: PostgreSQL  
- **API Integrations**:  
  - KinoCheck API – Movie trailers and previews  
  - Watchmode API – Streaming availability data  
  - IMDB API – Detailed film metadata  
  - DeepSeek API – Content-based recommendation engine  
- **Authentication**: Django AllAuth (for user registration & login)  

### Frontend Stack
- **Technologies**: HTML5, CSS3, JavaScript  
- **Frameworks & Libraries**: HTMX, PrimeNG, Tailwind CSS  
- **Frontend-Backend Communication**: RESTful API endpoints  

## Project Scope

### Mandatory Features
- Film rating system (1–5 scale)  
- CRUD functionality for user comments/reviews  
- User profile page displaying watched films  
- Film information pages (cast, release date, description, etc.)  
- Movie list creation  
- Authentication (login, register, logout)  
- Recommendation system based on user profile and ratings (via DeepSeek API)  
- Display of film trailers (via KinoCheck API)  
- Streaming platform availability (via Watchmode API)  

### Optional Features
- Film tagging system  
- Users can mark 3 favorite movies on their profile  
- Friendship/following system between users  
- Personalized “Friend Activity” feed  

### Out-of-Scope Features
- In-app movie playback  
- Payment systems or subscriptions  
- AI-based sentiment analysis of reviews  


# FILMOSPHERE — Frontend (UI Upgrade + IMDB Search Integration)
_Last updated: 09 December 2025_  
_Branch: `feature/frontend-ui`_

Filmosphere is a modern movie discovery platform. This development sprint introduces a significant UI upgrade, profile management enhancements, and an IMDB-based search system.

---

## 🚀 Newly Implemented Features (09.12.2025)

### 🔎 1. **Search Bar + IMDB API Search System**
A new **autocomplete** search bar has been added to the project.

#### ✔ Features:
- Search queries are executed against the IMDB API as the user types  
- Poster + Movie Title + Year information is displayed in the dropdown  
- Includes poster scaling and a responsive layout  
- Theme colors are consistent with the Filmosphere design  
- Dropdown content is now wide, readable, and free of scrolling/trigger errors  
- API requests are now routed through the Django backend (CORS issue fully resolved)

#### 🔧 Technical Detail:
The architecture utilizes the Frontend → Django Proxy → IMDB API flow:
`GET /api/search/imdb/?q=`


This approach achieves:
- Complete elimination of browser CORS issues  
- Prevents API key leakage to the frontend  
- IMDB results are normalized before being returned to the frontend  

---

### 👤 2. **Profile Page Overhaul (Avatar + Bio)**

The profile screen has been completely modernized.

#### ✔ Added Features:
- Ability for the user to **update their avatar**
- Modal screen for avatar selection
- Avatar selections are shown with a preview
- User can edit their **bio (about) text** inline
- Save operations are handled by a Patch request to the backend
- Changes are instantly visible upon returning to the profile
- User information is synchronized via LocalStorage

#### ✔ UI Enhancements:
- "Save Changes" button restyled to fit the green theme  
- "Save Avatar" button uses a black & minimal theme  
- "Cancel" button is gray, simple, and professional  
- Focus, hover, and border animations are updated to match the theme  

---

## 🎨 Other UI Adjustments

### ✔ Navbar Updated:
- Profile dropdown menu added  
- Avatar + Username is now displayed in the navbar  
- Modern popover menu: My Profile / Settings / Logout  

### ✔ Movie Modal Improvements:
- Cleaner detail modal animations  
- Improved responsive viewing  

### ✔ General UI Refactoring:
- Home page carousel layout optimized  
- Components are updated to be compatible with modern PrimeNG 20  
- Typography and spacing adjustments  

---

## 🌐 Backend Proxy Integration (CORS Solution)

A new app was created on the Django side for the search functionality:  
`search/`


The added endpoint:
`GET /api/search/imdb/?q=`


This endpoint:
- Makes the request to the IMDB API  
- Normalizes the results  
- Securely passes the data to the frontend without CORS issues  

Files used on the Backend:
- `search/views.py`
- `search/urls.py`
- `config/urls.py` was updated  

---

## 📁 New Files and Structure

### Frontend:
`src/app/pages/profile/`
* `profile.ts`
* `profile.html`
* `profile.css`
`src/app/services/search.service.ts`


### Backend:
`/search`
* `views.py`
* `urls.py`

---

## 🧪 Scenarios Tested

| Feature | Status |
|--------|-------|
| IMDB Search | ✔ Working |
| Poster Display | ✔ Returns with every result |
| Profile Avatar Change | ✔ Backend + UI sync |
| Bio Editing | ✔ Saved permanently |
| Navbar Dropdown | ✔ Seamless |
| CORS Issues | ✔ Resolved |
| Mobile Responsive | ✔ Corrected |

---

## 📝 Notes

This README documents the major revision completed on December 09, 2025.  
Backend API integration, profile screen, and UI refinements are included in this commit.

---

## 📌 Next Steps (Roadmap)
- Dynamically fetch movie detail screen data from API  
- User watchlist system  
- Connect "Trending" + "Top Rated" sections to TMDB / IMDB API  
- Personal recommendation algorithm  
- Dark / light theme switching  

---

## 👨‍💻 Contributor
**Emir Köse**

---

