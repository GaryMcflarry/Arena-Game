import pygame
import math
import random
from constants import *
from raycaster import RayCaster
from arena_map import ArenaMap
from enemy import Enemy
from boss import Boss
from spell import Spell

class ArenaState:
    def __init__(self, screen, game_manager, player):
        self.screen = screen
        self.game_manager = game_manager
        self.player = player
        
        self.arena_map = ArenaMap()
        self.raycaster = RayCaster(screen)
        
        self.sound_manager = None
        
        # Entity lists
        self.enemies = []
        self.bosses = []
        self.spells = []
        
        # Wave management
        self.current_wave = 1
        self.wave_progress_saved = False
        self.enemies_remaining = 0
        self.wave_completed = False
        self.wave_start_time = 0
        self.between_waves = False
        self.wave_delay = 3000
        
        # Boss wave tracking
        self.boss_wave = False
        self.boss_defeated = False
        self.show_shop_prompt = False
        self.shop_prompt_timer = 0
        self.shop_prompt_duration = 10000
        
        # Game over state
        self.game_over = False
        self.game_over_timer = 0
        self.game_over_duration = 5000
        
        # Fonts
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
        # Arena spawn settings
        self.arena_center_x = 10 * TILE_SIZE
        self.arena_center_y = 10 * TILE_SIZE
        self.spawn_radius = 7 * TILE_SIZE
        
    def initialize_arena(self):
        """Initialize/reset arena for new session"""
        # Reset player position
        self.player.x = self.arena_center_x
        self.player.y = self.arena_center_y
        self.player.angle = 0
        
        self.player.reset_for_arena()
        
        if not self.wave_progress_saved:
            self.current_wave = 1
        
        # Clear all entities
        self.enemies = []
        self.bosses = []
        self.spells = []
        self.wave_completed = False
        self.between_waves = False
        self.boss_wave = False
        self.boss_defeated = False
        self.show_shop_prompt = False
        
        self.start_wave()
        
    def continue_from_shop(self):
        """Continue arena after visiting shop - preserve wave"""
        self.wave_progress_saved = True
        self.current_wave += 1
        self.initialize_arena()
        self.wave_progress_saved = False
        
    def continue_from_town(self):
        """Continue arena after visiting town (preserves wave)"""
        self.preserve_wave = True
        self.initialize_arena()
        
    def continue_arena(self):
        """Continue arena after shopping"""
        self.show_shop_prompt = False
        self.boss_defeated = False
        self.boss_wave = False
        self.current_wave += 1
        if self.sound_manager:
            self.sound_manager.play_sound('wave_complete')
        self.start_wave()
        
    def start_wave(self):
        """Start a new wave"""
        self.wave_start_time = pygame.time.get_ticks()
        self.wave_completed = False
        self.between_waves = False
        
        # Every 5th wave is a boss wave
        if self.current_wave % 5 == 0:
            self.start_boss_wave()
        else:
            self.start_regular_wave()
            
    def start_regular_wave(self):
        """Start a regular enemy wave"""
        self.boss_wave = False
        
        # Scale enemy count with wave number
        base_enemies = 4
        additional_enemies = (self.current_wave - 1) // 2
        num_enemies = base_enemies + additional_enemies
        
        for _ in range(num_enemies):
            self.spawn_enemy()
            
        self.enemies_remaining = len(self.enemies)
        
    def start_boss_wave(self):
        """Start a boss wave"""
        self.boss_wave = True
        
        if self.sound_manager:
            self.sound_manager.play_sound('boss_spawn')
        
        # Cycle through boss types
        boss_types = [BossType.NECROMANCER, BossType.ORC_CHIEFTAIN, BossType.ANCIENT_TROLL, BossType.DEMON_LORD]
        boss_index = ((self.current_wave // 5) - 1) % len(boss_types)
        boss_type = boss_types[boss_index]
        
        boss_x, boss_y = self.get_spawn_position()
        boss = Boss(boss_x, boss_y, boss_type, self)
        
        # Scale boss stats with wave
        wave_multiplier = 1.0 + ((self.current_wave - 5) // 5) * 0.5
        boss.health = int(boss.health * wave_multiplier)
        boss.max_health = boss.health
        boss.attack_damage = int(boss.attack_damage * wave_multiplier)
        
        self.bosses.append(boss)
        self.enemies_remaining = len(self.enemies) + len(self.bosses)
        
    def spawn_enemy(self):
        """Spawn a random enemy"""
        # Unlock enemy types progressively
        if self.current_wave <= 3:
            enemy_types = [EnemyType.SKELETON]
        elif self.current_wave <= 6:
            enemy_types = [EnemyType.SKELETON, EnemyType.ORC]
        elif self.current_wave <= 10:
            enemy_types = [EnemyType.SKELETON, EnemyType.ORC, EnemyType.TROLL]
        else:
            enemy_types = [EnemyType.SKELETON, EnemyType.ORC, EnemyType.TROLL, EnemyType.DEMON]
            
        enemy_type = random.choice(enemy_types)
        enemy_x, enemy_y = self.get_spawn_position()
        enemy = Enemy(enemy_x, enemy_y, enemy_type)
        
        # Scale enemy stats with wave
        health_multiplier = 1.0 + (self.current_wave - 1) * 0.3
        damage_multiplier = 1.0 + (self.current_wave - 1) * 0.2
        
        enemy.health = int(enemy.health * health_multiplier)
        enemy.max_health = enemy.health
        enemy.attack_damage = int(enemy.attack_damage * damage_multiplier)
        
        self.enemies.append(enemy)
        
    def get_spawn_position(self):
        """Get a valid spawn position around the arena"""
        attempts = 0
        while attempts < 50:
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(self.spawn_radius * 0.7, self.spawn_radius)
            
            x = self.arena_center_x + math.cos(angle) * distance
            y = self.arena_center_y + math.sin(angle) * distance
            
            # Check for valid position away from player
            if not self.check_spawn_collision(x, y) and self.get_distance_to_player(x, y) > 100:
                return x, y
            attempts += 1
            
        return self.arena_center_x + 200, self.arena_center_y + 200
                
    def check_spawn_collision(self, x, y):
        """Check if spawn position collides with walls"""
        map_x = int(x // TILE_SIZE)
        map_y = int(y // TILE_SIZE)
        
        if map_x < 0 or map_x >= 20 or map_y < 0 or map_y >= 20:
            return True
        
        return not self.arena_map.is_walkable(map_x, map_y)
        
    def get_distance_to_player(self, x, y):
        """Get distance from position to player"""
        dx = x - self.player.x
        dy = y - self.player.y
        return math.sqrt(dx * dx + dy * dy)
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.game_over:
                self.game_manager.change_state(GameState.MENU)
                return
            elif self.show_shop_prompt:
                if event.key == pygame.K_y:
                    self.game_manager.change_state(GameState.TOWN)
                elif event.key == pygame.K_n:
                    self.continue_arena()
            else:
                if event.key == pygame.K_1:
                    self.cast_spell(self.player.current_spell)
                elif event.key == pygame.K_2:
                    self.cycle_spell()
                elif event.key == pygame.K_3:
                    self.cycle_spell()
        elif event.type == pygame.MOUSEBUTTONDOWN and not self.show_shop_prompt and not self.game_over:
            if event.button == 1:  # Left click to cast
                self.cast_spell(self.player.current_spell)
            elif event.button == 3:  # Right click to cycle spell
                self.cycle_spell()
        elif event.type == pygame.MOUSEMOTION and not self.show_shop_prompt and not self.game_over:
            self.player.handle_mouse_look(event.rel)
            
    def cycle_spell(self):
        """Cycle to next available spell"""
        available_spells = self.player.get_available_spells()
        if len(available_spells) <= 1:
            return
            
        current_index = available_spells.index(self.player.current_spell)
        next_index = (current_index + 1) % len(available_spells)
        self.player.current_spell = available_spells[next_index]
        
        if self.sound_manager:
            self.sound_manager.play_sound('menu_select')
            
    def cast_spell(self, spell_type):
        """Cast a spell"""
        if self.player.mana >= self.player.spell_costs[spell_type]:
            self.player.mana -= self.player.spell_costs[spell_type]
            
            if self.sound_manager:
                self.sound_manager.play_sound('spell_cast')
            
            # Heal spell is instant
            if spell_type == "heal":
                heal_amount = 20 * self.player.get_spell_damage_multiplier()
                self.player.heal(heal_amount)
                if self.sound_manager:
                    self.sound_manager.play_sound('heal')
                return
            
            # Create projectile spell
            spell = Spell(self.player.x, self.player.y, self.player.angle, spell_type, self.sound_manager)
            spell.damage = int(spell.damage * self.player.get_spell_damage_multiplier())
            self.spells.append(spell)
                
    def update(self, dt):
        current_time = pygame.time.get_ticks()
        
        # Handle game over state
        if self.game_over:
            if current_time - self.game_over_timer > self.game_over_duration:
                self.game_manager.change_state(GameState.MENU)
            return
        
        # Handle shop prompt timeout
        if self.show_shop_prompt:
            if current_time - self.shop_prompt_timer > self.shop_prompt_duration:
                self.continue_arena()
            return
        
        # Player movement with collision
        keys = pygame.key.get_pressed()
        old_x, old_y = self.player.x, self.player.y
        
        self.player.move(keys, dt, self.arena_map.collision_map, 
                        self.arena_map.width, self.arena_map.height)
        
        # Check for out of bounds or wall collision
        player_tile_x = int(self.player.x // TILE_SIZE)
        player_tile_y = int(self.player.y // TILE_SIZE)
        
        if (player_tile_x < 0 or player_tile_x >= self.arena_map.width or
            player_tile_y < 0 or player_tile_y >= self.arena_map.height or
            self.arena_map.collision_map[player_tile_y][player_tile_x] != 0):
            self.player.x, self.player.y = old_x, old_y
            
        self.player.update(dt)
        
        # Update enemies
        for enemy in self.enemies[:]:
            old_health = enemy.health
            enemy.update(self.player, dt, current_time)
            
            if enemy.alive and enemy.health < old_health:
                if self.sound_manager:
                    self.sound_manager.play_sound('enemy_hit')
            
            if not enemy.alive:
                self.player.add_gold(enemy.score_value)
                self.player.total_score += enemy.score_value
                self.enemies.remove(enemy)
                if self.sound_manager:
                    self.sound_manager.play_sound('enemy_death')
                
        # Update bosses
        for boss in self.bosses[:]:
            old_health = boss.health
            boss.update(self.player, dt, current_time)
            
            if boss.alive and boss.health < old_health:
                if self.sound_manager:
                    self.sound_manager.play_sound('enemy_hit')
            
            if not boss.alive:
                self.player.add_gold(boss.score_value)
                self.player.total_score += boss.score_value
                self.bosses.remove(boss)
                if self.boss_wave:
                    self.boss_defeated = True
                if self.sound_manager:
                    self.sound_manager.play_sound('enemy_death')
                    
        # Update spells and check collisions
        for spell in self.spells[:]:
            spell.update(dt, self.arena_map.collision_map, 
                        self.arena_map.width, self.arena_map.height)
            
            if not spell.alive:
                self.spells.remove(spell)
                continue
                
            # Check spell hits on enemies
            for enemy in self.enemies:
                if enemy.alive and self.check_spell_collision(spell, enemy):
                    enemy.take_damage(spell.damage)
                    spell.on_hit_target()
                    spell.alive = False
                    break
                    
            # Check spell hits on bosses
            for boss in self.bosses:
                if boss.alive and self.check_spell_collision(spell, boss):
                    boss.take_damage(spell.damage)
                    spell.on_hit_target()
                    spell.alive = False
                    break
        
        # Check wave completion
        if not self.between_waves and len(self.enemies) == 0 and len(self.bosses) == 0:
            self.wave_completed = True
            
            if self.boss_wave and self.boss_defeated:
                self.show_shop_prompt = True
                self.shop_prompt_timer = current_time
            else:
                self.between_waves = True
                self.wave_start_time = current_time
                if self.sound_manager:
                    self.sound_manager.play_sound('wave_complete')
                
        # Start next wave after delay
        if self.between_waves and current_time - self.wave_start_time > self.wave_delay:
            self.current_wave += 1
            self.player.highest_wave = max(self.player.highest_wave, self.current_wave)
            self.start_wave()
            
        # Check for player death
        if self.player.health <= 0:
            self.trigger_game_over(current_time)
            
    def trigger_game_over(self, current_time):
        """Trigger game over screen"""
        self.game_over = True
        self.game_over_timer = current_time
        if self.sound_manager:
            self.sound_manager.play_sound('player_hit')
            
    def check_spell_collision(self, spell, target):
        """Check if spell hits target"""
        dx = spell.x - target.x
        dy = spell.y - target.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < target.size + spell.size
        
    def render(self):
        self.screen.fill(BLACK)
        
        # Render 3D view
        rays = self.raycaster.cast_rays(self.player, self.arena_map.collision_map,
                                       self.arena_map.width, self.arena_map.height)
        self.raycaster.render_3d_arena(rays, self.enemies, self.spells, self.player)
        
        self.render_enemies_3d(rays)
        
        if self.bosses:
            self.render_bosses_3d(rays)
        
        # Render spell trails
        for spell in self.spells:
            if hasattr(spell, 'render_trail'):
                spell.render_trail(self.screen)
        
        self.draw_health_bars()
        self.draw_minimap()
        self.draw_ui()
        
        if self.show_shop_prompt:
            self.draw_shop_prompt()
            
        if self.game_over:
            self.draw_game_over_screen()
    
    def render_enemies_3d(self, rays):
        """Render enemies in 3D space with proper wall occlusion"""
        view_bob = int(self.player.z * 0.3)
        
        for enemy in self.enemies:
            if not enemy.alive:
                continue
                
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            enemy_distance = math.sqrt(dx * dx + dy * dy)
            
            if enemy_distance < 0.1:
                continue
                
            enemy_angle = math.atan2(dy, dx)
            angle_diff = enemy_angle - self.player.angle
            
            # Normalize angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
                
            if abs(angle_diff) < HALF_FOV:
                # Check if enemy is blocked by walls
                enemy_blocked = False
                steps = max(10, int(enemy_distance / 8))
                
                for step in range(1, steps):
                    t = step / steps
                    check_x = self.player.x + dx * t
                    check_y = self.player.y + dy * t
                    check_tile_x = int(check_x // TILE_SIZE)
                    check_tile_y = int(check_y // TILE_SIZE)
                    
                    if (check_tile_x < 0 or check_tile_x >= self.arena_map.width or
                        check_tile_y < 0 or check_tile_y >= self.arena_map.height):
                        enemy_blocked = True
                        break
                    
                    if self.arena_map.get_tile(check_tile_x, check_tile_y) != 0:
                        enemy_blocked = True
                        break
                
                if not enemy_blocked:  
                    screen_x = (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2) + (SCREEN_WIDTH // 2)
                    
                    # Scale enemy based on distance
                    enemy_scale = max(4, int(enemy.size * 1000 / (enemy_distance + 0.1)))
                    enemy_width = enemy_scale
                    enemy_height = enemy_scale
                    
                    enemy_y = (SCREEN_HEIGHT // 2 - enemy_height // 2) + view_bob
                    
                    # Render enemy sprite or colored rect
                    if hasattr(enemy, 'image') and enemy.image:
                        scaled_enemy = pygame.transform.scale(enemy.image, (enemy_width, enemy_height))
                        
                        # Apply distance-based darkness
                        if enemy_distance > 100:
                            dark_surface = pygame.Surface((enemy_width, enemy_height))
                            dark_surface.fill((0, 0, 0))
                            darkness = min(128, int((enemy_distance - 100) * 2))
                            dark_surface.set_alpha(darkness)
                            
                            enemy_rect = scaled_enemy.get_rect(center=(int(screen_x), int(enemy_y + enemy_height // 2)))
                            self.screen.blit(scaled_enemy, enemy_rect)
                            self.screen.blit(dark_surface, enemy_rect)
                        else:
                            enemy_rect = scaled_enemy.get_rect(center=(int(screen_x), int(enemy_y + enemy_height // 2)))
                            self.screen.blit(scaled_enemy, enemy_rect)
                    else:
                        enemy_rect = (
                            screen_x - enemy_width // 2,
                            enemy_y,
                            enemy_width,
                            enemy_height
                        )
                        pygame.draw.rect(self.screen, enemy.color, enemy_rect)
            
    def render_bosses_3d(self, rays):
        """Render bosses in 3D space with proper wall occlusion"""
        view_bob = int(self.player.z * 0.3)
        
        for boss in self.bosses:
            if not boss.alive:
                continue
                
            dx = boss.x - self.player.x
            dy = boss.y - self.player.y
            boss_distance = math.sqrt(dx * dx + dy * dy)
            
            if boss_distance < 0.1:
                continue
                
            boss_angle = math.atan2(dy, dx)
            angle_diff = boss_angle - self.player.angle
            
            # Normalize angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
                
            if abs(angle_diff) < HALF_FOV:
                # Check if boss is blocked by walls
                boss_blocked = False
                steps = max(10, int(boss_distance / 8)) 
                
                for step in range(1, steps):
                    t = step / steps
                    check_x = self.player.x + dx * t
                    check_y = self.player.y + dy * t
                    check_tile_x = int(check_x // TILE_SIZE)
                    check_tile_y = int(check_y // TILE_SIZE)
                    
                    if (check_tile_x < 0 or check_tile_x >= self.arena_map.width or
                        check_tile_y < 0 or check_tile_y >= self.arena_map.height):
                        boss_blocked = True
                        break
                    
                    if self.arena_map.get_tile(check_tile_x, check_tile_y) != 0:
                        boss_blocked = True
                        break

                if not boss_blocked:
                    screen_x = (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2) + (SCREEN_WIDTH // 2)
                    
                    # Scale boss larger than normal enemies
                    boss_scale = max(8, int(boss.size * 1200 / (boss_distance + 0.1)))
                    boss_width = boss_scale
                    boss_height = boss_scale * 1.5
                    
                    boss_y = (SCREEN_HEIGHT - boss_height) // 2 + view_bob
                    
                    # Render boss sprite
                    if hasattr(boss, 'image') and boss.image:
                        scaled_boss = pygame.transform.scale(boss.image, (int(boss_width), int(boss_height)))
                        
                        # Apply distance-based darkness
                        if boss_distance > 150:
                            dark_surface = pygame.Surface((int(boss_width), int(boss_height)))
                            dark_surface.fill((0, 0, 0))
                            darkness = min(100, int((boss_distance - 150) * 1.5))
                            dark_surface.set_alpha(darkness)
                            
                            boss_rect = (screen_x - boss_width // 2, boss_y, boss_width, boss_height)
                            self.screen.blit(scaled_boss, boss_rect)
                            self.screen.blit(dark_surface, boss_rect)
                        else:
                            boss_rect = (screen_x - boss_width // 2, boss_y, boss_width, boss_height)
                            self.screen.blit(scaled_boss, boss_rect)
                            
                        # Show rage mode indicator
                        if hasattr(boss, 'rage_mode') and boss.rage_mode:
                            rage_rect = pygame.Rect(screen_x - boss_width // 2, boss_y, boss_width, boss_height)
                            pygame.draw.rect(self.screen, RED, rage_rect, 3)
                    else:
                        boss_rect = (
                            screen_x - boss_width // 2,
                            boss_y,
                            boss_width,
                            boss_height
                        )
                        pygame.draw.rect(self.screen, boss.color, boss_rect)
                    
                    # Draw boss name when close
                    if boss_distance < 200 and boss_scale > 20:
                        boss_names = {
                            BossType.NECROMANCER: "Necromancer",
                            BossType.ORC_CHIEFTAIN: "Orc Chieftain", 
                            BossType.ANCIENT_TROLL: "Ancient Troll",
                            BossType.DEMON_LORD: "Demon Lord"
                        }
                        name_text = boss_names.get(boss.boss_type, "Boss")
                        
                        name_font = pygame.font.Font(None, max(16, int(boss_scale // 4)))
                        name_surface = name_font.render(name_text, True, WHITE)
                        name_rect = name_surface.get_rect(center=(screen_x, boss_y - 20))
                        
                        bg_rect = name_rect.inflate(6, 4)
                        pygame.draw.rect(self.screen, BLACK, bg_rect)
                        pygame.draw.rect(self.screen, boss.color, bg_rect, 2)
                        
                        self.screen.blit(name_surface, name_rect)
    
    def draw_minimap(self):
        """Draw arena minimap with enemies and player"""
        map_scale = 6
        map_size = 120
        map_x = SCREEN_WIDTH - map_size - 10
        map_y = 10
        
        # Draw minimap background
        pygame.draw.rect(self.screen, DARK_GRAY, (map_x, map_y, map_size, map_size))
        pygame.draw.rect(self.screen, WHITE, (map_x, map_y, map_size, map_size), 2)
        
        # Draw map tiles
        for y in range(self.arena_map.height):
            for x in range(self.arena_map.width):
                tile_type = self.arena_map.get_tile(x, y)
                
                if tile_type != 0:
                    color = WHITE
                    if tile_type == 1:
                        color = BROWN
                    elif tile_type == 2:
                        color = GRAY
                        
                    tile_x = map_x + x * map_scale
                    tile_y = map_y + y * map_scale
                    pygame.draw.rect(self.screen, color, 
                                   (tile_x, tile_y, map_scale, map_scale))
                    
        # Draw enemies on minimap
        for enemy in self.enemies:
            if enemy.alive:
                enemy_map_x = int(map_x + (enemy.x / TILE_SIZE) * map_scale)
                enemy_map_y = int(map_y + (enemy.y / TILE_SIZE) * map_scale)
                
                if (map_x <= enemy_map_x <= map_x + map_size and 
                    map_y <= enemy_map_y <= map_y + map_size):
                    pygame.draw.circle(self.screen, RED, (enemy_map_x, enemy_map_y), 3)
        
        # Draw bosses on minimap
        for boss in self.bosses:
            if boss.alive:
                boss_map_x = int(map_x + (boss.x / TILE_SIZE) * map_scale)
                boss_map_y = int(map_y + (boss.y / TILE_SIZE) * map_scale)
                
                if (map_x <= boss_map_x <= map_x + map_size and 
                    map_y <= boss_map_y <= map_y + map_size):
                    pygame.draw.circle(self.screen, PURPLE, (boss_map_x, boss_map_y), 5)
                    
        # Draw player on minimap
        player_map_x = int(map_x + (self.player.x / TILE_SIZE) * map_scale)
        player_map_y = int(map_y + (self.player.y / TILE_SIZE) * map_scale)
        
        if (map_x <= player_map_x <= map_x + map_size and 
            map_y <= player_map_y <= map_y + map_size):
            pygame.draw.circle(self.screen, YELLOW, (player_map_x, player_map_y), 4)
            
            # Draw player direction indicator
            end_x = player_map_x + int(math.cos(self.player.angle) * 8)
            end_y = player_map_y + int(math.sin(self.player.angle) * 8)
            pygame.draw.line(self.screen, YELLOW, (player_map_x, player_map_y), (end_x, end_y), 2)
        
        label_text = "Arena"
        label_surface = self.small_font.render(label_text, True, WHITE)
        self.screen.blit(label_surface, (map_x, map_y + map_size + 5))
            
    def draw_health_bars(self):
        """Draw health bars for enemies and bosses"""
        for enemy in self.enemies:
            if enemy.alive and enemy.health < enemy.max_health:
                self.draw_enemy_health_bar(enemy)
                
        for boss in self.bosses:
            if boss.alive:
                self.draw_boss_health_bar(boss)
                
    def draw_enemy_health_bar(self, enemy):
        """Draw health bar above enemy"""
        dx = enemy.x - self.player.x
        dy = enemy.y - self.player.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 300:
            return
            
        angle_to_enemy = math.atan2(dy, dx)
        angle_diff = angle_to_enemy - self.player.angle
        
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
            
        if abs(angle_diff) > HALF_FOV: 
            return
            
        screen_x = (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2) + (SCREEN_WIDTH // 2)
        screen_y = SCREEN_HEIGHT // 2 - int(100 / max(distance / 100, 1))
        
        bar_width = 30
        bar_height = 4
        
        bar_x = screen_x - bar_width // 2
        bar_y = screen_y - 20
        
        # Draw health bar background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, RED, bg_rect)
        
        # Draw health bar fill
        health_percentage = enemy.health / enemy.max_health
        if health_percentage > 0.6:
            health_color = GREEN
        elif health_percentage > 0.3:
            health_color = YELLOW
        else:
            health_color = RED
            
        health_width = int(bar_width * health_percentage)
        health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
        pygame.draw.rect(self.screen, health_color, health_rect)
        
        pygame.draw.rect(self.screen, WHITE, bg_rect, 2)
            
    def draw_ui(self):
        """Draw arena UI with visual health/mana bars"""
        self.draw_player_bars()
        
        # Draw wave stats
        stats_y = 80
        stats = [
            f"Wave: {self.current_wave}",
            f"Gold: {self.player.gold}",
            f"Score: {self.player.total_score}"
        ]
        
        for i, stat in enumerate(stats):
            color = WHITE
            stat_text = self.font.render(stat, True, color)
            self.screen.blit(stat_text, (10, stats_y + i * 30))
            
        # Show enemy count
        enemies_remaining = len(self.enemies) + len(self.bosses)
        if enemies_remaining > 0:
            enemies_text = f"Enemies: {enemies_remaining}"
            text_surface = self.font.render(enemies_text, True, RED)
            self.screen.blit(text_surface, (10, stats_y + len(stats) * 30))
            
        # Show wave status
        if self.between_waves:
            wave_text = f"Wave {self.current_wave} Starting..."
            text_surface = self.large_font.render(wave_text, True, YELLOW)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
            self.screen.blit(text_surface, text_rect)
        elif self.boss_wave and len(self.bosses) > 0:
            boss_text = "BOSS WAVE!"
            
            # Pulsing boss text
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 0.3 + 0.7
            scaled_font = pygame.font.Font(None, int(48 * pulse))
            boss_text_pulsed = scaled_font.render(boss_text, True, RED)
            text_rect = boss_text_pulsed.get_rect(center=(SCREEN_WIDTH // 2, 80))
            self.screen.blit(boss_text_pulsed, text_rect)
            
        # Spell UI
        current_time = pygame.time.get_ticks()
        spell_y = SCREEN_HEIGHT - 120
        
        current_spell_text = f"Current Spell: {self.player.current_spell.title()}"
        spell_colors = {
            "fireball": ORANGE,
            "lightning": YELLOW,
            "ice": LIGHT_BLUE,
            "heal": GREEN,
            "shield": PURPLE,
            "teleport": (255, 0, 255)
        }
        spell_color = spell_colors.get(self.player.current_spell, WHITE)
        
        current_spell_surface = self.font.render(current_spell_text, True, spell_color)
        self.screen.blit(current_spell_surface, (10, spell_y - 60))
        
        # Show mana cost
        mana_cost = self.player.spell_costs[self.player.current_spell]
        can_cast = self.player.mana >= mana_cost
        cost_color = spell_color if can_cast else GRAY
        
        cost_text = f"Mana Cost: {mana_cost}"
        cost_surface = self.small_font.render(cost_text, True, cost_color)
        self.screen.blit(cost_surface, (10, spell_y - 35))
        
        # Mouse controls
        mouse_controls = [
            "Left Click: Cast Spell",
            "Right Click: Change Spell"
        ]
        
        for i, control in enumerate(mouse_controls):
            control_color = spell_color if i == 0 and can_cast else WHITE
            control_surface = self.small_font.render(control, True, control_color)
            self.screen.blit(control_surface, (10, spell_y + i * 20))
        
        # Show available spells
        available_spells = self.player.get_available_spells()
        if len(available_spells) > 1:
            spells_text = "Available: " + ", ".join([s.title() for s in available_spells])
            spells_surface = self.small_font.render(spells_text, True, GRAY)
            self.screen.blit(spells_surface, (10, spell_y + 45))
            
        # Basic controls
        controls = [
            "WASD: Move",
            "Mouse: Look & Cast",
        ]
        
        for i, control in enumerate(controls):
            control_text = self.small_font.render(control, True, GRAY)
            control_rect = control_text.get_rect(right=SCREEN_WIDTH - 10)
            self.screen.blit(control_text, (control_rect.x, spell_y + i * 22))

    def draw_player_bars(self):
        """Draw visual health and mana bars"""
        bar_x = 10
        bar_y = 10
        bar_width = 200
        bar_height = 25
        
        # Health bar
        health_percentage = self.player.health / self.player.get_max_health()
        
        health_bg = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, DARK_RED, health_bg)
        
        health_fill_width = int(bar_width * health_percentage)
        health_fill = pygame.Rect(bar_x, bar_y, health_fill_width, bar_height)
        
        if health_percentage > 0.6:
            health_color = GREEN
        elif health_percentage > 0.3:
            health_color = YELLOW
        else:
            health_color = RED
            
        pygame.draw.rect(self.screen, health_color, health_fill)
        pygame.draw.rect(self.screen, WHITE, health_bg, 2)
        
        health_text = f"Health: {int(self.player.health)}/{self.player.get_max_health()}"
        health_surface = self.small_font.render(health_text, True, WHITE)
        text_rect = health_surface.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
        self.screen.blit(health_surface, text_rect)
        
        # Mana bar
        mana_y = bar_y + bar_height + 10
        mana_percentage = self.player.mana / self.player.get_max_mana()
        
        mana_bg = pygame.Rect(bar_x, mana_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (0, 0, 50), mana_bg) 
        
        mana_fill_width = int(bar_width * mana_percentage)
        mana_fill = pygame.Rect(bar_x, mana_y, mana_fill_width, bar_height)
        
        if mana_percentage > 0.6:
            mana_color = BLUE
        elif mana_percentage > 0.3:
            mana_color = (100, 100, 255)  
        else:
            mana_color = (50, 50, 150) 
            
        pygame.draw.rect(self.screen, mana_color, mana_fill)
        pygame.draw.rect(self.screen, WHITE, mana_bg, 2)
        
        mana_text = f"Mana: {int(self.player.mana)}/{self.player.get_max_mana()}"
        mana_surface = self.small_font.render(mana_text, True, WHITE)
        text_rect = mana_surface.get_rect(center=(bar_x + bar_width // 2, mana_y + bar_height // 2))
        self.screen.blit(mana_surface, text_rect)
            
    def draw_shop_prompt(self):
        """Draw shop prompt after boss defeat"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        box_width = 450
        box_height = 250
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        
        pygame.draw.rect(self.screen, DARK_GRAY, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, GOLD, (box_x, box_y, box_width, box_height), 3)
        
        time_remaining = (self.shop_prompt_duration - (pygame.time.get_ticks() - self.shop_prompt_timer)) // 1000
        
        texts = [
            "BOSS DEFEATED!",
            f"Wave {self.current_wave} Complete!",
            f"Gold Earned: {self.bosses[0].score_value if self.bosses else 'N/A'}",
            "",
            "Visit town to buy upgrades?",
            "• Heal and restore mana",
            "• Buy better weapons & armor", 
            "• Upgrade magical abilities",
            "",
            "Y - Go to Town",
            "N - Continue Fighting",
            "",
            f"Auto-continue in {time_remaining}s"
        ]
        
        for i, text in enumerate(texts):
            if "BOSS DEFEATED" in text:
                color = GOLD
                font = self.large_font
            elif "Wave" in text and "Complete" in text:
                color = GREEN
                font = self.font
            elif "Gold Earned" in text:
                color = YELLOW
                font = self.small_font
            elif text in ["Y - Go to Town", "N - Continue Fighting"]:
                color = YELLOW
                font = self.font
            elif text.startswith("•"):
                color = LIGHT_BLUE
                font = self.small_font
            else:
                color = WHITE
                font = self.small_font
                
            if text:
                text_surface = font.render(text, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, box_y + 25 + i * 18))
                self.screen.blit(text_surface, text_rect)
        
    def draw_boss_health_bar(self, boss):
        """Draw boss health bar at top of screen"""
        bar_width = 300
        bar_height = 20
        
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = 20
        
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, DARK_RED, bg_rect)
        
        health_percentage = boss.get_health_percentage()
        if health_percentage > 0.5:
            health_color = GREEN
        elif health_percentage > 0.25:
            health_color = YELLOW
        else:
            health_color = RED
            
        health_width = int(bar_width * health_percentage)
        health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
        pygame.draw.rect(self.screen, health_color, health_rect)
        
        pygame.draw.rect(self.screen, WHITE, bg_rect, 2)
        
        # Boss name and health text
        boss_names = {
            BossType.NECROMANCER: "Necromancer",
            BossType.ORC_CHIEFTAIN: "Orc Chieftain", 
            BossType.ANCIENT_TROLL: "Ancient Troll",
            BossType.DEMON_LORD: "Demon Lord"
        }
        name_text = boss_names.get(boss.boss_type, "Boss")
        
        if boss.boss_type == BossType.ORC_CHIEFTAIN and hasattr(boss, 'rage_mode') and boss.rage_mode:
            name_text += " (ENRAGED)"
            
        health_text = f"{name_text}: {int(boss.health)}/{boss.max_health}"
        
        text_surface = self.font.render(health_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(bar_x + bar_width // 2, bar_y - 15))
        self.screen.blit(text_surface, text_rect)
        
    def draw_game_over_screen(self):
        """Draw game over screen with stats"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        box_width = 500
        box_height = 300
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        
        pygame.draw.rect(self.screen, DARK_RED, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, RED, (box_x, box_y, box_width, box_height), 4)
        
        time_remaining = (self.game_over_duration - (pygame.time.get_ticks() - self.game_over_timer)) // 1000
        
        texts = [
            "GAME OVER",
            "",
            f"Wave Reached: {self.current_wave}",
            f"Total Score: {self.player.total_score}",
            f"Gold Earned: {self.player.gold}",
            f"Highest Wave: {self.player.highest_wave}",
            "",
            "Final Stats:",
            f"Weapon Level: {self.player.weapon_level}",
            f"Armor Level: {self.player.armor_level}",
            f"Magic Level: {self.player.spell_level}",
            "",
            "Press any key to return to menu",
            f"Auto-return in {time_remaining}s"
        ]
        
        for i, text in enumerate(texts):
            if "GAME OVER" in text:
                color = RED
                font = self.large_font
            elif text in ["Final Stats:", f"Wave Reached: {self.current_wave}"]:
                color = YELLOW
                font = self.font
            elif text.startswith("Total Score:") or text.startswith("Gold Earned:"):
                color = GOLD
                font = self.font
            elif text.startswith("Highest Wave:"):
                color = WHITE
                font = self.font
            elif "Press any key" in text:
                color = GREEN
                font = self.small_font
            elif "Auto-return" in text:
                color = GRAY
                font = self.small_font
            else:
                color = WHITE
                font = self.small_font
                
            if text: 
                text_surface = font.render(text, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, box_y + 30 + i * 18))
                self.screen.blit(text_surface, text_rect)