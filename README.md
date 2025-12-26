# 🎬 Filmosphere

A modern full-stack movie discovery and tracking platform built with Django and Angular.

## ✨ Features

- 🔍 **Smart Search** - Find movies across multiple databases
- 🤖 **AI Recommendations** - Get personalized film suggestions
- 📝 **Reviews & Ratings** - Share your thoughts and rate films
- 📺 **Streaming Info** - See where to watch
- 👥 **Social Features** - Follow users, like reviews, create lists
- 🎭 **Mood-based Discovery** - Find films by mood
- ⭐ **Watchlist & History** - Track what you've seen and want to watch

## 🚀 Quick Deploy (10 Minutes)

**Want to deploy right now?** See [QUICK_START.md](./QUICK_START.md)

```bash
# 1. Push to GitHub
git push

# 2. Deploy on Render
# Go to render.com → New Blueprint → Select repo → Deploy

# 3. You're live! 🎉
```

## 📚 Documentation

- **[Quick Start Guide](./QUICK_START.md)** - Deploy in 10 minutes
- **[Full Deployment Guide](./DEPLOYMENT_GUIDE.md)** - Comprehensive deployment instructions
- **[Deployment Summary](./DEPLOYMENT_SUMMARY.md)** - Overview of changes and options

## 🛠️ Tech Stack

### Backend
- Django 5.1.3 + Django REST Framework
- JWT Authentication
- SQLite/PostgreSQL
- Integration with IMDb, Kinocheck, Watchmode APIs
- AI recommendations via DeepSeek

### Frontend
- Angular 20
- PrimeNG UI Components
- Responsive design
- Modern TypeScript

## 💻 Local Development

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend runs at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs at `http://localhost:4200`

### Create Admin User

```bash
cd backend
python manage.py createsuperuser
```

Access admin at `http://localhost:8000/admin`

## 🌐 Deployment Options

| Platform | Speed | Cost | Best For |
|----------|-------|------|----------|
| **Render** | Fast | Free tier | Recommended for beginners |
| **Railway** | Fastest | $5 credit | Simplest deployment |
| **Vercel + Render** | Fast | Free | Best performance |
| **Heroku** | Fast | ~$14/mo | Production apps |

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions.

## 📋 API Documentation

- **Interactive API Docs**: `/api/schema/swagger-ui/`
- **ReDoc**: `/api/schema/redoc/`
- **OpenAPI Schema**: `/api/schema/`

### Key Endpoints

```
POST   /api/users/register/          - User registration
POST   /api/users/login/             - User login
GET    /api/films/                   - List films
GET    /api/films/{id}/              - Film details
POST   /api/films/{id}/rate/         - Rate a film
GET    /api/search/films/            - Search films
POST   /api/recommendation/chat/     - AI recommendations
GET    /api/films/moods/             - Get mood-based films
```

## 🔑 Environment Variables

### Required for Full Features

```bash
# Backend (.env)
DEEPSEEK_API_KEY=your-key-here        # For AI recommendations
WATCHMODE_API_KEY=your-key-here       # For streaming info
SECRET_KEY=your-secret-key            # Django security
```

See `backend/.env.example` for full list.

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📁 Project Structure

```
Filmosphere/
├── backend/                 # Django REST API
│   ├── config/             # Django settings
│   ├── users/              # User management
│   ├── films/              # Film data & reviews
│   ├── core/               # External API services
│   └── requirements.txt
├── frontend/               # Angular app
│   ├── src/
│   │   ├── app/           # Components & services
│   │   └── environments/  # Environment configs
│   └── package.json
├── render.yaml            # Deployment config
└── DEPLOYMENT_GUIDE.md    # Deployment instructions
```

## 🚦 Getting Started

### For Users (Just want to deploy)
1. Read [QUICK_START.md](./QUICK_START.md)
2. Push to GitHub
3. Deploy to Render
4. Done!

### For Developers (Want to customize)
1. Clone the repository
2. Follow Local Development setup
3. Make your changes
4. Deploy using [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

## 🔒 Security Notes

- Current config uses `DEBUG = True` and `SECRET_KEY` is exposed
- **Before production**: Follow security checklist in [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)
- Run `python manage.py check --deploy` for security recommendations
- Update CORS settings to restrict to your frontend domain only

## 📈 Scaling

### Free Tier (Good for testing)
- Services spin down after 15 min inactivity
- 750 hours/month free
- SQLite database (resets on restart)

### Production Upgrade (~$14-21/month)
- Always-on services
- PostgreSQL database (persistent)
- Better performance
- Custom domains

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for upgrade instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is provided as-is for educational and commercial use.

## 🆘 Troubleshooting

### Common Issues

**Backend won't start**
- Check environment variables are set
- Review logs in deployment platform
- Ensure migrations completed

**Frontend can't connect to backend**
- Verify API URL in `frontend/src/environments/environment.prod.ts`
- Check CORS settings in Django

**Database issues**
- Free tier: Database resets on restart (expected)
- Upgrade to PostgreSQL for persistence

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for more troubleshooting.

## 📞 Support

- Check the [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for comprehensive documentation
- Review [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md) for quick reference
- Check logs in your deployment platform

---

## 🎯 Quick Links

- **Deploy Now**: [QUICK_START.md](./QUICK_START.md)
- **Full Guide**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Summary**: [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)
- **Backend Docs**: [backend/API_ENDPOINTS_REFERENCE.md](./backend/API_ENDPOINTS_REFERENCE.md)

---

**Ready to deploy?** Start with [QUICK_START.md](./QUICK_START.md) and you'll be live in 10 minutes! 🚀

Built with ❤️ using Django & Angular

