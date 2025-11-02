import pygame
import math
from constants import GameState
from player import Player
from town_state import TownState
from arena_state import ArenaState
from shop_state import ShopState
from menu_state import MenuState

class FileSoundManager:
    """Sound manager that loads actual sound files"""
    def __init__(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except Exception as e:
            pass
        
        self.sounds = {}
        self.music = {}
        self.current_music = None
        self.sfx_volume = 0.8
        self.music_volume = 0.6
        
        self.load_sound_files()
        self.load_music_files()
        
    def load_sound_files(self):
        """Load sound effect files from assets folder"""
        import os
        
        actual_sounds = {}
        sound_files = {
            'flame_spell': '../assets/sounds/sfx/flame_spell.mp3',
            'health_spell': '../assets/sounds/sfx/health_spell.mp3',
            'boss_spawn': '../assets/sounds/sfx/boss_spawn.mp3',
            'enemy_hit': '../assets/sounds/sfx/enemy_hit.mp3',
            'enemy_death': '../assets/sounds/sfx/enemy_death.mp3',
            'player_hit': '../assets/sounds/sfx/player_hit.mp3',
            'wave_complete': '../assets/sounds/sfx/wave_complete.mp3',
            'shop_buy': '../assets/sounds/sfx/shop_buy.mp3',
            'menu_select': '../assets/sounds/sfx/menu_select.mp3',
            'spell_hit': '../assets/sounds/sfx/spell_hit.mp3',
        }
        
        # Load available sound files
        for sound_key, file_path in sound_files.items():
            try:
                if os.path.exists(file_path):
                    sound = pygame.mixer.Sound(file_path)
                    sound.set_volume(self.sfx_volume)
                    actual_sounds[sound_key] = sound
            except Exception as e:
                pass
        
        # Map loaded sounds to game events
        if 'flame_spell' in actual_sounds:
            self.sounds['spell_cast'] = actual_sounds['flame_spell']
        
        if 'spell_hit' in actual_sounds:
            self.sounds['spell_hit'] = actual_sounds['spell_hit']
            
        if 'enemy_hit' in actual_sounds:
            self.sounds['enemy_hit'] = actual_sounds['enemy_hit']
            
        if 'enemy_death' in actual_sounds:
            self.sounds['enemy_death'] = actual_sounds['enemy_death']
            
        if 'boss_spawn' in actual_sounds:
            self.sounds['boss_spawn'] = actual_sounds['boss_spawn']
            
        if 'menu_select' in actual_sounds:
            self.sounds['menu_select'] = actual_sounds['menu_select']

        if 'health_spell' in actual_sounds:
            self.sounds['heal'] = actual_sounds['health_spell']
            
        if 'player_hit' in actual_sounds:
            self.sounds['player_hit'] = actual_sounds['player_hit']
            
        if 'wave_complete' in actual_sounds:
            self.sounds['wave_complete'] = actual_sounds['wave_complete']
            
        if 'shop_buy' in actual_sounds:
            self.sounds['shop_buy'] = actual_sounds['shop_buy']
        
        # Create placeholders if no sounds loaded
        if not self.sounds:
            self.create_placeholder_sounds()

    def create_placeholder_sounds(self):
        """Create placeholder sounds that just print messages"""
        sound_names = [
            'spell_cast', 'spell_hit', 'enemy_hit', 'enemy_death', 
            'player_hit', 'boss_spawn', 'wave_complete', 'shop_buy', 
            'menu_select', 'heal', 'teleport'
        ]
        
        for sound_name in sound_names:
            self.sounds[sound_name] = f"placeholder_{sound_name}"

    def load_music_files(self):
        """Load background music files"""
        import os
        
        music_file_map = {
            'menu': '../assets/sounds/music/menu_theme.mp3',
            'town': '../assets/sounds/music/town_theme.mp3', 
            'arena': '../assets/sounds/music/arena_theme.mp3',
            'shop': '../assets/sounds/music/shop_theme.mp3'
        }
        
        for music_name, file_path in music_file_map.items():
            try:
                if os.path.exists(file_path):
                    self.music[music_name] = file_path
            except Exception as e:
                pass
        
        # Start menu music if available
        if 'menu' in self.music:
            self.play_music('menu')
        
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            try:
                sound = self.sounds[sound_name]
                if isinstance(sound, str) and sound.startswith("placeholder_"):
                    pass
                else:
                    sound.play()
            except pygame.error as e:
                pass

    def play_music(self, music_name, loop=True):
        """Play background music"""
        if music_name in self.music and music_name != self.current_music:
            try:
                pygame.mixer.music.load(self.music[music_name])
                pygame.mixer.music.set_volume(self.music_volume)
                loops = -1 if loop else 0
                pygame.mixer.music.play(loops)
                self.current_music = music_name
            except pygame.error as e:
                pass

    def stop_music(self):
        """Stop current background music"""
        pygame.mixer.music.stop()
        self.current_music = None

    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
                
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if hasattr(sound, 'set_volume'):
                sound.set_volume(self.sfx_volume)


class WorkingSoundManager:
    """Working sound manager that creates sounds programmatically"""
    def __init__(self):
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
        except Exception as e:
            pass
        
        self.sounds = {}
        self.sfx_volume = 0.7
        self.music_volume = 0.5
        
        self.create_procedural_sounds()
        self.start_menu_music()
        
    def create_procedural_sounds(self):
        """Create sounds using pygame's built-in capabilities"""
        
        try:
            self.sounds['spell_cast'] = self.create_tone_sequence([440, 550, 660], [100, 100, 100])
        except:
            self.sounds['spell_cast'] = None
            
        try:
            self.sounds['spell_hit'] = self.create_noise_burst(200, 0.3)
        except:
            self.sounds['spell_hit'] = None
            
        try:
            self.sounds['enemy_hit'] = self.create_noise_burst(150, 0.4)
        except:
            self.sounds['enemy_hit'] = None
            
        try:
            self.sounds['enemy_death'] = self.create_tone_sequence([330, 220, 110], [150, 150, 200])
        except:
            self.sounds['enemy_death'] = None
            
        try:
            self.sounds['player_hit'] = self.create_noise_burst(300, 0.6)
        except:
            self.sounds['player_hit'] = None
            
        try:
            self.sounds['boss_spawn'] = self.create_tone_sequence([220, 440, 880], [200, 200, 400])
        except:
            self.sounds['boss_spawn'] = None
            
        try:
            self.sounds['wave_complete'] = self.create_tone_sequence([440, 523, 659, 880], [150, 150, 150, 300])
        except:
            self.sounds['wave_complete'] = None
            
        try:
            self.sounds['shop_buy'] = self.create_tone_sequence([523, 659, 784], [100, 100, 200])
        except:
            self.sounds['shop_buy'] = None
            
        try:
            self.sounds['menu_select'] = self.create_simple_beep(550, 100)
        except:
            self.sounds['menu_select'] = None
            
        try:
            self.sounds['heal'] = self.create_tone_sequence([392, 523, 659], [200, 200, 200])
        except:
            self.sounds['heal'] = None
            
        try:
            self.sounds['teleport'] = self.create_tone_sequence([880, 440, 220, 440, 880], [80, 80, 80, 80, 80])
        except:
            self.sounds['teleport'] = None
    
    def create_simple_beep(self, frequency, duration_ms):
        """Create a simple beep using pygame's built-in sound generation"""
        try:
            sample_rate = 22050
            frames = duration_ms * sample_rate // 1000
            
            volume = int(self.sfx_volume * 16384)
            samples = []
            
            for i in range(frames):
                angle = 2.0 * math.pi * frequency * i / sample_rate
                sample = int(volume * math.sin(angle))
                
                # Apply fade out
                fade_factor = 1.0 - (i / frames) * 0.5
                sample = int(sample * fade_factor)
                
                samples.extend([sample, sample])
            
            # Convert to bytes
            sound_buffer = bytes()
            for sample in samples:
                if sample > 32767:
                    sample = 32767
                elif sample < -32768:
                    sample = -32768
                sound_buffer += sample.to_bytes(2, byteorder='little', signed=True)
            
            sound = pygame.mixer.Sound(buffer=sound_buffer)
            return sound
            
        except Exception as e:
            return None
    
    def create_tone_sequence(self, frequencies, durations):
        """Create a sequence of tones"""
        try:
            sample_rate = 22050
            all_samples = []
            
            for freq, duration_ms in zip(frequencies, durations):
                frames = duration_ms * sample_rate // 1000
                volume = int(self.sfx_volume * 8192)
                
                for i in range(frames):
                    angle = 2.0 * math.pi * freq * i / sample_rate
                    sample = int(volume * math.sin(angle))
                    
                    # Apply envelope
                    envelope = 1.0
                    if i < frames * 0.1:
                        envelope = i / (frames * 0.1)
                    elif i > frames * 0.8:
                        envelope = (frames - i) / (frames * 0.2)
                    
                    sample = int(sample * envelope)
                    all_samples.extend([sample, sample])
            
            # Convert to bytes
            sound_buffer = bytes()
            for sample in all_samples:
                if sample > 32767:
                    sample = 32767
                elif sample < -32768:
                    sample = -32768
                sound_buffer += sample.to_bytes(2, byteorder='little', signed=True)
            
            return pygame.mixer.Sound(buffer=sound_buffer)
            
        except Exception as e:
            return None
    
    def create_noise_burst(self, duration_ms, intensity=0.5):
        """Create a noise burst for impact sounds"""
        try:
            import random
            sample_rate = 22050
            frames = duration_ms * sample_rate // 1000
            volume = int(self.sfx_volume * intensity * 16384)
            
            samples = []
            for i in range(frames):
                noise = random.randint(-volume, volume)
                
                # Apply decay
                decay = math.exp(-i / (frames * 0.3))
                sample = int(noise * decay)
                
                samples.extend([sample, sample])
            
            # Convert to bytes
            sound_buffer = bytes()
            for sample in samples:
                if sample > 32767:
                    sample = 32767
                elif sample < -32768:
                    sample = -32768
                sound_buffer += sample.to_bytes(2, byteorder='little', signed=True)
            
            return pygame.mixer.Sound(buffer=sound_buffer)
            
        except Exception as e:
            return None
    
    def start_menu_music(self):
        """Start menu music - create a simple looping melody"""
        try:
            menu_melody = self.create_menu_melody()
            if menu_melody:
                menu_melody.play(loops=-1)
        except Exception as e:
            pass
    
    def create_menu_melody(self):
        """Create a simple looping menu melody"""
        try:
            notes = [
                (523, 500), 
                (440, 500),
                (349, 500),
                (392, 500),
                (523, 1000),
            ]
            
            sample_rate = 22050
            all_samples = []
            
            for freq, duration_ms in notes:
                frames = duration_ms * sample_rate // 1000
                volume = int(self.music_volume * 4096)
                
                for i in range(frames):
                    angle = 2.0 * math.pi * freq * i / sample_rate
                    # Create harmonics for richer sound
                    sample = int(volume * (
                        0.6 * math.sin(angle) +
                        0.3 * math.sin(angle * 2) +
                        0.1 * math.sin(angle * 3)
                    ))
                    
                    # Apply envelope
                    envelope = 1.0
                    if i < frames * 0.05:
                        envelope = i / (frames * 0.05)
                    elif i > frames * 0.9:
                        envelope = (frames - i) / (frames * 0.1)
                    
                    sample = int(sample * envelope)
                    all_samples.extend([sample, sample])
                
                # Add silence between notes
                silence_frames = sample_rate // 20
                for _ in range(silence_frames):
                    all_samples.extend([0, 0])
            
            # Convert to bytes
            sound_buffer = bytes()
            for sample in all_samples:
                if sample > 32767:
                    sample = 32767
                elif sample < -32768:
                    sample = -32768
                sound_buffer += sample.to_bytes(2, byteorder='little', signed=True)
            
            return pygame.mixer.Sound(buffer=sound_buffer)
            
        except Exception as e:
            return None
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except pygame.error as e:
                pass
    
    def play_music(self, music_name):
        """Play background music (simplified)"""
        pass
    
    def stop_music(self):
        """Stop all music"""
        pygame.mixer.stop()
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume):
        """Set music volume"""
        self.music_volume = max(0.0, min(1.0, volume))


class UltraSimpleSoundManager:
    """Ultra simple sound manager using only basic pygame"""
    def __init__(self):
        try:
            pygame.mixer.init()
        except Exception as e:
            pass
        
        self.sounds = {}
        self.sfx_volume = 0.8
        self.create_placeholder_sounds()
        
    def create_placeholder_sounds(self):
        """Create placeholder sounds that just print messages"""
        sound_names = [
            'spell_cast', 'spell_hit', 'enemy_hit', 'enemy_death', 
            'player_hit', 'boss_spawn', 'wave_complete', 'shop_buy', 
            'menu_select', 'teleport', 'heal'
        ]
        
        for sound_name in sound_names:
            try:
                self.sounds[sound_name] = sound_name
            except Exception as e:
                pass
        
    def play_sound(self, sound_name):
        """Play a sound effect (placeholder - silent)"""
        pass
                
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))


class GameStateManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_state = GameState.MENU
        self.states = {}
        
        # Initialize sound system with fallback chain
        try:
            self.sound_manager = FileSoundManager()
        except Exception as e:
            try:
                self.sound_manager = WorkingSoundManager()
            except Exception as e2:
                try:
                    self.sound_manager = UltraSimpleSoundManager()
                except Exception as e3:
                    self.sound_manager = None
        
        self.player = Player(400, 300, 0)
        
        # Initialize game states
        self.states[GameState.MENU] = MenuState(screen, self)
        self.states[GameState.TOWN] = TownState(screen, self, self.player)
        self.states[GameState.ARENA] = ArenaState(screen, self, self.player)
        self.states[GameState.SHOP] = ShopState(screen, self, self.player)
        
        # Set sound manager for all states
        for state in self.states.values():
            if hasattr(state, 'sound_manager'):
                state.sound_manager = self.sound_manager
        
        self.mouse_captured = False
        self.came_from_arena_shop = False
        
    def play_sound(self, sound_name):
        """Play a sound effect through the sound manager"""
        if self.sound_manager:
            self.sound_manager.play_sound(sound_name)
        
    def change_state(self, new_state, shop_type=None):
        """Change the current game state"""
        self.play_sound('menu_select')
        
        # Track if coming from arena shop
        if self.current_state == GameState.ARENA and new_state == GameState.TOWN:
            arena_state = self.states[GameState.ARENA]
            if hasattr(arena_state, 'show_shop_prompt') and arena_state.show_shop_prompt:
                self.came_from_arena_shop = True
        
        # Handle mouse capture/release
        if new_state in [GameState.MENU, GameState.SHOP]:
            self.release_mouse()
        elif new_state in [GameState.TOWN, GameState.ARENA]:
            self.capture_mouse()
            
        self.current_state = new_state
        
        # Change background music
        if hasattr(self.sound_manager, 'play_music'):
            if new_state == GameState.MENU:
                self.sound_manager.play_music('menu')
            elif new_state == GameState.TOWN:
                self.sound_manager.play_music('town')
            elif new_state == GameState.ARENA:
                self.sound_manager.play_music('arena')
            elif new_state == GameState.SHOP:
                self.sound_manager.play_music('shop')
        
        # Initialize state-specific logic
        if new_state == GameState.SHOP and shop_type:
            self.states[GameState.SHOP].set_shop_type(shop_type)
        elif new_state == GameState.ARENA:
            if hasattr(self.states[GameState.ARENA], 'sound_manager'):
                self.states[GameState.ARENA].sound_manager = self.sound_manager
            
            if self.came_from_arena_shop:
                self.states[GameState.ARENA].continue_from_shop()
                self.came_from_arena_shop = False
            else:
                self.states[GameState.ARENA].initialize_arena()
        elif new_state == GameState.TOWN:
            if hasattr(self.states[GameState.TOWN], 'sound_manager'):
                self.states[GameState.TOWN].sound_manager = self.sound_manager
            self.states[GameState.TOWN].initialize_town()
            
    def capture_mouse(self):
        """Capture mouse for FPS controls"""
        if not self.mouse_captured:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
            self.mouse_captured = True
            
    def release_mouse(self):
        """Release mouse for menu navigation"""
        if self.mouse_captured:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
            pygame.mouse.set_pos(400, 300)
            self.mouse_captured = False
            
    def handle_event(self, event):
        """Handle events for the current state"""
        # ESC to exit town
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and 
            self.current_state == GameState.TOWN):
            self.change_state(GameState.MENU)
            return
        
        current_state_obj = self.states[self.current_state]
        current_state_obj.handle_event(event)
        
    def update(self, dt):
        """Update the current state"""
        current_state_obj = self.states[self.current_state]
        current_state_obj.update(dt)
        
    def render(self):
        """Render the current state"""
        current_state_obj = self.states[self.current_state]
        current_state_obj.render()
        
        # Draw crosshair for first-person states
        if self.current_state in [GameState.TOWN, GameState.ARENA]:
            self.draw_crosshair()
        
    def draw_crosshair(self):
        """Draw a crosshair in the center of the screen"""
        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2
        
        crosshair_size = 20
        crosshair_thickness = 2
        crosshair_gap = 5
        crosshair_color = (255, 255, 255)
        
        # Horizontal lines
        pygame.draw.rect(self.screen, crosshair_color, 
                        (center_x - crosshair_size, center_y - crosshair_thickness//2, 
                         crosshair_size - crosshair_gap, crosshair_thickness))
        pygame.draw.rect(self.screen, crosshair_color,
                        (center_x + crosshair_gap, center_y - crosshair_thickness//2,
                         crosshair_size - crosshair_gap, crosshair_thickness))
        
        # Vertical lines
        pygame.draw.rect(self.screen, crosshair_color,
                        (center_x - crosshair_thickness//2, center_y - crosshair_size,
                         crosshair_thickness, crosshair_size - crosshair_gap))
        pygame.draw.rect(self.screen, crosshair_color,
                        (center_x - crosshair_thickness//2, center_y + crosshair_gap,
                         crosshair_thickness, crosshair_size - crosshair_gap))
        
        # Center dot
        pygame.draw.circle(self.screen, crosshair_color, (center_x, center_y), 1)
        
    def quit_game(self):
        """Quit the game"""
        pygame.quit()
        exit()