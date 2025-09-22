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
        
        # Initialize arena map and raycaster
        self.arena_map = ArenaMap()
        self.raycaster = RayCaster(screen)
        
        # Sound manager - will be set by game manager
        self.sound_manager = None
        
        # Game state
        self.enemies = []
        self.bosses = []
        self.spells = []
        
        # Wave system - persistent across visits
        self.current_wave = 1
        self.wave_progress_saved = False  # Track if we came from shop after boss
        self.enemies_remaining = 0
        self.wave_completed = False
        self.wave_start_time = 0
        self.between_waves = False
        self.wave_delay = 3000  # 3 seconds between waves
        
        # Boss system
        self.boss_wave = False
        self.boss_defeated = False
        self.show_shop_prompt = False
        self.shop_prompt_timer = 0
        self.shop_prompt_duration = 10000  # 10 seconds to decide
        
        # Game over system
        self.game_over = False
        self.game_over_timer = 0
        self.game_over_duration = 5000  # 5 seconds before auto-return to menu
        
        # UI
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
        # Arena center for spawning
        self.arena_center_x = 10 * TILE_SIZE
        self.arena_center_y = 10 * TILE_SIZE
        self.spawn_radius = 7 * TILE_SIZE
        
    def initialize_arena(self):
        """Initialize/reset arena for new session"""
        # Place player at arena center
        self.player.x = self.arena_center_x
        self.player.y = self.arena_center_y
        self.player.angle = 0
        
        # Reset player health and mana
        self.player.reset_for_arena()
        
        # Only reset to wave 1 if not continuing from shop
        if not self.wave_progress_saved:
            self.current_wave = 1
        
        # Always reset these
        self.enemies = []
        self.bosses = []
        self.spells = []
        self.wave_completed = False
        self.between_waves = False
        self.boss_wave = False
        self.boss_defeated = False
        self.show_shop_prompt = False
        
        # Start current wave
        self.start_wave()
        
    def continue_from_shop(self):
        """Continue arena after visiting shop - preserve wave"""
        self.wave_progress_saved = True
        self.current_wave += 1  # Move to next wave after shop visit
        self.initialize_arena()
        self.wave_progress_saved = False  # Reset flag
        
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
        # Play wave complete sound
        if self.sound_manager:
            self.sound_manager.play_sound('wave_complete')
        self.start_wave()
        
    def start_wave(self):
        """Start a new wave"""
        self.wave_start_time = pygame.time.get_ticks()
        self.wave_completed = False
        self.between_waves = False
        
        # Check if this is a boss wave (every 5th wave)
        if self.current_wave % 5 == 0:
            self.start_boss_wave()
        else:
            self.start_regular_wave()
            
    def start_regular_wave(self):
        """Start a regular enemy wave"""
        self.boss_wave = False
        
        # Calculate number of enemies based on wave
        base_enemies = 4
        additional_enemies = (self.current_wave - 1) // 2  # +1 enemy every 2 waves
        num_enemies = base_enemies + additional_enemies
        
        # Spawn enemies
        for _ in range(num_enemies):
            self.spawn_enemy()
            
        self.enemies_remaining = len(self.enemies)
        
    def start_boss_wave(self):
        """Start a boss wave"""
        self.boss_wave = True
        
        # Play boss spawn sound
        if self.sound_manager:
            self.sound_manager.play_sound('boss_spawn')
        
        # Determine boss type based on wave number
        boss_types = [BossType.NECROMANCER, BossType.ORC_CHIEFTAIN, BossType.ANCIENT_TROLL, BossType.DEMON_LORD]
        boss_index = ((self.current_wave // 5) - 1) % len(boss_types)
        boss_type = boss_types[boss_index]
        
        # Spawn boss at a safe distance from player
        boss_x, boss_y = self.get_spawn_position()
        boss = Boss(boss_x, boss_y, boss_type, self)  # Pass arena reference
        
        # Scale boss for higher waves
        wave_multiplier = 1.0 + ((self.current_wave - 5) // 5) * 0.5  # +50% stats every 5 waves
        boss.health = int(boss.health * wave_multiplier)
        boss.max_health = boss.health
        boss.attack_damage = int(boss.attack_damage * wave_multiplier)
        
        self.bosses.append(boss)
        
        # Don't spawn additional minions here - bosses handle their own minions
        self.enemies_remaining = len(self.enemies) + len(self.bosses)
        
    def spawn_enemy(self):
        """Spawn a random enemy"""
        # Choose enemy type based on wave progression
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
        
        # Scale enemy stats based on wave level
        health_multiplier = 1.0 + (self.current_wave - 1) * 0.3  # +30% health per wave
        damage_multiplier = 1.0 + (self.current_wave - 1) * 0.2  # +20% damage per wave
        
        enemy.health = int(enemy.health * health_multiplier)
        enemy.max_health = enemy.health
        enemy.attack_damage = int(enemy.attack_damage * damage_multiplier)
        
        self.enemies.append(enemy)
        
    def get_spawn_position(self):
        """Get a valid spawn position around the arena"""
        attempts = 0
        while attempts < 50:  # Prevent infinite loop
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(self.spawn_radius * 0.7, self.spawn_radius)
            
            x = self.arena_center_x + math.cos(angle) * distance
            y = self.arena_center_y + math.sin(angle) * distance
            
            # Check if position is valid and not too close to player
            if not self.check_spawn_collision(x, y) and self.get_distance_to_player(x, y) > 100:
                return x, y
            attempts += 1
            
        # Fallback position if can't find good spot
        return self.arena_center_x + 200, self.arena_center_y + 200
                
    def check_spawn_collision(self, x, y):
        """Check if spawn position collides with walls"""
        map_x = int(x // TILE_SIZE)
        map_y = int(y // TILE_SIZE)
        
        if map_x < 0 or map_x >= 20 or map_y < 0 or map_y >= 20:
            return True
            
        center_x, center_y = 10, 10
        distance = math.sqrt((map_x - center_x) ** 2 + (map_y - center_y) ** 2)
        
        return distance > 8
        
    def get_distance_to_player(self, x, y):
        """Get distance from position to player"""
        dx = x - self.player.x
        dy = y - self.player.y
        return math.sqrt(dx * dx + dy * dy)
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.game_over:
                # Any key press during game over returns to menu
                self.game_manager.change_state(GameState.MENU)
                return
            elif self.show_shop_prompt:
                if event.key == pygame.K_y:
                    # Go to shop
                    self.game_manager.change_state(GameState.TOWN)
                elif event.key == pygame.K_n:
                    # Continue arena
                    self.continue_arena()
            else:
                # Spell casting with keyboard (backup)
                if event.key == pygame.K_1:
                    self.cast_spell(self.player.current_spell)
                elif event.key == pygame.K_2:
                    self.cycle_spell()
                elif event.key == pygame.K_3:
                    self.cycle_spell()
        elif event.type == pygame.MOUSEBUTTONDOWN and not self.show_shop_prompt and not self.game_over:
            # Mouse controls
            if event.button == 1:  # Left click - cast current spell
                self.cast_spell(self.player.current_spell)
            elif event.button == 3:  # Right click - cycle through spells
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
        
        # Play menu select sound for spell cycling
        if self.sound_manager:
            self.sound_manager.play_sound('menu_select')
            
    def cast_spell(self, spell_type):
        """Cast a spell (no cooldowns, only mana cost)"""
        if self.player.mana >= self.player.spell_costs[spell_type]:
            # Deduct mana cost
            self.player.mana -= self.player.spell_costs[spell_type]
            
            # Handle heal spell specially
            if spell_type == "heal":
                heal_amount = 20 * self.player.get_spell_damage_multiplier()
                self.player.heal(heal_amount)
                # Play heal sound but no casting sound
                if self.sound_manager:
                    self.sound_manager.play_sound('heal')
                return  # Don't create projectile for heal
            
            # Create spell projectile for damage spells - NO casting sound
            spell = Spell(self.player.x, self.player.y, self.player.angle, spell_type, self.sound_manager)
            # Apply spell level damage multiplier
            spell.damage = int(spell.damage * self.player.get_spell_damage_multiplier())
            self.spells.append(spell)
                
    def update(self, dt):
        current_time = pygame.time.get_ticks()
        
        # Handle game over state
        if self.game_over:
            if current_time - self.game_over_timer > self.game_over_duration:
                # Auto-return to menu after 5 seconds
                self.game_manager.change_state(GameState.MENU)
            return
        
        # Handle shop prompt timeout
        if self.show_shop_prompt:
            if current_time - self.shop_prompt_timer > self.shop_prompt_duration:
                # Auto-continue if player doesn't decide
                self.continue_arena()
            return
        
        # Update player
        keys = pygame.key.get_pressed()
        old_x, old_y = self.player.x, self.player.y
        
        self.player.move(keys, dt, self.arena_map.collision_map, 
                        self.arena_map.width, self.arena_map.height)
        
        # Check collision and rollback if necessary
        player_tile_x = int(self.player.x // TILE_SIZE)
        player_tile_y = int(self.player.y // TILE_SIZE)
        
        if (player_tile_x < 0 or player_tile_x >= self.arena_map.width or
            player_tile_y < 0 or player_tile_y >= self.arena_map.height or
            self.arena_map.collision_map[player_tile_y][player_tile_x] != 0):
            self.player.x, self.player.y = old_x, old_y
            
        self.player.update(dt)
        
        # Update enemies with death sounds
        for enemy in self.enemies[:]:
            old_health = enemy.health
            enemy.update(self.player, dt, current_time)
            
            # Check if enemy took damage and play hit sound
            if enemy.alive and enemy.health < old_health:
                if self.sound_manager:
                    self.sound_manager.play_sound('enemy_hit')
            
            if not enemy.alive:
                self.player.add_gold(enemy.score_value)
                self.player.total_score += enemy.score_value
                self.enemies.remove(enemy)
                # Play enemy death sound
                if self.sound_manager:
                    self.sound_manager.play_sound('enemy_death')
                
        # Update bosses with death sounds
        for boss in self.bosses[:]:
            old_health = boss.health
            boss.update(self.player, dt, current_time)
            
            # Check if boss took damage and play hit sound
            if boss.alive and boss.health < old_health:
                if self.sound_manager:
                    self.sound_manager.play_sound('enemy_hit')
            
            if not boss.alive:
                self.player.add_gold(boss.score_value)
                self.player.total_score += boss.score_value
                self.bosses.remove(boss)
                if self.boss_wave:
                    self.boss_defeated = True
                # Play enemy death sound (bosses use same sound)
                if self.sound_manager:
                    self.sound_manager.play_sound('enemy_death')
                    
        # Update spells with sound feedback
        for spell in self.spells[:]:
            spell.update(dt, self.arena_map.collision_map, 
                        self.arena_map.width, self.arena_map.height)
            
            if not spell.alive:
                self.spells.remove(spell)
                continue
                
            # Check spell collisions with enemies
            for enemy in self.enemies:
                if enemy.alive and self.check_spell_collision(spell, enemy):
                    enemy.take_damage(spell.damage)
                    spell.on_hit_target()  # Play hit sound
                    spell.alive = False
                    break
                    
            # Check spell collisions with bosses
            for boss in self.bosses:
                if boss.alive and self.check_spell_collision(spell, boss):
                    boss.take_damage(spell.damage)
                    spell.on_hit_target()  # Play hit sound
                    spell.alive = False
                    break
        
        # Check wave completion
        if not self.between_waves and len(self.enemies) == 0 and len(self.bosses) == 0:
            self.wave_completed = True
            
            if self.boss_wave and self.boss_defeated:
                # Show shop prompt after boss defeat
                self.show_shop_prompt = True
                self.shop_prompt_timer = current_time
            else:
                # Start next wave after delay
                self.between_waves = True
                self.wave_start_time = current_time
                # Play wave complete sound
                if self.sound_manager:
                    self.sound_manager.play_sound('wave_complete')
                
        # Handle wave transitions
        if self.between_waves and current_time - self.wave_start_time > self.wave_delay:
            self.current_wave += 1
            self.player.highest_wave = max(self.player.highest_wave, self.current_wave)
            self.start_wave()
            
        # Check player death
        if self.player.health <= 0:
            self.trigger_game_over(current_time)
            
    def trigger_game_over(self, current_time):
        """Trigger game over screen"""
        self.game_over = True
        self.game_over_timer = current_time
        # Play player death sound - could add a specific game over sound
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
        
        # Cast rays and render 3D view
        rays = self.raycaster.cast_rays(self.player, self.arena_map.collision_map,
                                       self.arena_map.width, self.arena_map.height)
        self.raycaster.render_3d_arena(rays, self.enemies, self.spells, self.player)
        
        # Render bosses manually if raycaster doesn't support them
        if self.bosses:
            self.render_bosses_3d()
        
        # Render spell trails over 3D view
        for spell in self.spells:
            if hasattr(spell, 'render_trail'):
                spell.render_trail(self.screen)
        
        # Draw 2D health bars and effects over 3D view
        self.draw_health_bars()
        
        # Draw UI
        self.draw_ui()
        
        # Draw shop prompt if needed
        if self.show_shop_prompt:
            self.draw_shop_prompt()
            
        # Draw game over screen if needed
        if self.game_over:
            self.draw_game_over_screen()
            
    def draw_game_over_screen(self):
        """Draw game over screen with stats"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over box
        box_width = 500
        box_height = 300
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        
        pygame.draw.rect(self.screen, DARK_RED, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, RED, (box_x, box_y, box_width, box_height), 4)
        
        # Game over text
        time_remaining = (self.game_over_duration - (pygame.time.get_ticks() - self.game_over_timer)) // 1000
        
        texts = [
            "💀 GAME OVER 💀",
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
                
            if text:  # Skip empty strings
                text_surface = font.render(text, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, box_y + 30 + i * 18))
                self.screen.blit(text_surface, text_rect)
            
    def render_bosses_3d(self):
        """Render bosses in 3D space (similar to enemies)"""
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
            
            # Normalize angle difference
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
                
            # Check if boss is in FOV
            if abs(angle_diff) < HALF_FOV:
                screen_x = (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2) + (SCREEN_WIDTH // 2)
                
                boss_scale = max(12, int(boss.size * 1200 / (boss_distance + 0.1)))  # Bosses larger than enemies
                boss_width = boss_scale
                boss_height = boss_scale * 1.5  # Bosses are taller
                
                boss_y = (SCREEN_HEIGHT - boss_height) // 2 + view_bob
                
                # Scale the boss image to the calculated size
                if hasattr(boss, 'image') and boss.image:
                    scaled_boss = pygame.transform.scale(boss.image, (int(boss_width), int(boss_height)))
                    
                    # Apply distance-based darkening
                    if boss_distance > 150:  # Darken distant bosses
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
                        
                    # Add rage effect for Orc Chieftain
                    if hasattr(boss, 'rage_mode') and boss.rage_mode:
                        rage_rect = pygame.Rect(screen_x - boss_width // 2, boss_y, boss_width, boss_height)
                        pygame.draw.rect(self.screen, RED, rage_rect, 3)
                else:
                    # Fallback to colored rectangle
                    boss_rect = (
                        screen_x - boss_width // 2,
                        boss_y,
                        boss_width,
                        boss_height
                    )
                    pygame.draw.rect(self.screen, boss.color, boss_rect)
                
                # Draw boss name if close enough
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
                    
                    # Draw background for name
                    bg_rect = name_rect.inflate(6, 4)
                    pygame.draw.rect(self.screen, BLACK, bg_rect)
                    pygame.draw.rect(self.screen, boss.color, bg_rect, 2)
                    
                    self.screen.blit(name_surface, name_rect)
            
    def draw_health_bars(self):
        """Draw health bars for enemies and bosses"""
        # Draw enemy health bars
        for enemy in self.enemies:
            if enemy.alive and enemy.health < enemy.max_health:
                self.draw_enemy_health_bar(enemy)
                
        # Draw boss health bars
        for boss in self.bosses:
            if boss.alive:
                self.draw_boss_health_bar(boss)
                
    def draw_enemy_health_bar(self, enemy):
        """Draw health bar above enemy (simplified 2D version)"""
        # Calculate screen position (this is simplified - in a real 3D engine you'd project 3D to 2D)
        # For now, we'll use a simple distance-based approximation
        dx = enemy.x - self.player.x
        dy = enemy.y - self.player.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 300:  # Don't show health bars for distant enemies
            return
            
        # Simple screen position calculation (this is a placeholder)
        # In a real implementation, you'd use the raycasting engine's projection
        angle_to_enemy = math.atan2(dy, dx)
        angle_diff = angle_to_enemy - self.player.angle
        
        # Normalize angle
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
            
        if abs(angle_diff) > HALF_FOV:  # Enemy not in view
            return
            
        screen_x = (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2) + (SCREEN_WIDTH // 2)
        screen_y = SCREEN_HEIGHT // 2 - int(100 / max(distance / 100, 1))  # Rough height calculation
        
        # Health bar dimensions
        bar_width = 30
        bar_height = 4
        
        bar_x = screen_x - bar_width // 2
        bar_y = screen_y - 20
        
        # Background (red)
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, RED, bg_rect)
        
        # Health (green to red based on health)
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
        
        # Border
        pygame.draw.rect(self.screen, WHITE, bg_rect, 2)
            
    def draw_ui(self):
        """Draw arena UI with visual health/mana bars"""
        # Draw visual health and mana bars at top left
        self.draw_player_bars()
        
        # Player stats text
        stats_y = 80  # Moved down to make room for bars
        stats = [
            f"Wave: {self.current_wave}",
            f"Gold: {self.player.gold}",
            f"Score: {self.player.total_score}"
        ]
        
        for i, stat in enumerate(stats):
            color = WHITE
            stat_text = self.font.render(stat, True, color)
            self.screen.blit(stat_text, (10, stats_y + i * 30))
            
        # Enemies remaining
        enemies_remaining = len(self.enemies) + len(self.bosses)
        if enemies_remaining > 0:
            enemies_text = f"Enemies: {enemies_remaining}"
            text_surface = self.font.render(enemies_text, True, RED)
            self.screen.blit(text_surface, (10, stats_y + len(stats) * 30))
            
        # Wave status
        if self.between_waves:
            wave_text = f"Wave {self.current_wave} Starting..."
            text_surface = self.large_font.render(wave_text, True, YELLOW)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
            self.screen.blit(text_surface, text_rect)
        elif self.boss_wave and len(self.bosses) > 0:  # Only show if boss is actually present
            boss_text = "BOSS WAVE!"
            
            # Add pulsing effect for boss wave announcement
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 0.3 + 0.7
            scaled_font = pygame.font.Font(None, int(48 * pulse))
            boss_text_pulsed = scaled_font.render(boss_text, True, RED)
            text_rect = boss_text_pulsed.get_rect(center=(SCREEN_WIDTH // 2, 80))
            self.screen.blit(boss_text_pulsed, text_rect)
            
        # Current spell display and mouse controls
        current_time = pygame.time.get_ticks()
        spell_y = SCREEN_HEIGHT - 120
        
        # Current spell indicator
        current_spell_text = f"Current Spell: {self.player.current_spell.title()}"
        spell_colors = {
            "fireball": ORANGE,
            "lightning": YELLOW,
            "ice": LIGHT_BLUE,
            "heal": GREEN,
            "shield": PURPLE,
            "teleport": (255, 0, 255)  # Magenta
        }
        spell_color = spell_colors.get(self.player.current_spell, WHITE)
        
        current_spell_surface = self.font.render(current_spell_text, True, spell_color)
        self.screen.blit(current_spell_surface, (10, spell_y - 60))
        
        # Mana cost for current spell
        mana_cost = self.player.spell_costs[self.player.current_spell]
        can_cast = self.player.mana >= mana_cost
        cost_color = spell_color if can_cast else GRAY
        
        cost_text = f"Mana Cost: {mana_cost}"
        cost_surface = self.small_font.render(cost_text, True, cost_color)
        self.screen.blit(cost_surface, (10, spell_y - 35))
        
        # Mouse control instructions
        mouse_controls = [
            "Left Click: Cast Spell",
            "Right Click: Change Spell"
        ]
        
        for i, control in enumerate(mouse_controls):
            control_color = spell_color if i == 0 and can_cast else WHITE
            control_surface = self.small_font.render(control, True, control_color)
            self.screen.blit(control_surface, (10, spell_y + i * 20))
        
        # Available spells list
        available_spells = self.player.get_available_spells()
        if len(available_spells) > 1:
            spells_text = "Available: " + ", ".join([s.title() for s in available_spells])
            spells_surface = self.small_font.render(spells_text, True, GRAY)
            self.screen.blit(spells_surface, (10, spell_y + 45))
            
        # Controls
        controls = [
            "WASD: Move",
            "Mouse: Look & Cast",
            "1/2/3: Spells (Alt)",
            "ESC: Menu"
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
        
        # Health bar background
        health_bg = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, DARK_RED, health_bg)
        
        # Health bar fill
        health_fill_width = int(bar_width * health_percentage)
        health_fill = pygame.Rect(bar_x, bar_y, health_fill_width, bar_height)
        
        # Color based on health level
        if health_percentage > 0.6:
            health_color = GREEN
        elif health_percentage > 0.3:
            health_color = YELLOW
        else:
            health_color = RED
            
        pygame.draw.rect(self.screen, health_color, health_fill)
        
        # Health bar border
        pygame.draw.rect(self.screen, WHITE, health_bg, 2)
        
        # Health text
        health_text = f"Health: {int(self.player.health)}/{self.player.get_max_health()}"
        health_surface = self.small_font.render(health_text, True, WHITE)
        text_rect = health_surface.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
        self.screen.blit(health_surface, text_rect)
        
        # Mana bar (below health bar)
        mana_y = bar_y + bar_height + 10
        mana_percentage = self.player.mana / self.player.get_max_mana()
        
        # Mana bar background
        mana_bg = pygame.Rect(bar_x, mana_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (0, 0, 50), mana_bg)  # Dark blue
        
        # Mana bar fill
        mana_fill_width = int(bar_width * mana_percentage)
        mana_fill = pygame.Rect(bar_x, mana_y, mana_fill_width, bar_height)
        
        # Mana color
        if mana_percentage > 0.6:
            mana_color = BLUE
        elif mana_percentage > 0.3:
            mana_color = (100, 100, 255)  # Light blue
        else:
            mana_color = (50, 50, 150)   # Dark blue
            
        pygame.draw.rect(self.screen, mana_color, mana_fill)
        
        # Mana bar border
        pygame.draw.rect(self.screen, WHITE, mana_bg, 2)
        
        # Mana text
        mana_text = f"Mana: {int(self.player.mana)}/{self.player.get_max_mana()}"
        mana_surface = self.small_font.render(mana_text, True, WHITE)
        text_rect = mana_surface.get_rect(center=(bar_x + bar_width // 2, mana_y + bar_height // 2))
        self.screen.blit(mana_surface, text_rect)
            
    def draw_shop_prompt(self):
        """Draw shop prompt after boss defeat"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Prompt box
        box_width = 450
        box_height = 250
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        
        pygame.draw.rect(self.screen, DARK_GRAY, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, GOLD, (box_x, box_y, box_width, box_height), 3)
        
        # Text
        time_remaining = (self.shop_prompt_duration - (pygame.time.get_ticks() - self.shop_prompt_timer)) // 1000
        
        texts = [
            "🎉 BOSS DEFEATED! 🎉",
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
                
            if text:  # Skip empty strings
                text_surface = font.render(text, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, box_y + 25 + i * 18))
                self.screen.blit(text_surface, text_rect)
        
    def draw_boss_health_bar(self, boss):
        """Draw boss health bar at top of screen"""
        # Boss health bar is large and prominent at top of screen
        bar_width = 300
        bar_height = 20
        
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = 20
        
        # Background (dark red)
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, DARK_RED, bg_rect)
        
        # Health (color based on health percentage)
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
        
        # Border
        pygame.draw.rect(self.screen, WHITE, bg_rect, 2)
        
        # Boss name and health text
        boss_names = {
            BossType.NECROMANCER: "Necromancer",
            BossType.ORC_CHIEFTAIN: "Orc Chieftain", 
            BossType.ANCIENT_TROLL: "Ancient Troll",
            BossType.DEMON_LORD: "Demon Lord"
        }
        name_text = boss_names.get(boss.boss_type, "Boss")
        
        # Add rage indicator for Orc Chieftain
        if boss.boss_type == BossType.ORC_CHIEFTAIN and hasattr(boss, 'rage_mode') and boss.rage_mode:
            name_text += " (ENRAGED)"
            
        health_text = f"{name_text}: {int(boss.health)}/{boss.max_health}"
        
        text_surface = self.font.render(health_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(bar_x + bar_width // 2, bar_y - 15))
        self.screen.blit(text_surface, text_rect)