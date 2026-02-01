import pygame
from src.config import *

class GraphicsRenderer:
    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self.font = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.large_font = pygame.font.SysFont("Segoe UI", 36, bold=True)

    def draw_environment(self):
        """Draws the intersection with asphalt, curbs, crosswalks, and markings."""
        self.surface.fill(COLOR_GRASS)
        
        cx = INTERSECTION_CENTER
        cy = INTERSECTION_CENTER
        rw = ROAD_WIDTH // 2
        
        # 1. Draw Roads (Asphalt)
        pygame.draw.rect(self.surface, COLOR_ROAD, (cx - rw, 0, ROAD_WIDTH, HEIGHT))
        pygame.draw.rect(self.surface, COLOR_ROAD, (0, cy - rw, WIDTH, ROAD_WIDTH))
        
        # 2. Draw Sidewalks (Connecting Grass to Road)
        # We draw grey areas where pedestrians walk/wait
        # Corners logic:
        # TL Corner Sidewalk
        sw_width = 30
        pygame.draw.rect(self.surface, COLOR_SIDEWALK, (cx - rw - sw_width, 0, sw_width, cy - rw)) # Vertical strip
        pygame.draw.rect(self.surface, COLOR_SIDEWALK, (0, cy - rw - sw_width, cx - rw, sw_width)) # Horizontal strip
        
        # Draw Borders (Curbs)
        border_col = (20, 20, 20)
        # Vertical
        pygame.draw.line(self.surface, border_col, (cx - rw, 0), (cx - rw, HEIGHT), 2)
        pygame.draw.line(self.surface, border_col, (cx + rw, 0), (cx + rw, HEIGHT), 2)
        # Horizontal
        pygame.draw.line(self.surface, border_col, (0, cy - rw), (WIDTH, cy - rw), 2)
        pygame.draw.line(self.surface, border_col, (0, cy + rw), (WIDTH, cy + rw), 2)

        # 3. Draw Crosswalks (Zebra Stripes) - Shifted BEHIND stop lines
        stripe_w = 6
        cw_len = ROAD_WIDTH + 20 
        
        # North Crosswalk
        cw_n_y = STOP_LINES["N"] - CW_OFFSET
        pygame.draw.rect(self.surface, (80, 80, 80), (cx - rw - 10, cw_n_y, cw_len, CW_WIDTH)) 
        for i in range(cx - rw, cx + rw, 15):
             pygame.draw.rect(self.surface, COLOR_MARKING, (i, cw_n_y, stripe_w, CW_WIDTH))

        # South Crosswalk
        cw_s_y = STOP_LINES["S"] + CW_OFFSET - CW_WIDTH
        pygame.draw.rect(self.surface, (80, 80, 80), (cx - rw - 10, cw_s_y, cw_len, CW_WIDTH))
        for i in range(cx - rw, cx + rw, 15):
             pygame.draw.rect(self.surface, COLOR_MARKING, (i, cw_s_y, stripe_w, CW_WIDTH))

        # West Crosswalk
        cw_w_x = STOP_LINES["W"] - CW_OFFSET
        pygame.draw.rect(self.surface, (80, 80, 80), (cw_w_x, cy - rw - 10, CW_WIDTH, cw_len))
        for i in range(cy - rw, cy + rw, 15):
             pygame.draw.rect(self.surface, COLOR_MARKING, (cw_w_x, i, CW_WIDTH, stripe_w))

        # East Crosswalk
        cw_e_x = STOP_LINES["E"] + CW_OFFSET - CW_WIDTH
        pygame.draw.rect(self.surface, (80, 80, 80), (cw_e_x, cy - rw - 10, CW_WIDTH, cw_len))
        for i in range(cy - rw, cy + rw, 15):
             pygame.draw.rect(self.surface, COLOR_MARKING, (cw_e_x, i, CW_WIDTH, stripe_w))

        # 4. Draw Center Lines (Double Yellow) - Interrupted
        # N
        pygame.draw.line(self.surface, (200, 150, 0), (cx - 2, 0), (cx - 2, cw_n_y), 2)
        pygame.draw.line(self.surface, (200, 150, 0), (cx + 2, 0), (cx + 2, cw_n_y), 2)
        # S
        pygame.draw.line(self.surface, (200, 150, 0), (cx - 2, cw_s_y + CW_WIDTH), (cx - 2, HEIGHT), 2)
        pygame.draw.line(self.surface, (200, 150, 0), (cx + 2, cw_s_y + CW_WIDTH), (cx + 2, HEIGHT), 2)
        # W
        pygame.draw.line(self.surface, (200, 150, 0), (0, cy - 2), (cw_w_x, cy - 2), 2)
        pygame.draw.line(self.surface, (200, 150, 0), (0, cy + 2), (cw_w_x, cy + 2), 2)
        # E
        pygame.draw.line(self.surface, (200, 150, 0), (cw_e_x + CW_WIDTH, cy - 2), (WIDTH, cy - 2), 2)
        pygame.draw.line(self.surface, (200, 150, 0), (cw_e_x + CW_WIDTH, cy + 2), (WIDTH, cy + 2), 2)

        # 5. Draw Stop Lines (Thick White)
        # Drawn at the STOP_LINES coordinates (between intersection and crosswalk)
        # N
        pygame.draw.line(self.surface, COLOR_STOP_LINE, (cx - rw, STOP_LINES["N"]), (cx, STOP_LINES["N"]), 6)
        # S
        pygame.draw.line(self.surface, COLOR_STOP_LINE, (cx, STOP_LINES["S"]), (cx + rw, STOP_LINES["S"]), 6)
        # E
        pygame.draw.line(self.surface, COLOR_STOP_LINE, (STOP_LINES["E"], cy - rw), (STOP_LINES["E"], cy), 6)
        # W
        pygame.draw.line(self.surface, COLOR_STOP_LINE, (STOP_LINES["W"], cy), (STOP_LINES["W"], cy + rw), 6)
        
    def draw_traffic_light(self, x: int, y: int, color: Tuple[int, int, int], horizontal: bool = False):
        w, h = (60, 20) if horizontal else (20, 60)
        pygame.draw.rect(self.surface, COLOR_POLE, (x, y, w, h), border_radius=5)
        
        r_col = COLOR_RED_ON if color == COLOR_RED_ON else COLOR_RED_OFF
        y_col = COLOR_YELLOW_ON if color == COLOR_YELLOW_ON else COLOR_YELLOW_OFF
        g_col = COLOR_GREEN_ON if color == COLOR_GREEN_ON else COLOR_GREEN_OFF
        
        radius = 7
        if horizontal:
            pygame.draw.circle(self.surface, r_col, (x + 10, y + 10), radius)
            pygame.draw.circle(self.surface, y_col, (x + 30, y + 10), radius)
            pygame.draw.circle(self.surface, g_col, (x + 50, y + 10), radius)
        else:
            pygame.draw.circle(self.surface, r_col, (x + 10, y + 10), radius)
            pygame.draw.circle(self.surface, y_col, (x + 10, y + 30), radius)
            pygame.draw.circle(self.surface, g_col, (x + 10, y + 50), radius)

    def draw_ui(self, queues: dict, emergency: bool):
        pygame.draw.rect(self.surface, (0, 0, 0, 180), (10, 10, 200, 70), border_radius=5)
        text_ns = self.font.render(f"North/South Queue: {queues['NS']}", True, COLOR_TEXT)
        text_ew = self.font.render(f"East/West Queue:   {queues['EW']}", True, COLOR_TEXT)
        self.surface.blit(text_ns, (20, 20))
        self.surface.blit(text_ew, (20, 45))
        
        if emergency:
            emer_text = self.large_font.render("!!! EMERGENCY VEHICLE !!!", True, COLOR_CAR_EMERGENCY)
            rect = emer_text.get_rect(center=(WIDTH//2, 50))
            self.surface.blit(emer_text, rect)
