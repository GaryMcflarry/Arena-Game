import pygame
from constants import GameState
from player import Player
from town_state import TownState
from arena_state import ArenaState
from shop_state import ShopState
from menu_state import MenuState

class FileSoundManager:
    """Sound manager that loads actual sound files"""
    def __init__(self):
        print("FileSoundManager: Initializing...")
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print(f"FileSoundManager: Mixer initialized: {pygame.mixer.get_init()}")
        except Exception as e:
            print(f"FileSoundManager: Mixer init failed: {e}")
        
        self.sounds = {}
        self.sfx_volume = 0.8
        print("FileSoundManager: Loading sound files...")
        self.load_sound_files()
        print(f"FileSoundManager: Finished - loaded {len(self.sounds)} sounds")
        
    def load_sound_files(self):
        """Load sound files from assets folder"""
        import os
        
        # Map game sound names to your available files
        sound_file_map = {
            'spell_cast': '../assets/sounds/sfx/flame_spell.mp3',
            'spell_hit': '../assets/sounds/sfx/flame_spell.mp3',  # Reuse flame spell
            'heal': '../assets/sounds/sfx/health_spell.mp3',
            'enemy_hit': '../assets/sounds/sfx/flame_spell.mp3',  # Reuse flame spell
            'enemy_death': '../assets/sounds/sfx/flame_spell.mp3',  # Reuse flame spell
            'player_hit': '../assets/sounds/sfx/health_spell.mp3',  # Reuse health spell
            'boss_spawn': '../assets/sounds/sfx/flame_spell.mp3',  # Reuse flame spell
            'wave_complete': '../assets/sounds/sfx/health_spell.mp3',  # Reuse health spell
            'shop_buy': '../assets/sounds/sfx/health_spell.mp3',  # Reuse health spell
            'menu_select': '../assets/sounds/sfx/flame_spell.mp3',  # Reuse flame spell
            'teleport': '../assets/sounds/sfx/health_spell.mp3'  # Reuse health spell
        }
        
        for sound_name, file_path in sound_file_map.items():
            try:
                print(f"  Loading {sound_name} from {file_path}...")
                if os.path.exists(file_path):
                    sound = pygame.mixer.Sound(file_path)
                    sound.set_volume(self.sfx_volume)
                    self.sounds[sound_name] = sound
                    print(f"  ✓ Loaded {sound_name}")
                else:
                    print(f"  ✗ File not found: {file_path}")
            except Exception as e:
                print(f"  ✗ Failed to load {sound_name}: {e}")
        
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
                print(f"♪ Playing: {sound_name}")
            except pygame.error as e:
                print(f"Failed to play {sound_name}: {e}")
        else:
            print(f"Sound {sound_name} not found in {list(self.sounds.keys())}")
                
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

class UltraSimpleSoundManager:
    """Ultra simple sound manager using only basic pygame"""
    def __init__(self):
        print("UltraSimpleSoundManager: Initializing...")
        try:
            pygame.mixer.init()
            print(f"UltraSimpleSoundManager: Mixer initialized: {pygame.mixer.get_init()}")
        except Exception as e:
            print(f"UltraSimpleSoundManager: Mixer init failed: {e}")
        
        self.sounds = {}
        self.sfx_volume = 0.8
        print("UltraSimpleSoundManager: Creating placeholder sounds...")
        self.create_placeholder_sounds()
        print(f"UltraSimpleSoundManager: Finished - created {len(self.sounds)} sounds")
        
    def create_placeholder_sounds(self):
        """Create placeholder sounds that just print messages"""
        sound_names = [
            'spell_cast', 'spell_hit', 'enemy_hit', 'enemy_death', 
            'player_hit', 'boss_spawn', 'wave_complete', 'shop_buy', 
            'menu_select', 'teleport'
        ]
        
        for sound_name in sound_names:
            try:
                # Create a minimal "sound" object that just tracks the name
                self.sounds[sound_name] = sound_name
                print(f"  ✓ Created placeholder for {sound_name}")
            except Exception as e:
                print(f"  ✗ Failed to create placeholder {sound_name}: {e}")
        
    def play_sound(self, sound_name):
        """Play a sound effect (placeholder - just prints)"""
        if sound_name in self.sounds:
            print(f"🔊 SOUND: {sound_name}")
        else:
            print(f"Sound {sound_name} not found in {list(self.sounds.keys())}")
                
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))

class SimpleSoundManager:
    """Simplified sound manager without numpy dependency"""
    def __init__(self):
        print("SimpleSoundManager: Initializing...")
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print(f"SimpleSoundManager: Mixer initialized: {pygame.mixer.get_init()}")
        except Exception as e:
            print(f"SimpleSoundManager: Mixer init failed: {e}")
        
        self.sounds = {}
        self.sfx_volume = 0.8
        print("SimpleSoundManager: About to create sounds...")
        self.create_simple_sounds()
        print(f"SimpleSoundManager: Finished - created {len(self.sounds)} sounds")
        
    def create_simple_sounds(self):
        """Create simple beep sounds without numpy"""
        print("Creating simple sounds...")
        sound_configs = {
            'spell_cast': (440, 300),     # 440Hz for 300ms
            'spell_hit': (330, 200),      # 330Hz for 200ms  
            'enemy_hit': (220, 150),      # 220Hz for 150ms
            'enemy_death': (165, 500),    # 165Hz for 500ms
            'player_hit': (110, 400),     # 110Hz for 400ms
            'boss_spawn': (880, 800),     # 880Hz for 800ms
            'wave_complete': (523, 600),  # 523Hz for 600ms
            'shop_buy': (660, 250),       # 660Hz for 250ms
            'menu_select': (550, 100),    # 550Hz for 100ms
            'teleport': (770, 400)        # 770Hz for 400ms
        }
        
        for sound_name, (frequency, duration) in sound_configs.items():
            try:
                print(f"  Creating {sound_name} ({frequency}Hz, {duration}ms)...")
                self.sounds[sound_name] = self.create_beep(frequency, duration)
                print(f"  ✓ Created {sound_name}")
            except Exception as e:
                print(f"  ✗ Failed to create sound {sound_name}: {e}")
                import traceback
                traceback.print_exc()
                
    def create_beep(self, frequency, duration_ms):
        """Create a simple beep sound"""
        try:
            sample_rate = 22050
            frames = duration_ms * sample_rate // 1000
            
            print(f"    Creating beep: {frames} frames")
            
            # Create simple sine wave approximation using square wave
            arr = []
            cycle_length = max(1, sample_rate // frequency)  # Prevent division by zero
            
            for i in range(frames):
                # Simple square wave that approximates sine
                wave_val = int(4096 * self.sfx_volume) if (i % cycle_length) < (cycle_length // 2) else int(-4096 * self.sfx_volume)
                # Fade out effect
                fade_factor = max(0, 1 - (i / frames) * 0.5)
                wave_val = int(wave_val * fade_factor)
                arr.append([wave_val, wave_val])  # Stereo
            
            print(f"    Created array with {len(arr)} samples")
            sound = pygame.sndarray.make_sound(arr)
            print(f"    pygame.sndarray.make_sound successful")
            return sound
            
        except Exception as e:
            print(f"    create_beep failed: {e}")
            import traceback
            traceback.print_exc()
            raise
        
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
                print(f"Played sound: {sound_name}")
            except pygame.error as e:
                print(f"Failed to play {sound_name}: {e}")
        else:
            print(f"Sound {sound_name} not found in {list(self.sounds.keys())}")
                
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))

class SoundManager:
    """Handles all game sound effects"""
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.sounds = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.load_sounds()
        
    def load_sounds(self):
        """Load all sound effects with fallback generation"""
        sound_files = {
            'spell_cast': 'assets/sounds/spell_cast.wav',
            'spell_hit': 'assets/sounds/spell_hit.wav', 
            'enemy_hit': 'assets/sounds/enemy_hit.wav',
            'enemy_death': 'assets/sounds/enemy_death.wav',
            'player_hit': 'assets/sounds/player_hit.wav',
            'boss_spawn': 'assets/sounds/boss_spawn.wav',
            'wave_complete': 'assets/sounds/wave_complete.wav',
            'shop_buy': 'assets/sounds/shop_buy.wav',
            'menu_select': 'assets/sounds/menu_select.wav',
            'teleport': 'assets/sounds/teleport.wav'
        }
        
        for sound_name, file_path in sound_files.items():
            try:
                self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                self.sounds[sound_name].set_volume(self.sfx_volume)
            except (pygame.error, FileNotFoundError):
                # Generate fallback sounds
                self.sounds[sound_name] = self.generate_fallback_sound(sound_name)
                
    def generate_fallback_sound(self, sound_type):
        """Generate simple procedural sound effects"""
        try:
            import numpy as np
        except ImportError:
            # If numpy isn't available, create simple beep sounds
            return self.create_simple_beep(sound_type)
        
        sample_rate = 22050
        
        if sound_type == 'spell_cast':
            # Rising pitch whoosh
            duration = 0.3
            t = np.linspace(0, duration, int(sample_rate * duration))
            frequency = 200 + 300 * t / duration
            wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 3)
            
        elif sound_type == 'spell_hit':
            # Sharp impact
            duration = 0.2
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = np.random.normal(0, 0.3, len(t)) * np.exp(-t * 8)
            
        elif sound_type == 'enemy_hit':
            # Grunt sound
            duration = 0.15
            t = np.linspace(0, duration, int(sample_rate * duration))
            frequency = 150
            wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 5)
            
        elif sound_type == 'enemy_death':
            # Falling pitch
            duration = 0.5
            t = np.linspace(0, duration, int(sample_rate * duration))
            frequency = 300 - 250 * t / duration
            wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 2)
            
        elif sound_type == 'player_hit':
            # Low thud
            duration = 0.3
            t = np.linspace(0, duration, int(sample_rate * duration))
            frequency = 80
            wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 4)
            
        elif sound_type == 'boss_spawn':
            # Dramatic rising chord
            duration = 1.0
            t = np.linspace(0, duration, int(sample_rate * duration))
            freq1 = 100 + 200 * t / duration
            freq2 = 150 + 300 * t / duration
            wave = (np.sin(2 * np.pi * freq1 * t) + np.sin(2 * np.pi * freq2 * t)) * 0.5
            
        elif sound_type == 'wave_complete':
            # Victory chime
            duration = 0.8
            t = np.linspace(0, duration, int(sample_rate * duration))
            frequencies = [523, 659, 784]  # C, E, G major chord
            wave = np.zeros(len(t))
            for freq in frequencies:
                wave += np.sin(2 * np.pi * freq * t) * np.exp(-t * 1.5)
            wave /= len(frequencies)
            
        elif sound_type == 'shop_buy':
            # Coin clink
            duration = 0.4
            t = np.linspace(0, duration, int(sample_rate * duration))
            frequency = 800
            wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 6)
            
        elif sound_type == 'menu_select':
            # Simple beep
            duration = 0.1
            t = np.linspace(0, duration, int(sample_rate * duration))
            frequency = 600
            wave = np.sin(2 * np.pi * frequency * t)
            
        elif sound_type == 'teleport':
            # Magical sparkle
            duration = 0.6
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = np.zeros(len(t))
            for i in range(5):
                freq = 400 + i * 200
                phase = i * 0.2
                wave += np.sin(2 * np.pi * freq * (t + phase)) * np.exp(-(t + phase) * 3)
            wave /= 5
            
        else:
            # Default beep
            duration = 0.1
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = np.sin(2 * np.pi * 440 * t)
        
        # Normalize and convert to pygame sound
        wave = np.clip(wave * 32767 * self.sfx_volume, -32767, 32767).astype(np.int16)
        # Convert mono to stereo
        stereo_wave = np.array([wave, wave]).T
        
        try:
            sound = pygame.sndarray.make_sound(stereo_wave)
            return sound
        except:
            # Fallback to simple beep if numpy conversion fails
            return self.create_simple_beep(sound_type)
    
    def create_simple_beep(self, sound_type):
        """Create simple beep sounds without numpy"""
        # Simple frequency-based sounds
        frequencies = {
            'spell_cast': 440,
            'spell_hit': 330,
            'enemy_hit': 220,
            'enemy_death': 165,
            'player_hit': 110,
            'boss_spawn': 880,
            'wave_complete': 523,
            'shop_buy': 660,
            'menu_select': 550,
            'teleport': 770
        }
        
        freq = frequencies.get(sound_type, 440)
        duration = 200  # milliseconds
        
        # Create a simple sine wave beep
        sample_rate = 22050
        frames = int(duration * sample_rate / 1000)
        
        arr = []
        for i in range(frames):
            time_point = float(i) / sample_rate
            wave_val = int(4096 * self.sfx_volume * 
                          (1.0 if i < frames // 4 else 
                           max(0, 1.0 - (i - frames // 4) / (frames * 3 // 4))) *
                          (1 if int(2 * freq * time_point) % 2 else -1))
            arr.append([wave_val, wave_val])  # Stereo
        
        sound = pygame.sndarray.make_sound(arr)
        return sound
        
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except pygame.error:
                pass  # Ignore sound errors
                
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

class GameStateManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_state = GameState.MENU
        self.states = {}
        
        # Initialize sound manager with fallback
        print("=== INITIALIZING SOUND MANAGER ===")
        try:
            print("1. Trying file-based SoundManager...")
            self.sound_manager = FileSoundManager()
            print(f"File SoundManager created: {self.sound_manager}")
            if self.sound_manager and hasattr(self.sound_manager, 'sounds'):
                print(f"File SoundManager has {len(self.sound_manager.sounds)} sounds")
                if len(self.sound_manager.sounds) > 0:
                    print("Using file-based sound manager!")
                else:
                    raise Exception("File SoundManager created no sounds")
        except Exception as e:
            print(f"File SoundManager failed: {e}")
            try:
                print("2. Trying complex SoundManager...")
                self.sound_manager = SoundManager()
                print(f"Complex SoundManager created: {self.sound_manager}")
                if self.sound_manager and hasattr(self.sound_manager, 'sounds'):
                    print(f"Complex SoundManager has {len(self.sound_manager.sounds)} sounds")
                    if len(self.sound_manager.sounds) == 0:
                        raise Exception("Complex SoundManager created no sounds")
            except Exception as e2:
                print(f"Complex SoundManager also failed: {e2}")
                try:
                    print("3. Trying simple SoundManager...")
                    self.sound_manager = SimpleSoundManager()
                    print(f"Simple SoundManager created: {self.sound_manager}")
                    if self.sound_manager and hasattr(self.sound_manager, 'sounds'):
                        print(f"Simple SoundManager has {len(self.sound_manager.sounds)} sounds")
                        if len(self.sound_manager.sounds) == 0:
                            raise Exception("Simple SoundManager created no sounds")
                except Exception as e3:
                    print(f"Simple SoundManager also failed: {e3}")
                    try:
                        print("4. Trying ultra simple SoundManager...")
                        self.sound_manager = UltraSimpleSoundManager()
                        print(f"Ultra simple SoundManager created: {self.sound_manager}")
                        if self.sound_manager and hasattr(self.sound_manager, 'sounds'):
                            print(f"Ultra simple SoundManager has {len(self.sound_manager.sounds)} sounds")
                    except Exception as e4:
                        print(f"All sound managers failed: {e4}")
                        import traceback
                        traceback.print_exc()
                        self.sound_manager = None
        
        print(f"Final sound_manager: {self.sound_manager}")
        print(f"Sound manager is not None: {self.sound_manager is not None}")
        print("=== END SOUND MANAGER INIT ===")
        
        # Initialize player (persistent across states)
        self.player = Player(400, 300, 0)  # Start in town center
        
        # Initialize all game states
        self.states[GameState.MENU] = MenuState(screen, self)
        self.states[GameState.TOWN] = TownState(screen, self, self.player)
        self.states[GameState.ARENA] = ArenaState(screen, self, self.player)
        self.states[GameState.SHOP] = ShopState(screen, self, self.player)
        
        # Set sound manager for each state with detailed logging
        print("=== SETTING SOUND MANAGERS ===")
        for state_name, state in self.states.items():
            print(f"Checking state {state_name}...")
            if hasattr(state, 'sound_manager'):
                print(f"  - Has sound_manager attribute")
                print(f"  - Before assignment: {getattr(state, 'sound_manager', 'NOT SET')}")
                state.sound_manager = self.sound_manager
                print(f"  - After assignment: {getattr(state, 'sound_manager', 'NOT SET')}")
                print(f"  - Assignment successful: {state.sound_manager is self.sound_manager}")
                print(f"  - State sound_manager is not None: {state.sound_manager is not None}")
            else:
                print(f"  - No sound_manager attribute")
        print("=== END SETTING SOUND MANAGERS ===")
        
        # Mouse capture settings
        self.mouse_captured = False
        
        # Track arena wave progression
        self.came_from_arena_shop = False
        
    def debug_sound_system(self):
        print("=== SOUND SYSTEM DEBUG ===")
        print(f"Sound manager exists: {self.sound_manager is not None}")
        
        if self.sound_manager:
            print(f"Pygame mixer info: {pygame.mixer.get_init()}")
            print(f"Number of sounds loaded: {len(self.sound_manager.sounds)}")
            print(f"Available sounds: {list(self.sound_manager.sounds.keys())}")
            
            # Test basic pygame sound capability
            try:
                print("Testing basic pygame sound...")
                # Create a simple beep
                duration = 500  # milliseconds
                sample_rate = 22050
                frames = duration * sample_rate // 1000
                
                # Simple square wave
                arr = []
                for i in range(frames):
                    wave_val = 2000 if (i // 50) % 2 else -2000
                    arr.append([wave_val, wave_val])  # Stereo
                
                test_sound = pygame.sndarray.make_sound(arr)
                test_sound.play()
                print("✓ Basic pygame sound test played")
                
            except Exception as e:
                print(f"✗ Basic pygame sound test failed: {e}")
            
            # Test our sound manager
            try:
                print("Testing sound manager spell_cast...")
                self.sound_manager.play_sound('spell_cast')
                print("✓ Sound manager test completed")
            except Exception as e:
                print(f"✗ Sound manager test failed: {e}")
        else:
            print("✗ Sound manager is None")
        
        print("=== END SOUND DEBUG ===")
        
    def play_sound(self, sound_name):
        """Play a sound effect through the sound manager"""
        if self.sound_manager:
            self.sound_manager.play_sound(sound_name)
        
    def change_state(self, new_state, shop_type=None):
        """Change the current game state"""
        # Play menu selection sound
        self.play_sound('menu_select')
        
        # Track if coming from arena for shop after boss fight
        if self.current_state == GameState.ARENA and new_state == GameState.TOWN:
            # Check if this was from a shop prompt after boss fight
            arena_state = self.states[GameState.ARENA]
            if hasattr(arena_state, 'show_shop_prompt') and arena_state.show_shop_prompt:
                self.came_from_arena_shop = True
        
        # Release mouse when going to menu states
        if new_state in [GameState.MENU, GameState.SHOP]:
            self.release_mouse()
        # Capture mouse for 3D states
        elif new_state in [GameState.TOWN, GameState.ARENA]:
            self.capture_mouse()
            
        self.current_state = new_state
        
        # Initialize the new state
        if new_state == GameState.SHOP and shop_type:
            self.states[GameState.SHOP].set_shop_type(shop_type)
        elif new_state == GameState.ARENA:
            # CRITICAL: Ensure arena has sound manager before initializing
            if hasattr(self.states[GameState.ARENA], 'sound_manager'):
                self.states[GameState.ARENA].sound_manager = self.sound_manager
                print(f"Arena sound manager set: {self.states[GameState.ARENA].sound_manager is not None}")
            
            if self.came_from_arena_shop:
                # Continue from where player left off
                self.states[GameState.ARENA].continue_from_shop()
                self.came_from_arena_shop = False
            else:
                # Fresh start
                self.states[GameState.ARENA].initialize_arena()
        elif new_state == GameState.TOWN:
            # Ensure town has sound manager too
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
            pygame.mouse.set_pos(400, 300)  # Center mouse
            self.mouse_captured = False
            
    def handle_event(self, event):
        """Handle events for the current state"""
        # Global ESC handling for town state
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and 
            self.current_state == GameState.TOWN):
            self.change_state(GameState.MENU)
            return
        
        # Let current state handle all other events
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
        
        # Draw crosshair for 3D states
        if self.current_state in [GameState.TOWN, GameState.ARENA]:
            self.draw_crosshair()
        
    def draw_crosshair(self):
        """Draw a crosshair in the center of the screen"""
        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2
        
        crosshair_size = 20
        crosshair_thickness = 2
        crosshair_gap = 5
        
        # Use white with slight transparency for visibility
        crosshair_color = (255, 255, 255)
        
        # Draw horizontal lines
        pygame.draw.rect(self.screen, crosshair_color, 
                        (center_x - crosshair_size, center_y - crosshair_thickness//2, 
                         crosshair_size - crosshair_gap, crosshair_thickness))
        pygame.draw.rect(self.screen, crosshair_color,
                        (center_x + crosshair_gap, center_y - crosshair_thickness//2,
                         crosshair_size - crosshair_gap, crosshair_thickness))
        
        # Draw vertical lines  
        pygame.draw.rect(self.screen, crosshair_color,
                        (center_x - crosshair_thickness//2, center_y - crosshair_size,
                         crosshair_thickness, crosshair_size - crosshair_gap))
        pygame.draw.rect(self.screen, crosshair_color,
                        (center_x - crosshair_thickness//2, center_y + crosshair_gap,
                         crosshair_thickness, crosshair_size - crosshair_gap))
        
        # Optional: Draw center dot
        pygame.draw.circle(self.screen, crosshair_color, (center_x, center_y), 1)
        
    def quit_game(self):
        """Quit the game"""
        pygame.quit()
        exit()