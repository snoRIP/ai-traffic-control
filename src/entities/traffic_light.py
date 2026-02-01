import pygame
from typing import Dict, Literal, Optional
from src.config import *
from src.graphics import GraphicsRenderer

Axis = Literal["NS", "EW"]
LightState = Literal["NS_GREEN", "NS_YELLOW", "EW_GREEN", "EW_YELLOW"]

class TrafficLight:
    """
    Manages the state and logic of traffic lights.
    Visuals are handled by GraphicsRenderer, but this class calculates *where* they go.
    """

    def __init__(self) -> None:
        self.state: LightState = "NS_GREEN"
        self.timer: int = 0
        self.emergency_mode: bool = False

    def update(self, queues: Dict[Axis, int]) -> None:
        if self.emergency_mode:
            return

        self.timer += 1
        
        if self.state == "NS_GREEN":
            if self.timer > MIN_GREEN_TIME:
                if queues['EW'] > queues['NS']:
                    self.state = "NS_YELLOW"
                    self.timer = 0
        
        elif self.state == "NS_YELLOW":
            if self.timer >= YELLOW_TIME:
                self.state = "EW_GREEN"
                self.timer = 0
                
        elif self.state == "EW_GREEN":
            if self.timer > MIN_GREEN_TIME:
                if queues['NS'] > queues['EW']:
                    self.state = "EW_YELLOW"
                    self.timer = 0
                    
        elif self.state == "EW_YELLOW":
            if self.timer >= YELLOW_TIME:
                self.state = "NS_GREEN"
                self.timer = 0

    def get_color_state(self, axis: Axis) -> Tuple[int, int, int]:
        """Returns the RGB color constant for the given axis based on state."""
        if axis == "NS":
            if self.state == "NS_GREEN": return COLOR_GREEN_ON
            if self.state == "NS_YELLOW": return COLOR_YELLOW_ON
            return COLOR_RED_ON
        elif axis == "EW":
            if self.state == "EW_GREEN": return COLOR_GREEN_ON
            if self.state == "EW_YELLOW": return COLOR_YELLOW_ON
            return COLOR_RED_ON
        return COLOR_RED_ON

    def set_emergency_mode(self, active: bool, direction: Optional[str] = None) -> None:
        self.emergency_mode = active
        if active and direction:
            if direction in ["N", "S"]:
                self.state = "NS_GREEN"
            else:
                self.state = "EW_GREEN"
            self.timer = 0 

    def apply_action(self, action: int) -> None:
        """
        Applies an action from the RL agent.
        Action 0: Stay (keep current Green)
        Action 1: Switch (trigger Yellow then next Green)
        """
        if self.emergency_mode or self.timer < MIN_GREEN_TIME:
            return

        if action == 1:
            if self.state == "NS_GREEN":
                self.state = "NS_YELLOW"
                self.timer = 0
            elif self.state == "EW_GREEN":
                self.state = "EW_YELLOW"
                self.timer = 0

    def draw(self, renderer: GraphicsRenderer) -> None:
        """
        Delegates drawing of 4 distinct lights to the renderer.
        """
        cx = INTERSECTION_CENTER
        rw = ROAD_WIDTH // 2
        margin = 10 # Offset from road edge

        # North Facing Light (Controls Southbound traffic coming from top)
        # Position: Top-Left corner of intersection, facing Right (conceptually)
        # Actually, standard US placement: Far right corner or suspended.
        # Let's place them on the corners "stopping" the traffic.
        
        ns_col = self.get_color_state("NS")
        ew_col = self.get_color_state("EW")

        # 1. North Light (For traffic coming from North/Top) - Placed at Top-Left of intersection
        renderer.draw_traffic_light(cx - rw - 30, cx - rw - 70, ns_col, horizontal=False)

        # 2. South Light (For traffic coming from South/Bottom) - Placed at Bottom-Right
        renderer.draw_traffic_light(cx + rw + 10, cx + rw + 10, ns_col, horizontal=False)

        # 3. West Light (For traffic coming from West/Left) - Placed at Bottom-Left
        renderer.draw_traffic_light(cx - rw - 70, cx + rw + 10, ew_col, horizontal=True)

        # 4. East Light (For traffic coming from East/Right) - Placed at Top-Right
        renderer.draw_traffic_light(cx + rw + 10, cx - rw - 30, ew_col, horizontal=True)