import math
import pygame
from constants import *


class Enemy:
    enemy_images = {}
    
    @classmethod
    def load_images(cls):
        """Load enemy images with fallback handling"""
        try:
            cls.enemy_images = {
                EnemyType.SKELETON: pygame.image.load("../assets/textures/enemies/skeleton.gif"),
                EnemyType.ORC: pygame.image.load("../assets/textures/enemies/orc.gif"),
                EnemyType.TROLL: pygame.image.load("../assets/textures/enemies/troll.gif"),
                EnemyType.DEMON: pygame.image.load("../assets/textures/enemies/demon.png"),
            }
        except pygame.error:
            cls.enemy_images = {}
            colors = {
                EnemyType.SKELETON: WHITE,
                EnemyType.ORC: DARK_GREEN,
                EnemyType.TROLL: BROWN,
                EnemyType.DEMON: DARK_RED
            }
            for enemy_type, color in colors.items():
                surface = pygame.Surface((32, 32))
                surface.fill(color)
                cls.enemy_images[enemy_type] = surface

    def __init__(self, x: float, y: float, enemy_type: str = EnemyType.SKELETON):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type

        if enemy_type == EnemyType.SKELETON:
            self.health = 75
            self.max_health = 75
            self.speed = 40
            self.attack_damage = 15
            self.size = 15
            self.score_value = 15 
            self.attack_range = 45
            self.is_ranged = False
        elif enemy_type == EnemyType.ORC:
            self.health = 100
            self.max_health = 120
            self.speed = 35
            self.attack_damage = 25
            self.size = 18
            self.score_value = 20  
            self.attack_range = 45
            self.is_ranged = False
        elif enemy_type == EnemyType.TROLL:
            self.health = 120
            self.max_health = 200
            self.speed = 25
            self.attack_damage = 40
            self.size = 25
            self.score_value = 45  
            self.attack_range = 45
            self.is_ranged = False
        elif enemy_type == EnemyType.DEMON:
            self.health = 150
            self.max_health = 150
            self.speed = 50
            self.attack_damage = 30
            self.size = 20
            self.score_value = 60  
            self.attack_range = 120 
            self.is_ranged = True

        if not Enemy.enemy_images:
            Enemy.load_images()
            
        self.image = pygame.transform.scale(
            Enemy.enemy_images[self.enemy_type], (self.size * 2, self.size * 2)
        )
        self.rect = self.image.get_rect(center=(self.x, self.y))

        self.last_attack = 0
        self.attack_cooldown = 2000  
        self.alive = True
        
        self.projectiles = []
        self.projectile_speed = 200

    def update(self, player, dt, current_time):
        """Update enemy behavior"""
        if not self.alive:
            return

        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if self.is_ranged:
            if distance > self.attack_range:
                self.move_towards_player(player, dt, distance, dx, dy)
            elif distance < 80:
                self.move_away_from_player(player, dt, distance, dx, dy)
            
            if distance <= self.attack_range and current_time - self.last_attack > self.attack_cooldown:
                self.ranged_attack(player, current_time)
        else:
            if distance > self.attack_range:
                self.move_towards_player(player, dt, distance, dx, dy)
            elif current_time - self.last_attack > self.attack_cooldown:
                self.melee_attack(player, current_time)
        
        if self.is_ranged:
            self.update_projectiles(dt, player)

    def move_towards_player(self, player, dt, distance, dx, dy):
        """Move towards the player"""
        if distance > 0:
            dx /= distance
            dy /= distance

            new_x = self.x + dx * self.speed * dt
            new_y = self.y + dy * self.speed * dt

            if not self.check_collision(new_x, new_y):
                self.x = new_x
                self.y = new_y
                self.rect.center = (self.x, self.y)

    def move_away_from_player(self, player, dt, distance, dx, dy):
        """Move away from the player (for ranged enemies)"""
        if distance > 0:
            dx /= distance
            dy /= distance

            new_x = self.x - dx * self.speed * 0.5 * dt 
            new_y = self.y - dy * self.speed * 0.5 * dt

            if not self.check_collision(new_x, new_y):
                self.x = new_x
                self.y = new_y
                self.rect.center = (self.x, self.y)

    def melee_attack(self, player, current_time):
        """Perform melee attack"""
        player.take_damage(self.attack_damage)
        self.last_attack = current_time

    def ranged_attack(self, player, current_time):
        """Perform ranged attack by creating a projectile"""
        dx = player.x - self.x
        dy = player.y - self.y
        angle = math.atan2(dy, dx)
        
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
        """Update enemy projectiles"""
        for projectile in self.projectiles[:]:  
            if not projectile['alive']:
                self.projectiles.remove(projectile)
                continue
                
            projectile['x'] += math.cos(projectile['angle']) * self.projectile_speed * dt
            projectile['y'] += math.sin(projectile['angle']) * self.projectile_speed * dt
            
            dx = projectile['x'] - player.x
            dy = projectile['y'] - player.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < 20:  
                player.take_damage(projectile['damage'])
                projectile['alive'] = False
                
            elif self.check_collision(projectile['x'], projectile['y']):
                projectile['alive'] = False

    def check_collision(self, x: float, y: float) -> bool:
        """Collision check with bounds"""
        map_x = int(x // TILE_SIZE)
        map_y = int(y // TILE_SIZE)

        if map_x < 0 or map_x >= 20 or map_y < 0 or map_y >= 20:
            return True

        center_x, center_y = 10, 10
        distance = math.sqrt((map_x - center_x) ** 2 + (map_y - center_y) ** 2)

        return distance > 8

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False

    def get_distance_to(self, x, y):
        dx = self.x - x
        dy = self.y - y
        return math.sqrt(dx * dx + dy * dy)

    def get_health_percentage(self):
        """Get health as percentage for health bar"""
        return self.health / self.max_health

    def draw(self, surface):
        """Render the enemy on screen"""
        if self.alive:
            surface.blit(self.image, self.rect)

    def draw_projectiles_2d(self, surface, camera_x=0, camera_y=0):
        """Draw enemy projectiles in 2D (for debugging/minimap)"""
        for projectile in self.projectiles:
            if projectile['alive']:
                proj_x = int(projectile['x'] - camera_x)
                proj_y = int(projectile['y'] - camera_y)
                
                pygame.draw.circle(surface, RED, (proj_x, proj_y), 3)
                pygame.draw.circle(surface, YELLOW, (proj_x, proj_y), 1)