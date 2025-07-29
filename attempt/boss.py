import math
import random

import pygame
from constants import DARK_GREEN, BossType
from constants import *

class Boss:
    def __init__(self, x: float, y: float, boss_type: str = BossType.NECROMANCER):
        self.x = x
        self.y = y
        self.boss_type = boss_type
        
        # Base boss stats - all bosses are much stronger than regular enemies
        if boss_type == BossType.NECROMANCER:
            self.health = 400
            self.max_health = 400
            self.speed = 30
            self.attack_damage = 50
            self.color = PURPLE
            self.size = 35
            self.score_value = 500
            self.special_ability = "summon_skeletons"
        elif boss_type == BossType.ORC_CHIEFTAIN:
            self.health = 600
            self.max_health = 600
            self.speed = 40
            self.attack_damage = 75
            self.color = DARK_GREEN
            self.size = 40
            self.score_value = 750
            self.special_ability = "berserker_rage"
        elif boss_type == BossType.ANCIENT_TROLL:
            self.health = 800
            self.max_health = 800
            self.speed = 25
            self.attack_damage = 100
            self.color = DARK_BROWN
            self.size = 50
            self.score_value = 1000
            self.special_ability = "regeneration"
        elif boss_type == BossType.DEMON_LORD:
            self.health = 1000
            self.max_health = 1000
            self.speed = 45
            self.attack_damage = 80
            self.color = DARK_RED
            self.size = 45
            self.score_value = 1500
            self.special_ability = "teleport_attack"
            
        # Boss mechanics
        self.attack_range = 60
        self.last_attack = 0
        self.attack_cooldown = 1500  # Faster than regular enemies
        self.alive = True
        
        # Special ability tracking
        self.last_special_ability = 0
        self.special_ability_cooldown = 8000  # 8 seconds
        self.rage_mode = False
        self.rage_end_time = 0
        
        # Movement pattern
        self.movement_pattern = "aggressive"  # aggressive, defensive, teleport
        self.pattern_change_time = 0
        self.pattern_duration = 5000  # 5 seconds per pattern
        
    def update(self, player, dt, current_time):
        """Update boss behavior with special abilities"""
        if not self.alive:
            return
            
        # Update special states
        self.update_special_states(current_time)
        
        # Use special ability if available
        if current_time - self.last_special_ability > self.special_ability_cooldown:
            self.use_special_ability(player, current_time)
            
        # Move toward player with boss-specific behavior
        self.move_towards_player(player, dt, current_time)
        
        # Attack player if in range
        if self.get_distance_to(player.x, player.y) <= self.attack_range:
            if current_time - self.last_attack > self.attack_cooldown:
                self.attack_player(player, current_time)
                
    def update_special_states(self, current_time):
        """Update special boss states"""
        # Handle rage mode for Orc Chieftain
        if self.boss_type == BossType.ORC_CHIEFTAIN and self.rage_mode:
            if current_time > self.rage_end_time:
                self.rage_mode = False
                self.speed = 40  # Return to normal speed
                self.attack_damage = 75  # Return to normal damage
                
        # Handle regeneration for Ancient Troll
        if self.boss_type == BossType.ANCIENT_TROLL:
            # Regenerate health slowly
            regen_rate = 10  # HP per second
            self.health = min(self.max_health, self.health + regen_rate * 0.016)  # Assuming 60 FPS
            
    def use_special_ability(self, player, current_time):
        """Use boss special ability"""
        self.last_special_ability = current_time
        
        if self.special_ability == "summon_skeletons":
            # Necromancer summons skeleton minions (would need enemy spawning system)
            pass  # Implementation would spawn 2-3 skeletons around the boss
            
        elif self.special_ability == "berserker_rage":
            # Orc Chieftain enters rage mode
            if not self.rage_mode:
                self.rage_mode = True
                self.rage_end_time = current_time + 5000  # 5 seconds of rage
                self.speed *= 1.5  # 50% faster
                self.attack_damage = int(self.attack_damage * 1.3)  # 30% more damage
                
        elif self.special_ability == "regeneration":
            # Ancient Troll heals significantly
            heal_amount = 150
            self.health = min(self.max_health, self.health + heal_amount)
            
        elif self.special_ability == "teleport_attack":
            # Demon Lord teleports behind player and attacks
            # Calculate position behind player
            behind_x = player.x - math.cos(player.angle) * 80
            behind_y = player.y - math.sin(player.angle) * 80
            
            # Check if position is valid (not in wall)
            if not self.check_collision(behind_x, behind_y):
                self.x = behind_x
                self.y = behind_y
                # Immediate attack after teleport
                player.take_damage(self.attack_damage * 1.5)  # Bonus damage
                
    def move_towards_player(self, player, dt, current_time):
        """Move toward player with boss-specific patterns"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > self.attack_range:
            # Normalize direction
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
                    
    def attack_player(self, player, current_time):
        """Attack the player"""
        damage = self.attack_damage
        
        # Rage mode bonus damage
        if self.rage_mode:
            damage = int(damage * 1.3)
            
        player.take_damage(damage)
        self.last_attack = current_time
        
    def check_collision(self, x: float, y: float) -> bool:
        """Check collision with arena walls (same as regular enemies for now)"""
        map_x = int(x // TILE_SIZE)
        map_y = int(y // TILE_SIZE)
        
        # Basic arena bounds
        if map_x < 0 or map_x >= 20 or map_y < 0 or map_y >= 20:
            return True
            
        # Center area check
        center_x, center_y = 10, 10
        distance = math.sqrt((map_x - center_x) ** 2 + (map_y - center_y) ** 2)
        
        return distance > 8  # Arena radius
        
    def take_damage(self, damage):
        """Take damage with boss-specific resistances"""
        # Bosses have some damage resistance
        resistance = 0.1  # 10% damage reduction
        actual_damage = damage * (1 - resistance)
        
        self.health -= actual_damage
        if self.health <= 0:
            self.alive = False
            
        # Trigger rage mode for Orc Chieftain when low on health
        if (self.boss_type == BossType.ORC_CHIEFTAIN and 
            self.health < self.max_health * 0.3 and 
            not self.rage_mode):
            current_time = pygame.time.get_ticks() if 'pygame' in globals() else 0
            self.use_special_ability(None, current_time)
            
    def get_distance_to(self, x, y):
        """Get distance to a point"""
        dx = self.x - x
        dy = self.y - y
        return math.sqrt(dx * dx + dy * dy)
        
    def get_health_percentage(self):
        """Get health as percentage for UI display"""
        return self.health / self.max_health