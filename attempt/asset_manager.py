import pygame
import os

class AssetManager:
    """Manages loading and caching of game assets"""
    
    def __init__(self):
        self.textures = {}
        self.sounds = {}
        self.fonts = {}
        
        self.texture_path = "assets/textures/"
        self.sound_path = "assets/sounds/"
        self.font_path = "assets/fonts/"
        
        self.create_directories()
        
        self.load_default_assets()
        
    def create_directories(self):
        """Create asset directories if they don't exist"""
        directories = [
            "assets",
            "assets/textures",
            "assets/textures/town",
            "assets/textures/arena", 
            "assets/textures/ui",
            "assets/textures/npcs",
            "assets/textures/enemies",
            "assets/textures/bosses",
            "assets/sounds",
            "assets/sounds/sfx",
            "assets/sounds/music",
            "assets/fonts"
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
    
    def load_texture(self, filename, key=None):
        """Load a texture and cache it"""
        if key is None:
            key = filename
            
        if key in self.textures:
            return self.textures[key]
            
        full_path = os.path.join(self.texture_path, filename)
        
        if not os.path.exists(full_path):
            print(f"Texture file not found: {filename} (will use placeholder)")
            placeholder = self.create_placeholder_texture()
            self.textures[key] = placeholder
            return placeholder
            
        try:
            texture = pygame.image.load(full_path).convert_alpha()
            self.textures[key] = texture
            print(f"Loaded texture: {filename}")
            return texture
        except pygame.error as e:
            print(f"Could not load texture {filename}: {e}")
            placeholder = self.create_placeholder_texture()
            self.textures[key] = placeholder
            return placeholder
    
    def create_placeholder_texture(self, size=(64, 64), color=(128, 128, 128)):
        """Create a placeholder texture when file is missing"""
        surface = pygame.Surface(size)
        surface.fill(color)
        
        pygame.draw.rect(surface, (200, 200, 200), (0, 0, size[0]//2, size[1]//2))
        pygame.draw.rect(surface, (200, 200, 200), (size[0]//2, size[1]//2, size[0]//2, size[1]//2))
        
        return surface
    
    def load_default_assets(self):
        """Load default textures with fallbacks"""
        default_textures = {
            "town_wall": "town/stone_wall.png",
            "house_wall": "town/wood_wall.png", 
            "weapon_shop": "town/forge_wall.png",
            "magic_shop": "town/magic_wall.png",
            "healer_wall": "town/temple_wall.png",
            "arena_entrance": "town/arena_wall.png",
            
            "cobblestone": "town/cobblestone.png",
            "dirt_path": "town/dirt.png",
            
            "arena_wall": "arena/stone_wall.png",
            "arena_pillar": "arena/pillar.png",
            "arena_floor": "arena/stone_floor.png",
            
            "crosshair": "ui/crosshair.png",
            "health_bar": "ui/health_bar.png",
        }
        
        for key, filename in default_textures.items():
            try:
                self.load_texture(filename, key)
            except Exception as e:
                print(f"Could not load {filename}, will use placeholder: {e}")
                self.textures[key] = self.create_placeholder_texture()
    
    def get_texture(self, key):
        """Get a texture by key, return placeholder if not found"""
        if key in self.textures:
            return self.textures[key]
        else:
            print(f"Texture '{key}' not found, using placeholder")
            return self.create_placeholder_texture()
    
    def get_scaled_texture(self, key, width, height):
        """Get a texture scaled to specific dimensions"""
        texture = self.get_texture(key)
        return pygame.transform.scale(texture, (width, height))
    
    def load_sound(self, filename, key=None):
        """Load a sound effect"""
        if key is None:
            key = filename
            
        if key in self.sounds:
            return self.sounds[key]
            
        full_path = os.path.join(self.sound_path, filename)
        
        try:
            sound = pygame.mixer.Sound(full_path)
            self.sounds[key] = sound
            print(f"Loaded sound: {filename}")
            return sound
        except pygame.error as e:
            print(f"Could not load sound {filename}: {e}")
            return None
    
    def get_sound(self, key):
        """Get a sound by key"""
        return self.sounds.get(key, None)
    
    def preload_assets(self):
        """Preload commonly used assets for better performance"""
        common_textures = [
            "town_wall", "house_wall", "cobblestone", 
            "arena_wall", "arena_floor"
        ]
        
        for texture_key in common_textures:
            self.get_texture(texture_key)

asset_manager = AssetManager()