# NHL Data Projects

A full-stack application that fetches NHL game data from an external API, stores it in a PostgreSQL database, and displays team statistics through an Angular frontend.

## 🚀 Live Application

- **Frontend**: [Netlify Deployment URL]
- **Backend API**: `https://nhl-data-projects-production.up.railway.app`
- **API Test**: `https://nhl-data-projects-production.up.railway.app/api/test`

## Architecture

- **Frontend**: Angular 19 application displaying NHL team statistics
- **Backend**: Flask API serving aggregated team data
- **Database**: PostgreSQL (Neon Database) storing NHL game data
- **Data Source**: NHL API via RapidAPI
- **Deployment**: Railway (backend) + Netlify (frontend)

## Project Structure & Branch Strategy

```
nhl-data-projects/
├── main branch (Railway deployment)
│   ├── src/
│   │   ├── app/           # Angular frontend
│   │   ├── app.py         # Flask API
│   │   ├── nhl_data.py    # Data fetching script
│   │   └── .env           # Environment variables
│   ├── requirements.txt   # Python dependencies
│   ├── Procfile          # Railway deployment config
│   └── railway.json      # Railway settings
│
└── netlify-deploy branch (Netlify deployment)
    ├── src/app/           # Angular frontend only
    ├── package.json       # Node.js dependencies
    ├── angular.json       # Angular configuration
    └── netlify.toml       # Netlify build settings
```

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 20.19+ / 22.12+
- PostgreSQL

### Backend Setup

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables in `src/.env`:**
```bash
# Development Database
export DB_HOST=localhost
export DB_NAME=devdb
export DB_USER=devuser
export DB_PASSWORD=devpass
export DB_PORT=5432

# Production Database (Neon)
export DB_HOST_PROD=your-neon-host
export DB_NAME_PROD=neondb
export DB_USER_PROD=neondb_owner
export DB_PASSWORD_PROD=your-password
export DB_PORT_PROD=5432
```

4. **Create database table:**
```sql
CREATE TABLE "nhl_games" (
    id VARCHAR(20) PRIMARY KEY,
    date DATE,
    time DATE,
    timestamp DATE,
    timezone VARCHAR(50),
    status_long VARCHAR(50),
    status_short VARCHAR(10),
    country_name VARCHAR(50),
    country_code VARCHAR(10),
    league_name VARCHAR(50),
    league_season INT4,
    home_team_name VARCHAR(100),
    away_team_name VARCHAR(100),
    home_team_score INT4,
    away_team_score INT4,
    periods_first VARCHAR(10),
    periods_second VARCHAR(10),
    periods_third VARCHAR(10),
    periods_overtime VARCHAR(10),
    periods_penalties VARCHAR(10),
    events INT2,
    season_type VARCHAR(20) DEFAULT 'regular'
);
```

5. **Populate database with NHL data:**
```bash
cd src
source .env
python nhl_data.py
```

6. **Run Flask API:**
```bash
cd src
python app/app.py
```

### Frontend Setup

1. **Install Node.js dependencies:**
```bash
npm install
```

2. **Run Angular development server:**
```bash
ng serve
```

Navigate to `http://localhost:4200/`

## Production Deployment

This project uses a **dual-branch deployment strategy** to handle the monorepo structure:

### Backend Deployment (Railway)
**Branch**: `main`
1. **Connect Railway** to the `main` branch
2. **Environment Variables** (set in Railway dashboard):
   ```
   DB_HOST_PROD=your-neon-host
   DB_NAME_PROD=neondb
   DB_USER_PROD=neondb_owner
   DB_PASSWORD_PROD=your-password
   DB_PORT_PROD=5432
   FLASK_ENV=production
   ```
3. **Automatic deployment** via `Procfile`: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
4. **Database**: Automatically connects to Neon Database

### Frontend Deployment (Netlify)
**Branch**: `netlify-deploy` (Python-free branch)
1. **Connect Netlify** to the `netlify-deploy` branch
2. **Build Settings**:
   - Build command: `npm install && ng build`
   - Publish directory: `dist/nhl-data/browser`
   - Node.js version: 20
3. **Auto-deployment** from clean Angular-only branch

### Branch Management
- **`main`**: Full-stack development, Railway deployment
- **`netlify-deploy`**: Frontend-only, Netlify deployment
- **Sync changes**: Merge main → netlify-deploy when updating frontend

## API Endpoints

- `GET /api/nhldata` - Returns aggregated team statistics
- `GET /api/nhldata?season_type=playoffs` - Returns playoff statistics
- `GET /api/test` - Health check endpoint

## Features

- **Real-time NHL data**: Fetches live game data from NHL API via RapidAPI
- **Team statistics**: Aggregated wins, losses, goals, and games played
- **Responsive frontend**: Angular 19 with modern UI components
- **PostgreSQL persistence**: Reliable data storage with Neon Database
- **Production deployment**: Dual-platform deployment (Railway + Netlify)
- **Monorepo architecture**: Single repository with branch-based deployments

## Technology Stack

- **Frontend**: Angular 19, TypeScript, CSS
- **Backend**: Python Flask, psycopg2, gunicorn
- **Database**: PostgreSQL (Neon Database)
- **Deployment**: Railway (backend), Netlify (frontend)
- **External API**: NHL API via RapidAPI
- **Environment**: Node.js 20+, Python 3.11+

## Deployment URLs

- **Backend API**: `https://nhl-data-projects-production.up.railway.app`
- **Frontend**: [Update with Netlify URL after successful deployment]
- **Repository**: `https://github.com/Grudged/nhl-data-projects`