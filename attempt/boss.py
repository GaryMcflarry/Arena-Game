import math
import random
import pygame
from constants import DARK_GREEN, BossType
from constants import *
from enemy import Enemy  # Changed from enhanced_enemy_with_healthbars

class Boss:
    def __init__(self, x: float, y: float, boss_type: str = BossType.NECROMANCER, arena_state=None):
        self.x = x
        self.y = y
        self.boss_type = boss_type
        self.arena_state = arena_state  # Reference to spawn enemies
        
        # Base boss stats with enhanced gimmicks
        if boss_type == BossType.NECROMANCER:
            self.health = 300
            self.max_health = 300
            self.speed = 30
            self.attack_damage = 40
            self.color = PURPLE
            self.size = 35
            self.score_value = 150  # Reduced from 250
            self.special_ability = "summon_skeletons"
            self.is_ranged = True
            self.attack_range = 150
        elif boss_type == BossType.ORC_CHIEFTAIN:
            self.health = 800  # More health
            self.max_health = 800
            self.speed = 60  # Moves faster
            self.attack_damage = 45  # Reduced from 60 - focus on speed not damage
            self.color = DARK_GREEN
            self.size = 40
            self.score_value = 200  # Reduced from 375
            self.special_ability = "berserker_rage"
            self.is_ranged = False
            self.attack_range = 60
        elif boss_type == BossType.ANCIENT_TROLL:
            self.health = 600
            self.max_health = 600
            self.speed = 25
            self.attack_damage = 80
            self.color = DARK_BROWN
            self.size = 50
            self.score_value = 300  # Reduced from 500
            self.special_ability = "create_decoy"
            self.is_ranged = False
            self.attack_range = 70
            self.is_real = True  # For decoy system
        elif boss_type == BossType.DEMON_LORD:
            self.health = 1200  # More health
            self.max_health = 1200
            self.speed = 70  # Moves fast
            self.attack_damage = 85
            self.color = DARK_RED
            self.size = 45
            self.score_value = 450  # Reduced from 750
            self.special_ability = "demon_summon"
            self.is_ranged = True
            self.attack_range = 200
            
        # Boss mechanics
        self.last_attack = 0
        self.attack_cooldown = 1500  # Faster than regular enemies
        self.alive = True
        
        # Special ability tracking
        self.last_special_ability = 0
        if boss_type == BossType.NECROMANCER:
            self.special_ability_cooldown = 2000  # 2 seconds for skeleton spawning
        elif boss_type == BossType.DEMON_LORD:
            self.special_ability_cooldown = 5000  # 5 seconds for demon spawning
        else:
            self.special_ability_cooldown = 8000  # 8 seconds for other abilities
            
        self.rage_mode = False
        self.rage_end_time = 0
        
        # Ranged attack properties
        self.projectiles = []
        self.projectile_speed = 250
        
        # Create boss image with placeholder design
        self.image = self.create_boss_placeholder(self.boss_type, self.size, self.color)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
        # Boss-specific flags
        self.spawned_minions = False  # For one-time minion spawning
        self.skeleton_spawn_active = True  # For necromancer
        
    def create_boss_placeholder(self, boss_type, size, color):
        """Create a placeholder image for the boss"""
        image_size = size * 2
        surface = pygame.Surface((image_size, image_size))
        surface.fill(color)
        
        # Add distinctive features based on boss type
        if boss_type == BossType.NECROMANCER:
            # Purple with white skull-like features
            pygame.draw.circle(surface, WHITE, (image_size//2, image_size//3), size//4)  # Head
            pygame.draw.rect(surface, BLACK, (image_size//2 - 3, image_size//3 - 3, 6, 8))  # Eyes
            pygame.draw.polygon(surface, BLACK, [(image_size//2, image_size//3 + 5), 
                                               (image_size//2 - 3, image_size//3 + 10),
                                               (image_size//2 + 3, image_size//3 + 10)])  # Nose
        elif boss_type == BossType.ORC_CHIEFTAIN:
            # Green with war paint
            pygame.draw.rect(surface, RED, (0, image_size//4, image_size, image_size//8))  # War paint stripe
            pygame.draw.circle(surface, YELLOW, (image_size//3, image_size//3), 3)  # Eye
            pygame.draw.circle(surface, YELLOW, (2*image_size//3, image_size//3), 3)  # Eye
        elif boss_type == BossType.ANCIENT_TROLL:
            # Brown with rocky texture
            for i in range(0, image_size, 8):
                for j in range(0, image_size, 8):
                    if (i + j) % 16 == 0:
                        pygame.draw.rect(surface, DARK_BROWN, (i, j, 4, 4))
        elif boss_type == BossType.DEMON_LORD:
            # Dark red with flame effects
            pygame.draw.circle(surface, ORANGE, (image_size//2, image_size//2), size//2)  # Inner glow
            pygame.draw.circle(surface, RED, (image_size//4, image_size//4), 3)  # Eye
            pygame.draw.circle(surface, RED, (3*image_size//4, image_size//4), 3)  # Eye
            
        # Add border to make boss stand out
        pygame.draw.rect(surface, WHITE, (0, 0, image_size, image_size), 2)
        
        return surface
        
    def update(self, player, dt, current_time):
        """Update boss behavior with special abilities"""
        if not self.alive:
            return
            
        # Update special states
        self.update_special_states(current_time)
        
        # Use special ability if available
        if current_time - self.last_special_ability > self.special_ability_cooldown:
            self.use_special_ability(player, current_time)
            
        # Move and attack based on boss type
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if self.is_ranged:
            # Ranged bosses maintain distance and shoot
            if distance > self.attack_range:
                self.move_towards_player(player, dt, distance, dx, dy)
            elif distance < 100:
                self.move_away_from_player(player, dt, distance, dx, dy)
                
            if distance <= self.attack_range and current_time - self.last_attack > self.attack_cooldown:
                self.ranged_attack(player, current_time)
        else:
            # Melee bosses charge at player
            if distance > self.attack_range:
                self.move_towards_player(player, dt, distance, dx, dy)
            elif current_time - self.last_attack > self.attack_cooldown:
                self.melee_attack(player, current_time)
        
        # Update projectiles
        self.update_projectiles(dt, player)
        
        # Spawn initial minions for certain bosses
        if not self.spawned_minions:
            self.spawn_initial_minions()
            self.spawned_minions = True
                
    def spawn_initial_minions(self):
        """Spawn initial minions with boss"""
        if not self.arena_state:
            return
            
        if self.boss_type == BossType.ORC_CHIEFTAIN:
            # Spawn 3 orc minions
            for _ in range(3):
                minion_x, minion_y = self.get_minion_spawn_position()
                minion = Enemy(minion_x, minion_y, EnemyType.ORC)
                self.arena_state.enemies.append(minion)
                
        elif self.boss_type == BossType.ANCIENT_TROLL:
            # Spawn 4 troll minions  
            for _ in range(4):
                minion_x, minion_y = self.get_minion_spawn_position()
                minion = Enemy(minion_x, minion_y, EnemyType.TROLL)
                self.arena_state.enemies.append(minion)
                
            # Create decoy troll
            decoy_x, decoy_y = self.get_minion_spawn_position()
            decoy = Boss(decoy_x, decoy_y, BossType.ANCIENT_TROLL, self.arena_state)
            decoy.is_real = False  # Mark as decoy
            decoy.health = 1  # Dies in one hit
            decoy.max_health = 1
            decoy.score_value = 0  # No reward for killing decoy
            self.arena_state.bosses.append(decoy)
                
    def get_minion_spawn_position(self):
        """Get spawn position near boss"""
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(60, 120)
        
        x = self.x + math.cos(angle) * distance
        y = self.y + math.sin(angle) * distance
        
        # Keep within arena bounds
        x = max(100, min(1180, x))
        y = max(100, min(1180, y))
        
        return x, y
                
    def use_special_ability(self, player, current_time):
        """Use boss special ability"""
        self.last_special_ability = current_time
        
        if self.special_ability == "summon_skeletons" and self.skeleton_spawn_active:
            # Necromancer summons 2 skeletons every 2 seconds
            if self.arena_state:
                for _ in range(2):
                    skeleton_x, skeleton_y = self.get_minion_spawn_position()
                    skeleton = Enemy(skeleton_x, skeleton_y, EnemyType.SKELETON)
                    self.arena_state.enemies.append(skeleton)
                    
        elif self.special_ability == "demon_summon":
            # Demon Lord summons 3 demons every 5 seconds
            if self.arena_state:
                for _ in range(3):
                    demon_x, demon_y = self.get_minion_spawn_position()
                    demon = Enemy(demon_x, demon_y, EnemyType.DEMON)
                    self.arena_state.enemies.append(demon)
                    
        elif self.special_ability == "berserker_rage":
            # Orc Chieftain enters rage mode
            if not self.rage_mode:
                self.rage_mode = True
                self.rage_end_time = current_time + 5000  # 5 seconds of rage
                self.speed *= 1.5  # 50% faster
                self.attack_damage = int(self.attack_damage * 1.3)  # 30% more damage
                
    def move_towards_player(self, player, dt, distance, dx, dy):
        """Move toward player with boss-specific patterns"""
        if distance > 0:
            dx /= distance
            dy /= distance
            
            # Apply speed modifiers
            current_speed = self.speed
            if self.rage_mode:
                current_speed *= 1.5
                
            new_x = self.x + dx * current_speed * dt
            new_y = self.y + dy * current_speed * dt
            
            # Check collision before moving
            if not self.check_collision(new_x, new_y):
                self.x = new_x
                self.y = new_y
                self.rect.center = (self.x, self.y)

    def move_away_from_player(self, player, dt, distance, dx, dy):
        """Move away from player (for ranged bosses)"""
        if distance > 0:
            dx /= distance
            dy /= distance

            new_x = self.x - dx * self.speed * 0.7 * dt
            new_y = self.y - dy * self.speed * 0.7 * dt

            if not self.check_collision(new_x, new_y):
                self.x = new_x
                self.y = new_y
                self.rect.center = (self.x, self.y)

    def melee_attack(self, player, current_time):
        """Melee attack with special damage values"""
        damage = self.attack_damage
        if self.rage_mode:
            damage = int(damage * 1.3)
        player.take_damage(damage)
        self.last_attack = current_time

    def ranged_attack(self, player, current_time):
        """Ranged attack - bosses shoot multiple projectiles"""
        # Calculate angle to player
        dx = player.x - self.x
        dy = player.y - self.y
        base_angle = math.atan2(dy, dx)
        
        # Bosses shoot multiple projectiles in a spread
        num_projectiles = 3 if self.boss_type == BossType.DEMON_LORD else 1
        spread_angle = 0.3  # Radians
        
        for i in range(num_projectiles):
            if num_projectiles == 1:
                angle = base_angle
            else:
                angle = base_angle + (i - 1) * spread_angle
                
            projectile = {
                'x': self.x,
                'y': self.y,
                'angle': angle,
                'damage': self.attack_damage,
                'alive': True
            }
            self.projectiles.append(projectile)
            
        self.last_attack = current_time

    def update_projectiles(self, dt, player):
        """Update boss projectiles"""
        for projectile in self.projectiles[:]:
            if not projectile['alive']:
                self.projectiles.remove(projectile)
                continue
                
            # Move projectile
            projectile['x'] += math.cos(projectile['angle']) * self.projectile_speed * dt
            projectile['y'] += math.sin(projectile['angle']) * self.projectile_speed * dt
            
            # Check collision with player
            dx = projectile['x'] - player.x
            dy = projectile['y'] - player.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < 25:  # Hit player
                player.take_damage(projectile['damage'])
                projectile['alive'] = False
                
            # Check collision with walls
            elif self.check_collision(projectile['x'], projectile['y']):
                projectile['alive'] = False
                
    def update_special_states(self, current_time):
        """Update special boss states"""
        # Handle rage mode for Orc Chieftain
        if self.boss_type == BossType.ORC_CHIEFTAIN and self.rage_mode:
            if current_time > self.rage_end_time:
                self.rage_mode = False
                self.speed = 60  # Return to normal speed
                self.attack_damage = 60  # Return to normal damage
                
    def check_collision(self, x: float, y: float) -> bool:
        """Check collision with arena walls"""
        map_x = int(x // TILE_SIZE)
        map_y = int(y // TILE_SIZE)
        
        if map_x < 0 or map_x >= 20 or map_y < 0 or map_y >= 20:
            return True
            
        center_x, center_y = 10, 10
        distance = math.sqrt((map_x - center_x) ** 2 + (map_y - center_y) ** 2)
        
        return distance > 8
        
    def take_damage(self, damage):
        """Take damage with boss-specific resistances"""
        # Decoy trolls die instantly
        if self.boss_type == BossType.ANCIENT_TROLL and not self.is_real:
            self.alive = False
            return
            
        # Bosses have some damage resistance
        resistance = 0.15  # 15% damage reduction
        actual_damage = damage * (1 - resistance)
        
        self.health -= actual_damage
        if self.health <= 0:
            self.alive = False
            # Stop skeleton spawning when necromancer dies
            if self.boss_type == BossType.NECROMANCER:
                self.skeleton_spawn_active = False
            
        # Trigger rage mode for Orc Chieftain when low on health
        if (self.boss_type == BossType.ORC_CHIEFTAIN and 
            self.health < self.max_health * 0.3 and 
            not self.rage_mode):
            current_time = pygame.time.get_ticks()
            self.use_special_ability(None, current_time)
            
    def get_distance_to(self, x, y):
        """Get distance to a point"""
        dx = self.x - x
        dy = self.y - y
        return math.sqrt(dx * dx + dy * dy)
        
    def get_health_percentage(self):
        """Get health as percentage for UI display"""
        return self.health / self.max_health

    def draw(self, surface):
        """Render the boss on screen"""
        if self.alive:
            surface.blit(self.image, self.rect)
            
            # Draw special effects
            if self.rage_mode:
                # Red outline for rage mode
                pygame.draw.rect(surface, RED, self.rect, 3)
                
            # Draw decoy indicator
            if self.boss_type == BossType.ANCIENT_TROLL and not self.is_real:
                # Slightly transparent for decoy
                alpha_surface = pygame.Surface(self.image.get_size())
                alpha_surface.set_alpha(180)
                alpha_surface.fill(WHITE)
                surface.blit(alpha_surface, self.rect, special_flags=pygame.BLEND_ALPHA_SDL2)

    def draw_projectiles(self, surface, camera_x=0, camera_y=0):
        """Draw boss projectiles (larger and more impressive)"""
        for projectile in self.projectiles:
            if projectile['alive']:
                proj_x = int(projectile['x'] - camera_x)
                proj_y = int(projectile['y'] - camera_y)
                
                # Boss projectiles are larger and more colorful
                if self.boss_type == BossType.NECROMANCER:
                    pygame.draw.circle(surface, PURPLE, (proj_x, proj_y), 8)
                    pygame.draw.circle(surface, WHITE, (proj_x, proj_y), 4)
                elif self.boss_type == BossType.DEMON_LORD:
                    pygame.draw.circle(surface, DARK_RED, (proj_x, proj_y), 6)
                    pygame.draw.circle(surface, ORANGE, (proj_x, proj_y), 3)