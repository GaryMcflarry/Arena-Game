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

            # Cast ray and find wall collision
            for depth in range(0, MAX_DEPTH * TILE_SIZE, 4):  # Step by 4 for performance
                target_x = player.x + cos_a * depth
                target_y = player.y + sin_a * depth

                map_x = int(target_x // TILE_SIZE)
                map_y = int(target_y // TILE_SIZE)

                # Check bounds first
                if map_x < 0 or map_x >= map_width or map_y < 0 or map_y >= map_height:
                    wall_type = 1  # Hit boundary
                    break
                
                # Check for wall collision
                wall_type = collision_map[map_y][map_x]
                if wall_type != 0:
                    break

            # Apply fisheye correction
            depth *= math.cos(player.angle - ray_angle)
            rays.append((depth, ray_angle, wall_type))
            ray_angle += DELTA_ANGLE

        return rays

    def render_3d_town(self, rays: List[Tuple[float, float, int]], player):
        """Render 3D town view"""
        # Jump effect - modify view height based on player z position
        view_bob = int(player.z * 0.3)
        
        # Draw sky
        sky_rect = (0, 0 + view_bob, SCREEN_WIDTH, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, LIGHT_BLUE, sky_rect)
        
        # Draw ground
        ground_rect = (0, SCREEN_HEIGHT // 2 + view_bob, SCREEN_WIDTH, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, GRAY, ground_rect)

        # Draw walls
        for i, (depth, ray_angle, wall_type) in enumerate(rays):
            if wall_type != 0:  # Only draw actual walls
                # Prevent division by zero
                wall_height = min(SCREEN_HEIGHT, 21000 / max(depth, 1))
                
                # Different building colors
                if wall_type == 1:  # Town walls
                    base_color = BROWN
                elif wall_type == 2:  # Houses
                    base_color = DARK_GRAY
                elif wall_type == 3:  # Weapon shop
                    base_color = DARK_RED
                elif wall_type == 4:  # Magic shop
                    base_color = PURPLE
                elif wall_type == 5:  # Healer
                    base_color = WHITE
                elif wall_type == 6:  # Arena
                    base_color = GOLD
                else:
                    base_color = RED  # Bright red for debugging
                    
                # Distance shading
                color_intensity = max(50, 255 - int(depth * 4))
                wall_color = tuple(min(255, int(c * color_intensity / 255)) for c in base_color)

                # Apply jump bob to wall rendering
                wall_y = (SCREEN_HEIGHT - wall_height) // 2 + view_bob
                
                pygame.draw.rect(
                    self.screen,
                    wall_color,
                    (i * 2, wall_y, 2, wall_height)
                )

    def render_3d_arena(self, rays: List[Tuple[float, float, int]], enemies, spells, player):
        """Render 3D arena view"""
        view_bob = int(player.z * 0.3)
        
        # Draw ceiling
        ceiling_rect = (0, 0 + view_bob, SCREEN_WIDTH, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, (32, 32, 40), ceiling_rect)
        
        # Draw floor
        floor_rect = (0, SCREEN_HEIGHT // 2 + view_bob, SCREEN_WIDTH, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, (48, 48, 56), floor_rect)

        # Draw walls
        for i, (depth, ray_angle, wall_type) in enumerate(rays):
            if wall_type != 0:
                wall_height = min(SCREEN_HEIGHT, 21000 / max(depth, 1))
                
                if wall_type == 1:  # Outer wall
                    base_color = DARK_BROWN
                elif wall_type == 2:  # Pillar
                    base_color = GRAY
                else:
                    base_color = GRAY
                    
                color_intensity = max(30, 255 - int(depth * 6))
                wall_color = tuple(min(255, int(c * color_intensity / 255)) for c in base_color)

                wall_y = max(0, (SCREEN_HEIGHT - wall_height) // 2 + view_bob)
                wall_height = min(wall_height, SCREEN_HEIGHT - wall_y)
                
                if wall_height > 0:
                    pygame.draw.rect(self.screen, wall_color, (i * 2, wall_y, 2, wall_height))

        # Render spells and enemies
        self.render_spells(spells, view_bob)
        self.render_enemies(player, enemies, view_bob)

    def render_spells(self, spells, view_bob: int = 0):
        """Simple spell rendering"""
        for spell in spells:
            if not spell.alive:
                continue
                
            # Simple screen projection without modulo operations
            screen_x = int(spell.x * 0.5)  # Simple scaling
            screen_y = int(spell.y * 0.5) + view_bob
            
            # Keep on screen
            if 0 <= screen_x < SCREEN_WIDTH and 0 <= screen_y < SCREEN_HEIGHT:
                pygame.draw.circle(self.screen, spell.color, (screen_x, screen_y), spell.size)

    def render_enemies(self, player, enemies, view_bob: int = 0):
        """Simple enemy rendering"""
        for enemy in enemies:
            if not enemy.alive:
                continue
                
            dx = enemy.x - player.x
            dy = enemy.y - player.y
            enemy_distance = math.sqrt(dx * dx + dy * dy)
            
            if enemy_distance < 1:  # Avoid division by zero
                continue
                
            enemy_angle = math.atan2(dy, dx)
            angle_diff = enemy_angle - player.angle
            
            # Normalize angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
                
            # Check if in FOV
            if abs(angle_diff) < HALF_FOV:
                screen_x = (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2) + (SCREEN_WIDTH // 2)
                
                enemy_size = max(4, enemy.size * 1000 / enemy_distance)
                enemy_height = enemy_size
                
                enemy_rect = (
                    screen_x - enemy_size // 2,
                    (SCREEN_HEIGHT - enemy_height) // 2 + view_bob,
                    enemy_size,
                    enemy_height
                )
                pygame.draw.rect(self.screen, enemy.color, enemy_rect)