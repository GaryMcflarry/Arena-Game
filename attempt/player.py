import pygame
import math

from constants import TILE_SIZE  

class Player:
    def __init__(self, x: float, y: float, angle: float):
        self.x = x
        self.y = y
        self.angle = angle
        self.base_speed = 120
        self.rot_speed = 3.0
        
        # Health and mana
        self.health = 60000000000
        self.max_health = 6000000000
        self.mana = 60000
        self.max_mana = 60000
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
        
        # Currency system
        self.gold = 1000000  # Starting gold
        
        # Equipment and upgrades
        self.weapon_level = 1  # 1-5
        self.armor_level = 1   # 1-5
        self.spell_level = 1   # 1-5
        
        # Enhanced spell system
        self.current_spell = "fireball"
        self.known_spells = ["fireball"]  # Player starts with fireball
        self.spell_costs = {
            "fireball": 20,
            "lightning": 15, 
            "ice": 25,
            "heal": 30,
            "shield": 40,
            "teleport": 50
        }
        # Removed cooldowns - now only mana limits casting
        
        # Arena stats
        self.total_score = 0
        self.highest_wave = 0
        
    def get_available_spells(self):
        """Get list of spells the player knows"""
        return self.known_spells.copy()
        
    def learn_spell(self, spell_name):
        """Learn a new spell"""
        if spell_name not in self.known_spells:
            self.known_spells.append(spell_name)
            
    def get_weapon_damage(self):
        """Get weapon damage based on level"""
        base_damage = 30
        return base_damage + (self.weapon_level - 1) * 15
        
    def get_armor_defense(self):
        """Get damage reduction based on armor level"""
        return (self.armor_level - 1) * 0.1  # 10% reduction per level
        
    def get_spell_damage_multiplier(self):
        """Get spell damage multiplier based on spell level"""
        return 1.0 + (self.spell_level - 1) * 0.25  # 25% increase per level
        
    def get_max_health(self):
        """Get max health including armor bonus"""
        return self.max_health + (self.armor_level - 1) * 20
        
    def get_max_mana(self):
        """Get max mana including spell level bonus"""
        return self.max_mana + (self.spell_level - 1) * 15

    def jump(self):
        """Make the player jump"""
        if self.can_jump and not self.is_jumping:
            self.z_velocity = self.jump_power
            self.is_jumping = True
            self.can_jump = False

    def take_damage(self, damage):
        """Take damage with armor reduction"""
        actual_damage = damage * (1 - self.get_armor_defense())
        self.health = max(0, self.health - actual_damage)

    def heal(self, amount):
        """Heal the player"""
        max_hp = self.get_max_health()
        self.health = min(max_hp, self.health + amount)
        
    def restore_mana(self, amount):
        """Restore mana"""
        max_mp = self.get_max_mana()
        self.mana = min(max_mp, self.mana + amount)
        
    def spend_gold(self, amount):
        """Spend gold if player has enough"""
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
        
    def add_gold(self, amount):
        """Add gold to player"""
        self.gold += amount

    def update(self, dt):
        """Update player state"""
        # Regenerate mana
        max_mana = self.get_max_mana()
        self.mana = min(max_mana, self.mana + self.mana_regen * dt)
        
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

    def move(self, keys, dt, collision_map=None, map_width=0, map_height=0):
        """Move the player based on input"""
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
        
        # Apply movement with collision checking
        if collision_map:
            new_x = self.x + dx
            if not self.check_collision(new_x, self.y, collision_map, map_width, map_height):
                self.x = new_x
            
            new_y = self.y + dy
            if not self.check_collision(self.x, new_y, collision_map, map_width, map_height):
                self.y = new_y
        else:
            self.x += dx
            self.y += dy
        
        # Arrow keys for rotation (backup controls)
        if keys[pygame.K_LEFT]:
            self.angle -= self.rot_speed * dt
        if keys[pygame.K_RIGHT]:
            self.angle += self.rot_speed * dt
        
        # Jump
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.jump()
        
        self.angle = self.angle % (2 * math.pi)

    def check_collision(self, x: float, y: float, collision_map, map_width, map_height) -> bool:
        """Check collision with map boundaries and walls"""
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
            
            if map_x < 0 or map_x >= map_width or map_y < 0 or map_y >= map_height:
                return True
            
            if collision_map[map_y][map_x] != 0:
                return True
        
        return False
        
    def reset_for_arena(self):
        """Reset temporary stats for arena"""
        max_hp = self.get_max_health()
        max_mp = self.get_max_mana()
        self.health = max_hp
        self.mana = max_mp