import asyncio
import logging
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Dict, Optional

import numpy as np

from poke_battle_logger.batch.extractor import Extractor
from poke_battle_logger.batch.frame_detector import FrameDetector
from poke_battle_logger.batch.pokemon_extractor import PokemonExtractor

logger = logging.getLogger(__name__)


@dataclass
class FrameData:
    frame: np.ndarray
    timestamp: datetime
    frame_number: int
    frame_type: Optional[str] = None
    confidence: float = 0.0


@dataclass
class BattleEvent:
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    confidence: float


class BattleStateMachine:
    def __init__(self):
        self.current_state = "idle"
        self.battle_id = None
        self.accumulated_data = {}
        self.last_rank = None

    def process_frame_type(
        self, frame_type: str, extracted_data: Dict[str, Any]
    ) -> Optional[BattleEvent]:
        if frame_type == "ranking" and self.current_state == "idle":
            self.current_state = "pre_battle"
            rank_data = extracted_data.get("rank")
            if rank_data and rank_data != self.last_rank:
                self.last_rank = rank_data
                self.battle_id = f"battle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                return BattleEvent(
                    event_type="battle_start",
                    data={"battle_id": self.battle_id, "starting_rank": rank_data},
                    timestamp=datetime.now(),
                    confidence=extracted_data.get("confidence", 0.0),
                )

        elif frame_type == "pokemon_selection" and self.current_state == "pre_battle":
            pokemon_data = extracted_data.get("selected_pokemon", [])
            if pokemon_data:
                self.current_state = "battle"
                return BattleEvent(
                    event_type="pokemon_selected",
                    data={"battle_id": self.battle_id, "pokemon": pokemon_data},
                    timestamp=datetime.now(),
                    confidence=extracted_data.get("confidence", 0.0),
                )

        elif frame_type == "level_50" and self.current_state == "pre_battle":
            # Level 50 frame indicates battle is about to start
            self.current_state = "battle"
            return BattleEvent(
                event_type="battle_in_progress",
                data={"battle_id": self.battle_id, "status": "battle_started"},
                timestamp=datetime.now(),
                confidence=extracted_data.get("confidence", 0.8),
            )

        elif frame_type == "win_or_lost":
            if self.current_state in ["battle", "pre_battle"]:
                self.current_state = "post_battle"
                result = extracted_data.get("battle_result")
                if result:
                    return BattleEvent(
                        event_type="battle_result",
                        data={"battle_id": self.battle_id, "result": result},
                        timestamp=datetime.now(),
                        confidence=extracted_data.get("confidence", 0.0),
                    )

        elif frame_type == "ranking" and self.current_state == "post_battle":
            rank_data = extracted_data.get("rank")
            if rank_data is not None and rank_data != self.last_rank:
                old_rank = self.last_rank
                self.last_rank = rank_data
                self.current_state = "idle"
                
                # Calculate rank change only if we have both old and new rank
                rank_change = 0
                if old_rank is not None and isinstance(old_rank, (int, float)) and isinstance(rank_data, (int, float)):
                    rank_change = rank_data - old_rank
                
                # Reset battle_id for next battle
                completed_battle_id = self.battle_id
                self.battle_id = None
                
                return BattleEvent(
                    event_type="battle_complete",
                    data={
                        "battle_id": completed_battle_id,
                        "final_rank": rank_data,
                        "starting_rank": old_rank,
                        "rank_change": rank_change,
                    },
                    timestamp=datetime.now(),
                    confidence=extracted_data.get("confidence", 0.0),
                )

        return None


class LiveStreamProcessor:
    def __init__(
        self,
        trainer_id: str,
        language: str = "en",
        buffer_size: int = 300,
        processing_interval: float = 0.1,
    ):
        self.trainer_id = trainer_id
        self.language = language
        self.buffer_size = buffer_size
        self.processing_interval = processing_interval

        self.frame_buffer = deque(maxlen=buffer_size)
        self.frame_detector = FrameDetector()
        self.extractor = Extractor(lang=language)
        self.pokemon_extractor = PokemonExtractor()
        self.state_machine = BattleStateMachine()

        self.frame_counter = 0
        self.processing_lock = asyncio.Lock()
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="frame_processor")
        self.event_handlers = []
        self._should_stop = False

    def add_event_handler(self, handler: Callable[[BattleEvent], None]):
        self.event_handlers.append(handler)

    def emit_event(self, event: BattleEvent):
        for handler in self.event_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")

    async def process_frame(self, frame: np.ndarray) -> Optional[BattleEvent]:
        # Non-blocking check if processing is available
        if self.processing_lock.locked():
            logger.debug("Frame processing busy, skipping frame")
            return None

        async with self.processing_lock:
            try:
                frame_data = FrameData(
                    frame=frame.copy(),  # Copy frame to avoid concurrent access issues
                    timestamp=datetime.now(),
                    frame_number=self.frame_counter
                )

                # Run frame detection in executor to avoid blocking
                frame_type = await asyncio.get_event_loop().run_in_executor(
                    self.executor, self.frame_detector.classify_frame, frame
                )
                frame_data.frame_type = frame_type

                if frame_type and frame_type != "unknown":
                    extracted_data = await self._extract_data_from_frame(frame_data)
                    if extracted_data:
                        # State machine processing is CPU-light, keep in main thread
                        event = self.state_machine.process_frame_type(
                            frame_type, extracted_data
                        )
                        if event:
                            self.emit_event(event)
                            return event

                self.frame_buffer.append(frame_data)
                self.frame_counter += 1

            except Exception as e:
                logger.error(f"Error processing frame {self.frame_counter}: {e}")

        return None

    async def _extract_data_from_frame(
        self, frame_data: FrameData
    ) -> Optional[Dict[str, Any]]:
        frame_type = frame_data.frame_type
        frame = frame_data.frame

        try:
            if frame_type == "ranking":
                rank = await asyncio.get_event_loop().run_in_executor(
                    self.executor, self.extractor.extract_current_rank, frame
                )
                return {"rank": rank, "confidence": 0.8}

            elif frame_type == "pokemon_selection":
                pokemon_list = await asyncio.get_event_loop().run_in_executor(
                    self.executor, self.extractor.extract_selected_pokemon_order, frame
                )
                return {"selected_pokemon": pokemon_list, "confidence": 0.7}

            elif frame_type == "win_or_lost":
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor, self.extractor.extract_win_or_lost, frame
                )
                return {"battle_result": result, "confidence": 0.9}

            elif frame_type == "message_window":
                message = await asyncio.get_event_loop().run_in_executor(
                    self.executor, self.extractor.extract_message, frame
                )
                return {"message": message, "confidence": 0.6}

        except Exception as e:
            logger.error(f"Error extracting data from {frame_type} frame: {e}")

        return None

    async def start_processing_stream(
        self, frame_stream: AsyncGenerator[np.ndarray, None]
    ):
        logger.info(f"Starting live stream processing for trainer {self.trainer_id}")
        self._should_stop = False

        try:
            async for frame in frame_stream:
                if self._should_stop:
                    logger.info("Stream processing stop requested")
                    break

                try:
                    event = await self.process_frame(frame)
                    if event:
                        logger.info(f"Generated event: {event.event_type}")

                    await asyncio.sleep(self.processing_interval)

                except Exception as e:
                    logger.error(f"Error in stream processing loop: {e}")
                    continue

        except asyncio.CancelledError:
            logger.info("Stream processing cancelled")
            raise
        except Exception as e:
            logger.error(f"Fatal error in stream processing: {e}")
            raise
        finally:
            await self._cleanup()

    async def stop_processing(self):
        """Stop the processing stream gracefully"""
        logger.info("Stopping stream processing...")
        self._should_stop = True
        await self._cleanup()

    async def _cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'executor') and self.executor:
                self.executor.shutdown(wait=True)
                logger.debug("Thread pool executor shutdown complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def get_current_battle_state(self) -> Dict[str, Any]:
        return {
            "current_state": self.state_machine.current_state,
            "battle_id": self.state_machine.battle_id,
            "last_rank": self.state_machine.last_rank,
            "frames_processed": self.frame_counter,
            "buffer_size": len(self.frame_buffer),
        }
