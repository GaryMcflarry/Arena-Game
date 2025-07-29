import pygame
import math
import sys
import random
from typing import Tuple, List
 
# Initialize Pygame
pygame.init()
 
# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
FOV = math.pi / 3  # 60 degrees
HALF_FOV = FOV / 2
NUM_RAYS = SCREEN_WIDTH // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20
 
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 128, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
DARK_RED = (139, 0, 0)
 
# Map
TILE_SIZE = 64
MAP_WIDTH = 20
MAP_HEIGHT = 20
 
# Arena layout - circular arena with pillars
def create_arena_map():
    arena_map = [[1 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    
    center_x, center_y = MAP_WIDTH // 2, MAP_HEIGHT // 2
    arena_radius = 8
    
    # Create circular arena
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            if distance < arena_radius:
                arena_map[y][x] = 0  # Open space
    
    # Add pillars for cover
    pillar_positions = [
        (center_x - 3, center_y - 3),
        (center_x + 3, center_y - 3),
        (center_x - 3, center_y + 3),
        (center_x + 3, center_y + 3),
        (center_x, center_y - 5),
        (center_x, center_y + 5),
        (center_x - 5, center_y),
        (center_x + 5, center_y),
    ]
    
    for px, py in pillar_positions:
        if 0 <= px < MAP_WIDTH and 0 <= py < MAP_HEIGHT:
            arena_map[py][px] = 2  # Pillar
    
    return arena_map

game_map = create_arena_map()

class EnemyType:
    SKELETON = "skeleton"
    ORC = "orc"
    TROLL = "troll"
    DEMON = "demon"

class Enemy:
    def __init__(self, x: float, y: float, enemy_type: str = EnemyType.SKELETON):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        
        # Type-specific stats
        if enemy_type == EnemyType.SKELETON:
            self.health = 75
            self.max_health = 75
            self.speed = 40
            self.attack_damage = 15
            self.color = WHITE
            self.size = 15
            self.score_value = 50
        elif enemy_type == EnemyType.ORC:
            self.health = 120
            self.max_health = 120
            self.speed = 35
            self.attack_damage = 25
            self.color = GREEN
            self.size = 18
            self.score_value = 75
        elif enemy_type == EnemyType.TROLL:
            self.health = 200
            self.max_health = 200
            self.speed = 25
            self.attack_damage = 40
            self.color = BROWN
            self.size = 25
            self.score_value = 150
        elif enemy_type == EnemyType.DEMON:
            self.health = 150
            self.max_health = 150
            self.speed = 50
            self.attack_damage = 30
            self.color = DARK_RED
            self.size = 20
            self.score_value = 200
            
        self.attack_range = 45
        self.last_attack = 0
        self.attack_cooldown = 2000  # milliseconds
        self.alive = True
        
    def update(self, player, dt, current_time):
        if not self.alive:
            return
            
        # Move toward player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > self.attack_range:
            # Normalize direction and move
            if distance > 0:
                dx /= distance
                dy /= distance
                
                new_x = self.x + dx * self.speed * dt
                new_y = self.y + dy * self.speed * dt
                
                # Simple collision check
                if not self.check_collision(new_x, new_y):
                    self.x = new_x
                    self.y = new_y
                    
        # Attack player if in range
        elif distance <= self.attack_range and current_time - self.last_attack > self.attack_cooldown:
            player.take_damage(self.attack_damage)
            self.last_attack = current_time
            
    def check_collision(self, x: float, y: float) -> bool:
        map_x = int(x // TILE_SIZE)
        map_y = int(y // TILE_SIZE)
        
        if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
            return True
            
        return game_map[map_y][map_x] != 0
        
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            
    def get_distance_to(self, x, y):
        dx = self.x - x
        dy = self.y - y
        return math.sqrt(dx * dx + dy * dy)

class Spell:
    def __init__(self, x: float, y: float, angle: float, spell_type: str = "fireball"):
        self.x = x
        self.y = y
        self.angle = angle
        self.spell_type = spell_type
        self.alive = True
        
        if spell_type == "fireball":
            self.speed = 300
            self.damage = 60
            self.color = ORANGE
            self.size = 8
        elif spell_type == "lightning":
            self.speed = 500
            self.damage = 40
            self.color = YELLOW
            self.size = 6
        elif spell_type == "ice":
            self.speed = 250
            self.damage = 80
            self.color = BLUE
            self.size = 10
            
    def update(self, dt):
        if not self.alive:
            return
            
        # Move spell
        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt
        
        # Check collision with walls
        map_x = int(self.x // TILE_SIZE)
        map_y = int(self.y // TILE_SIZE)
        
        if (map_x < 0 or map_x >= MAP_WIDTH or 
            map_y < 0 or map_y >= MAP_HEIGHT or 
            game_map[map_y][map_x] != 0):
            self.alive = False

class Player:
    def __init__(self, x: float, y: float, angle: float):
        self.x = x
        self.y = y
        self.angle = angle
        self.base_speed = 120
        self.rot_speed = 3.0
        self.health = 100
        self.max_health = 100
        self.mana = 100
        self.max_mana = 100
        self.mana_regen = 20  # per second
        
        # Jump system
        self.z = 0  # Height off ground
        self.z_velocity = 0
        self.gravity = 800  # pixels per second squared
        self.jump_power = 250  # initial upward velocity
        self.is_jumping = False
        self.can_jump = True
        
        # Mouse look
        self.mouse_sensitivity = 0.003
        
        # Spell system
        self.current_spell = "fireball"
        self.spell_costs = {"fireball": 20, "lightning": 15, "ice": 25}
        self.spell_cooldowns = {"fireball": 800, "lightning": 500, "ice": 1200}
        self.last_spell_cast = {"fireball": 0, "lightning": 0, "ice": 0}

    def jump(self):
        """Make the player jump"""
        if self.can_jump and not self.is_jumping:
            self.z_velocity = self.jump_power
            self.is_jumping = True
            self.can_jump = False

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)

    def can_cast_spell(self, spell_type, current_time):
        return (self.mana >= self.spell_costs[spell_type] and 
                current_time - self.last_spell_cast[spell_type] > self.spell_cooldowns[spell_type])

    def cast_spell(self, spell_type, current_time):
        if self.can_cast_spell(spell_type, current_time):
            self.mana -= self.spell_costs[spell_type]
            self.last_spell_cast[spell_type] = current_time
            return True
        return False

    def update(self, dt):
        # Regenerate mana
        self.mana = min(self.max_mana, self.mana + self.mana_regen * dt)
        
        # Update jump physics
        if self.is_jumping or self.z > 0:
            self.z_velocity -= self.gravity * dt
            self.z += self.z_velocity * dt
            
            # Land
            if self.z <= 0:
                self.z = 0
                self.z_velocity = 0
                self.is_jumping = False
                self.can_jump = True

    def handle_mouse_look(self, mouse_rel):
        """Handle mouse movement for looking around"""
        self.angle += mouse_rel[0] * self.mouse_sensitivity
        self.angle = self.angle % (2 * math.pi)

    def move(self, keys, dt):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        
        current_speed = self.base_speed
        if keys[pygame.K_LSHIFT]:
            current_speed *= 1.5
        
        dx, dy = 0, 0
        
        if keys[pygame.K_w]:
            dx += cos_a * current_speed * dt
            dy += sin_a * current_speed * dt
        if keys[pygame.K_s]:
            dx -= cos_a * current_speed * dt
            dy -= sin_a * current_speed * dt
        if keys[pygame.K_a]:
            dx += sin_a * current_speed * dt
            dy -= cos_a * current_speed * dt
        if keys[pygame.K_d]:
            dx -= sin_a * current_speed * dt
            dy += cos_a * current_speed * dt
        
        new_x = self.x + dx
        if not self.check_collision(new_x, self.y):
            self.x = new_x
        
        new_y = self.y + dy
        if not self.check_collision(self.x, new_y):
            self.y = new_y
        
        # Arrow keys still work for keyboard-only players
        if keys[pygame.K_LEFT]:
            self.angle -= self.rot_speed * dt
        if keys[pygame.K_RIGHT]:
            self.angle += self.rot_speed * dt
        
        # Jump
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.jump()
        
        self.angle = self.angle % (2 * math.pi)

    def check_collision(self, x: float, y: float) -> bool:
        buffer = 8
        points = [
            (x - buffer, y - buffer),
            (x + buffer, y - buffer),
            (x - buffer, y + buffer),
            (x + buffer, y + buffer),
        ]
        
        for px, py in points:
            map_x = int(px // TILE_SIZE)
            map_y = int(py // TILE_SIZE)
            
            if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
                return True
            
            if game_map[map_y][map_x] != 0:
                return True
        
        return False
 
class RayCaster:
    def __init__(self, screen):
        self.screen = screen

    def cast_rays(self, player: Player) -> List[Tuple[float, float, int]]:
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

                if 0 <= map_x < MAP_WIDTH and 0 <= map_y < MAP_HEIGHT:
                    wall_type = game_map[map_y][map_x]
                    if wall_type != 0:
                        break
                else:
                    wall_type = 1
                    break

            depth *= math.cos(player.angle - ray_angle)
            rays.append((depth, ray_angle, wall_type))
            ray_angle += DELTA_ANGLE

        return rays

    def render_3d(self, rays: List[Tuple[float, float, int]], enemies: List[Enemy], spells: List[Spell], player: Player):
        # Jump effect - modify view height based on player z position
        view_bob = int(player.z * 0.3)  # Convert jump height to screen bob
        
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

        # Render spells
        self.render_spells(spells, view_bob)

    def render_spells(self, spells: List[Spell], view_bob: int = 0):
        for spell in spells:
            if not spell.alive:
                continue
                
            # Simple spell rendering as colored circles with jump effect
            screen_x = int(spell.x % SCREEN_WIDTH)
            screen_y = int(spell.y % SCREEN_HEIGHT) + view_bob
            
            if 0 <= screen_x < SCREEN_WIDTH and 0 <= screen_y < SCREEN_HEIGHT:
                pygame.draw.circle(self.screen, spell.color, (screen_x, screen_y), spell.size)

    def render_enemies(self, player: Player, enemies: List[Enemy]):
        view_bob = int(player.z * 0.3)  # Jump view effect
        
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

    def render_2d_map(self, player: Player, enemies: List[Enemy]):
        map_scale = 15
        map_offset_x = SCREEN_WIDTH - MAP_WIDTH * map_scale - 10
        map_offset_y = 10

        # Draw map
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if game_map[y][x] == 1:
                    color = DARK_BROWN
                elif game_map[y][x] == 2:
                    color = GRAY
                else:
                    color = BLACK
                    
                pygame.draw.rect(
                    self.screen,
                    color,
                    (map_offset_x + x * map_scale, map_offset_y + y * map_scale, map_scale, map_scale)
                )

        # Draw enemies on minimap
        for enemy in enemies:
            if enemy.alive:
                enemy_x = map_offset_x + int(enemy.x * map_scale / TILE_SIZE)
                enemy_y = map_offset_y + int(enemy.y * map_scale / TILE_SIZE)
                color = {
                    EnemyType.SKELETON: WHITE,
                    EnemyType.ORC: GREEN,
                    EnemyType.TROLL: BROWN,
                    EnemyType.DEMON: DARK_RED
                }.get(enemy.enemy_type, RED)
                pygame.draw.circle(self.screen, color, (enemy_x, enemy_y), 3)

        # Draw player on minimap
        player_x = map_offset_x + int(player.x * map_scale / TILE_SIZE)
        player_y = map_offset_y + int(player.y * map_scale / TILE_SIZE)
        pygame.draw.circle(self.screen, BLUE, (player_x, player_y), 4)

        # Draw player direction
        end_x = player_x + int(math.cos(player.angle) * 12)
        end_y = player_y + int(math.sin(player.angle) * 12)
        pygame.draw.line(self.screen, BLUE, (player_x, player_y), (end_x, end_y), 2)
 
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Elder Scrolls Arena - Mouse to Shoot, SPACE to Jump!")
        self.clock = pygame.time.Clock()
        
        # Mouse capture for FPS-style controls
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        # Start player in center of arena
        center_x = MAP_WIDTH * TILE_SIZE // 2
        center_y = MAP_HEIGHT * TILE_SIZE // 2
        self.player = Player(center_x, center_y, 0)
        
        self.raycaster = RayCaster(self.screen)
        self.running = True
        self.show_map = False
        
        # Wave system
        self.enemies = []
        self.spells = []
        self.score = 0
        self.current_wave = 0
        self.wave_active = False
        self.enemies_killed_this_wave = 0
        self.wave_start_time = 0
        self.time_between_waves = 5000  # 5 seconds
        
        self.start_next_wave()

    def get_spawn_positions(self, count):
        """Get random spawn positions around the arena edge"""
        positions = []
        center_x, center_y = MAP_WIDTH // 2, MAP_HEIGHT // 2
        
        for _ in range(count):
            # Spawn around the edge of the arena
            angle = random.uniform(0, 2 * math.pi)
            radius = 7  # Near the edge but inside the arena
            
            spawn_x = center_x + math.cos(angle) * radius
            spawn_y = center_y + math.sin(angle) * radius
            
            # Convert to world coordinates
            world_x = spawn_x * TILE_SIZE
            world_y = spawn_y * TILE_SIZE
            
            positions.append((world_x, world_y))
            
        return positions

    def start_next_wave(self):
        self.current_wave += 1
        self.wave_active = True
        self.enemies_killed_this_wave = 0
        self.wave_start_time = pygame.time.get_ticks()
        
        # Calculate enemies for this wave
        base_enemies = 3
        additional_enemies = (self.current_wave - 1) * 2
        total_enemies = min(15, base_enemies + additional_enemies)  # Cap at 15
        
        # Enemy type distribution based on wave
        enemy_types = []
        
        # Always have skeletons
        skeleton_count = max(1, total_enemies // 3)
        enemy_types.extend([EnemyType.SKELETON] * skeleton_count)
        
        # Add orcs starting from wave 2
        if self.current_wave >= 2:
            orc_count = max(1, total_enemies // 4)
            enemy_types.extend([EnemyType.ORC] * orc_count)
            
        # Add trolls starting from wave 4
        if self.current_wave >= 4:
            troll_count = max(1, total_enemies // 6)
            enemy_types.extend([EnemyType.TROLL] * troll_count)
            
        # Add demons starting from wave 6
        if self.current_wave >= 6:
            demon_count = max(1, total_enemies // 8)
            enemy_types.extend([EnemyType.DEMON] * demon_count)
        
        # Fill remaining slots with skeletons
        while len(enemy_types) < total_enemies:
            enemy_types.append(EnemyType.SKELETON)
            
        # Shuffle and limit
        random.shuffle(enemy_types)
        enemy_types = enemy_types[:total_enemies]
        
        # Spawn enemies
        spawn_positions = self.get_spawn_positions(len(enemy_types))
        
        for i, enemy_type in enumerate(enemy_types):
            x, y = spawn_positions[i]
            self.enemies.append(Enemy(x, y, enemy_type))

    def handle_events(self):
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_m:
                    self.show_map = not self.show_map
                elif event.key == pygame.K_1:
                    self.player.current_spell = "fireball"
                elif event.key == pygame.K_2:
                    self.player.current_spell = "lightning"
                elif event.key == pygame.K_3:
                    self.player.current_spell = "ice"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Left click to shoot spells
                if event.button == 1:  # Left mouse button
                    if self.player.cast_spell(self.player.current_spell, current_time):
                        spell = Spell(self.player.x, self.player.y, self.player.angle, self.player.current_spell)
                        self.spells.append(spell)
                # Right click to cycle spells
                elif event.button == 3:  # Right mouse button
                    spell_types = ["fireball", "lightning", "ice"]
                    current_index = spell_types.index(self.player.current_spell)
                    self.player.current_spell = spell_types[(current_index + 1) % len(spell_types)]
            elif event.type == pygame.MOUSEMOTION:
                # Mouse look
                self.player.handle_mouse_look(event.rel)

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        
        # Update player
        keys = pygame.key.get_pressed()
        self.player.move(keys, dt)
        self.player.update(dt)
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.player, dt, current_time)
        
        # Update spells
        for spell in self.spells[:]:
            spell.update(dt)
            if not spell.alive:
                self.spells.remove(spell)
                continue
                
            # Check spell-enemy collisions
            for enemy in self.enemies:
                if enemy.alive:
                    distance = enemy.get_distance_to(spell.x, spell.y)
                    if distance < enemy.size:
                        enemy.take_damage(spell.damage)
                        spell.alive = False
                        if not enemy.alive:
                            self.score += enemy.score_value
                            self.enemies_killed_this_wave += 1
                        break
        
        # Remove dead spells
        self.spells = [s for s in self.spells if s.alive]
        
        # Check wave completion
        alive_enemies = [e for e in self.enemies if e.alive]
        if self.wave_active and len(alive_enemies) == 0:
            self.wave_active = False
            self.enemies = []  # Clear dead enemies
            
        # Start next wave after delay
        if not self.wave_active and current_time - self.wave_start_time > self.time_between_waves:
            self.start_next_wave()
        
        # Check if player is dead
        if self.player.health <= 0:
            self.running = False

    def render(self):
        self.screen.fill(BLACK)

        # Cast rays and render 3D view
        rays = self.raycaster.cast_rays(self.player)
        self.raycaster.render_3d(rays, self.enemies, self.spells, self.player)
        
        # Render enemies
        self.raycaster.render_enemies(self.player, self.enemies)

        # Render 2D map if enabled
        if self.show_map:
            self.raycaster.render_2d_map(self.player, self.enemies)

        # Draw crosshair with jump indicator
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        crosshair_color = {
            "fireball": ORANGE,
            "lightning": YELLOW,
            "ice": BLUE
        }.get(self.player.current_spell, WHITE)
        
        # Make crosshair bigger when jumping for feedback
        crosshair_size = 12 + int(self.player.z * 0.1)
        line_width = 3 if self.player.is_jumping else 2
        
        pygame.draw.line(self.screen, crosshair_color, (center_x - crosshair_size, center_y), (center_x + crosshair_size, center_y), line_width)
        pygame.draw.line(self.screen, crosshair_color, (center_x, center_y - crosshair_size), (center_x, center_y + crosshair_size), line_width)
        
        # Jump indicator
        if self.player.is_jumping:
            jump_text = pygame.font.Font(None, 20).render("JUMPING!", True, YELLOW)
            text_rect = jump_text.get_rect(center=(center_x, center_y - 40))
            self.screen.blit(jump_text, text_rect)

        # Draw UI
        self.draw_ui()

        pygame.display.flip()
        
    def draw_ui(self):
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 18)
        
        # Health bar
        health_ratio = self.player.health / self.player.max_health
        health_bar_width = 200
        health_bar_height = 15
        health_x = 10
        health_y = SCREEN_HEIGHT - 80
        
        pygame.draw.rect(self.screen, RED, (health_x, health_y, health_bar_width, health_bar_height))
        pygame.draw.rect(self.screen, GREEN, (health_x, health_y, health_bar_width * health_ratio, health_bar_height))
        
        health_text = small_font.render(f"Health: {int(self.player.health)}/{self.player.max_health}", True, WHITE)
        self.screen.blit(health_text, (health_x, health_y - 18))
        
        # Mana bar
        mana_ratio = self.player.mana / self.player.max_mana
        mana_y = health_y + 20
        
        pygame.draw.rect(self.screen, PURPLE, (health_x, mana_y, health_bar_width, health_bar_height))
        pygame.draw.rect(self.screen, BLUE, (health_x, mana_y, health_bar_width * mana_ratio, health_bar_height))
        
        mana_text = small_font.render(f"Mana: {int(self.player.mana)}/{self.player.max_mana}", True, WHITE)
        self.screen.blit(mana_text, (health_x, mana_y + 18))
        
        # Current spell
        spell_colors = {"fireball": ORANGE, "lightning": YELLOW, "ice": BLUE}
        spell_text = small_font.render(f"Spell: {self.player.current_spell.title()}", True, spell_colors[self.player.current_spell])
        self.screen.blit(spell_text, (health_x, mana_y + 40))
        
        # Wave info
        alive_enemies = sum(1 for enemy in self.enemies if enemy.alive)
        wave_text = font.render(f"Wave: {self.current_wave}", True, GOLD)
        self.screen.blit(wave_text, (SCREEN_WIDTH - 150, 10))
        
        enemies_text = small_font.render(f"Enemies: {alive_enemies}", True, WHITE)
        self.screen.blit(enemies_text, (SCREEN_WIDTH - 150, 35))
        
        score_text = small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - 150, 55))
        
        # Wave status
        if not self.wave_active:
            current_time = pygame.time.get_ticks()
            time_left = max(0, self.time_between_waves - (current_time - self.wave_start_time))
            next_wave_text = font.render(f"Next Wave: {time_left // 1000 + 1}s", True, YELLOW)
            text_rect = next_wave_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            self.screen.blit(next_wave_text, text_rect)

        # Spell costs and cooldowns
        spell_info_y = 100
        for i, (spell, cost) in enumerate(self.player.spell_costs.items()):
            current_time = pygame.time.get_ticks()
            can_cast = self.player.can_cast_spell(spell, current_time)
            
            color = spell_colors[spell] if can_cast else GRAY
            key_text = f"{i+1}: {spell.title()} ({cost} mana)"
            
            if not can_cast and self.player.mana >= cost:
                cooldown_left = self.player.spell_cooldowns[spell] - (current_time - self.player.last_spell_cast[spell])
                key_text += f" ({cooldown_left // 1000 + 1}s)"
            
            text = small_font.render(key_text, True, color)
            self.screen.blit(text, (10, spell_info_y + i * 20))

        # Controls
        controls = [
            "WASD: Move",
            "Mouse: Look & Shoot",
            "SPACE: Jump",
            "Right Click: Cycle Spells",
            "1/2/3: Select Spell",
            "M: Toggle Map",
            "Shift: Sprint"
        ]

        for i, control in enumerate(controls):
            text = small_font.render(control, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH - 200, 80 + i * 18))

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()

        # Game over screen
        self.show_game_over()
        pygame.quit()
        sys.exit()
        
    def show_game_over(self):
        """Display game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 24)
        
        game_over_text = font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(game_over_text, game_over_rect)
        
        wave_text = small_font.render(f"Reached Wave: {self.current_wave}", True, WHITE)
        wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(wave_text, wave_rect)
        
        score_text = small_font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(score_text, score_rect)
        
        restart_text = small_font.render("Press ESC to exit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        
        # Wait for key press
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    waiting = False
 
if __name__ == "__main__":
    game = Game()
    game.run()