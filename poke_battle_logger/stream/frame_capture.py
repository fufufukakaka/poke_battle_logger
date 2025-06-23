import asyncio
import cv2
import numpy as np
from typing import AsyncGenerator, Optional, Dict, Any
from abc import ABC, abstractmethod
import logging
from datetime import datetime

try:
    import obsws_python as obs
    OBS_AVAILABLE = True
except ImportError:
    OBS_AVAILABLE = False
    
try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

logger = logging.getLogger(__name__)

class FrameCaptureSource(ABC):
    @abstractmethod
    async def start_capture(self) -> AsyncGenerator[np.ndarray, None]:
        pass
    
    @abstractmethod
    async def stop_capture(self):
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass

class OBSWebSocketCapture(FrameCaptureSource):
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 4455, 
                 password: Optional[str] = None,
                 scene_name: Optional[str] = None,
                 source_name: Optional[str] = None):
        self.host = host
        self.port = port
        self.password = password
        self.scene_name = scene_name
        self.source_name = source_name
        self.client = None
        self.is_capturing = False
        
    def is_available(self) -> bool:
        return OBS_AVAILABLE
    
    async def start_capture(self) -> AsyncGenerator[np.ndarray, None]:
        if not self.is_available():
            raise RuntimeError("OBS WebSocket library not available")
            
        try:
            self.client = obs.ReqClient(
                host=self.host,
                port=self.port,
                password=self.password
            )
            
            logger.info(f"Connected to OBS WebSocket at {self.host}:{self.port}")
            self.is_capturing = True
            
            while self.is_capturing:
                try:
                    response = self.client.get_source_screenshot(
                        self.source_name or "Game Capture",
                        "png",
                        width=1920,
                        height=1080
                    )
                    
                    if response and hasattr(response, 'image_data'):
                        image_data = response.image_data
                        nparr = np.frombuffer(image_data, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        if frame is not None:
                            yield frame
                            
                    await asyncio.sleep(1/30)  # 30 FPS
                    
                except Exception as e:
                    logger.error(f"Error capturing frame from OBS: {e}")
                    await asyncio.sleep(0.5)
                    
        except Exception as e:
            logger.error(f"Failed to connect to OBS WebSocket: {e}")
            raise
            
    async def stop_capture(self):
        self.is_capturing = False
        if self.client:
            self.client.disconnect()
            self.client = None

class ScreenCapture(FrameCaptureSource):
    def __init__(self, 
                 monitor: int = 1,
                 region: Optional[Dict[str, int]] = None,
                 target_fps: int = 30):
        self.monitor = monitor
        self.region = region or {"top": 0, "left": 0, "width": 1920, "height": 1080}
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps
        self.sct = None
        self.is_capturing = False
        
    def is_available(self) -> bool:
        return MSS_AVAILABLE
    
    async def start_capture(self) -> AsyncGenerator[np.ndarray, None]:
        if not self.is_available():
            raise RuntimeError("MSS library not available")
            
        self.sct = mss.mss()
        self.is_capturing = True
        
        logger.info(f"Starting screen capture for monitor {self.monitor}")
        
        try:
            while self.is_capturing:
                try:
                    screenshot = self.sct.grab(self.region)
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    
                    yield frame
                    await asyncio.sleep(self.frame_interval)
                    
                except Exception as e:
                    logger.error(f"Error capturing screen: {e}")
                    await asyncio.sleep(0.5)
                    
        finally:
            if self.sct:
                self.sct.close()
                
    async def stop_capture(self):
        self.is_capturing = False

class RTMPStreamCapture(FrameCaptureSource):
    def __init__(self, stream_url: str, target_fps: int = 30):
        self.stream_url = stream_url
        self.target_fps = target_fps
        self.cap = None
        self.is_capturing = False
        
    def is_available(self) -> bool:
        return True  # OpenCV is required for the main app
    
    async def start_capture(self) -> AsyncGenerator[np.ndarray, None]:
        self.cap = cv2.VideoCapture(self.stream_url)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open RTMP stream: {self.stream_url}")
            
        logger.info(f"Connected to RTMP stream: {self.stream_url}")
        self.is_capturing = True
        
        try:
            while self.is_capturing:
                ret, frame = self.cap.read()
                if ret:
                    yield frame
                else:
                    logger.warning("Failed to read frame from RTMP stream")
                    await asyncio.sleep(0.1)
                    
        finally:
            if self.cap:
                self.cap.release()
                
    async def stop_capture(self):
        self.is_capturing = False

class WebcamCapture(FrameCaptureSource):
    def __init__(self, camera_index: int = 0, target_fps: int = 30):
        self.camera_index = camera_index
        self.target_fps = target_fps
        self.cap = None
        self.is_capturing = False
        
    def is_available(self) -> bool:
        return True
    
    async def start_capture(self) -> AsyncGenerator[np.ndarray, None]:
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera {self.camera_index}")
            
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        logger.info(f"Connected to camera {self.camera_index}")
        self.is_capturing = True
        
        try:
            while self.is_capturing:
                ret, frame = self.cap.read()
                if ret:
                    yield frame
                else:
                    await asyncio.sleep(0.1)
                    
        finally:
            if self.cap:
                self.cap.release()
                
    async def stop_capture(self):
        self.is_capturing = False

class FrameCaptureManager:
    def __init__(self):
        self.available_sources = self._detect_available_sources()
        self.current_source = None
        
    def _detect_available_sources(self) -> Dict[str, FrameCaptureSource]:
        sources = {}
        
        if OBS_AVAILABLE:
            sources["obs"] = OBSWebSocketCapture()
            
        if MSS_AVAILABLE:
            sources["screen"] = ScreenCapture()
            
        sources["rtmp"] = RTMPStreamCapture("rtmp://localhost:1935/live/stream")
        sources["webcam"] = WebcamCapture()
        
        return sources
    
    def get_available_sources(self) -> list[str]:
        return [name for name, source in self.available_sources.items() 
                if source.is_available()]
    
    def create_source(self, source_type: str, **kwargs) -> FrameCaptureSource:
        if source_type == "obs":
            return OBSWebSocketCapture(**kwargs)
        elif source_type == "screen":
            return ScreenCapture(**kwargs)
        elif source_type == "rtmp":
            return RTMPStreamCapture(**kwargs)
        elif source_type == "webcam":
            return WebcamCapture(**kwargs)
        else:
            raise ValueError(f"Unknown source type: {source_type}")
    
    async def test_source(self, source: FrameCaptureSource, timeout: float = 5.0) -> bool:
        try:
            async with asyncio.timeout(timeout):
                async for frame in source.start_capture():
                    if frame is not None and frame.size > 0:
                        await source.stop_capture()
                        return True
                    break
        except Exception as e:
            logger.error(f"Source test failed: {e}")
            
        await source.stop_capture()
        return False