import math
from constants import *

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
        """Update enemy behavior"""
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
        """Check collision with arena walls"""
        from arena_map import ArenaMap  # Import here to avoid circular imports
        
        # Simple bounds check - assumes we're in arena
        map_x = int(x // TILE_SIZE)
        map_y = int(y // TILE_SIZE)
        
        # Basic arena bounds (this should be improved to use actual arena map)
        if map_x < 0 or map_x >= 20 or map_y < 0 or map_y >= 20:
            return True
            
        # For now, assume center area is clear and edges are walls
        center_x, center_y = 10, 10
        distance = math.sqrt((map_x - center_x) ** 2 + (map_y - center_y) ** 2)
        
        return distance > 8  # Arena radius
        
    def take_damage(self, damage):
        """Take damage and check if enemy dies"""
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            
    def get_distance_to(self, x, y):
        """Get distance to a point"""
        dx = self.x - x
        dy = self.y - y
        return math.sqrt(dx * dx + dy * dy)