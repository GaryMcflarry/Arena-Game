import pygame
import math
from constants import *
from raycaster import RayCaster
from town_map import TownMap

class NPC:
    """Simple NPC that wanders around town"""
    def __init__(self, x, y, name, color=BLUE, dialogue=None):
        self.x = x
        self.y = y
        self.name = name
        self.color = color
        self.size = 12
        self.speed = 15
        
        # Dialogue system
        self.dialogue = dialogue or [f"Greetings, traveler! I am {name}."]
        self.has_talked = False
        
        # Wandering behavior
        self.target_x = x
        self.target_y = y
        self.wander_radius = 80
        self.home_x = x
        self.home_y = y
        self.target_reached_time = 0
        self.wait_time = 3000  # Wait 3 seconds before moving to new target
        
    def update(self, dt, current_time):
        """Update NPC movement"""
        # Check if we've reached our target
        distance_to_target = math.sqrt((self.x - self.target_x)**2 + (self.y - self.target_y)**2)
        
        if distance_to_target < 20:  # Close enough to target
            if current_time - self.target_reached_time > self.wait_time:
                self.set_new_target()
                self.target_reached_time = current_time
        else:
            # Move toward target
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            if distance_to_target > 0:
                dx /= distance_to_target
                dy /= distance_to_target
                
                self.x += dx * self.speed * dt
                self.y += dy * self.speed * dt
                
    def set_new_target(self):
        """Set a new random target within wander radius"""
        import random
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(30, self.wander_radius)
        
        self.target_x = self.home_x + math.cos(angle) * distance
        self.target_y = self.home_y + math.sin(angle) * distance
        
        # Keep within town bounds (20x20 map = 1280x1280 world coordinates)
        self.target_x = max(100, min(1180, self.target_x))  # Stay within map
        self.target_y = max(100, min(1180, self.target_y))  # Stay within map

class TownState:
    def __init__(self, screen, game_manager, player):
        self.screen = screen
        self.game_manager = game_manager
        self.player = player
        
        # Initialize town map
        self.town_map = TownMap()
        self.raycaster = RayCaster(screen)
        
        # Interaction system
        self.interaction_range = 80
        self.show_interaction_prompt = False
        self.current_interaction = None
        
        # Initialize NPCs around town
        self.npcs = [
            NPC(200, 300, "Townsperson", BLUE),
            NPC(400, 200, "Merchant", GREEN),
            NPC(600, 400, "Guard", BROWN),
            NPC(300, 500, "Villager", PURPLE),
        ]
        
        self.font = pygame.font.Font(None, 24)
        self.dialogue_font = pygame.font.Font(None, 20)
        
    def initialize_town(self):
        """Initialize/reset town state"""
        # Place player at town entrance (bottom center opening)
        self.player.x = 9 * TILE_SIZE + TILE_SIZE // 2  # Center of opening
        self.player.y = 18 * TILE_SIZE + TILE_SIZE // 2  # Just inside the opening
        self.player.angle = math.pi / 2  # Facing north
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                if self.current_interaction:
                    self.interact_with_building()
                elif self.current_npc:
                    self.talk_to_npc()
            elif event.key == pygame.K_m:
                pass  # Could toggle minimap
        elif event.type == pygame.MOUSEMOTION:
            self.player.handle_mouse_look(event.rel)
            
    def talk_to_npc(self):
        """Handle talking to NPCs"""
        if self.current_npc:
            import random
            self.dialogue_text = random.choice(self.current_npc.dialogue)
            self.show_dialogue = True
            self.dialogue_timer = 0
            self.current_npc.has_talked = True
            
    def interact_with_building(self):
        """Handle interaction with buildings"""
        if self.current_interaction == "weapon_shop":
            self.game_manager.change_state(GameState.SHOP, ShopType.WEAPON)
        elif self.current_interaction == "magic_shop":
            self.game_manager.change_state(GameState.SHOP, ShopType.MAGIC)
        elif self.current_interaction == "healer":
            self.game_manager.change_state(GameState.SHOP, ShopType.HEALER)
        elif self.current_interaction == "arena":
            self.game_manager.change_state(GameState.ARENA)
            
    def check_interactions(self):
        """Check for nearby interactive objects and NPCs"""
        self.show_interaction_prompt = False
        self.current_interaction = None
        self.current_npc = None
        
        # Check for NPCs first
        for npc in self.npcs:
            distance = math.sqrt(
                (self.player.x - npc.x) ** 2 + 
                (self.player.y - npc.y) ** 2
            )
            
            if distance < self.interaction_range:
                self.show_interaction_prompt = True
                self.current_npc = npc
                return  # Priority to NPCs over buildings
        
        # Check for buildings if no NPC nearby
        player_map_x = int(self.player.x // TILE_SIZE)
        player_map_y = int(self.player.y // TILE_SIZE)
        
        # Check for interactive tiles around player
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                check_x = player_map_x + dx
                check_y = player_map_y + dy
                
                if (0 <= check_x < self.town_map.width and 
                    0 <= check_y < self.town_map.height):
                    
                    tile_type = self.town_map.get_tile(check_x, check_y)
                    
                    # Calculate distance to tile center
                    tile_center_x = check_x * TILE_SIZE + TILE_SIZE // 2
                    tile_center_y = check_y * TILE_SIZE + TILE_SIZE // 2
                    
                    distance = math.sqrt(
                        (self.player.x - tile_center_x) ** 2 + 
                        (self.player.y - tile_center_y) ** 2
                    )
                    
                    if distance < self.interaction_range:
                        if tile_type == 3:  # Weapon shop
                            self.show_interaction_prompt = True
                            self.current_interaction = "weapon_shop"
                        elif tile_type == 4:  # Magic shop
                            self.show_interaction_prompt = True
                            self.current_interaction = "magic_shop"
                        elif tile_type == 5:  # Healer
                            self.show_interaction_prompt = True
                            self.current_interaction = "healer"
                        elif tile_type == 6:  # Arena entrance
                            self.show_interaction_prompt = True
                            self.current_interaction = "arena"
                            
    def update(self, dt):
        current_time = pygame.time.get_ticks()
        
        # Update player
        keys = pygame.key.get_pressed()
        self.player.move(keys, dt, self.town_map.collision_map, 
                        self.town_map.width, self.town_map.height)
        self.player.update(dt)
        
        # Update NPCs
        for npc in self.npcs:
            npc.update(dt, current_time)
        
        # Check for interactions
        self.check_interactions()
        
    def render(self):
        self.screen.fill(BLACK)
        
        # Cast rays and render 3D view
        rays = self.raycaster.cast_rays(self.player, self.town_map.collision_map,
                                       self.town_map.width, self.town_map.height)
        self.raycaster.render_3d_town(rays, self.player)
        
        # Render NPCs in 3D space
        self.render_npcs()
        
        # Draw UI
        self.draw_ui()
        
    def render_npcs(self):
        """Render NPCs in 3D space"""
        view_bob = int(self.player.z * 0.3)
        
        for npc in self.npcs:
            dx = npc.x - self.player.x
            dy = npc.y - self.player.y
            npc_distance = math.sqrt(dx * dx + dy * dy)
            
            if npc_distance < 0.1:
                continue
                
            npc_angle = math.atan2(dy, dx)
            angle_diff = npc_angle - self.player.angle
            
            # Normalize angle difference
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
                
            # Check if NPC is in FOV
            if abs(angle_diff) < HALF_FOV:
                screen_x = (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2) + (SCREEN_WIDTH // 2)
                
                npc_size = npc.size * 800 / (npc_distance + 0.1)
                npc_height = npc_size * 1.5  # NPCs are taller than wide
                
                # Draw NPC with jump bob effect
                npc_rect = (
                    screen_x - npc_size // 2,
                    (SCREEN_HEIGHT - npc_height) // 2 + view_bob,
                    npc_size,
                    npc_height
                )
                pygame.draw.rect(self.screen, npc.color, npc_rect)
                
                # Draw simple face
                if npc_size > 10:
                    # Eyes
                    eye_size = max(1, int(npc_size // 8))
                    left_eye_x = int(screen_x - npc_size // 4)
                    right_eye_x = int(screen_x + npc_size // 4)
                    eye_y = int((SCREEN_HEIGHT - npc_height) // 2 + npc_height // 3 + view_bob)
                    
                    pygame.draw.circle(self.screen, WHITE, (left_eye_x, eye_y), eye_size)
                    pygame.draw.circle(self.screen, WHITE, (right_eye_x, eye_y), eye_size)
                
                # Draw name above NPC if close enough
                if npc_distance < 150 and npc_size > 15:
                    name_font = pygame.font.Font(None, max(12, int(npc_size // 3)))
                    name_text = name_font.render(npc.name, True, WHITE)
                    name_rect = name_text.get_rect(center=(screen_x, npc_rect[1] - 15))
                    
                    # Draw background for name
                    bg_rect = name_rect.inflate(4, 2)
                    pygame.draw.rect(self.screen, BLACK, bg_rect)
                    pygame.draw.rect(self.screen, WHITE, bg_rect, 1)
                    
                    self.screen.blit(name_text, name_rect)
        
    def draw_ui(self):
        # Draw player stats
        stats_y = 10
        stats = [
            f"Gold: {self.player.gold}",
            f"Health: {int(self.player.health)}/{self.player.get_max_health()}",
            f"Mana: {int(self.player.mana)}/{self.player.get_max_mana()}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.font.render(stat, True, WHITE)
            self.screen.blit(stat_text, (10, stats_y + i * 25))
            
        # Draw interaction prompt
        if self.show_interaction_prompt:
            if self.current_npc:
                prompt_text = f"Press E to talk to {self.current_npc.name.split()[0]}"
                prompt_color = self.current_npc.color
            else:
                interaction_names = {
                    "weapon_shop": "Weapon Shop",
                    "magic_shop": "Magic Shop", 
                    "healer": "Healer",
                    "arena": "Arena Entrance"
                }
                prompt_text = f"Press E to enter {interaction_names.get(self.current_interaction, 'building')}"
                prompt_color = YELLOW
            
            text_surface = self.font.render(prompt_text, True, prompt_color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            
            # Draw background for better visibility
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            pygame.draw.rect(self.screen, prompt_color, bg_rect, 2)
            
            self.screen.blit(text_surface, text_rect)
            
        # Draw dialogue if active
        if self.show_dialogue:
            dialogue_y = SCREEN_HEIGHT - 120
            dialogue_rect = pygame.Rect(50, dialogue_y, SCREEN_WIDTH - 100, 60)
            
            # Draw dialogue background
            pygame.draw.rect(self.screen, BLACK, dialogue_rect)
            pygame.draw.rect(self.screen, WHITE, dialogue_rect, 2)
            
            # Draw dialogue text (word wrap)
            words = self.dialogue_text.split(' ')
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                text_width = self.dialogue_font.get_size(test_line)[0]
                
                if text_width < dialogue_rect.width - 20:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw lines
            for i, line in enumerate(lines[:2]):  # Max 2 lines
                line_y = dialogue_y + 15 + i * 20
                line_surface = self.dialogue_font.render(line, True, WHITE)
                self.screen.blit(line_surface, (dialogue_rect.x + 10, line_y))
            
        # Draw minimap with NPCs
        self.draw_minimap()
        
    def draw_minimap(self):
        """Draw a minimap with NPCs"""
        map_scale = 6
        map_size = 120
        map_x = SCREEN_WIDTH - map_size - 10
        map_y = 10
        
        # Draw map background
        pygame.draw.rect(self.screen, DARK_GRAY, (map_x, map_y, map_size, map_size))
        pygame.draw.rect(self.screen, WHITE, (map_x, map_y, map_size, map_size), 2)
        
        # Draw map tiles
        for y in range(min(20, self.town_map.height)):
            for x in range(min(20, self.town_map.width)):
                if x < self.town_map.width and y < self.town_map.height:
                    tile_type = self.town_map.get_tile(x, y)
                    
                    if tile_type != 0:  # Not empty space
                        color = WHITE
                        if tile_type == 1:  # Wall
                            color = BROWN
                        elif tile_type == 2:  # House
                            color = GRAY
                        elif tile_type in [3, 4, 5]:  # Shops
                            color = BLUE
                        elif tile_type == 6:  # Arena
                            color = RED
                            
                        tile_x = map_x + x * map_scale
                        tile_y = map_y + y * map_scale
                        pygame.draw.rect(self.screen, color, 
                                       (tile_x, tile_y, map_scale, map_scale))
                    
        # Draw NPCs on minimap
        for npc in self.npcs:
            npc_map_x = int(map_x + (npc.x / TILE_SIZE) * map_scale)
            npc_map_y = int(map_y + (npc.y / TILE_SIZE) * map_scale)
            
            if (map_x <= npc_map_x <= map_x + map_size and 
                map_y <= npc_map_y <= map_y + map_size):
                pygame.draw.circle(self.screen, npc.color, (npc_map_x, npc_map_y), 2)
                    
        # Draw player position
        player_map_x = int(self.player.x // TILE_SIZE)
        player_map_y = int(self.player.y // TILE_SIZE)
        
        if (0 <= player_map_x < 20 and 0 <= player_map_y < 20):
            player_x = map_x + player_map_x * map_scale
            player_y = map_y + player_map_y * map_scale
            
            pygame.draw.circle(self.screen, YELLOW, (player_x, player_y), 3)
            
            # Draw player direction
            end_x = player_x + int(math.cos(self.player.angle) * 8)
            end_y = player_y + int(math.sin(self.player.angle) * 8)
            pygame.draw.line(self.screen, YELLOW, (player_x, player_y), (end_x, end_y), 2)
            
            pygame.draw.circle(self.screen, YELLOW, (player_x, player_y), 3)
            
            # Draw player direction
            end_x = player_x + int(math.cos(self.player.angle) * 8)
            end_y = player_y + int(math.sin(self.player.angle) * 8)
            pygame.draw.line(self.screen, YELLOW, (player_x, player_y), (end_x, end_y), 2)