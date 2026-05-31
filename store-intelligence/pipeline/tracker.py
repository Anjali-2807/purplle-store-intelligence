import numpy as np
import uuid

class CentroidTracker:
    def __init__(self, max_disappeared=50):
        self.next_object_id = 0
        self.objects = {}
        self.disappeared = {}
        self.max_disappeared = max_disappeared

    def register(self, centroid):
        obj_id = f"VIS_{uuid.uuid4().hex[:6]}"
        self.objects[obj_id] = centroid
        self.disappeared[obj_id] = 0
        return obj_id

    def deregister(self, obj_id):
        if obj_id in self.objects:
            del self.objects[obj_id]
        if obj_id in self.disappeared:
            del self.disappeared[obj_id]

    def update(self, rects):
        # rects: list of bounding boxes (x1, y1, x2, y2)
        if len(rects) == 0:
            for obj_id in list(self.disappeared.keys()):
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] >= self.max_disappeared:
                    self.deregister(obj_id)
            return self.objects

        input_centroids = np.zeros((len(rects), 2), dtype="int")
        for i, (startX, startY, endX, endY) in enumerate(rects):
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            input_centroids[i] = (cX, cY)

        if len(self.objects) == 0:
            for i in range(len(input_centroids)):
                self.register(input_centroids[i])
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            # Distance matrix between active objects and new input centroids
            D = np.linalg.norm(np.array(object_centroids)[:, np.newaxis] - input_centroids, axis=2)

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                obj_id = object_ids[row]
                self.objects[obj_id] = input_centroids[col]
                self.disappeared[obj_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)

            for row in unused_rows:
                obj_id = object_ids[row]
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] >= self.max_disappeared:
                    self.deregister(obj_id)

            for col in unused_cols:
                self.register(input_centroids[col])

        return self.objects


class MultiCameraTracker:
    def __init__(self):
        self.camera_trackers = {}
        # Mapping for cross-camera Re-ID handoff (visitor_id mapping)
        # Keeps track of recently disappeared visitor_ids and their last location
        self.recent_exits = []

    def get_tracker(self, camera_id):
        if camera_id not in self.camera_trackers:
            self.camera_trackers[camera_id] = CentroidTracker()
        return self.camera_trackers[camera_id]

    def register_transition(self, visitor_id, camera_id, zone_id, timestamp):
        # Track active cross-camera movement
        pass

    def classify_staff_by_uniform(self, frame_crop) -> bool:
        # Staff uniform in Purplle stores is solid black clothing.
        # We can analyze the average color of the person's upper body / clothing crop.
        if frame_crop is None or frame_crop.size == 0:
            return False
            
        try:
            # Convert to HSV color space
            import cv2
            hsv = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2HSV)
            # Black clothing color range in HSV: low value (brightness < 50)
            # We check the percentage of dark pixels in the crop
            v_channel = hsv[:, :, 2]
            dark_pixels = np.sum(v_channel < 55)
            total_pixels = v_channel.size
            dark_ratio = dark_pixels / total_pixels if total_pixels > 0 else 0.0
            
            # If more than 70% of the bounding box crop is dark/black, they represent staff!
            return dark_ratio > 0.70
        except Exception:
            # Fallback
            return False
