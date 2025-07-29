import pygame
import math
from constants import GameState, ShopType
from constants import *
from raycaster import RayCaster
from town_map import TownMap

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
        
        self.font = pygame.font.Font(None, 24)
        
    def initialize_town(self):
        """Initialize/reset town state"""
        # Place player at town entrance
        self.player.x = 6 * TILE_SIZE + TILE_SIZE // 2
        self.player.y = 14 * TILE_SIZE + TILE_SIZE // 2
        self.player.angle = math.pi / 2  # Facing north
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and self.current_interaction:
                self.interact_with_building()
            elif event.key == pygame.K_m:
                pass  # Could toggle minimap
        elif event.type == pygame.MOUSEMOTION:
            self.player.handle_mouse_look(event.rel)
            
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
        """Check for nearby interactive objects"""
        self.show_interaction_prompt = False
        self.current_interaction = None
        
        # Get player map position
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
        # Update player
        keys = pygame.key.get_pressed()
        self.player.move(keys, dt, self.town_map.collision_map, 
                        self.town_map.width, self.town_map.height)
        self.player.update(dt)
        
        # Check for interactions
        self.check_interactions()
        
    def render(self):
        self.screen.fill(BLACK)
        
        # Cast rays and render 3D view
        rays = self.raycaster.cast_rays(self.player, self.town_map.collision_map,
                                       self.town_map.width, self.town_map.height)
        self.raycaster.render_3d_town(rays, self.player)
        
        # Draw UI
        self.draw_ui()
        
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
            interaction_names = {
                "weapon_shop": "Weapon Shop",
                "magic_shop": "Magic Shop", 
                "healer": "Healer",
                "arena": "Arena Entrance"
            }
            
            prompt_text = f"Press E to enter {interaction_names.get(self.current_interaction, 'building')}"
            text_surface = self.font.render(prompt_text, True, YELLOW)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            
            # Draw background for better visibility
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            pygame.draw.rect(self.screen, YELLOW, bg_rect, 2)
            
            self.screen.blit(text_surface, text_rect)
            
        # Draw minimap
        self.draw_minimap()
        
    def draw_minimap(self):
        """Draw a simple minimap"""
        map_scale = 8
        map_size = 120
        map_x = SCREEN_WIDTH - map_size - 10
        map_y = 10
        
        # Draw map background
        pygame.draw.rect(self.screen, DARK_GRAY, (map_x, map_y, map_size, map_size))
        pygame.draw.rect(self.screen, WHITE, (map_x, map_y, map_size, map_size), 2)
        
        # Draw map tiles
        for y in range(self.town_map.height):
            for x in range(self.town_map.width):
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
                    
        # Draw player position
        player_map_x = int(self.player.x // TILE_SIZE)
        player_map_y = int(self.player.y // TILE_SIZE)
        
        player_x = map_x + player_map_x * map_scale + map_scale // 2
        player_y = map_y + player_map_y * map_scale + map_scale // 2
        
        pygame.draw.circle(self.screen, YELLOW, (player_x, player_y), 3)
        
        # Draw player direction
        end_x = player_x + int(math.cos(self.player.angle) * 8)
        end_y = player_y + int(math.sin(self.player.angle) * 8)
        pygame.draw.line(self.screen, YELLOW, (player_x, player_y), (end_x, end_y), 2)