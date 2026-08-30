import cv2
import numpy

from modules.shared.src.contract_video_analysis_protocol import (
    VideoAnalysisProtocol,
)
from modules.shared.src.taxonomy_vision_constant import (
    DILATION_ITERATIONS,
    DILATION_KERNEL_SIZE,
    GAUSSIAN_BLUR_KERNEL,
    HIST_HUE_BINS,
    HIST_SAT_BINS,
    MIN_MOTION_AREA,
    MOTION_DIFF_THRESHOLD,
    MOTION_MAX_PIXEL_VALUE,
    SCENE_THRESHOLD,
)
from modules.shared.src.taxonomy_vision_event import (
    MotionEvent,
    SceneChange,
)
from modules.shared.src.taxonomy_vision_vo import (
    FilePath,
    MinArea,
    MotionDirection,
    MotionMagnitude,
    SceneThreshold,
    SimilarityScore,
    Timestamp,
)
from modules.shared.src.utility_opencv_ops import (
    apply_dilate,
    apply_gaussian_blur,
    apply_threshold,
    compare_histograms,
    compute_abs_diff,
    compute_histogram_hsv,
    compute_moments,
    find_contours,
    get_bounding_box,
    get_contour_area,
    open_video_capture,
    to_grayscale,
)


class VideoAnalysisAnalyzer(VideoAnalysisProtocol):
    """Analyze video for scene changes and motion events."""

    def __init__(self):
        # No instance state required; all methods are stateless and operate on video files.
        pass

    def detect_scenes(
        self, video_path: FilePath, threshold: SceneThreshold
    ) -> list[SceneChange]:
        """Detect scene changes by comparing consecutive frame histograms."""
        cap = open_video_capture(video_path)
        if not cap.isOpened():
            return []

        fps = cap.get(cv2.CAP_PROP_FPS)
        scenes: list[SceneChange] = []
        prev_hist = None
        frame_idx = 0
        thresh_val = threshold.value if threshold else SCENE_THRESHOLD

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            hist = compute_histogram_hsv(frame, HIST_HUE_BINS, HIST_SAT_BINS)

            if prev_hist is not None:
                score = compare_histograms(prev_hist, hist)
                # Low correlation = scene change
                if score < (1.0 - thresh_val / 100.0):
                    timestamp = frame_idx / fps if fps > 0 else frame_idx
                    scenes.append(
                        SceneChange(
                            timestamp=Timestamp(value=round(timestamp, 2)),
                            score=SimilarityScore(value=round(1.0 - score, 4)),
                        )
                    )

            prev_hist = hist
            frame_idx += 1

        cap.release()
        return scenes

    def _compute_motion_direction(
        self, cnt, x: int, y: int, w: int, h: int
    ) -> float | None:
        """Compute motion direction in degrees from contour moments, or None if indeterminate."""
        moments = compute_moments(cnt)
        if moments["m00"] <= 0:
            return None
        cx = int(moments["m10"] / moments["m00"]) - x - w // 2
        cy = int(moments["m01"] / moments["m00"]) - y - h // 2
        return round(numpy.degrees(numpy.arctan2(cy, cx)) % 360, 1)

    def _find_motion_events(
        self,
        thresh,
        frame,
        frame_idx: int,
        fps: float,
        min_area_val: float,
    ) -> list[MotionEvent]:
        """Extract motion events from a threshold image for a single frame pair."""
        contours = find_contours(thresh)
        frame_area = frame.shape[0] * frame.shape[1]
        timestamp = frame_idx / fps if fps > 0 else frame_idx
        events: list[MotionEvent] = []

        for cnt in contours:
            area = get_contour_area(cnt)
            if area < min_area_val:
                continue

            box = get_bounding_box(cnt)
            magnitude = area / frame_area
            direction = self._compute_motion_direction(
                cnt, box.x, box.y, box.width, box.height
            )

            events.append(
                MotionEvent(
                    timestamp=Timestamp(value=round(timestamp, 2)),
                    magnitude=MotionMagnitude(value=round(magnitude, 6)),
                    direction=(
                        MotionDirection(value=direction)
                        if direction is not None
                        else None
                    ),
                    region=box,
                )
            )

        return events

    def detect_motion(
        self, video_path: FilePath, min_area: MinArea
    ) -> list[MotionEvent]:
        """Detect significant motion events using frame differencing."""
        cap = open_video_capture(video_path)
        if not cap.isOpened():
            return []

        fps = cap.get(cv2.CAP_PROP_FPS)
        events: list[MotionEvent] = []
        prev_gray = None
        frame_idx = 0
        min_area_val = min_area.value if min_area else MIN_MOTION_AREA

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = apply_gaussian_blur(to_grayscale(frame), GAUSSIAN_BLUR_KERNEL)

            if prev_gray is not None:
                delta = compute_abs_diff(prev_gray, gray)
                thresh = apply_threshold(
                    delta,
                    MOTION_DIFF_THRESHOLD,
                    MOTION_MAX_PIXEL_VALUE,
                )
                thresh = apply_dilate(
                    thresh,
                    DILATION_KERNEL_SIZE,
                    DILATION_ITERATIONS,
                )
                events.extend(
                    self._find_motion_events(
                        thresh, frame, frame_idx, fps, min_area_val
                    )
                )

            prev_gray = gray
            frame_idx += 1

        cap.release()
        return events
