import asyncio
import logging
import unicodedata
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from poke_battle_logger.database.database_handler import DatabaseHandler
from poke_battle_logger.stream.frame_capture import FrameCaptureManager
from poke_battle_logger.stream.live_processor import BattleEvent, LiveStreamProcessor
from poke_battle_logger.types import Battle, BattleLog, InBattlePokemon, Message, PreBattlePokemon

logger = logging.getLogger(__name__)


class LiveBattleAnalyzer:
    def __init__(
        self,
        trainer_id: str,
        language: str = "en",
        capture_source: str = "obs",
        capture_config: Optional[Dict[str, Any]] = None,
        db_handler: Optional[DatabaseHandler] = None,
    ):
        self.trainer_id = trainer_id
        self.language = language
        self.capture_source_type = capture_source
        self.capture_config = capture_config or {}

        self.processor = LiveStreamProcessor(trainer_id, language)
        self.capture_manager = FrameCaptureManager()
        self.capture_source = None
        self.db_handler = db_handler

        self.is_running = False
        self.stats = {
            "frames_processed": 0,
            "events_generated": 0,
            "start_time": None,
            "last_event_time": None,
            "errors": 0,
        }

        self.event_callbacks = []
        self.processor.add_event_handler(self._handle_battle_event)
        
        # Initialize temporary storage for pending data
        self._pending_battle_results = {}
        
        # Validate database connection if provided
        if self.db_handler:
            self._validate_database_connection()

    def add_event_callback(self, callback: Callable[[BattleEvent], None]):
        self.event_callbacks.append(callback)

    def _handle_battle_event(self, event: BattleEvent):
        self.stats["events_generated"] += 1
        self.stats["last_event_time"] = datetime.now()

        logger.info(f"Battle event: {event.event_type} - {event.data}")

        if self.db_handler:
            asyncio.create_task(self._save_event_to_db(event))

        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")

    def _validate_database_connection(self):
        """Validate database connection and trainer existence"""
        try:
            # Check if trainer exists in database
            if not self.db_handler.check_trainer_id_exists(self.trainer_id):
                logger.warning(f"Trainer {self.trainer_id} not found in database. "
                             "Live events will be logged but not saved to database.")
                self.db_handler = None
            else:
                logger.info(f"Database connection validated for trainer {self.trainer_id}")
        except Exception as e:
            logger.error(f"Database validation failed: {e}")
            self.db_handler = None

    def _update_frame_stats(self):
        """Update frame processing statistics"""
        if hasattr(self.processor, 'frame_counter'):
            self.stats["frames_processed"] = self.processor.frame_counter

    async def _save_event_to_db(self, event: BattleEvent):
        try:
            if event.event_type == "battle_start":
                await self._save_battle_start(event)
            elif event.event_type == "pokemon_selected":
                await self._save_pokemon_selection(event)
            elif event.event_type == "battle_result":
                await self._save_battle_result(event)
            elif event.event_type == "battle_complete":
                await self._save_battle_complete(event)
        except Exception as e:
            logger.error(f"Error saving event to database: {e}")
            self.stats["errors"] += 1

    async def _save_battle_start(self, event: BattleEvent):
        """Save battle start event to database"""
        try:
            if not self.db_handler:
                logger.warning("No database handler available")
                return

            battle_id = event.data.get("battle_id")
            if not battle_id:
                logger.error("No battle_id in battle_start event")
                return

            # Get internal trainer ID from database
            trainer_id_in_db = self.db_handler.get_trainer_id_in_DB(self.trainer_id)
            if trainer_id_in_db == -1:
                logger.error(f"Trainer {self.trainer_id} not found in database")
                return

            # Create Battle record
            battles = [Battle(battle_id=battle_id, trainer_id=trainer_id_in_db)]
            
            # Run database operation in executor to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                None, self.db_handler.insert_battle_id, battles
            )
            
            logger.info(f"Battle record created: {battle_id}")

        except Exception as e:
            logger.error(f"Error saving battle start to database: {e}")
            self.stats["errors"] += 1

    async def _save_pokemon_selection(self, event: BattleEvent):
        """Save pokemon selection event to database"""
        try:
            if not self.db_handler:
                logger.warning("No database handler available")
                return

            battle_id = event.data.get("battle_id")
            pokemon_list = event.data.get("pokemon", [])
            
            if not battle_id or not pokemon_list:
                logger.error("Missing battle_id or pokemon data in pokemon_selection event")
                return

            # Create BattlePokemonTeam records for selected pokemon
            battle_pokemon_team = []
            for pokemon_name in pokemon_list:
                if pokemon_name:
                    # Normalize pokemon name
                    normalized_name = unicodedata.normalize("NFC", pokemon_name)
                    battle_pokemon_team.append(
                        PreBattlePokemon(
                            battle_id=battle_id,
                            team="your",
                            pokemon_name=normalized_name
                        )
                    )

            if battle_pokemon_team:
                # Run database operation in executor
                await asyncio.get_event_loop().run_in_executor(
                    None, self.db_handler.insert_battle_pokemon_team, battle_pokemon_team
                )
                
                logger.info(f"Pokemon selection saved: {len(battle_pokemon_team)} pokemon for battle {battle_id}")

        except Exception as e:
            logger.error(f"Error saving pokemon selection to database: {e}")
            self.stats["errors"] += 1

    async def _save_battle_result(self, event: BattleEvent):
        """Save battle result event to database (temporary storage for battle completion)"""
        try:
            battle_id = event.data.get("battle_id")
            result = event.data.get("result")
            
            if not battle_id or not result:
                logger.error("Missing battle_id or result in battle_result event")
                return

            # Store battle result temporarily for battle completion
            if not hasattr(self, '_pending_battle_results'):
                self._pending_battle_results = {}
            
            self._pending_battle_results[battle_id] = {
                "result": result,
                "timestamp": event.timestamp
            }
            
            logger.debug(f"Battle result stored temporarily: {battle_id} -> {result}")

        except Exception as e:
            logger.error(f"Error processing battle result: {e}")
            self.stats["errors"] += 1

    async def _save_battle_complete(self, event: BattleEvent):
        """Save battle completion event to database"""
        try:
            if not self.db_handler:
                logger.warning("No database handler available")
                return

            battle_id = event.data.get("battle_id")
            final_rank = event.data.get("final_rank")
            starting_rank = event.data.get("starting_rank")
            rank_change = event.data.get("rank_change", 0)
            
            if not battle_id or final_rank is None:
                logger.error("Missing battle_id or final_rank in battle_complete event")
                return

            # Get stored battle result
            battle_result = None
            if hasattr(self, '_pending_battle_results') and battle_id in self._pending_battle_results:
                battle_result = self._pending_battle_results[battle_id]["result"]
                del self._pending_battle_results[battle_id]
            
            if not battle_result:
                logger.warning(f"No battle result found for battle {battle_id}, defaulting to 'unknown'")
                battle_result = "unknown"

            # Create BattleLog record
            battle_summary = [
                BattleLog(
                    battle_id=battle_id,
                    created_at=event.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    win_or_lose=battle_result,
                    next_rank=final_rank,
                    your_team="",  # TODO: Get from pokemon selection data
                    opponent_team="",  # TODO: Get from opponent detection
                    your_pokemon_1="",  # TODO: Get from selection data
                    your_pokemon_2="",
                    your_pokemon_3="",
                    opponent_pokemon_1="",  # TODO: Get from opponent detection
                    opponent_pokemon_2="",
                    opponent_pokemon_3="",
                    video=f"live_stream_{battle_id}",  # Mark as live stream
                    memo=f"Live analysis - Rank change: {rank_change:+d}" if rank_change else "Live analysis"
                )
            ]

            # Save battle summary to database
            await asyncio.get_event_loop().run_in_executor(
                None, self.db_handler.insert_battle_summary, battle_summary
            )
            
            logger.info(f"Battle completed and saved: {battle_id}, Result: {battle_result}, "
                       f"Rank: {starting_rank} -> {final_rank} ({rank_change:+d})")

        except Exception as e:
            logger.error(f"Error saving battle completion to database: {e}")
            self.stats["errors"] += 1

    async def start_analysis(self):
        if self.is_running:
            logger.warning("Analysis already running")
            return

        analysis_task = None
        stats_task = None

        try:
            # Create and test capture source
            self.capture_source = self.capture_manager.create_source(
                self.capture_source_type, **self.capture_config
            )

            if not await self.capture_manager.test_source(self.capture_source):
                raise RuntimeError(
                    f"Failed to initialize capture source: {self.capture_source_type}"
                )

            self.is_running = True
            self.stats["start_time"] = datetime.now()
            self.stats["errors"] = 0  # Reset error count

            logger.info(f"Starting live battle analysis for {self.trainer_id}")
            logger.info(f"Capture source: {self.capture_source_type}")
            logger.info(f"Language: {self.language}")
            logger.info(f"Database saving: {'enabled' if self.db_handler else 'disabled'}")

            frame_stream = self.capture_source.start_capture()

            # Create tasks for concurrent execution
            analysis_task = asyncio.create_task(
                self.processor.start_processing_stream(frame_stream)
            )
            stats_task = asyncio.create_task(self._stats_logger())

            # Wait for both tasks to complete
            await asyncio.gather(analysis_task, stats_task, return_exceptions=True)

        except asyncio.CancelledError:
            logger.info("Analysis cancelled by user")
            raise
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            self.stats["errors"] += 1
            raise
        finally:
            # Clean up tasks if they're still running
            if analysis_task and not analysis_task.done():
                analysis_task.cancel()
                try:
                    await analysis_task
                except asyncio.CancelledError:
                    pass

            if stats_task and not stats_task.done():
                stats_task.cancel()
                try:
                    await stats_task
                except asyncio.CancelledError:
                    pass

            await self.stop_analysis()

    async def stop_analysis(self):
        if not self.is_running:
            return

        logger.info("Stopping live battle analysis...")
        self.is_running = False

        try:
            # Stop the processor gracefully
            if hasattr(self.processor, 'stop_processing'):
                await self.processor.stop_processing()

            # Stop the capture source
            if self.capture_source:
                await self.capture_source.stop_capture()

        except Exception as e:
            logger.error(f"Error during analysis shutdown: {e}")

        logger.info("Live battle analysis stopped")
        logger.info(f"Final stats: {self.get_stats()}")

    async def _stats_logger(self):
        while self.is_running:
            await asyncio.sleep(30)  # Log stats every 30 seconds
            if self.is_running:
                logger.info(f"Analysis stats: {self.get_stats()}")

    def get_stats(self) -> Dict[str, Any]:
        # Update frame processing stats
        self._update_frame_stats()
        
        stats = self.stats.copy()

        if stats["start_time"]:
            runtime = datetime.now() - stats["start_time"]
            stats["runtime_seconds"] = runtime.total_seconds()

            if stats["frames_processed"] > 0:
                stats["avg_fps"] = stats["frames_processed"] / runtime.total_seconds()

        stats["current_battle_state"] = self.processor.get_current_battle_state()

        return stats

    def get_available_capture_sources(self) -> List[str]:
        return self.capture_manager.get_available_sources()

    async def test_capture_source(
        self, source_type: str, config: Dict[str, Any]
    ) -> bool:
        try:
            test_source = self.capture_manager.create_source(source_type, **config)
            return await self.capture_manager.test_source(test_source)
        except Exception as e:
            logger.error(f"Error testing capture source {source_type}: {e}")
            return False


# Usage example function
async def run_live_analysis(
    trainer_id: str,
    capture_source: str = "obs",
    language: str = "en",
    capture_config: Optional[Dict[str, Any]] = None,
):
    analyzer = LiveBattleAnalyzer(
        trainer_id=trainer_id,
        language=language,
        capture_source=capture_source,
        capture_config=capture_config or {},
    )

    def print_event(event: BattleEvent):
        print(f"[{event.timestamp}] {event.event_type}: {event.data}")

    analyzer.add_event_callback(print_event)

    try:
        await analyzer.start_analysis()
    except KeyboardInterrupt:
        print("\nStopping analysis...")
        await analyzer.stop_analysis()
    except Exception as e:
        print(f"Error in analysis: {e}")
        await analyzer.stop_analysis()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python live_battle_analyzer.py <trainer_id> [capture_source] [language]"
        )
        sys.exit(1)

    trainer_id = sys.argv[1]
    capture_source = sys.argv[2] if len(sys.argv) > 2 else "obs"
    language = sys.argv[3] if len(sys.argv) > 3 else "en"

    # Example configurations for different capture sources
    capture_configs = {
        "obs": {"host": "localhost", "port": 4455, "password": None},
        "screen": {
            "monitor": 1,
            "region": {"top": 0, "left": 0, "width": 1920, "height": 1080},
        },
        "rtmp": {"stream_url": "rtmp://localhost:1935/live/stream"},
        "webcam": {"camera_index": 0},
    }

    config = capture_configs.get(capture_source, {})

    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_live_analysis(trainer_id, capture_source, language, config))
