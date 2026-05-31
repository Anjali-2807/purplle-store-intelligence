# PROMPT: Write a pytest file to test the retail intelligence pipeline. It should test the CentroidTracker update logic with multiple bounding boxes, empty bounding boxes to verify disappeared tracking deregistration, and coordinate-to-zone mapping. Use the specified prompt header.
# CHANGES MADE: Added explicit assertions for unique visitor ID tracking, centroid calculations, and camera specific zone polygon routing.

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from pipeline.tracker import CentroidTracker
from pipeline.detect import StoreIntelligencePipeline

def test_centroid_tracker_registration():
    tracker = CentroidTracker(max_disappeared=2)
    
    # 1. Register a person
    rects = [(10, 10, 50, 50)] # centroid (30, 30)
    objects = tracker.update(rects)
    
    assert len(objects) == 1
    obj_id = list(objects.keys())[0]
    assert objects[obj_id][0] == 30
    assert objects[obj_id][1] == 30
    
    # 2. Track moves slightly
    rects_moved = [(15, 15, 55, 55)] # centroid (35, 35)
    objects_moved = tracker.update(rects_moved)
    
    assert len(objects_moved) == 1
    assert list(objects_moved.keys())[0] == obj_id
    assert objects_moved[obj_id][0] == 35
    
    # 3. Disappears (empty frame)
    objects_empty = tracker.update([])
    assert len(objects_empty) == 1
    assert tracker.disappeared[obj_id] == 1
    
    # 4. Exceeds max_disappeared (deregisters)
    objects_empty_again = tracker.update([])
    assert len(objects_empty_again) == 0
    assert obj_id not in tracker.objects

def test_coordinate_zone_mapping():
    pipeline = StoreIntelligencePipeline(store_id="STORE_BLR_002")
    
    # Test CAM_3 maps to Entry
    assert pipeline.map_coordinates_to_zone("CAM_3", (100, 100)) == "Entry"
    
    # Test CAM_5 maps to Cash Counter
    assert pipeline.map_coordinates_to_zone("CAM_5", (500, 500)) == "CASH COUNTER"
    
    # Test CAM_1 maps to skincare shelves based on coordinates
    assert pipeline.map_coordinates_to_zone("CAM_1", (200, 100)) == "The Face Shop"
    assert pipeline.map_coordinates_to_zone("CAM_1", (800, 100)) == "Good Vibes"
    assert pipeline.map_coordinates_to_zone("CAM_1", (1500, 100)) == "Minimalist"
    
    # Test CAM_2 maps to makeup shelves
    assert pipeline.map_coordinates_to_zone("CAM_2", (200, 100)) == "Maybelline"
    assert pipeline.map_coordinates_to_zone("CAM_2", (800, 100)) == "Lakme"
    assert pipeline.map_coordinates_to_zone("CAM_2", (1500, 100)) == "Alps Goodness"
