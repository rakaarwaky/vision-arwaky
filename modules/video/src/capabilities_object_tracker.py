import cv2

from modules.shared.src.contract_object_tracking_protocol import (
    ObjectTrackingProtocol,
)
from modules.shared.src.taxonomy_vision_constant import MAX_TRACK_FRAMES
from modules.shared.src.taxonomy_vision_vo import (
    BoundingBox,
    FilePath,
    MaxFrames,
)
from modules.shared.src.utility_opencv_ops import open_video_capture


class ObjectTrackingTracker(ObjectTrackingProtocol):
    """Track objects through video frames using OpenCV trackers."""

    def __init__(self):
        # No instance state required; tracker instances are created on demand per call.
        pass

    def _create_tracker(self):
        """Helper to dynamically construct the OpenCV tracker to avoid complexity and mypy issues."""
        try:
            csrt_creator = getattr(cv2, "TrackerCSRT_create", None)
            if csrt_creator is not None:
                return csrt_creator()

            legacy = getattr(cv2, "legacy", None)
            if legacy is not None:
                legacy_csrt_creator = getattr(legacy, "TrackerCSRT_create", None)
                if legacy_csrt_creator is not None:
                    return legacy_csrt_creator()
        except (AttributeError, RuntimeError, OSError):
            pass

        try:
            kcf_creator = getattr(cv2, "TrackerKCF_create", None)
            if kcf_creator is not None:
                return kcf_creator()

            legacy = getattr(cv2, "legacy", None)
            if legacy is not None:
                legacy_kcf_creator = getattr(legacy, "TrackerKCF_create", None)
                if legacy_kcf_creator is not None:
                    return legacy_kcf_creator()
        except (AttributeError, RuntimeError, OSError):
            pass

        return None

    def track_object(
        self,
        video_path: FilePath,
        initial_box: BoundingBox,
        max_frames: MaxFrames,
    ) -> list[BoundingBox]:
        """Track an object starting from an initial bounding box."""
        cap = open_video_capture(video_path)
        if not cap.isOpened():
            return []

        # Read first frame
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return []

        # Initialize tracker dynamically to avoid static mypy type ignores
        tracker = self._create_tracker()

        if tracker is None:
            cap.release()
            return []

        bbox_tuple = (
            initial_box.x,
            initial_box.y,
            initial_box.width,
            initial_box.height,
        )
        ok = tracker.init(frame, bbox_tuple)

        # OpenCV 4.x init returns None on success, not True
        if ok is False:
            cap.release()
            return []

        boxes: list[BoundingBox] = [initial_box]
        frame_count = 0
        max_frames_val = max_frames.value if max_frames else MAX_TRACK_FRAMES

        while frame_count < max_frames_val:
            ret, frame = cap.read()
            if not ret:
                break

            ok, bbox = tracker.update(frame)
            if ok:
                x, y, w, h = [int(v) for v in bbox]
                boxes.append(BoundingBox(x=x, y=y, width=w, height=h))
            else:
                # Lost tracking — stop
                break

            frame_count += 1

        cap.release()
        return boxes
