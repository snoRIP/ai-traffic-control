import pygame
import random
import sys
import numpy as np
import time
from typing import List, Dict, Literal

from src.config import *
from src.entities.traffic_light import TrafficLight
from src.entities.vehicle import Vehicle
from src.entities.pedestrian import Pedestrian
from src.entities.agent import DQNAgent
from src.visualizer import VisualizationManager

class TrafficSimulation:
    """
    Main Simulation Kernel. Coordinates DRL Agent, Entity Dynamics, 
    and Visualization. Includes Production Health Checks.
    """
    def __init__(self, use_drl: bool = True) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.running: bool = True
        self.frame_count: int = 0
        
        # Core Systems
        self.viz = VisualizationManager(self.screen)
        self.traffic_light = TrafficLight()
        self.cars: List[Vehicle] = []
        self.pedestrians: List[Pedestrian] = []
        self.junction_reservation: List[Vehicle] = []
        
        # Metrics & Health
        self.total_flow_samples = 0
        self.summed_flow_efficiency = 0.0
        self.lifetime_flow = 100.0
        self.last_health_check = time.time()
        self.total_reward = 0
        
        # AI Intelligence
        self.use_drl = use_drl
        self.agent = DQNAgent(state_size=3, action_size=2)
        self.last_state = np.zeros((1, 3))
        self.last_action = 0

    def handle_events(self) -> None:
        """Process user input and system signals."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Interactive UI: Emergency Trigger
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(EMERGENCY_BUTTON_RECT).collidepoint(event.pos):
                    self._spawn_emergency_vehicle()

    def _spawn_emergency_vehicle(self) -> None:
        """Force-spawns an Ambulance from a random lane."""
        origin = random.choice(list(LANE_POSITIONS.keys()))
        start_x, start_y, direction = LANE_POSITIONS[origin]
        self.cars.append(Vehicle(start_pos=(start_x, start_y), 
                               direction_vector=direction, 
                               origin=origin, is_emergency=True))
        self.viz.add_event(f"USER: Emergency Spawn [{origin}]")

    def spawn_entities(self) -> None:
        """Periodic entity generation logic with density control."""
        # 1. Vehicles
        if self.frame_count % SPAWN_RATE == 0:
            origin = random.choice(list(LANE_POSITIONS.keys()))
            sx, sy, direction = LANE_POSITIONS[origin]
            
            # Spawn safety validation
            spawn_rect = pygame.Rect(sx, sy, 40, 40).inflate(SAFE_DISTANCE, SAFE_DISTANCE)
            if not any(c.rect.colliderect(spawn_rect) for c in self.cars):
                is_emer = random.random() < EMERGENCY_CHANCE
                self.cars.append(Vehicle((sx, sy), direction, origin, is_emer))

        # 2. Pedestrians
        if self.frame_count % PEDESTRIAN_SPAWN_RATE == 0:
            self._spawn_pedestrian()

    def _spawn_pedestrian(self) -> None:
        corners = [CORNER_TL, CORNER_TR, CORNER_BL, CORNER_BR]
        base_start = random.choice(corners)
        jx, jy = random.uniform(-15, 15), random.uniform(-15, 15)
        
        targets = {
            CORNER_TL: [(CORNER_TR, "EW", "NS"), (CORNER_BL, "NS", "EW")],
            CORNER_TR: [(CORNER_TL, "EW", "NS"), (CORNER_BR, "NS", "EW")],
            CORNER_BL: [(CORNER_TL, "NS", "EW"), (CORNER_BR, "EW", "NS")],
            CORNER_BR: [(CORNER_TR, "NS", "EW"), (CORNER_BL, "EW", "NS")]
        }
        target_data = random.choice(targets[base_start])
        start_pos = (base_start[0] + jx, base_start[1] + jy)
        target_pos = (target_data[0][0] + jx, target_data[0][1] + jy)
        
        self.pedestrians.append(Pedestrian(start_pos, target_pos, target_data[1], target_data[2]))

    def update(self) -> None:
        """System update loop: Perception -> Logic -> Physics."""
        self.frame_count += 1
        
        # 1. State Analysis
        queues = self._calculate_queues()
        emergency_data = self._check_emergency_vehicles()
        self._update_flow_metrics()

        # 2. Control Tier
        if self.use_drl and not emergency_data['present'] and self.frame_count % 60 == 0:
            self._execute_ai_control(queues)
        
        # 3. Regulatory Logic
        if emergency_data['present']:
            self.traffic_light.set_emergency_mode(True, emergency_data['origin'])
        else:
            self.traffic_light.set_emergency_mode(False)
            if not self.use_drl or "YELLOW" in self.traffic_light.state:
                self.traffic_light.update(queues)
            else:
                self.traffic_light.timer += 1

        # 4. Entity Dynamics
        self._update_entities()
        
        # 5. Production Health Check
        if time.time() - self.last_health_check > 5.0:
            self._run_health_check()

    def _calculate_queues(self) -> Dict[str, int]:
        q = {'NS': 0, 'EW': 0}
        for c in self.cars:
            if c.stopped:
                if c.origin in ["N", "S"]: q['NS'] += 1
                else: q['EW'] += 1
        return q

    def _check_emergency_vehicles(self) -> Dict[str, Any]:
        for c in self.cars:
            if c.is_emergency: return {'present': True, 'origin': c.origin}
        return {'present': False, 'origin': None}

    def _update_flow_metrics(self) -> None:
        moving = sum(1 for c in self.cars if not c.stopped)
        current_flow = (moving / max(1, len(self.cars))) * 100
        self.summed_flow_efficiency += current_flow
        self.total_flow_samples += 1
        self.lifetime_flow = self.summed_flow_efficiency / self.total_flow_samples

    def _execute_ai_control(self, queues: Dict[str, int]) -> None:
        state = np.array([[min(queues['NS']/20.0, 1.0), min(queues['EW']/20.0, 1.0), 
                          0 if "NS" in self.traffic_light.state else 1]])
        reward = (sum(1 for c in self.cars if not c.stopped) / max(1, len(self.cars))) - 0.5 * sum(queues.values())
        self.agent.remember(self.last_state, self.last_action, reward, state, False)
        self.agent.train()
        
        action = self.agent.act(state)
        if action == 1: self.viz.add_event("AI: Optimizing Phase")
        self.traffic_light.apply_action(action)
        self.last_state, self.last_action = state, action

    def _update_entities(self) -> None:
        # Cache rect for intersection check
        cx, rw = INTERSECTION_CENTER, ROAD_WIDTH // 2
        box = pygame.Rect(cx - rw, cx - rw, ROAD_WIDTH, ROAD_WIDTH).inflate(20, 20)
        
        for p in self.pedestrians: p.update(self.traffic_light, self.pedestrians, self.cars)
        self.pedestrians = [p for p in self.pedestrians if not p.done]
        
        # Filter junction queue
        self.junction_reservation = [v for v in self.junction_reservation if v in self.cars and v.rect.colliderect(box)]

        old_count = len(self.cars)
        for c in self.cars: c.move(self.traffic_light, self.cars, self.pedestrians, self)
        
        self.cars = [c for c in self.cars if -100 <= c.x <= WIDTH + 100 and -100 <= c.y <= HEIGHT + 100]
        if old_count > len(self.cars): self.viz.avoided_count += (old_count - len(self.cars))

    def _run_health_check(self) -> None:
        """Automated system audit for production stability."""
        fps = int(self.clock.get_fps())
        perf_ms = self.clock.get_rawtime()
        
        # Check for static deadlocks (not moving for > 10s)
        stuck_agents = sum(1 for c in self.cars if c.stopped and c.patience > 5.0)
        
        status = "CRITICAL" if fps < 30 else "STABLE"
        print(f"[HEALTH] {status} | FPS: {fps} | Latency: {perf_ms}ms | Agents: {len(self.cars)} | Stuck: {stuck_agents}")
        self.last_health_check = time.time()

    def draw(self) -> None:
        self.viz.render(self)
        pygame.display.flip()

    def run(self) -> None:
        try:
            while self.running:
                self.clock.tick(FPS)
                self.handle_events()
                self.spawn_entities()
                self.update()
                self.draw()
        except Exception as e:
            print(f"[FATAL] Production Failure: {e}")
        finally:
            pygame.quit()
