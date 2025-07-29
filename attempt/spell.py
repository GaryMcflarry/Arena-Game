import math
from constants import *

class Spell:
    def __init__(self, x: float, y: float, angle: float, spell_type: str = "fireball"):
        self.x = x
        self.y = y
        self.angle = angle
        self.spell_type = spell_type
        self.alive = True
        
        # Spell-specific properties
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
            
    def update(self, dt, collision_map=None, map_width=0, map_height=0):
        """Update spell position and check collisions"""
        if not self.alive:
            return
            
        # Move spell
        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt
        
        # Check collision with walls if collision map provided
        if collision_map:
            map_x = int(self.x // TILE_SIZE)
            map_y = int(self.y // TILE_SIZE)
            
            if (map_x < 0 or map_x >= map_width or 
                map_y < 0 or map_y >= map_height or 
                collision_map[map_y][map_x] != 0):
                self.alive = False