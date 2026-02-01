import pygame
import math
import time
from collections import deque
from typing import List, Tuple, Dict, Any, Optional
from src.config import *

# --- CYBER-CITY NOCTURNE PALETTE ---
NEON_CYAN = (0, 255, 255)
NEON_GREEN = (57, 255, 20)
NEON_FUCHSIA = (255, 0, 255)
NEON_ORANGE = (255, 165, 0)
NEON_RED = (255, 20, 60)
DEEP_SPACE = (10, 10, 20)
ASPHALT_NIGHT = (25, 25, 35)
SIDEWALK_GLOW = (40, 40, 60)

class VisualizationManager:
    """
    Principal Visualization Engine for Autonomous Traffic Simulation.
    Handles multi-layered debug rendering, HUD analytics, and agent telemetry.
    """
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_main = pygame.font.SysFont("Consolas", 14)
        self.font_hud = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_logo = pygame.font.SysFont("Consolas", 24, bold=True)
        
        # Performance Tracking
        self.start_time = time.time()
        
        # Event Log
        self.event_log = deque(maxlen=8)
        self.collision_count = 0
        self.avoided_count = 0
        
        # Inspector State
        self.hovered_agent = None

    def add_event(self, message: str):
        timestamp = time.strftime("%M:%S", time.gmtime(time.time() - self.start_time))
        self.event_log.append(f"[{timestamp}] {message}")

    def render(self, sim):
        """Main rendering pipeline."""
        self.screen.fill(DEEP_SPACE)
        self._draw_infrastructure()
        
        # Agent Layers
        for car in sim.cars:
            self._draw_car_perception(car, sim.pedestrians, sim.traffic_light)
            self._draw_agent_vectors(car)
            self._draw_entity_core(car, NEON_CYAN if not car.is_emergency else NEON_RED)

        for p in sim.pedestrians:
            self._draw_pedestrian_perception(p, sim.cars)
            self._draw_agent_vectors(p)
            self._draw_entity_core_ped(p, NEON_GREEN)

        self._draw_traffic_lights(sim.traffic_light)
        self._draw_hud(sim)
        self._draw_emergency_button(sim)
        self._handle_inspector(sim)

    def _draw_emergency_button(self, sim):
        """Renders the manual emergency spawn button."""
        bx, by, bw, bh = EMERGENCY_BUTTON_RECT
        is_active = any(c.is_emergency for c in sim.cars)
        color = NEON_RED if is_active else NEON_CYAN
        
        # Glow when active emergency vehicle on screen
        if is_active:
            for i in range(1, 4):
                pygame.draw.rect(self.screen, (*NEON_RED, 30 // i), (bx-i*2, by-i*2, bw+i*4, bh+i*4), border_radius=8)
        
        pygame.draw.rect(self.screen, (10, 10, 30), EMERGENCY_BUTTON_RECT, border_radius=8)
        pygame.draw.rect(self.screen, color, EMERGENCY_BUTTON_RECT, 2, border_radius=8)
        
        text = "SPAWN AMBULANCE"
        txt_surf = self.font_hud.render(text, True, color)
        self.screen.blit(txt_surf, txt_surf.get_rect(center=(bx + bw//2, by + bh//2)))

    def _draw_infrastructure(self):
        cx, cy = INTERSECTION_CENTER, INTERSECTION_CENTER
        rw = ROAD_WIDTH // 2
        
        # Asphalt
        pygame.draw.rect(self.screen, ASPHALT_NIGHT, (cx - rw, 0, ROAD_WIDTH, HEIGHT))
        pygame.draw.rect(self.screen, ASPHALT_NIGHT, (0, cy - rw, WIDTH, ROAD_WIDTH))
        
        # Draw Crosswalks (Neon Zebra Stripes)
        stripe_color = (60, 60, 100)
        stripe_w = 4
        
        # North
        cw_n_y = STOP_LINES["N"] - CW_OFFSET
        for i in range(cx - rw + 5, cx + rw, 15):
            pygame.draw.rect(self.screen, stripe_color, (i, cw_n_y, stripe_w, CW_WIDTH))
        pygame.draw.rect(self.screen, NEON_CYAN, (cx - rw, cw_n_y, ROAD_WIDTH, CW_WIDTH), 1)
        
        # South
        cw_s_y = STOP_LINES["S"] + CW_OFFSET - CW_WIDTH
        for i in range(cx - rw + 5, cx + rw, 15):
            pygame.draw.rect(self.screen, stripe_color, (i, cw_s_y, stripe_w, CW_WIDTH))
        pygame.draw.rect(self.screen, NEON_CYAN, (cx - rw, cw_s_y, ROAD_WIDTH, CW_WIDTH), 1)
        
        # West
        cw_w_x = STOP_LINES["W"] - CW_OFFSET
        for i in range(cy - rw + 5, cy + rw, 15):
            pygame.draw.rect(self.screen, stripe_color, (cw_w_x, i, CW_WIDTH, stripe_w))
        pygame.draw.rect(self.screen, NEON_CYAN, (cw_w_x, cy - rw, CW_WIDTH, ROAD_WIDTH), 1)
        
        # East
        cw_e_x = STOP_LINES["E"] + CW_OFFSET - CW_WIDTH
        for i in range(cy - rw + 5, cy + rw, 15):
            pygame.draw.rect(self.screen, stripe_color, (cw_e_x, i, CW_WIDTH, stripe_w))
        pygame.draw.rect(self.screen, NEON_CYAN, (cw_e_x, cy - rw, CW_WIDTH, ROAD_WIDTH), 1)

        # Neon Markings
        line_color = (60, 60, 90)
        pygame.draw.line(self.screen, line_color, (cx - rw, 0), (cx - rw, HEIGHT), 2)
        pygame.draw.line(self.screen, line_color, (cx + rw, 0), (cx + rw, HEIGHT), 2)
        pygame.draw.line(self.screen, line_color, (0, cy - rw), (WIDTH, cy - rw), 2)
        pygame.draw.line(self.screen, line_color, (0, cy + rw), (WIDTH, cy + rw), 2)

    def _draw_entity_core(self, agent, color):
        # Body Glow
        for i in range(3):
            alpha = 100 // (i + 1)
            surf = pygame.Surface((agent.rect.width + i*4, agent.rect.height + i*4), pygame.SRCALPHA)
            pygame.draw.rect(surf, (*color, alpha), surf.get_rect(), border_radius=4)
            self.screen.blit(surf, agent.rect.move(-i*2, -i*2))
        
        pygame.draw.rect(self.screen, color, agent.rect, border_radius=4)

    def _draw_entity_core_ped(self, p, color):
        # Pedestrian is a circle in this view for cleaner look
        pygame.draw.circle(self.screen, (*color, 60), (int(p.x), int(p.y)), p.radius + 4)
        pygame.draw.circle(self.screen, color, (int(p.x), int(p.y)), p.radius)

    def _draw_car_perception(self, car, peds, lights):
        look_ahead = max(60, car.current_speed * 40)
        rays = [(-15, 0.8), (0, 1.0), (15, 0.8)]
        
        for angle, l_mult in rays:
            length = look_ahead * l_mult
            end_pos = self._get_ray_end(car, angle, length)
            ray_color = (100, 100, 150, 100)
            marker = None

            # Logic Check
            if car._is_light_red(lights):
                ray_color, marker = (*NEON_CYAN, 200), "diamond"
            
            for p in peds:
                dist = math.hypot(car.rect.centerx - p.x, car.rect.centery - p.y)
                if dist < look_ahead:
                    ray_color, marker = (*NEON_RED, 255), "triangle"
            
            pygame.draw.aaline(self.screen, ray_color[:3], car.rect.center, end_pos)
            if marker: self._draw_ray_marker(end_pos, ray_color[:3], marker)

        # Predictive Trajectory
        self._draw_path(car, NEON_ORANGE if car.stopped else NEON_CYAN)

    def _draw_pedestrian_perception(self, p, cars):
        fov_angle = 90
        dir_angle = math.degrees(math.atan2(-p.dir_y, p.dir_x))
        color = NEON_GREEN
        
        for car in cars:
            if math.hypot(p.x - car.rect.centerx, p.y - car.rect.centery) < 80:
                color = NEON_ORANGE
                break
        
        # Draw FOV Arc
        rect = pygame.Rect(p.x - 40, p.y - 40, 80, 80)
        start_rad = math.radians(dir_angle - fov_angle/2)
        end_rad = math.radians(dir_angle + fov_angle/2)
        pygame.draw.arc(self.screen, (*color, 100), rect, start_rad, end_rad, 2)

        # Comfort Zone
        cz_color = NEON_CYAN if color == NEON_GREEN else NEON_RED
        pygame.draw.circle(self.screen, (*cz_color, 40), (int(p.x), int(p.y)), 25, 1)

    def _draw_agent_vectors(self, agent):
        if hasattr(agent, 'direction'): # Car
            vx, vy = agent.direction[0] * 25, agent.direction[1] * 25
            pygame.draw.line(self.screen, NEON_GREEN, agent.rect.center, 
                             (agent.rect.centerx + vx, agent.rect.centery + vy), 2)
        elif hasattr(agent, 'dir_x'): # Pedestrian
            vx, vy = agent.dir_x * 15, agent.dir_y * 15
            pygame.draw.line(self.screen, NEON_GREEN, (int(agent.x), int(agent.y)), 
                             (int(agent.x + vx), int(agent.y + vy)), 2)

    def _draw_path(self, agent, color):
        points = []
        for i in range(1, 6):
            step = i * 25
            if hasattr(agent, 'direction'):
                px = agent.rect.centerx + agent.direction[0] * step
                py = agent.rect.centery + agent.direction[1] * step
            else:
                px = agent.x + agent.dir_x * step
                py = agent.y + agent.dir_y * step
            points.append((px, py))
        
        for p in points:
            pygame.draw.circle(self.screen, color, (int(p[0]), int(p[1])), 2)

    def _draw_ray_marker(self, pos, color, type):
        if type == "diamond":
            pts = [(pos[0], pos[1]-5), (pos[0]+5, pos[1]), (pos[0], pos[1]+5), (pos[0]-5, pos[1])]
            pygame.draw.polygon(self.screen, color, pts)
        elif type == "triangle":
            pts = [(pos[0], pos[1]-6), (pos[0]+5, pos[1]+4), (pos[0]-5, pos[1]+4)]
            pygame.draw.polygon(self.screen, color, pts)

    def _get_ray_end(self, car, angle_offset, length):
        base_angle = math.atan2(car.direction[1], car.direction[0])
        total_angle = base_angle + math.radians(angle_offset)
        return (car.rect.centerx + math.cos(total_angle) * length, 
                car.rect.centery + math.sin(total_angle) * length)

    def _draw_traffic_lights(self, tl):
        cx, rw = INTERSECTION_CENTER, ROAD_WIDTH // 2
        # Defined positions and orientations for the 4 traffic lights
        # (x, y, axis, horizontal_flag)
        configs = [
            (cx - rw - 25, cx - rw - 75, "NS", False), # North-West corner (facing North)
            (cx + rw + 5, cx + rw + 15, "NS", False),  # South-East corner (facing South)
            (cx - rw - 75, cx + rw + 5, "EW", True),   # South-West corner (facing West)
            (cx + rw + 15, cx - rw - 25, "EW", True)   # North-East corner (facing East)
        ]
        
        for x, y, axis, is_horiz in configs:
            # Draw Housing
            w, h = (60, 20) if is_horiz else (20, 60)
            pygame.draw.rect(self.screen, (20, 20, 40), (x, y, w, h), border_radius=5)
            pygame.draw.rect(self.screen, NEON_CYAN, (x, y, w, h), 1, border_radius=5)
            
            # Determine which bulb is active
            active_color = tl.get_color_state(axis)
            
            # Define bulbs (Red, Yellow, Green)
            bulbs = [COLOR_RED_ON, COLOR_YELLOW_ON, COLOR_GREEN_ON]
            off_colors = [(80, 0, 0), (80, 60, 0), (0, 80, 0)]
            
            for i, bulb_color in enumerate(bulbs):
                is_active = (bulb_color == active_color)
                draw_color = bulb_color if is_active else off_colors[i]
                
                # Bulb Position
                if is_horiz:
                    bx, by = x + 10 + i*20, y + 10
                else:
                    bx, by = x + 10, y + 10 + i*20
                
                # Render Glow for active bulb
                if is_active:
                    for r in range(1, 4):
                        pygame.draw.circle(self.screen, (*draw_color, 60 // r), (bx, by), 6 + r*2)
                
                pygame.draw.circle(self.screen, draw_color, (bx, by), 6)

    def _draw_hud(self, sim):
        # Stats Panels
        self._draw_panel(10, 10, 300, 160)
        self._draw_panel(WIDTH - 310, 10, 300, 150)
        
        # Left HUD: System Info & AI Settings
        stats = [
            (f"AI_TRAFFIC_OS_v2.5", NEON_CYAN),
            (f"FPS: {int(sim.clock.get_fps())}", NEON_GREEN),
            (f"AI_EPSILON: {sim.agent.epsilon:.3f}", NEON_ORANGE),
            (f"AI_LR:      {sim.agent.learning_rate:.5f}", NEON_ORANGE),
            (f"AI_GAMMA:   {sim.agent.gamma:.2f}", NEON_ORANGE),
            (f"AGENTS: C:{len(sim.cars):02} P:{len(sim.pedestrians):02}", NEON_CYAN)
        ]
        for i, (txt, col) in enumerate(stats):
            self.screen.blit(self.font_hud.render(txt, True, col), (20, 20 + i*22))

        # Right HUD: Traffic Metrics
        flow = sum(1 for c in sim.cars if not c.stopped) / max(1, len(sim.cars)) * 100
        r_stats = [
            (f"REALTIME_FLOW: {flow:.1f}%", NEON_ORANGE),
            (f"LIFETIME_FLOW: {sim.lifetime_flow:.1f}%", NEON_GREEN),
            (f"AVG_VELOCITY:  {sum(c.current_speed for c in sim.cars) / max(1, len(sim.cars)):.2f}u", NEON_CYAN),
            (f"INCIDENTS:     {self.collision_count}", NEON_RED),
            (f"SIM_TIME:      {time.strftime('%M:%S', time.gmtime(time.time() - self.start_time))}", NEON_FUCHSIA)
        ]
        for i, (txt, col) in enumerate(r_stats):
            self.screen.blit(self.font_hud.render(txt, True, col), (WIDTH - 300, 20 + i*22))

        # Event Log
        for i, log in enumerate(self.event_log):
            self.screen.blit(self.font_main.render(log, True, (180, 180, 220)), (10, HEIGHT - 180 + i*20))

    def _draw_panel(self, x, y, w, h):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 160))
        pygame.draw.rect(surf, NEON_CYAN, surf.get_rect(), 1)
        self.screen.blit(surf, (x, y))

    def _handle_inspector(self, sim):
        m_pos = pygame.mouse.get_pos()
        self.hovered_agent = None
        for a in sim.cars + sim.pedestrians:
            if a.rect.collidepoint(m_pos):
                self.hovered_agent = a; break
        
        if self.hovered_agent:
            a = self.hovered_agent
            p_type = "CAR" if hasattr(a, 'current_speed') else "NPC"
            
            # Popup
            popup = pygame.Surface((200, 100), pygame.SRCALPHA); popup.fill((10, 10, 30, 230))
            pygame.draw.rect(popup, NEON_CYAN, popup.get_rect(), 1)
            
            info = [
                f"ID: {p_type}_{id(a)%9999}",
                f"STATUS: {'IDLE' if getattr(a, 'stopped', False) else 'MOVING'}",
                f"SPEED: {getattr(a, 'current_speed', 1.0):.2f}u",
                f"POS: {int(a.x)}, {int(a.y)}"
            ]
            for i, txt in enumerate(info):
                popup.blit(self.font_main.render(txt, True, NEON_CYAN), (10, 10 + i*20))
            self.screen.blit(popup, (m_pos[0]+15, m_pos[1]+15))
