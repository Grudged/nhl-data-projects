# NHL Data Projects

A comprehensive sports data visualization application featuring NHL game statistics with dual-sport capabilities (NHL + NFL). Built as a full-stack solution with Python Flask backend, PostgreSQL database, and Angular frontend using a smart dual-branch deployment strategy.

## 🚀 Live Application

- **Frontend**: `https://nhl-data-visualizer.netlify.app`
- **Backend API**: `https://nhl-data-projects-production.up.railway.app`
- **API Health Check**: `https://nhl-data-projects-production.up.railway.app/api/test`
- **Repository**: `https://github.com/Grudged/nhl-data-projects`

## 🏗 Architecture Overview

- **Frontend**: Angular 20 application with Material Design components
- **Backend**: Python Flask API with comprehensive endpoints
- **Database**: PostgreSQL (Neon Database) with optimized queries
- **Data Sources**: NHL API via RapidAPI + NFL player statistics
- **Deployment**: Dual-platform deployment (Railway + Netlify)
- **Monitoring**: Built-in health checks and debug endpoints

## 📂 Project Structure & Branch Strategy

This project uses a **dual-branch deployment strategy** to handle the monorepo structure efficiently:

```
nhl-data-projects/
├── 🌟 main branch (Backend Focus - Railway Deployment)
│   ├── src/
│   │   ├── app/                    # Complete Angular 20 frontend
│   │   │   ├── components/         # NHL/NFL table components
│   │   │   ├── shared/            # TypeScript interfaces
│   │   │   └── app.py             # Flask API server
│   │   ├── nhl_data.py            # Data fetching scripts
│   │   └── .env                   # Environment variables
│   ├── requirements.txt           # Python dependencies
│   ├── Procfile                   # Railway deployment config
│   ├── package.json              # Node.js dependencies
│   ├── angular.json              # Angular configuration
│   └── netlify.toml              # Netlify settings
│
└── 🚀 netlify-deploy branch (Frontend Focus - Netlify Deployment)
    ├── src/app/                   # Angular frontend ONLY
    │   ├── components/            # Clean frontend components
    │   ├── shared/               # TypeScript interfaces
    │   └── services/             # HTTP services
    ├── package.json              # Node.js dependencies only
    ├── angular.json              # Angular CLI configuration
    ├── netlify.toml              # Netlify build settings
    └── dist/                     # Built Angular application
```

### 🔄 Branch Strategy Explanation

**Main Branch (Backend + Scripts + Database)**
- Contains Python Flask API server and database scripts
- Includes complete Angular frontend for development
- Deployed to **Railway** for backend API services
- Houses data fetching scripts (`nhl_data.py`) and database management
- Environment variables for PostgreSQL connections

**Netlify-Deploy Branch (Frontend Only)**
- **Python-free** branch containing only Angular application
- Optimized for **Netlify** deployment with faster builds
- No Python dependencies or backend code
- Clean frontend-only structure for static site generation

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

### 🔀 Branch Management Workflow

**Main Branch (Backend Focus)**
- ✅ Complete development environment with both frontend and backend
- ✅ Python Flask API server and database management scripts  
- ✅ Environment variables for PostgreSQL connections
- ✅ Automatically deployed to **Railway** for backend services
- ✅ Contains `requirements.txt`, `Procfile`, and Python dependencies

**Netlify-Deploy Branch (Frontend Only)**  
- ✅ **Python-free** environment optimized for static site generation
- ✅ Only Angular application with Node.js dependencies
- ✅ Faster builds without Python dependencies
- ✅ Automatically deployed to **Netlify** for frontend hosting
- ✅ Contains clean `package.json`, `angular.json`, and `netlify.toml`

**Sync Strategy:**
```bash
# When updating frontend code on main branch
git checkout main
# Make frontend changes and commit

git checkout netlify-deploy  
git merge main              # Merge frontend changes
# Netlify automatically rebuilds and deploys
```

## 🛠 API Endpoints

### NHL Data Endpoints
- **`GET /api/nhldata`** - Returns aggregated NHL team statistics
  - Default: 2025 regular season data
  - Response: Team wins, losses, goals, games played
  - Example: `/api/nhldata?season_type=regular&league_season=2024`

- **`GET /api/seasons`** - Returns available seasons and types in database
  - Lists all season types (preseason, regular, playoffs) per year
  - Useful for frontend season selectors

- **`GET /api/debug`** - Debug endpoint for troubleshooting data filters  
  - Shows raw data count and sample records for specific filters
  - Example: `/api/debug?season_type=preseason&league_season=2025`

### NFL Data Endpoints  
- **`GET /api/nfldata`** - Returns NFL player statistics (2024 season)
  - Fantasy points, touchdowns, yards, tackles, interceptions
  - Sorted by fantasy points (top 500 players)
  - Includes fantasy team owner assignments

- **`GET /api/fantasy-teams`** - Returns fantasy team rosters
  - Mock endpoint for Chris, Aaron, and Jay teams
  - **`POST /api/fantasy-teams/<owner>`** - Save fantasy team data

### System Endpoints
- **`GET /api/test`** - Simple health check endpoint
- **`GET /api/tables`** - Database table inspection (dev/debug)

### API Parameters
- **`season_type`**: `preseason`, `regular`, `playoffs` (default: `regular`)
- **`league_season`**: Year (e.g., `2024`, `2025`) (default: `2025`)
- **`owner`**: Fantasy team owner (`chris`, `aaron`, `jay`)

## ✨ Key Features

### 🏒 NHL Data Management
- **Multi-year Support**: View NHL data from multiple seasons (2024, 2025)
- **Season Type Filtering**: Switch between preseason, regular season, and playoffs
- **Real-time Data**: Fetches live game data from NHL API via RapidAPI
- **Team Statistics**: Aggregated wins, losses, goals, and games played
- **Win Percentages**: Calculated win rates and performance metrics
- **Data Persistence**: Reliable PostgreSQL storage with optimized queries

### 🏈 NFL Integration
- **Player Statistics**: Fantasy points, touchdowns, yards, and defensive stats
- **Fantasy Team Management**: Mock fantasy league with team assignments
- **Top Player Rankings**: Sorted by fantasy points (top 500 players)
- **Multi-position Support**: QB, RB, WR, TE, DEF statistics

### 🎨 Frontend Experience  
- **Angular 20**: Latest version with standalone components
- **Material Design**: Angular Material UI components
- **Interactive Controls**: Year and season type selectors with live filtering
- **Responsive Design**: Mobile-first design that works on all devices
- **Loading States**: User-friendly loading indicators and empty states
- **Sort Functionality**: Sortable columns for team and player data

### 🚀 Architecture & Deployment
- **Dual-Branch Strategy**: Optimized for both backend and frontend deployments
- **Production Ready**: Railway (backend) + Netlify (frontend) deployment
- **Health Monitoring**: Built-in health checks and debug endpoints
- **CORS Enabled**: Cross-origin resource sharing for API access
- **Environment Flexibility**: Development and production database configurations

## 🛠 Technology Stack

### Frontend Technologies
- **Angular 20** - Latest framework with standalone components
- **TypeScript 5.8** - Strong typing and modern JavaScript features
- **Angular Material 19** - UI component library with consistent design
- **Angular CDK** - Component development kit for advanced UI patterns
- **RxJS 7.8** - Reactive programming for async data handling
- **Angular Router** - Client-side routing and navigation

### Backend Technologies
- **Python 3.11+** - Modern Python runtime
- **Flask** - Lightweight web framework with CORS support
- **psycopg2** - PostgreSQL database adapter with connection pooling
- **Gunicorn** - WSGI HTTP server for production deployment
- **python-dotenv** - Environment variable management
- **Flask-CORS** - Cross-origin resource sharing middleware

### Database & Infrastructure
- **PostgreSQL** - Robust relational database with advanced queries
- **Neon Database** - Serverless PostgreSQL with automatic scaling
- **Railway** - Backend deployment platform with automatic builds
- **Netlify** - Frontend deployment with CDN and build optimization
- **Environment Management** - Development and production configurations

### Development Tools
- **Angular CLI 20** - Command-line interface for Angular development
- **Node.js 20** - JavaScript runtime for build tools
- **npm** - Package management and script execution
- **TypeScript Compiler** - Code compilation and type checking

## Deployment URLs

- **Frontend**: `https://nhl-data-visualizer.netlify.app`
- **Backend API**: `https://nhl-data-projects-production.up.railway.app`
- **Repository**: `https://github.com/Grudged/nhl-data-projects`

## 🆕 Recent Updates & Project Highlights

### 2025 Season Support (Latest)
- ✅ **Multi-year filtering**: Added support for 2025 NHL season data
- ✅ **Enhanced UI**: Year selector (2024/2025) and season type toggles
- ✅ **API improvements**: `league_season` parameter for flexible queries
- ✅ **Better UX**: Loading indicators and empty state handling
- ✅ **State management**: Improved frontend data handling and error states

### Architecture Improvements
- 🚀 **Dual-branch deployment**: Optimized for both Railway and Netlify
- 🚀 **Angular 20 upgrade**: Latest framework with standalone components  
- 🚀 **Material Design**: Consistent UI components throughout
- 🚀 **Health monitoring**: Debug endpoints and database inspection tools
- 🚀 **CORS configuration**: Proper API access from frontend domains

### Database Enhancements
- 📊 **Optimized queries**: Complex SQL for team statistics aggregation
- 📊 **Multi-sport support**: NHL games and NFL player statistics
- 📊 **Season flexibility**: Support for preseason, regular, and playoff data
- 📊 **Fantasy integration**: NFL fantasy team management capabilities

## 🏆 Project Highlights

✨ **Modern Tech Stack**: Angular 20 + Flask + PostgreSQL + Railway + Netlify  
🌐 **Dual-Sport Data**: NHL team statistics + NFL fantasy player data  
🚀 **Smart Deployment**: Branch-based deployment strategy for optimal performance  
📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile  
🔍 **Advanced Filtering**: Multi-year, multi-season data visualization  
🛠 **Developer Friendly**: Health checks, debug endpoints, and comprehensive API  
⚡ **Production Ready**: Automated deployments with monitoring and error handling  

---

**NHL Data Projects** - *Professional sports data visualization with modern web technologies*