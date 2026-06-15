"""Video analysis: scene change detection and motion detection."""

import cv2
import numpy as np
from typing import List
from src.shared.video_analysis_protocol import VideoAnalysisProtocol
from src.shared.opencv_image_port import OpenCVImagePort
from src.shared.vision_models_vo import SceneChange, MotionEvent, BoundingBox, FilePath, SceneThreshold, MinArea


class VideoAnalysisAnalyzer(VideoAnalysisProtocol):
    """Analyze video for scene changes and motion events."""

    def __init__(self, opencv_port: OpenCVImagePort):
        self._opencv = opencv_port

    def detect_scenes(self, video_path: FilePath, threshold: SceneThreshold) -> List[SceneChange]:
        """Detect scene changes by comparing consecutive frame histograms."""
        cap = self._opencv.get_video_capture(video_path.value)
        if not cap.isOpened():
            return []

        fps = cap.get(cv2.CAP_PROP_FPS)
        scenes: List[SceneChange] = []
        prev_hist = None
        frame_idx = 0
        thresh_val = threshold.value if threshold else 30.0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Compute color histogram
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
            cv2.normalize(hist, hist)

            if prev_hist is not None:
                score = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                # Low correlation = scene change
                if score < (1.0 - thresh_val / 100.0):
                    timestamp = frame_idx / fps if fps > 0 else frame_idx
                    scenes.append(SceneChange(
                        timestamp=round(timestamp, 2),
                        score=round(1.0 - score, 4),
                    ))

            prev_hist = hist
            frame_idx += 1

        cap.release()
        return scenes

    def detect_motion(self, video_path: FilePath, min_area: MinArea) -> List[MotionEvent]:
        """Detect significant motion events using frame differencing."""
        cap = self._opencv.get_video_capture(video_path.value)
        if not cap.isOpened():
            return []

        fps = cap.get(cv2.CAP_PROP_FPS)
        events: List[MotionEvent] = []
        prev_gray = None
        frame_idx = 0
        min_area_val = min_area.value if min_area else 500

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if prev_gray is not None:
                delta = cv2.absdiff(prev_gray, gray)
                thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
                
                # Use standard 3x3 structuring element kernel instead of None to avoid type: ignore
                kernel = np.ones((3, 3), dtype=np.uint8)
                thresh = cv2.dilate(thresh, kernel, iterations=2)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if area < min_area_val:
                        continue

                    x, y, w, h = cv2.boundingRect(cnt)
                    timestamp = frame_idx / fps if fps > 0 else frame_idx
                    magnitude = area / (frame.shape[0] * frame.shape[1])

                    # Compute direction from moments
                    moments = cv2.moments(cnt)
                    direction = None
                    if moments["m00"] > 0:
                        cx = int(moments["m10"] / moments["m00"]) - x - w // 2
                        cy = int(moments["m01"] / moments["m00"]) - y - h // 2
                        direction = round(np.degrees(np.arctan2(cy, cx)) % 360, 1)

                    events.append(MotionEvent(
                        timestamp=round(timestamp, 2),
                        magnitude=round(magnitude, 6),
                        direction=direction,
                        region=BoundingBox(x=x, y=y, width=w, height=h),
                    ))

            prev_gray = gray
            frame_idx += 1

        cap.release()
        return events
