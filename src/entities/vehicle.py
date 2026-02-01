import pygame
import math
from typing import Tuple, Literal, List, Any, Optional
from src.config import *
from src.entities.traffic_light import TrafficLight
from src.entities.pedestrian import Pedestrian

# --- STANDARDIZED TYPES ---
Direction = Literal["N", "S", "E", "W"]

class Vehicle:
    """
    Autonomous Vehicle Agent with Integrated Decision Tree (IDT) logic.
    Priority: Life Safety > Traffic Rules > Operational Efficiency.
    """
    def __init__(self, start_pos: Tuple[int, int], direction_vector: Tuple[int, int], 
                 origin: Direction, is_emergency: bool = False) -> None: 
        # Spatial State
        self.x, self.y = float(start_pos[0]), float(start_pos[1])
        self.direction = direction_vector
        self.origin = origin
        self.is_emergency = is_emergency
        
        # Dimensions & Rect Initialization
        if self.direction[0] != 0: 
            self.width, self.height = 40, 20
        else:
            self.width, self.height = 20, 40
            
        self.rect: pygame.Rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        
        # Dynamics State
        self.current_speed: float = float(CAR_SPEED)
        self.target_speed: float = float(CAR_SPEED)
        self.stopped: bool = False
        
        # Safety & Recovery State
        self.patience: float = 0.0
        self.ignore_npc: bool = False
        
        # Performance Cache
        self._cached_sensor_rect: Optional[pygame.Rect] = None
        self._last_look_ahead: float = 0.0

    def move(self, traffic_light: Optional[TrafficLight], all_cars: List['Vehicle'], 
             pedestrians: List[Pedestrian], sim: Any) -> None:
        """
        Main update cycle. Executes perception, decision making, and actuation.
        
        Args:
            traffic_light: Current controller for the junction.
            all_cars: List of all active vehicle agents.
            pedestrians: List of all active pedestrian agents.
            sim: Reference to the main simulation context.
        """
        if not sim: return

        # 1. Perception & Layer Analysis
        v_ped = self._check_pedestrians(pedestrians)
        v_rules = self._check_traffic_rules(traffic_light, all_cars, sim)
        
        # 2. Velocity Arbitrator (Safety-First)
        self.target_speed = min(v_ped, v_rules)
        
        # 3. Decision Persistence Logic
        self._update_patience(v_ped, v_rules, pedestrians)
        
        # 4. Physical Actuation
        self._apply_dynamics()

    def _check_pedestrians(self, pedestrians: List[Pedestrian]) -> float:
        """
        Priority 1: NPC Safety. Calculations based on braking distance projection.
        Returns: safe_velocity (float).
        """
        if self.is_emergency or self.ignore_npc or not pedestrians:
            return float(CAR_SPEED)

        # Dynamic Sensor Projection (L = v * t_brake)
        look_ahead = max(50.0, self.current_speed * BRAKING_TIME * FPS * STOPPING_DISTANCE_BUFFER)
        scan_rect = self._get_optimized_sensor_rect(look_ahead)
        
        min_v = float(CAR_SPEED)
        for p in pedestrians:
            if p.done or p.state == "DOWN": continue
            
            # Layer Masking via Rect check
            if scan_rect.colliderect(p.rect.inflate(20, 20)):
                dx, dy = self.rect.centerx - p.x, self.rect.centery - p.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < SAFE_HALT_DISTANCE:
                    return 0.0 # Emergency Halt initiated
                
                # Dynamic Deceleration Zone
                yield_factor = (dist - SAFE_HALT_DISTANCE) / look_ahead
                min_v = min(min_v, CAR_SPEED * max(0.0, yield_factor))
        
        return float(min_v)

    def _check_traffic_rules(self, traffic_light: Optional[TrafficLight], 
                             all_cars: List['Vehicle'], sim: Any) -> float:
        """
        Priority 2: Regulatory compliance and Gridlock prevention.
        """
        # Edge Case: Missing Traffic Light Controller
        if not traffic_light and not self.is_emergency:
            return 0.0

        # 1. Signal Logic
        if not self.is_emergency and traffic_light:
            axis = "NS" if self.origin in ["N", "S"] else "EW"
            if traffic_light.get_color_state(axis) != COLOR_GREEN_ON:
                dist_to_sl = self._get_dist_to_stop_line()
                if 5 < dist_to_sl < 50: return 0.0
                
                dist_to_cw = self._get_dist_to_crosswalk_entrance()
                if 5 < dist_to_cw < 50: return 0.0

        # 2. FCFS Junction Reservation
        dist_to_sl = self._get_dist_to_stop_line()
        if -20 < dist_to_sl < 60:
            if self not in sim.junction_reservation:
                sim.junction_reservation.append(self)
            
            # Queue Management
            if self in sim.junction_reservation:
                if sim.junction_reservation.index(self) > 1:
                    return 0.0

        # 3. Exit Space Validation (Anti-Gridlock)
        if -10 < dist_to_sl < 20 and not self._is_exit_clear(all_cars):
            return 0.0

        # 4. Adaptive Cruise Control (Car Spacing)
        for other in all_cars:
            if other is self or other.origin != self.origin: continue
            dist = self._get_dist_between(self, other)
            if 0 < dist < 50:
                if self._would_stop_on_crosswalk(dist):
                    if self._get_dist_to_crosswalk_entrance() > 5: return 0.0
                return 0.0 

        if self._is_intersection_blocked(all_cars): return 0.0
        
        return float(CAR_SPEED)

    def _get_optimized_sensor_rect(self, length: float) -> pygame.Rect:
        """Caches and returns the sensor rectangle to avoid redundant allocations."""
        if self._cached_sensor_rect and self._last_look_ahead == length:
            return self._cached_sensor_rect
            
        self._last_look_ahead = length
        if self.direction[0] != 0:
            r = pygame.Rect(0, self.rect.y - SENSOR_WIDTH_PADDING, length, self.height + 2 * SENSOR_WIDTH_PADDING)
            if self.direction[0] > 0: r.left = self.rect.right + RAYCAST_MIN_DIST
            else: r.right = self.rect.left - RAYCAST_MIN_DIST
        else:
            r = pygame.Rect(self.rect.x - SENSOR_WIDTH_PADDING, 0, self.width + 2 * SENSOR_WIDTH_PADDING, length)
            if self.direction[1] > 0: r.top = self.rect.bottom + RAYCAST_MIN_DIST
            else: r.bottom = self.rect.top - RAYCAST_MIN_DIST
        
        self._cached_sensor_rect = r
        return r

    def _is_exit_clear(self, all_cars: List['Vehicle']) -> bool:
        """Verifies destination lane availability on the far side of the junction."""
        cx, cy = INTERSECTION_CENTER, INTERSECTION_CENTER
        rw = ROAD_WIDTH // 2
        
        # Projection zone logic
        if self.direction[0] == 1: # East
            exit_rect = pygame.Rect(cx + rw, self.rect.y, 60, self.height)
        elif self.direction[0] == -1: # West
            exit_rect = pygame.Rect(cx - rw - 60, self.rect.y, 60, self.height)
        elif self.direction[1] == 1: # South
            exit_rect = pygame.Rect(self.rect.x, cy + rw, self.width, 60)
        else: # North
            exit_rect = pygame.Rect(self.rect.x, cy - rw - 60, self.width, 60)
            
        # Collision check against exit zone
        for other in all_cars:
            if other is self: continue
            if other.rect.colliderect(exit_rect.inflate(10, 10)):
                return False
        return True

    def _is_light_red(self, traffic_light: Optional[TrafficLight]) -> bool:
        """Telemetry helper for visualization systems."""
        if self.is_emergency or not traffic_light: return False
        axis = "NS" if self.origin in ["N", "S"] else "EW"
        if traffic_light.get_color_state(axis) == COLOR_GREEN_ON: return False
        return -10 < self._get_dist_to_stop_line() < 100

    def _get_dist_to_stop_line(self) -> float:
        sl = STOP_LINES[self.origin]
        if self.origin == "N": return float(sl - self.rect.bottom)
        if self.origin == "S": return float(self.rect.top - sl)
        if self.origin == "E": return float(self.rect.left - sl)
        if self.origin == "W": return float(sl - self.rect.right)
        return 999.0

    def _get_dist_to_crosswalk_entrance(self) -> float:
        sl = STOP_LINES[self.origin]
        if self.origin == "N": return float((sl - CW_OFFSET) - self.rect.bottom)
        if self.origin == "S": return float(self.rect.top - (sl + CW_OFFSET))
        if self.origin == "E": return float(self.rect.left - (sl + CW_OFFSET))
        if self.origin == "W": return float((sl - CW_OFFSET) - self.rect.right)
        return 999.0

    def _would_stop_on_crosswalk(self, dist_to_car: float) -> bool:
        """Predicts stopping position to ensure crosswalk remains clear."""
        my_dist_sl = self._get_dist_to_stop_line()
        stop_pos_sl = my_dist_sl - dist_to_car
        return (CW_OFFSET - CW_WIDTH - 10) < stop_pos_sl < (CW_OFFSET + 10)

    def _get_dist_between(self, car1: 'Vehicle', car2: 'Vehicle') -> float:
        if self.origin == "N": return float(car2.rect.top - car1.rect.bottom)
        if self.origin == "S": return float(car1.rect.top - car2.rect.bottom)
        if self.origin == "W": return float(car2.rect.left - car1.rect.right)
        if self.origin == "E": return float(car1.rect.left - car2.rect.right)
        return -1.0

    def _is_intersection_blocked(self, all_cars: List['Vehicle']) -> bool:
        """Check for cross-traffic interference inside the junction box."""
        cx, rw = INTERSECTION_CENTER, ROAD_WIDTH // 2
        intersection = pygame.Rect(cx - rw, cx - rw, ROAD_WIDTH, ROAD_WIDTH)
        
        if not self.rect.inflate(30, 30).colliderect(intersection): return False
        if intersection.collidepoint(self.rect.center): return False
        
        for other in all_cars:
            if other is self: continue
            if other.rect.colliderect(intersection):
                is_parallel = (self.direction[0] != 0 and other.direction[0] != 0) or \
                              (self.direction[1] != 0 and other.direction[1] != 0)
                if not is_parallel: return True
        return False

    def _apply_dynamics(self) -> None: 
        """Integrates velocity and updates position with clamping."""
        # Speed Interpolation
        if self.current_speed < self.target_speed:
            self.current_speed = min(self.target_speed, self.current_speed + ACCELERATION_RATE)
        elif self.current_speed > self.target_speed:
            self.current_speed = max(self.target_speed, self.current_speed - DECELERATION_RATE)

        # Clamping and State Update
        if self.current_speed < 0.05:
            self.current_speed = 0.0
            self.stopped = True
        else:
            self.stopped = False
            self.x += self.direction[0] * self.current_speed
            self.y += self.direction[1] * self.current_speed
            self.rect.topleft = (int(self.x), int(self.y))

    def _update_patience(self, v_ped: float, v_rules: float, pedestrians: List[Pedestrian]) -> None: 
        """Logic for Deadlock Recovery (Ghosting stuck NPCs)."""
        if v_ped == 0.0 and v_rules > 0.0 and self.current_speed == 0:
            self.patience += 1.0 / FPS
        else:
            self.patience = max(0.0, self.patience - 0.5 / FPS)
            
        if self.patience > PATIENCE_THRESHOLD:
            self.ignore_npc = True
            
        if self.ignore_npc and not any(self.rect.inflate(10, 10).colliderect(p.rect) for p in pedestrians):
            self.ignore_npc = False
            self.patience = 0.0
