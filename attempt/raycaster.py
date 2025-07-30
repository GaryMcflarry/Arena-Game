import pygame
import math
from typing import List, Tuple
from constants import *

class RayCaster:
    def __init__(self, screen):
        self.screen = screen

    def cast_rays(self, player, collision_map, map_width, map_height) -> List[Tuple[float, float, int]]:
        """Cast rays for raycasting rendering"""
        rays = []
        ray_angle = player.angle - HALF_FOV

        for ray in range(NUM_RAYS):
            depth = 0
            wall_type = 1
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            for depth in range(MAX_DEPTH * TILE_SIZE):
                target_x = player.x + cos_a * depth
                target_y = player.y + sin_a * depth

                map_x = int(target_x // TILE_SIZE)
                map_y = int(target_y // TILE_SIZE)

                if 0 <= map_x < map_width and 0 <= map_y < map_height:
                    wall_type = collision_map[map_y][map_x]
                    if wall_type != 0:
                        break
                else:
                    wall_type = 1
                    break

            depth *= math.cos(player.angle - ray_angle)
            rays.append((depth, ray_angle, wall_type))
            ray_angle += DELTA_ANGLE

        return rays

    def render_3d_town(self, rays: List[Tuple[float, float, int]], player):
        """Render 3D town view with variable building heights"""
        # Jump effect - modify view height based on player z position
        view_bob = int(player.z * 0.3)
        
        # Draw sky with gradient effect
        self.render_sky_gradient(view_bob)
        
        # Draw textured ground
        self.render_town_ground(view_bob)

        # Draw walls with different heights and textures based on building type
        for i, (depth, ray_angle, wall_type) in enumerate(rays):
            # Variable building heights based on type
            base_height = 21000
            if wall_type == 1:  # Town walls/boundaries
                wall_height = base_height * 0.8 / (depth + 0.0001)  # Lower walls
                base_color = BROWN
            elif wall_type == 2:  # Regular houses
                wall_height = base_height * 1.0 / (depth + 0.0001)  # Normal height
                base_color = DARK_GRAY
            elif wall_type == 3:  # Weapon shop (blacksmith)
                wall_height = base_height * 1.3 / (depth + 0.0001)  # Taller workshop
                base_color = DARK_RED
            elif wall_type == 4:  # Magic shop (tower)
                wall_height = base_height * 1.8 / (depth + 0.0001)  # Tall tower
                base_color = PURPLE
            elif wall_type == 5:  # Healer (temple)
                wall_height = base_height * 1.5 / (depth + 0.0001)  # Temple height
                base_color = WHITE
            elif wall_type == 6:  # Arena entrance
                wall_height = base_height * 2.0 / (depth + 0.0001)  # Impressive entrance
                base_color = GOLD
            else:
                wall_height = base_height / (depth + 0.0001)
                base_color = GRAY
                
            # Apply distance shading
            color_intensity = max(50, 255 - int(depth * 4))
            wall_color = tuple(min(255, int(c * color_intensity / 255)) for c in base_color)

            # Apply jump bob to wall rendering
            wall_y = (SCREEN_HEIGHT - wall_height) // 2 + view_bob
            
            # Add simple texture effect by varying brightness
            self.render_textured_wall(i, wall_y, wall_height, wall_color, wall_type, depth)

    def render_sky_gradient(self, view_bob):
        """Render a gradient sky instead of solid color"""
        for y in range(SCREEN_HEIGHT // 2):
            # Create gradient from light blue to white
            intensity = int(255 * (1 - y / (SCREEN_HEIGHT // 2)))
            sky_color = (min(255, LIGHT_BLUE[0] + intensity // 3), 
                        min(255, LIGHT_BLUE[1] + intensity // 2),
                        min(255, LIGHT_BLUE[2] + intensity // 4))
            
            pygame.draw.line(self.screen, sky_color, 
                           (0, y + view_bob), (SCREEN_WIDTH, y + view_bob))
    
    def render_town_ground(self, view_bob):
        """Render textured cobblestone-like ground"""
        ground_start_y = SCREEN_HEIGHT // 2 + view_bob
        
        # Create cobblestone pattern
        for y in range(ground_start_y, SCREEN_HEIGHT):
            for x in range(0, SCREEN_WIDTH, 20):
                # Alternate between two gray shades to simulate cobblestones
                if ((x // 20) + (y // 10)) % 2:
                    color = GRAY
                else:
                    color = DARK_GRAY
                    
                pygame.draw.rect(self.screen, color, (x, y, 20, 10))
    
    def render_textured_wall(self, x_pos, wall_y, wall_height, base_color, wall_type, depth):
        """Render walls with simple texture effects"""
        wall_width = 2
        
        # Base wall
        pygame.draw.rect(self.screen, base_color, (x_pos * 2, wall_y, wall_width, wall_height))
        
        # Add texture details based on wall type
        if wall_type == 3:  # Weapon shop - add forge-like effects
            if int(wall_height) > 20:  # Only add details if wall is big enough
                # Add darker vertical lines for forge effect
                for i in range(int(wall_height) // 15):
                    line_y = wall_y + i * 15
                    darker_color = tuple(max(0, c - 30) for c in base_color)
                    pygame.draw.line(self.screen, darker_color, 
                                   (x_pos * 2, line_y), (x_pos * 2 + wall_width, line_y))
                                   
        elif wall_type == 4:  # Magic shop - add mystical effects
            if int(wall_height) > 30:
                # Add purple highlights for magical effect
                highlight_color = tuple(min(255, c + 20) for c in base_color)
                pygame.draw.line(self.screen, highlight_color,
                               (x_pos * 2, wall_y), (x_pos * 2, wall_y + wall_height))
                               
        elif wall_type == 5:  # Healer - add clean stone blocks
            if int(wall_height) > 25:
                # Add horizontal lines for stone blocks
                for i in range(int(wall_height) // 20):
                    line_y = wall_y + i * 20
                    lighter_color = tuple(min(255, c + 15) for c in base_color)
                    pygame.draw.line(self.screen, lighter_color,
                                   (x_pos * 2, line_y), (x_pos * 2 + wall_width, line_y))
                                   
        elif wall_type == 6:  # Arena entrance - add ornate details
            if int(wall_height) > 40:
                # Add golden highlights
                highlight_color = tuple(min(255, c + 30) for c in base_color)
                # Vertical highlight in center
                pygame.draw.line(self.screen, highlight_color,
                               (x_pos * 2 + 1, wall_y), (x_pos * 2 + 1, wall_y + wall_height))

    def render_3d_arena(self, rays: List[Tuple[float, float, int]], enemies, spells, player):
        """Render 3D arena view with enemies and spells"""
        # Jump effect - modify view height based on player z position
        view_bob = int(player.z * 0.3)
        
        # Draw ceiling (darker for dungeon feel)
        ceiling_rect = (0, 0 + view_bob, SCREEN_WIDTH, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, (32, 32, 40), ceiling_rect)
        
        # Draw floor (stone-like)
        floor_rect = (0, SCREEN_HEIGHT // 2 + view_bob, SCREEN_WIDTH, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, (48, 48, 56), floor_rect)

        # Draw walls with different textures and jump effect
        for i, (depth, ray_angle, wall_type) in enumerate(rays):
            wall_height = 21000 / (depth + 0.0001)
            
            # Different wall colors based on type
            if wall_type == 1:  # Outer wall
                base_color = DARK_BROWN
            elif wall_type == 2:  # Pillar
                base_color = GRAY
            else:
                base_color = GRAY
                
            # Apply distance shading
            color_intensity = max(30, 255 - int(depth * 6))
            wall_color = tuple(min(255, int(c * color_intensity / 255)) for c in base_color)

            # Apply jump bob to wall rendering
            wall_y = (SCREEN_HEIGHT - wall_height) // 2 + view_bob
            
            pygame.draw.rect(
                self.screen,
                wall_color,
                (i * 2, wall_y, 2, wall_height)
            )

        # Render spells and enemies
        self.render_spells(spells, view_bob)
        self.render_enemies(player, enemies, view_bob)

    def render_spells(self, spells, view_bob: int = 0):
        """Render spells in 3D space"""
        for spell in spells:
            if not spell.alive:
                continue
                
            # Simple spell rendering as colored circles with jump effect
            screen_x = int(spell.x % SCREEN_WIDTH)
            screen_y = int(spell.y % SCREEN_HEIGHT) + view_bob
            
            if 0 <= screen_x < SCREEN_WIDTH and 0 <= screen_y < SCREEN_HEIGHT:
                pygame.draw.circle(self.screen, spell.color, (screen_x, screen_y), spell.size)

    def render_enemies(self, player, enemies, view_bob: int = 0):
        """Render enemies in 3D space"""
        for enemy in enemies:
            if not enemy.alive:
                continue
                
            dx = enemy.x - player.x
            dy = enemy.y - player.y
            enemy_distance = math.sqrt(dx * dx + dy * dy)
            
            if enemy_distance < 0.1:
                continue
                
            enemy_angle = math.atan2(dy, dx)
            angle_diff = enemy_angle - player.angle
            
            # Normalize angle difference
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
                
            # Check if enemy is in FOV
            if abs(angle_diff) < HALF_FOV:
                screen_x = (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2) + (SCREEN_WIDTH // 2)
                
                enemy_size = enemy.size * 1000 / (enemy_distance + 0.1)
                enemy_height = enemy_size
                
                # Type-specific rendering
                enemy_color = enemy.color
                health_ratio = enemy.health / enemy.max_health
                
                # Damage tinting
                if health_ratio < 0.5:
                    red_tint = int(128 * (1 - health_ratio))
                    enemy_color = tuple(min(255, c + red_tint) if i == 0 else c for i, c in enumerate(enemy_color))
                
                # Draw enemy with jump bob effect
                enemy_rect = (
                    screen_x - enemy_size // 2,
                    (SCREEN_HEIGHT - enemy_height) // 2 + view_bob,
                    enemy_size,
                    enemy_height
                )
                pygame.draw.rect(self.screen, enemy_color, enemy_rect)
                
                # Draw type indicator
                type_text = {
                    EnemyType.SKELETON: "S",
                    EnemyType.ORC: "O", 
                    EnemyType.TROLL: "T",
                    EnemyType.DEMON: "D"
                }
                
                font = pygame.font.Font(None, max(12, int(enemy_size // 3)))
                text = font.render(type_text.get(enemy.enemy_type, "?"), True, BLACK)
                text_rect = text.get_rect(center=(screen_x, (SCREEN_HEIGHT - enemy_height) // 2 + enemy_height // 2 + view_bob))
                self.screen.blit(text, text_rect)
                
                # Health bar with jump effect
                bar_width = enemy_size
                bar_height = max(2, int(enemy_size // 8))
                bar_x = screen_x - bar_width // 2
                bar_y = (SCREEN_HEIGHT - enemy_height) // 2 - bar_height - 5 + view_bob
                
                pygame.draw.rect(self.screen, RED, (bar_x, bar_y, bar_width, bar_height))
                health_width = int(bar_width * health_ratio)
                pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, health_width, bar_height))

    def render_bosses(self, player, bosses, view_bob: int = 0):
        """Render bosses in 3D space (larger and more detailed)"""
        for boss in bosses:
            if not boss.alive:
                continue
                
            dx = boss.x - player.x
            dy = boss.y - player.y
            boss_distance = math.sqrt(dx * dx + dy * dy)
            
            if boss_distance < 0.1:
                continue
                
            boss_angle = math.atan2(dy, dx)
            angle_diff = boss_angle - player.angle
            
            # Normalize angle difference
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
                
            # Check if boss is in FOV
            if abs(angle_diff) < HALF_FOV:
                screen_x = (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2) + (SCREEN_WIDTH // 2)
                
                boss_size = boss.size * 1200 / (boss_distance + 0.1)  # Larger than regular enemies
                boss_height = boss_size
                
                # Boss-specific rendering with special effects
                boss_color = boss.color
                health_ratio = boss.health / boss.max_health
                
                # Special boss glow effect
                glow_color = tuple(min(255, c + 50) for c in boss_color)
                
                # Draw boss with glow and jump bob effect
                boss_rect = (
                    screen_x - boss_size // 2,
                    (SCREEN_HEIGHT - boss_height) // 2 + view_bob,
                    boss_size,
                    boss_height
                )
                
                # Draw glow effect
                glow_rect = (boss_rect[0] - 5, boss_rect[1] - 5, boss_rect[2] + 10, boss_rect[3] + 10)
                pygame.draw.rect(self.screen, glow_color, glow_rect)
                pygame.draw.rect(self.screen, boss_color, boss_rect)
                
                # Draw boss indicator
                boss_indicators = {
                    BossType.NECROMANCER: "N",
                    BossType.ORC_CHIEFTAIN: "C", 
                    BossType.ANCIENT_TROLL: "A",
                    BossType.DEMON_LORD: "L"
                }
                
                font = pygame.font.Font(None, max(16, int(boss_size // 2)))
                text = font.render(boss_indicators.get(boss.boss_type, "B"), True, YELLOW)
                text_rect = text.get_rect(center=(screen_x, (SCREEN_HEIGHT - boss_height) // 2 + boss_height // 2 + view_bob))
                self.screen.blit(text, text_rect)
                
                # Boss health bar (larger and more prominent)
                bar_width = boss_size + 20
                bar_height = max(6, int(boss_size // 6))
                bar_x = screen_x - bar_width // 2
                bar_y = (SCREEN_HEIGHT - boss_height) // 2 - bar_height - 10 + view_bob
                
                pygame.draw.rect(self.screen, DARK_RED, (bar_x, bar_y, bar_width, bar_height))
                health_width = int(bar_width * health_ratio)
                pygame.draw.rect(self.screen, RED, (bar_x, bar_y, health_width, bar_height))
                
                # Boss name
                name_font = pygame.font.Font(None, max(12, int(boss_size // 4)))
                name_text = name_font.render(boss.boss_type.replace('_', ' ').title(), True, YELLOW)
                name_rect = name_text.get_rect(center=(screen_x, bar_y - 15))
                self.screen.blit(name_text, name_rect)