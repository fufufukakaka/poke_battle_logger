"""
Example SQLModel API endpoints showing the migration path from Peewee.

This file demonstrates how to:
1. Use SQLModel models with FastAPI
2. Migrate existing endpoints from Peewee to SQLModel
3. Leverage type safety and automatic validation
"""
from typing import Dict, List, Union

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from poke_battle_logger.models import (
    Battle, BattleSummary, Trainer, get_session
)

router = APIRouter()


# Dependency to get database session
def get_db_session():
    """Dependency to get database session."""
    with get_session() as session:
        yield session


@router.get("/api/v2/trainer/{trainer_id}/exists", response_model=bool)
async def check_trainer_exists_v2(
    trainer_id: str,
    session: Session = Depends(get_db_session)
) -> bool:
    """Check if trainer exists (SQLModel version)."""
    statement = select(Trainer).where(Trainer.identity == trainer_id)
    trainer = session.exec(statement).first()
    return trainer is not None


@router.get("/api/v2/trainer/{trainer_id}/recent_battles")
async def get_recent_battles_v2(
    trainer_id: str,
    limit: int = 5,
    session: Session = Depends(get_db_session)
) -> List[Dict[str, Union[str, int]]]:
    """Get recent battles for trainer (SQLModel version)."""
    # Find trainer
    trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
    trainer = session.exec(trainer_statement).first()
    
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    
    # Get battles for this trainer
    battle_statement = select(Battle.battle_id).where(Battle.trainer_id == trainer.id)
    battle_ids = session.exec(battle_statement).all()
    
    if not battle_ids:
        return []
    
    # Get battle summaries
    statement = (
        select(BattleSummary)
        .where(BattleSummary.battle_id.in_(battle_ids))
        .order_by(BattleSummary.created_at.desc())
        .limit(limit)
    )
    results = session.exec(statement).all()
    
    return [
        {
            "battle_id": result.battle_id,
            "created_at": result.created_at,
            "win_or_lose": result.win_or_lose,
            "next_rank": result.next_rank,
            "your_pokemon_1": result.your_pokemon_1,
            "opponent_pokemon_1": result.opponent_pokemon_1,
        }
        for result in results
    ]


@router.post("/api/v2/trainer", response_model=Dict[str, str])
async def create_trainer_v2(
    trainer_id: str,
    email: str,
    session: Session = Depends(get_db_session)
) -> Dict[str, str]:
    """Create new trainer (SQLModel version)."""
    # Check if trainer already exists
    existing_statement = select(Trainer).where(Trainer.identity == trainer_id)
    existing = session.exec(existing_statement).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Trainer already exists")
    
    # Create new trainer
    trainer = Trainer(identity=trainer_id, email=email)
    session.add(trainer)
    session.commit()
    session.refresh(trainer)
    
    return {"status": "created", "trainer_id": trainer_id}


@router.get("/api/v2/recent_battle_summary")
async def get_recent_battle_summary_v2(
    trainer_id: str,
    session: Session = Depends(get_db_session)
) -> Dict[str, Union[float, int, str, List[Dict[str, Union[str, int]]]]]:
    """Get recent battle summary (SQLModel version)."""
    # Check if trainer exists
    trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
    trainer = session.exec(trainer_statement).first()
    
    if not trainer:
        return {
            "win_rate": 0.0,
            "latest_rank": 0,
            "latest_win_pokemon": "",
            "latest_lose_pokemon": "",
            "recent_battle_history": [],
            "battle_counts": [],
        }
    
    # Get battles for this trainer
    battle_statement = select(Battle).where(Battle.trainer_id == trainer.id)
    battles = session.exec(battle_statement).all()
    
    if not battles:
        return {
            "win_rate": 0.0,
            "latest_rank": 0,
            "latest_win_pokemon": "",
            "latest_lose_pokemon": "",
            "recent_battle_history": [],
            "battle_counts": [],
        }
    
    battle_ids = [battle.battle_id for battle in battles]
    
    # Get battle summaries
    summary_statement = select(BattleSummary).where(
        BattleSummary.battle_id.in_(battle_ids)
    )
    summaries = session.exec(summary_statement).all()
    
    if not summaries:
        return {
            "win_rate": 0.0,
            "latest_rank": 0,
            "latest_win_pokemon": "",
            "latest_lose_pokemon": "",
            "recent_battle_history": [],
            "battle_counts": [],
        }
    
    # Calculate win rate
    wins = sum(1 for s in summaries if s.win_or_lose == "win")
    win_rate = wins / len(summaries)
    
    # Get latest rank
    latest_summary = max(summaries, key=lambda s: s.created_at)
    latest_rank = latest_summary.next_rank
    
    # Get latest win/lose pokemon
    win_summaries = [s for s in summaries if s.win_or_lose == "win"]
    lose_summaries = [s for s in summaries if s.win_or_lose == "lose"]
    
    latest_win_pokemon = ""
    if win_summaries:
        latest_win = max(win_summaries, key=lambda s: s.created_at)
        latest_win_pokemon = latest_win.opponent_pokemon_1  # Pick first opponent pokemon
    
    latest_lose_pokemon = ""
    if lose_summaries:
        latest_lose = max(lose_summaries, key=lambda s: s.created_at)
        # Pick a non-"Unseen" opponent pokemon
        opponents = [latest_lose.opponent_pokemon_1, latest_lose.opponent_pokemon_2, latest_lose.opponent_pokemon_3]
        valid_opponents = [p for p in opponents if p != "Unseen"]
        if valid_opponents:
            latest_lose_pokemon = valid_opponents[0]
    
    # Get recent battle history
    recent_summaries = sorted(summaries, key=lambda s: s.created_at, reverse=True)[:5]
    recent_battle_history = [
        {
            "battle_id": s.battle_id,
            "created_at": s.created_at,
            "win_or_lose": s.win_or_lose,
            "next_rank": s.next_rank,
            "your_pokemon_1": s.your_pokemon_1,
            "opponent_pokemon_1": s.opponent_pokemon_1,
        }
        for s in recent_summaries
    ]
    
    return {
        "win_rate": win_rate,
        "latest_rank": latest_rank,
        "latest_win_pokemon": latest_win_pokemon,
        "latest_lose_pokemon": latest_lose_pokemon,
        "recent_battle_history": recent_battle_history,
        "battle_counts": [],  # TODO: Implement battle counts
    }


@router.get("/api/v2/trainer/{trainer_id}/summary")
async def get_trainer_summary_v2(
    trainer_id: str,
    session: Session = Depends(get_db_session)
) -> Dict[str, Union[str, int, float]]:
    """Get trainer summary statistics (SQLModel version)."""
    # Find trainer
    trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
    trainer = session.exec(trainer_statement).first()
    
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    
    # Get battle count
    battle_count_statement = select(Battle).where(Battle.trainer_id == trainer.id)
    battles = session.exec(battle_count_statement).all()
    battle_count = len(battles)
    
    # Get battle summaries for win rate calculation
    if battles:
        battle_ids = [battle.battle_id for battle in battles]
        summary_statement = select(BattleSummary).where(
            BattleSummary.battle_id.in_(battle_ids)
        )
        summaries = session.exec(summary_statement).all()
        
        if summaries:
            wins = sum(1 for s in summaries if s.win_or_lose == "win")
            win_rate = wins / len(summaries)
            
            # Get latest rank
            latest_summary = max(summaries, key=lambda s: s.created_at)
            latest_rank = latest_summary.next_rank
        else:
            win_rate = 0.0
            latest_rank = 0
    else:
        win_rate = 0.0
        latest_rank = 0
    
    return {
        "trainer_id": trainer_id,
        "email": trainer.email,
        "battle_count": battle_count,
        "win_rate": win_rate,
        "latest_rank": latest_rank,
    }


@router.get("/api/v2/trainer/{trainer_id}/update_memo")
async def update_memo_v2(
    trainer_id: str,
    battle_id: str,
    memo: str,
    session: Session = Depends(get_db_session)
) -> Dict[str, str]:
    """Update battle memo (SQLModel version)."""
    # Find the battle summary
    statement = select(BattleSummary).where(BattleSummary.battle_id == battle_id)
    battle_summary = session.exec(statement).first()
    
    if not battle_summary:
        raise HTTPException(status_code=404, detail="Battle not found")
    
    # Update memo
    battle_summary.memo = memo
    session.add(battle_summary)
    session.commit()
    
    return {"status": "updated", "battle_id": battle_id, "memo": memo}