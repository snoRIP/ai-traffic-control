import pygame
import math
from typing import Tuple, Literal, List, Any, Optional
from src.config import *
from src.entities.traffic_light import TrafficLight

class Pedestrian:
    """
    Pedestrian Agent with autonomous avoidance and state-based navigation.
    """
    def __init__(self, start_pos: Tuple[int, int], target_pos: Tuple[int, int], 
                 crossing_axis: Literal["NS", "EW"], 
                 control_axis: Literal["NS", "EW"]) -> None:
        # Physical State
        self.x, self.y = float(start_pos[0]), float(start_pos[1])
        self.target_x, self.target_y = float(target_pos[0]), float(target_pos[1])
        self.crossing_axis = crossing_axis
        self.control_axis = control_axis
        
        self.radius = 8
        self.rect = pygame.Rect(int(self.x) - self.radius, int(self.y) - self.radius, self.radius*2, self.radius*2)
        
        # Operational State
        self.walking = False
        self.done = False
        self.state: Literal["WALKING", "DOWN"] = "WALKING"
        self.down_timer: float = 0.0
        
        # Vector Initialization
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        self.dir_x = dx / dist if dist > 0 else 0
        self.dir_y = dy / dist if dist > 0 else 0

    def hit(self) -> None:
        """Transitions NPC to 'DOWN' state upon critical force impact."""
        if self.state != "DOWN":
            self.state = "DOWN"
            self.down_timer = float(pygame.time.get_ticks())

    def update(self, traffic_light: Optional[TrafficLight], 
               all_peds: List['Pedestrian'], all_cars: List[Any]) -> None:
        """
        Agent logic cycle. Handles signal waiting, movement, and avoidance.
        """
        if self.done: return

        # 1. Damage Handling
        if self.state == "DOWN":
            if (pygame.time.get_ticks() - self.down_timer) / 1000.0 > DESPAWN_TIME:
                self.done = True
            return

        # 2. Signal Compliance
        if not self.walking and traffic_light:
            if traffic_light.get_color_state(self.control_axis) == COLOR_RED_ON:
                self.walking = True
        
        # 3. Motion Integration
        if self.walking:
            mv_x = self.dir_x * PEDESTRIAN_SPEED
            mv_y = self.dir_y * PEDESTRIAN_SPEED
            
            # Simple Navigation check
            self.x += mv_x
            self.y += mv_y
            self.rect.center = (int(self.x), int(self.y))
            
            # Destination Arrival Validation
            if math.hypot(self.target_x - self.x, self.target_y - self.y) < 10:
                self.done = True

    def draw(self, surface: pygame.Surface) -> None:
        """Visual representation placeholder (Graphics handled by VisualizationManager)."""
        pass
