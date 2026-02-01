from typing import Tuple, Dict

# Screen Dimensions
WIDTH: int = 800
HEIGHT: int = 800
CAPTION: str = "AI Traffic Control System v2.3 - Precise Crosswalks"

# Physics & Gameplay
FPS: int = 60
CAR_SPEED: int = 3
PEDESTRIAN_SPEED: float = 1.0 
SPAWN_RATE: int = 150        
PEDESTRIAN_SPAWN_RATE: int = 180
SAFE_DISTANCE: int = 45     
EMERGENCY_CHANCE: float = 0.05

# Traffic Light Timings
MIN_GREEN_TIME: int = 240   
YELLOW_TIME: int = 90       

# Colors
RED: Tuple[int, int, int] = (255, 0, 0)
COLOR_GRASS: Tuple[int, int, int] = (30, 100, 30)
COLOR_ROAD: Tuple[int, int, int] = (50, 50, 50)
COLOR_MARKING: Tuple[int, int, int] = (200, 200, 200)
COLOR_STOP_LINE: Tuple[int, int, int] = (255, 255, 255)
COLOR_SIDEWALK: Tuple[int, int, int] = (90, 90, 90)

# Lights
COLOR_RED_ON: Tuple[int, int, int] = (255, 0, 0)
COLOR_RED_OFF: Tuple[int, int, int] = (100, 0, 0)
COLOR_YELLOW_ON: Tuple[int, int, int] = (255, 200, 0)
COLOR_YELLOW_OFF: Tuple[int, int, int] = (100, 80, 0)
COLOR_GREEN_ON: Tuple[int, int, int] = (0, 255, 0)
COLOR_GREEN_OFF: Tuple[int, int, int] = (0, 80, 0)
COLOR_POLE: Tuple[int, int, int] = (20, 20, 20)

# Entities
COLOR_CAR_BODY: Tuple[int, int, int] = (70, 130, 180)
COLOR_CAR_EMERGENCY: Tuple[int, int, int] = (220, 20, 60)
COLOR_PEDESTRIAN_HEAD: Tuple[int, int, int] = (255, 220, 180) 
COLOR_PEDESTRIAN_SHIRT: Tuple[int, int, int] = (50, 50, 200) 
COLOR_PEDESTRIAN_SHOULDERS: Tuple[int, int, int] = (40, 40, 150)
COLOR_TEXT: Tuple[int, int, int] = (255, 255, 255)

# Dimensions
LANE_WIDTH: int = 60
ROAD_WIDTH: int = LANE_WIDTH * 2 
INTERSECTION_CENTER: int = WIDTH // 2
OFFSET = LANE_WIDTH // 2

# Directions
NORTH_DIR: Tuple[int, int] = (0, -1)
SOUTH_DIR: Tuple[int, int] = (0, 1)
EAST_DIR: Tuple[int, int] = (1, 0)
WEST_DIR: Tuple[int, int] = (-1, 0)

LANE_POSITIONS: Dict[str, Tuple[int, int, Tuple[int, int]]] = {
    "N": (INTERSECTION_CENTER - OFFSET, -50, SOUTH_DIR),      
    "S": (INTERSECTION_CENTER + OFFSET, HEIGHT + 50, NORTH_DIR), 
    "E": (WIDTH + 50, INTERSECTION_CENTER - OFFSET, WEST_DIR),   
    "W": (-50, INTERSECTION_CENTER + OFFSET, EAST_DIR)        
}

STOP_MARGIN = ROAD_WIDTH // 2 + 20
STOP_LINES: Dict[str, int] = {
    "N": INTERSECTION_CENTER - STOP_MARGIN, 
    "S": INTERSECTION_CENTER + STOP_MARGIN,
    "E": INTERSECTION_CENTER + STOP_MARGIN,
    "W": INTERSECTION_CENTER - STOP_MARGIN
}

# Crosswalks
# "60 pixels" BEHIND the stop line (closer than previous 140).
CW_OFFSET = 60 
CW_WIDTH = 40

# Deadlock Recovery & Physics
PATIENCE_THRESHOLD: float = 3.0       
COLLISION_FORCE_THRESHOLD: float = 2.0 
RAYCAST_MIN_DIST: float = 12.0        
DESPAWN_TIME: float = 1.0             

# Autonomous Driving Physics
BRAKING_TIME: float = 1.5             # Time in seconds to come to a full stop
ACCELERATION_RATE: float = 0.1        # Speed increase per frame
DECELERATION_RATE: float = 0.15       # Speed decrease per frame
SENSOR_WIDTH_PADDING: int = 30        # Side awareness (peripheral vision)
SAFE_HALT_DISTANCE: float = 40.0      # ~2.0m scaled distance for emergency stop
STOPPING_DISTANCE_BUFFER: float = 1.2 # Safety multiplier for stopping distance

# Emergency Button
EMERGENCY_BUTTON_RECT = (WIDTH - 210, HEIGHT - 60, 200, 50)

# Key Coordinates for Pedestrians (Start Points)
# ALIGNMENT FIX:
# The path must align with the CENTER of the crosswalk.
# Path Position = IntersectionCenter - StopMargin - CW_OFFSET + (CW_Width / 2)
# Distance from Center = StopMargin + CW_OFFSET - (CW_Width / 2)

ALIGNMENT_DIST = STOP_MARGIN + CW_OFFSET - (CW_WIDTH // 2)

CORNER_TL = (INTERSECTION_CENTER - ALIGNMENT_DIST, INTERSECTION_CENTER - ALIGNMENT_DIST)
CORNER_TR = (INTERSECTION_CENTER + ALIGNMENT_DIST, INTERSECTION_CENTER - ALIGNMENT_DIST)
CORNER_BL = (INTERSECTION_CENTER - ALIGNMENT_DIST, INTERSECTION_CENTER + ALIGNMENT_DIST)
CORNER_BR = (INTERSECTION_CENTER + ALIGNMENT_DIST, INTERSECTION_CENTER + ALIGNMENT_DIST)
