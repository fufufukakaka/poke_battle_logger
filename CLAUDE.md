# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pokemon Battle Logger extracts and analyzes battle data from Pokemon Scarlet/Violet ranked match YouTube videos. It uses computer vision, OCR, and machine learning to provide comprehensive battle analytics through a web dashboard.

## Architecture

### Core Pipeline Flow
1. **Video Input** → Frontend submits YouTube URL via [process_video/index.tsx](poke_battle_logger_vis/pages/process_video/index.tsx)
2. **Download & Extract** → [pokemon_battle_extractor.py](poke_battle_logger/batch/pokemon_battle_extractor.py) downloads video using yt-dlp
3. **Frame Analysis** → [frame_detector.py](poke_battle_logger/batch/frame_detector.py) detects battle states via template matching
4. **Pokemon Recognition** → [pokemon_extractor.py](poke_battle_logger/batch/pokemon_extractor.py) uses FAISS similarity search
5. **OCR Processing** → Multi-language Tesseract OCR extracts text (supports 8 languages)
6. **Data Storage** → [sqlmodel_handler.py](poke_battle_logger/database/sqlmodel_handler.py) persists to database
7. **Analytics Display** → Frontend dashboard displays battle statistics

### Technology Stack
- **Backend**: Python 3.10+, FastAPI, SQLModel (migrated from Peewee), OpenCV, Tesseract OCR
- **Frontend**: Next.js 15, React 19, TypeScript, Radix UI components
- **Database**: PostgreSQL (production), SQLite (local), Alembic for migrations
- **Cloud**: Google Cloud Platform (Storage, Firestore, Cloud Batch)
- **Package Management**: Poetry (backend), Yarn (frontend)

### Key Directories
- `poke_battle_logger/` - Backend API and batch processing
  - `api/app.py` - FastAPI endpoints for analytics and video processing
  - `batch/` - Video processing pipeline (extractor, frame detector, Pokemon recognition)
  - `database/sqlmodel_handler.py` - Database layer using SQLModel
  - `models/` - SQLModel data models (Battle, Pokemon, Trainer, etc.)
- `poke_battle_logger_vis/` - Next.js frontend dashboard
  - `pages/` - Main UI pages (index, analytics, battle_log, process_video)
  - `components/` - Reusable React components (UI primitives, data tables, charts)
- `template_images/` - Pokemon and UI template images for computer vision
- `alembic/` - Database migration scripts

## Development Commands

### Backend
```bash
# API Server
make run_api                           # Local with SQLite (ENV=local)
make run_api_local_use_postgres        # Local with PostgreSQL
make run_api_in_cloud_run             # Production (ENV=production)

# Testing and Quality
make test                              # Run pytest
make test_local                        # Run tests with local Tesseract
make lint                             # mypy + flake8
make format                           # isort + black

# Data Processing
make extract-data VIDEO_ID=<id> TRAINER_ID=<id> LANG=<lang>  # Extract battle data
make build-pokemon-faiss-index                                 # Build Pokemon image index
make build-pokemon-multi-name-dict                            # Build Pokemon name dictionary
```

### Frontend
```bash
make run_dashboard                     # Start Next.js dev server (port 3000)
cd poke_battle_logger_vis && yarn dev  # Alternative
cd poke_battle_logger_vis && yarn build && yarn start  # Production build
```

### Database Migrations (Alembic)
```bash
# Create new migration after model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head                   # Apply all pending migrations
ENV=production alembic upgrade head    # Apply to production database

# Check current version
alembic current

# Rollback
alembic downgrade -1                   # Rollback one version
```

### Docker
```bash
make init-docker-server                # Build server image
make init-docker-job                   # Build job processing image
make create-container-mount            # Dev container with volume mount
```

## Database Layer

**Recently migrated from Peewee to SQLModel** (ongoing as of Sept 2025). The codebase uses:
- **SQLModel** for ORM (SQLAlchemy-based with Pydantic validation)
- **Alembic** for schema migrations (config in [alembic.ini](alembic.ini))
- Environment-based connection: SQLite (ENV=local) or PostgreSQL (ENV=production)
- Database engine factory in [models/base.py](poke_battle_logger/models/base.py):get_engine()

### Data Models
Core entities in `poke_battle_logger/models/`:
- **Battle** - Core battle information and metadata
- **BattleSummary** - Match results and ranking changes
- **BattleVideo** - YouTube video references
- **BattlePokemonTeam** - Team compositions before battle
- **InBattlePokemonLog** - Active Pokemon during battle
- **SelectedMove** - Move usage tracking
- **MessageLog** - In-battle message logging
- **FaintedLog** - Pokemon fainting events
- **Trainer** - Player information
- **Season** - Game season information

## Template Recognition System

The application uses extensive template matching via OpenCV for game state detection:
- **Pokemon Templates**: `template_images/labeled_pokemon_templates/` - Labeled Pokemon images
- **Unknown Templates**: `template_images/unknown_pokemon_templates/` - Failed detections for manual labeling
- **UI Templates**: Game state detection (win/lose, ranking screens, battle UI)
- **Multi-language Support**: Separate template sets for 8 game languages
- **Annotation Workflow**: Failed Pokemon detections → manual labeling → rebuild FAISS index

When Pokemon detection fails, images are saved to `unknown_pokemon_templates/`. To fix:
1. Rename image to `{correct_pokemon_name}.png` (or `{name}_{number}.png` if duplicate)
2. Move to `labeled_pokemon_templates/`
3. Run `make build-pokemon-faiss-index` to rebuild search index

## Environment Setup

### Required Dependencies
- **Tesseract OCR**: Must have language data for English, Japanese, Chinese (simplified/traditional), Korean, French, Spanish, Italian, German
  - Set `TESSDATA_PREFIX` to tessdata_best location (e.g., `/opt/brew/Cellar/tesseract/5.3.0_1/share/tessdata_best/`)
- **Poetry**: Python package management (`poetry install`)
- **Node.js/Yarn**: Frontend development (Node 19.9.0 per Volta config)
- **PostgreSQL**: Production database (optional for local development)

### Environment Variables
- `ENV`: `local` (SQLite) or `production` (PostgreSQL)
- `TESSDATA_PREFIX`: Path to Tesseract language data
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to `.credentials/google-cloud-credential.json`
- `RESEND_API_KEY`: Email notification service
- PostgreSQL connection vars (when ENV=production):
  - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`

### Credentials Setup
- Auth0: `poke_battle_logger_vis/.env.local` needs `NEXT_PUBLIC_AUTH0_DOMAIN` and `NEXT_PUBLIC_AUTH0_CLIENT_ID`
- GCP: Service account JSON at `.credentials/google-cloud-credential.json`

## Video Processing Requirements

- **Format**: 1080p (1920x1080), 30fps YouTube videos
- **Content**: Pokemon Scarlet/Violet ranked matches (Master Ball tier and above)
- **Language**: Supports 8 game languages (English, Japanese, Chinese, Korean, French, Spanish, Italian, German)
- **Recording**: Must show complete battle flow from team selection → battle → results screen
- **Ranking**: Only extracts battles where rank changed (skips no-change battles)

## Machine Learning Components

- **FAISS Index**: Fast similarity search for Pokemon image recognition
- **Tesseract OCR**: Multi-language text extraction from battle frames
- **OpenCV Template Matching**: Game state detection and UI element recognition
- **Continuous Learning**: User annotations improve Pokemon detection accuracy

## Important Notes

- Always prefer editing existing files over creating new ones
- Do not create documentation files unless explicitly requested
- When making database schema changes, create Alembic migrations
- Test locally with `make test_local` before running full test suite
- Pokemon name mappings are in `data/pokemon_names.csv` (No., Japanese, English, etc.)
