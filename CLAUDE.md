# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pokemon Battle Logger is a sophisticated application that extracts and analyzes battle data from Pokemon Scarlet/Violet ranked match YouTube videos. It combines computer vision, OCR, machine learning, and web technologies to provide comprehensive battle analytics.

## Architecture

### Core Components
- **Backend API** (`poke_battle_logger/`) - FastAPI server with video processing capabilities
- **Frontend Dashboard** (`poke_battle_logger_vis/`) - Next.js React application with analytics
- **Batch Processing** (`poke_battle_logger/batch/`) - Video analysis and data extraction pipeline
- **Database Layer** (`poke_battle_logger/database/`) - PostgreSQL/SQLite with Peewee ORM
- **Cloud Integration** - Google Cloud Storage, Firestore, and Cloud Batch for scalable processing

### Technology Stack
- **Backend**: Python 3.10+, FastAPI, Peewee ORM, OpenCV, Tesseract OCR, TensorFlow/PyTorch
- **Frontend**: Next.js 13, React 18, TypeScript, Chakra UI, Auth0
- **Database**: PostgreSQL (production), SQLite (local development)
- **Cloud**: Google Cloud Platform (Storage, Firestore, Cloud Batch)
- **Package Management**: Poetry (backend), Yarn (frontend)

## Development Commands

### Backend Development
```bash
# API Server
make run_api                    # Local development with SQLite
make run_api_local_use_postgres # Local with PostgreSQL
make run_api_in_cloud_run      # Production environment

# Frontend Dashboard
make run_dashboard             # Start Next.js dev server (cd poke_battle_logger_vis && yarn dev)

# Testing and Quality
make test                      # Run pytest suite
make test_local               # Run tests with local Tesseract
make lint                     # Code linting with mypy and flake8
make format                   # Code formatting with isort and black

# Data Processing
make extract-data             # Extract battle data from video (requires VIDEO_ID, TRAINER_ID, LANG)
make build-pokemon-faiss-index # Build Pokemon image search index
make build-pokemon-multi-name-dict # Build Pokemon name dictionary
```

### Frontend Development
```bash
cd poke_battle_logger_vis
yarn dev                      # Development server
yarn build                    # Production build
yarn lint                     # ESLint
```

### Docker Workflows
```bash
make init-docker-server       # Build server Docker image
make init-docker-job         # Build job processing Docker image
make create-container-mount   # Development container with volume mount
```

## Data Extraction Pipeline

### Batch Processing (YouTube Videos)
1. **Video Input**: YouTube video URL submitted via frontend
2. **Download & Processing**: Video downloaded using yt-dlp, processed with OpenCV
3. **Computer Vision Pipeline**:
   - Frame extraction and template matching for game states
   - Multi-language OCR (English, Japanese, Chinese, Korean, French, Spanish, Italian, German)
   - Pokemon recognition using FAISS similarity search
   - Battle state detection (win/lose, ranking, team composition)
4. **Data Storage**: Structured battle data stored in database
5. **Analytics**: Real-time battle statistics and visualizations

## Key Entry Points

### API Endpoints (`poke_battle_logger/api/app.py`)
- `/api/v1/analytics` - Battle analytics and statistics
- `/api/v1/extract_stats_from_video` - Video processing endpoint
- `/api/v1/extract_pokemon_name_from_image` - Pokemon image recognition
- `/api/v1/recent_battle_summary` - Recent battle data

### Batch Processing (`poke_battle_logger/batch/`)
- `pokemon_battle_extractor.py` - Main video processing pipeline
- `pokemon_extractor.py` - Pokemon detection and recognition
- `frame_detector.py` - Battle state detection

### Frontend Pages (`poke_battle_logger_vis/pages/`)
- `index.tsx` - Main dashboard
- `analytics/index.tsx` - Battle analytics
- `battle_log/index.tsx` - Battle history
- `process_video/index.tsx` - Video processing interface

## Template Recognition System

The application uses extensive template matching for game state detection:
- **Pokemon Templates**: Individual Pokemon recognition images in `template_images/`
- **UI Templates**: Game state detection (win/lose, ranking screens)
- **Multi-language Support**: Separate template sets for different game languages
- **Unknown Pokemon Handling**: Failed detections saved to `template_images/unknown_pokemon_templates/` for manual labeling

## Environment Setup

### Required Dependencies
- **Tesseract OCR**: Multi-language support required (English, Japanese, Chinese, Korean, French, Spanish, Italian, German)
- **Poetry**: Python package management
- **Node.js/Yarn**: Frontend development
- **PostgreSQL**: Production database (SQLite for local development)

### Environment Variables
- `ENV`: `local` or `production`
- `TESSDATA_PREFIX`: Path to Tesseract language data
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to GCP service account JSON
- Database connection variables for PostgreSQL

### Credentials Setup
- Auth0 configuration in `poke_battle_logger_vis/.env.local`
- GCP service account JSON at `.credentials/google-cloud-credential.json`

## Data Models

Key database entities:
- **Battle**: Core battle information and metadata
- **BattleLog**: Match results and ranking changes
- **PreBattlePokemon**: Team compositions before battle
- **InBattlePokemon**: Active Pokemon during battle
- **SelectedMoves**: Move usage tracking
- **Message**: In-battle message logging

## Video Processing Requirements

- **Format**: 1080p (1920x1080), 30fps YouTube videos
- **Content**: Pokemon Scarlet/Violet ranked matches (Master Ball tier and above)
- **Language**: Supports multiple game languages
- **Recording**: OBS-compatible, must show complete battle flow from team selection to results

## Machine Learning Components

- **FAISS Index**: Fast similarity search for Pokemon image recognition
- **Hugging Face Models**: Text processing and classification
- **TensorFlow/Keras**: Neural networks for image classification
- **Continuous Learning**: User annotations improve model accuracy over time
