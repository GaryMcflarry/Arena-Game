import math
from constants import *

class Spell:
    def __init__(self, x: float, y: float, angle: float, spell_type: str = "fireball", sound_manager=None):
        self.x = x
        self.y = y
        self.angle = angle
        self.spell_type = spell_type
        self.alive = True
        self.sound_manager = sound_manager
        
        if spell_type == "fireball":
            self.speed = 300
            self.damage = 600
            self.color = ORANGE
            self.size = 8
            self.trail_particles = []  
        elif spell_type == "lightning":
            self.speed = 500
            self.damage = 40
            self.color = YELLOW
            self.size = 6
            self.trail_particles = []
        elif spell_type == "ice":
            self.speed = 250
            self.damage = 80
            self.color = LIGHT_BLUE
            self.size = 10
            self.trail_particles = []
        elif spell_type == "heal":
            self.speed = 0  
            self.damage = -50  
            self.color = GREEN
            self.size = 15
            self.trail_particles = []
        elif spell_type == "shield":
            self.speed = 0 
            self.damage = 0
            self.color = PURPLE
            self.size = 20
            self.trail_particles = []
        elif spell_type == "teleport":
            self.speed = 0  
            self.damage = 0
            self.color = (255, 0, 255)  
            self.size = 12
            self.trail_particles = []
        
        self.particle_timer = 0
        self.particle_spawn_rate = 50 
            
    def update(self, dt, collision_map=None, map_width=0, map_height=0):
        """Update spell position and check collisions"""
        if not self.alive:
            return
            
        if self.speed == 0:
            self.alive = False 
            return
            
        old_x, old_y = self.x, self.y
        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt
        
        self.particle_timer += dt * 1000
        if self.particle_timer > self.particle_spawn_rate:
            self.add_trail_particle(old_x, old_y)
            self.particle_timer = 0
        
        self.update_particles(dt)
        
        if collision_map:
            map_x = int(self.x // TILE_SIZE)
            map_y = int(self.y // TILE_SIZE)
            
            if (map_x < 0 or map_x >= map_width or 
                map_y < 0 or map_y >= map_height or 
                collision_map[map_y][map_x] != 0):
                if self.sound_manager:
                    self.sound_manager.play_sound('spell_hit')
                self.alive = False
    
    def add_trail_particle(self, x, y):
        """Add a particle to the spell's trail"""
        import random
        
        particle = {
            'x': x + random.uniform(-2, 2),
            'y': y + random.uniform(-2, 2),
            'life': 1.0, 
            'size': random.uniform(2, 4),
            'color': self.color
        }
        self.trail_particles.append(particle)
        
        if len(self.trail_particles) > 10:
            self.trail_particles.pop(0)
    
    def update_particles(self, dt):
        """Update trail particles"""
        for particle in self.trail_particles[:]:
            particle['life'] -= dt * 3  
            particle['size'] *= 0.98 
            
            if particle['life'] <= 0:
                self.trail_particles.remove(particle)
    
    def render_trail(self, screen):
        """Render spell trail particles"""
        import pygame
        
        for particle in self.trail_particles:
            if particle['life'] > 0:
                alpha = int(255 * particle['life'])
                size = max(1, int(particle['size']))
                
                particle_surface = pygame.Surface((size * 2, size * 2))
                particle_surface.set_alpha(alpha)
                particle_color = particle['color']
                
                brightness = particle['life']
                adjusted_color = tuple(int(c * brightness) for c in particle_color)
                
                pygame.draw.circle(particle_surface, adjusted_color, (size, size), size)
                screen.blit(particle_surface, (particle['x'] - size, particle['y'] - size))
    
    def on_hit_target(self):
        """Called when spell hits a target (enemy/boss)"""
        if self.sound_manager:
            if self.spell_type == "heal":
                pass
            else:
                self.sound_manager.play_sound('spell_hit')