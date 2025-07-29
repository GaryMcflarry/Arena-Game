import pygame
import math
import random
from constants import SPELL_TYPES, BossType, GameState
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
        
        # Initialize arena map
        self.arena_map = ArenaMap()
        self.raycaster = RayCaster(screen)
        
        # Game state
        self.enemies = []
        self.bosses = []
        self.spells = []
        self.score = 0
        self.current_wave = 0
        self.wave_active = False
        self.enemies_killed_this_wave = 0
        self.wave_start_time = 0
        self.time_between_waves = 5000  # 5 seconds
        self.show_map = False
        
        # Wave configuration
        self.waves_per_boss = 5  # Boss every 5 waves
        self.max_waves = 20
        
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
        
    def initialize_arena(self):
        """Initialize/reset arena for new run"""
        # Reset player stats for arena
        self.player.reset_for_arena()
        
        # Place player in center of arena
        center_x = self.arena_map.width * TILE_SIZE // 2
        center_y = self.arena_map.height * TILE_SIZE // 2
        self.player.x = center_x
        self.player.y = center_y
        self.player.angle = 0
        
        # Reset arena state
        self.enemies = []
        self.bosses = []
        self.spells = []
        self.score = 0
        self.current_wave = 0
        self.wave_active = False
        self.enemies_killed_this_wave = 0
        self.wave_start_time = 0
        
        self.start_next_wave()
        
    def get_spawn_positions(self, count):
        """Get random spawn positions around the arena edge"""
        positions = []
        center_x, center_y = self.arena_map.width // 2, self.arena_map.height // 2
        
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
        """Start the next wave of enemies"""
        self.current_wave += 1
        self.wave_active = True
        self.enemies_killed_this_wave = 0
        self.wave_start_time = pygame.time.get_ticks()
        
        # Check if this is a boss wave
        if self.current_wave % self.waves_per_boss == 0:
            self.spawn_boss_wave()
        else:
            self.spawn_regular_wave()
            
    def spawn_boss_wave(self):
        """Spawn a boss wave"""
        boss_type = None
        if self.current_wave == 5:
            boss_type = BossType.NECROMANCER
        elif self.current_wave == 10:
            boss_type = BossType.ORC_CHIEFTAIN
        elif self.current_wave == 15:
            boss_type = BossType.ANCIENT_TROLL
        elif self.current_wave == 20:
            boss_type = BossType.DEMON_LORD
            
        if boss_type:
            # Spawn boss in center
            center_x = self.arena_map.width * TILE_SIZE // 2
            center_y = self.arena_map.height * TILE_SIZE // 2
            boss = Boss(center_x, center_y, boss_type)
            self.bosses.append(boss)
            
            # Spawn some regular enemies too (fewer than normal)
            enemy_count = max(2, self.current_wave // 3)
            self.spawn_regular_enemies(enemy_count)
            
    def spawn_regular_wave(self):
        """Spawn a regular wave of enemies"""
        # Calculate enemies for this wave
        base_enemies = 3
        additional_enemies = (self.current_wave - 1) * 2
        total_enemies = min(15, base_enemies + additional_enemies)  # Cap at 15
        
        self.spawn_regular_enemies(total_enemies)
        
    def spawn_regular_enemies(self, count):
        """Spawn regular enemies"""
        # Enemy type distribution based on wave
        enemy_types = []
        
        # Always have skeletons
        skeleton_count = max(1, count // 3)
        enemy_types.extend([EnemyType.SKELETON] * skeleton_count)
        
        # Add orcs starting from wave 2
        if self.current_wave >= 2:
            orc_count = max(1, count // 4)
            enemy_types.extend([EnemyType.ORC] * orc_count)
            
        # Add trolls starting from wave 4
        if self.current_wave >= 4:
            troll_count = max(1, count // 6)
            enemy_types.extend([EnemyType.TROLL] * troll_count)
            
        # Add demons starting from wave 6
        if self.current_wave >= 6:
            demon_count = max(1, count // 8)
            enemy_types.extend([EnemyType.DEMON] * demon_count)
        
        # Fill remaining slots with skeletons
        while len(enemy_types) < count:
            enemy_types.append(EnemyType.SKELETON)
            
        # Shuffle and limit
        random.shuffle(enemy_types)
        enemy_types = enemy_types[:count]
        
        # Spawn enemies
        spawn_positions = self.get_spawn_positions(len(enemy_types))
        
        for i, enemy_type in enumerate(enemy_types):
            x, y = spawn_positions[i]
            enemy = Enemy(x, y, enemy_type)
            self.enemies.append(enemy)

    def handle_event(self, event):
        current_time = pygame.time.get_ticks()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
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
                    # Apply spell level damage bonus
                    spell.damage *= self.player.get_spell_damage_multiplier()
                    self.spells.append(spell)
            # Right click to cycle spells
            elif event.button == 3:  # Right mouse button
                current_index = SPELL_TYPES.index(self.player.current_spell)
                self.player.current_spell = SPELL_TYPES[(current_index + 1) % len(SPELL_TYPES)]
        elif event.type == pygame.MOUSEMOTION:
            # Mouse look
            self.player.handle_mouse_look(event.rel)

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        
        # Update player
        keys = pygame.key.get_pressed()
        self.player.move(keys, dt, self.arena_map.collision_map, 
                        self.arena_map.width, self.arena_map.height)
        self.player.update(dt)
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.player, dt, current_time)
        
        # Update bosses
        for boss in self.bosses:
            boss.update(self.player, dt, current_time)
        
        # Update spells
        for spell in self.spells[:]:
            spell.update(dt, self.arena_map.collision_map, 
                        self.arena_map.width, self.arena_map.height)
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
                            self.player.add_gold(enemy.score_value // 2)  # Convert some score to gold
                            self.enemies_killed_this_wave += 1
                        break
                        
            # Check spell-boss collisions
            for boss in self.bosses:
                if boss.alive:
                    distance = boss.get_distance_to(spell.x, spell.y)
                    if distance < boss.size:
                        boss.take_damage(spell.damage)
                        spell.alive = False
                        if not boss.alive:
                            self.score += boss.score_value
                            self.player.add_gold(boss.score_value // 2)
                        break
        
        # Remove dead spells
        self.spells = [s for s in self.spells if s.alive]
        
        # Check wave completion
        alive_enemies = [e for e in self.enemies if e.alive]
        alive_bosses = [b for b in self.bosses if b.alive]
        
        if self.wave_active and len(alive_enemies) == 0 and len(alive_bosses) == 0:
            self.wave_active = False
            # Clear dead entities
            self.enemies = []
            self.bosses = []
            
            # Update player's highest wave
            if self.current_wave > self.player.highest_wave:
                self.player.highest_wave = self.current_wave
                
            # Check if game is complete
            if self.current_wave >= self.max_waves:
                self.complete_arena()
                return
        
        # Start next wave after delay
        if (not self.wave_active and 
            current_time - self.wave_start_time > self.time_between_waves and
            self.current_wave < self.max_waves):
            self.start_next_wave()
        
        # Check if player is dead
        if self.player.health <= 0:
            self.end_arena()
            
    def complete_arena(self):
        """Handle arena completion"""
        bonus_gold = 1000
        self.player.add_gold(bonus_gold)
        self.player.total_score += self.score
        # Return to town
        self.game_manager.change_state(GameState.TOWN)
        
    def end_arena(self):
        """Handle arena failure/death"""
        self.player.total_score += self.score
        # Reset health for town
        self.player.health = self.player.get_max_health()
        # Return to town
        self.game_manager.change_state(GameState.TOWN)

    def render(self):
        self.screen.fill(BLACK)

        # Cast rays and render 3D view
        rays = self.raycaster.cast_rays(self.player, self.arena_map.collision_map,
                                       self.arena_map.width, self.arena_map.height)
        self.raycaster.render_3d_arena(rays, self.enemies, self.spells, self.player)
        
        # Render bosses
        if self.bosses:
            self.raycaster.render_bosses(self.player, self.bosses)

        # Render 2D map if enabled
        if self.show_map:
            self.render_2d_map()

        # Draw crosshair
        self.draw_crosshair()

        # Draw UI
        self.draw_ui()
        
    def draw_crosshair(self):
        """Draw crosshair with spell type indication"""
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        crosshair_color = {
            "fireball": ORANGE,
            "lightning": YELLOW,
            "ice": BLUE
        }.get(self.player.current_spell, WHITE)
        
        # Make crosshair bigger when jumping for feedback
        crosshair_size = 12 + int(self.player.z * 0.1)
        line_width = 3 if self.player.is_jumping else 2
        
        pygame.draw.line(self.screen, crosshair_color, 
                        (center_x - crosshair_size, center_y), 
                        (center_x + crosshair_size, center_y), line_width)
        pygame.draw.line(self.screen, crosshair_color, 
                        (center_x, center_y - crosshair_size), 
                        (center_x, center_y + crosshair_size), line_width)
        
        # Jump indicator
        if self.player.is_jumping:
            jump_text = self.font.render("JUMPING!", True, YELLOW)
            text_rect = jump_text.get_rect(center=(center_x, center_y - 40))
            self.screen.blit(jump_text, text_rect)

    def draw_ui(self):
        """Draw the game UI"""
        # Health bar
        health_ratio = self.player.health / self.player.get_max_health()
        health_bar_width = 200
        health_bar_height = 15
        health_x = 10
        health_y = SCREEN_HEIGHT - 120
        
        pygame.draw.rect(self.screen, RED, (health_x, health_y, health_bar_width, health_bar_height))
        pygame.draw.rect(self.screen, GREEN, (health_x, health_y, health_bar_width * health_ratio, health_bar_height))
        
        health_text = self.font.render(f"Health: {int(self.player.health)}/{self.player.get_max_health()}", True, WHITE)
        self.screen.blit(health_text, (health_x, health_y - 18))
        
        # Mana bar
        mana_ratio = self.player.mana / self.player.get_max_mana()
        mana_y = health_y + 25
        
        pygame.draw.rect(self.screen, PURPLE, (health_x, mana_y, health_bar_width, health_bar_height))
        pygame.draw.rect(self.screen, BLUE, (health_x, mana_y, health_bar_width * mana_ratio, health_bar_height))
        
        mana_text = self.font.render(f"Mana: {int(self.player.mana)}/{self.player.get_max_mana()}", True, WHITE)
        self.screen.blit(mana_text, (health_x, mana_y + 18))
        
        # Current spell
        spell_colors = {"fireball": ORANGE, "lightning": YELLOW, "ice": BLUE}
        spell_text = self.font.render(f"Spell: {self.player.current_spell.title()}", True, spell_colors[self.player.current_spell])
        self.screen.blit(spell_text, (health_x, mana_y + 45))
        
        # Wave info
        alive_enemies = sum(1 for enemy in self.enemies if enemy.alive)
        alive_bosses = sum(1 for boss in self.bosses if boss.alive)
        total_alive = alive_enemies + alive_bosses
        
        wave_text = self.font.render(f"Wave: {self.current_wave}/{self.max_waves}", True, GOLD)
        self.screen.blit(wave_text, (SCREEN_WIDTH - 200, 10))
        
        enemies_text = self.font.render(f"Enemies: {total_alive}", True, WHITE)
        self.screen.blit(enemies_text, (SCREEN_WIDTH - 200, 35))
        
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - 200, 60))
        
        gold_text = self.font.render(f"Gold: {self.player.gold}", True, YELLOW)
        self.screen.blit(gold_text, (SCREEN_WIDTH - 200, 85))
        
        # Wave status
        if not self.wave_active:
            current_time = pygame.time.get_ticks()
            time_left = max(0, self.time_between_waves - (current_time - self.wave_start_time))
            
            if self.current_wave >= self.max_waves:
                victory_text = self.big_font.render("ARENA COMPLETED!", True, GOLD)
                text_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(victory_text, text_rect)
            else:
                next_wave_text = self.font.render(f"Next Wave: {time_left // 1000 + 1}s", True, YELLOW)
                text_rect = next_wave_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
                self.screen.blit(next_wave_text, text_rect)
                
                # Boss wave indicator
                if (self.current_wave + 1) % self.waves_per_boss == 0:
                    boss_text = self.font.render("BOSS WAVE INCOMING!", True, RED)
                    boss_rect = boss_text.get_rect(center=(SCREEN_WIDTH // 2, 75))
                    self.screen.blit(boss_text, boss_rect)

        # Controls reminder
        controls_y = 100
        controls = [
            "WASD: Move",
            "Mouse: Look & Shoot", 
            "SPACE: Jump",
            "1/2/3: Select Spell",
            "Right Click: Cycle Spells",
            "M: Toggle Map"
        ]

        for i, control in enumerate(controls):
            text = self.font.render(control, True, GRAY)
            self.screen.blit(text, (SCREEN_WIDTH - 250, controls_y + i * 18))
            
    def render_2d_map(self):
        """Render 2D minimap"""
        map_scale = 15
        map_offset_x = SCREEN_WIDTH - self.arena_map.width * map_scale - 10
        map_offset_y = 10

        # Draw map
        for y in range(self.arena_map.height):
            for x in range(self.arena_map.width):
                tile_type = self.arena_map.get_tile(x, y)
                if tile_type == 1:
                    color = DARK_BROWN
                elif tile_type == 2:
                    color = GRAY
                else:
                    color = BLACK
                    
                pygame.draw.rect(
                    self.screen,
                    color,
                    (map_offset_x + x * map_scale, map_offset_y + y * map_scale, map_scale, map_scale)
                )

        # Draw enemies on minimap
        for enemy in self.enemies:
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
                
        # Draw bosses on minimap
        for boss in self.bosses:
            if boss.alive:
                boss_x = map_offset_x + int(boss.x * map_scale / TILE_SIZE)
                boss_y = map_offset_y + int(boss.y * map_scale / TILE_SIZE)
                pygame.draw.circle(self.screen, GOLD, (boss_x, boss_y), 5)

        # Draw player on minimap
        player_x = map_offset_x + int(self.player.x * map_scale / TILE_SIZE)
        player_y = map_offset_y + int(self.player.y * map_scale / TILE_SIZE)
        pygame.draw.circle(self.screen, BLUE, (player_x, player_y), 4)

        # Draw player direction
        end_x = player_x + int(math.cos(self.player.angle) * 12)
        end_y = player_y + int(math.sin(self.player.angle) * 12)
        pygame.draw.line(self.screen, BLUE, (player_x, player_y), (end_x, end_y), 2)