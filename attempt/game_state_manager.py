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
            print(f"FileSoundManager: Mixer initialized: {pygame.mixer.get_init()}")
        except Exception as e:
            print(f"FileSoundManager: Mixer init failed: {e}")
        
        self.sounds = {}
        self.music = {}
        self.current_music = None
        self.sfx_volume = 0.8
        self.music_volume = 0.6
        
        print("FileSoundManager: Loading sound files...")
        self.load_sound_files()
        print(f"FileSoundManager: Loaded {len(self.sounds)} sounds")
        
        print("FileSoundManager: Loading music files...")
        self.load_music_files()
        print(f"FileSoundManager: Loaded {len(self.music)} music tracks")
        
    def load_sound_files(self):
        """Load sound effect files from assets folder"""
        import os
        
        # First, try to load the actual sound files
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
        
        for sound_key, file_path in sound_files.items():
            try:
                if os.path.exists(file_path):
                    sound = pygame.mixer.Sound(file_path)
                    sound.set_volume(self.sfx_volume)
                    actual_sounds[sound_key] = sound
                    print(f"  ✓ Loaded {sound_key} from {file_path}")
                else:
                    print(f"  ✗ File not found: {file_path}")
            except Exception as e:
                print(f"  ✗ Failed to load {sound_key}: {e}")
        
        # Map game events to actual sounds (FIXED - moved outside loop)
        print("FileSoundManager: Mapping game sounds...")
        
        # Map available sounds to game events
        if 'flame_spell' in actual_sounds:
            self.sounds['spell_cast'] = actual_sounds['flame_spell']
            print("  ✓ Mapped spell_cast to flame_spell")
        
        if 'spell_hit' in actual_sounds:
            self.sounds['spell_hit'] = actual_sounds['spell_hit']
            print("  ✓ Mapped spell_hit")
            
        if 'enemy_hit' in actual_sounds:
            self.sounds['enemy_hit'] = actual_sounds['enemy_hit']
            print("  ✓ Mapped enemy_hit")
            
        if 'enemy_death' in actual_sounds:
            self.sounds['enemy_death'] = actual_sounds['enemy_death']
            print("  ✓ Mapped enemy_death")
            
        if 'boss_spawn' in actual_sounds:
            self.sounds['boss_spawn'] = actual_sounds['boss_spawn']
            print("  ✓ Mapped boss_spawn")
            
        if 'menu_select' in actual_sounds:
            self.sounds['menu_select'] = actual_sounds['menu_select']
            print("  ✓ Mapped menu_select")

        if 'health_spell' in actual_sounds:
            self.sounds['heal'] = actual_sounds['health_spell']
            print("  ✓ Mapped heal to health_spell")
            
        if 'player_hit' in actual_sounds:
            self.sounds['player_hit'] = actual_sounds['player_hit']
            print("  ✓ Mapped player_hit")
            
        if 'wave_complete' in actual_sounds:
            self.sounds['wave_complete'] = actual_sounds['wave_complete']
            print("  ✓ Mapped wave_complete")
            
        if 'shop_buy' in actual_sounds:
            self.sounds['shop_buy'] = actual_sounds['shop_buy']
            print("  ✓ Mapped shop_buy")
        
        # If no sounds loaded, create fallback placeholder sounds
        if not self.sounds:
            print("FileSoundManager: No sound files found, creating placeholders...")
            self.create_placeholder_sounds()

    def create_placeholder_sounds(self):
        """Create placeholder sounds that just print messages"""
        sound_names = [
            'spell_cast', 'spell_hit', 'enemy_hit', 'enemy_death', 
            'player_hit', 'boss_spawn', 'wave_complete', 'shop_buy', 
            'menu_select', 'heal', 'teleport'
        ]
        
        for sound_name in sound_names:
            # Create a minimal placeholder that tracks the name
            self.sounds[sound_name] = f"placeholder_{sound_name}"
            print(f"  ✓ Created placeholder for {sound_name}")

    def load_music_files(self):
        """Load background music files"""
        import os
        
        # Map game states to music files
        music_file_map = {
            'menu': '../assets/sounds/music/menu_theme.mp3',
            'town': '../assets/sounds/music/town_theme.mp3', 
            'arena': '../assets/sounds/music/arena_theme.mp3',
            'shop': '../assets/sounds/music/shop_theme.mp3'
        }
        
        for music_name, file_path in music_file_map.items():
            try:
                print(f"  Checking {music_name} music at {file_path}...")
                if os.path.exists(file_path):
                    self.music[music_name] = file_path  # Store path, not loaded music
                    print(f"  ✓ Found {music_name} music")
                else:
                    print(f"  ✗ Music file not found: {file_path}")
            except Exception as e:
                print(f"  ✗ Failed to check {music_name} music: {e}")
        
        # Start menu music if available
        if 'menu' in self.music:
            self.play_music('menu')
        
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            try:
                sound = self.sounds[sound_name]
                if isinstance(sound, str) and sound.startswith("placeholder_"):
                    # Placeholder sound - just print
                    print(f"🔊 PLACEHOLDER: {sound_name}")
                else:
                    # Real sound - play it
                    sound.play()
                    print(f"♪ Playing: {sound_name}")
            except pygame.error as e:
                print(f"Failed to play {sound_name}: {e}")
        else:
            print(f"Sound {sound_name} not available")

    def play_music(self, music_name, loop=True):
        """Play background music"""
        if music_name in self.music and music_name != self.current_music:
            try:
                pygame.mixer.music.load(self.music[music_name])
                pygame.mixer.music.set_volume(self.music_volume)
                loops = -1 if loop else 0  # -1 means infinite loop
                pygame.mixer.music.play(loops)
                self.current_music = music_name
                print(f"♫ Playing music: {music_name} (loop: {loop})")
            except pygame.error as e:
                print(f"Failed to play music {music_name}: {e}")
        elif music_name == self.current_music:
            print(f"Music {music_name} already playing")
        else:
            print(f"♫ Would play music: {music_name} (not available)")

    def stop_music(self):
        """Stop current background music"""
        pygame.mixer.music.stop()
        self.current_music = None
        print("Music stopped")

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
        print("WorkingSoundManager: Initializing...")
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            print(f"WorkingSoundManager: Mixer initialized: {pygame.mixer.get_init()}")
        except Exception as e:
            print(f"WorkingSoundManager: Mixer init failed: {e}")
        
        self.sounds = {}
        self.sfx_volume = 0.7
        self.music_volume = 0.5
        
        print("WorkingSoundManager: Creating procedural sounds...")
        self.create_procedural_sounds()
        print(f"WorkingSoundManager: Finished - created {len(self.sounds)} sounds")
        
        # Start menu music immediately
        self.start_menu_music()
        
    def create_procedural_sounds(self):
        """Create sounds using pygame's built-in capabilities"""
        # Create different types of sounds for different game events
        
        try:
            # Spell cast sound - rising tone
            self.sounds['spell_cast'] = self.create_tone_sequence([440, 550, 660], [100, 100, 100])
            print("  ✓ Created spell_cast")
        except:
            self.sounds['spell_cast'] = None
            
        try:
            # Spell hit - sharp impact
            self.sounds['spell_hit'] = self.create_noise_burst(200, 0.3)
            print("  ✓ Created spell_hit")
        except:
            self.sounds['spell_hit'] = None
            
        try:
            # Enemy hit - medium impact
            self.sounds['enemy_hit'] = self.create_noise_burst(150, 0.4)
            print("  ✓ Created enemy_hit")
        except:
            self.sounds['enemy_hit'] = None
            
        try:
            # Enemy death - falling tone
            self.sounds['enemy_death'] = self.create_tone_sequence([330, 220, 110], [150, 150, 200])
            print("  ✓ Created enemy_death")
        except:
            self.sounds['enemy_death'] = None
            
        try:
            # Player hit - low ominous tone
            self.sounds['player_hit'] = self.create_noise_burst(300, 0.6)
            print("  ✓ Created player_hit")
        except:
            self.sounds['player_hit'] = None
            
        try:
            # Boss spawn - dramatic chord
            self.sounds['boss_spawn'] = self.create_tone_sequence([220, 440, 880], [200, 200, 400])
            print("  ✓ Created boss_spawn")
        except:
            self.sounds['boss_spawn'] = None
            
        try:
            # Wave complete - victory fanfare
            self.sounds['wave_complete'] = self.create_tone_sequence([440, 523, 659, 880], [150, 150, 150, 300])
            print("  ✓ Created wave_complete")
        except:
            self.sounds['wave_complete'] = None
            
        try:
            # Shop buy - pleasant chime
            self.sounds['shop_buy'] = self.create_tone_sequence([523, 659, 784], [100, 100, 200])
            print("  ✓ Created shop_buy")
        except:
            self.sounds['shop_buy'] = None
            
        try:
            # Menu select - simple beep
            self.sounds['menu_select'] = self.create_simple_beep(550, 100)
            print("  ✓ Created menu_select")
        except:
            self.sounds['menu_select'] = None
            
        try:
            # Heal - soothing tone
            self.sounds['heal'] = self.create_tone_sequence([392, 523, 659], [200, 200, 200])
            print("  ✓ Created heal")
        except:
            self.sounds['heal'] = None
            
        try:
            # Teleport - warping sound
            self.sounds['teleport'] = self.create_tone_sequence([880, 440, 220, 440, 880], [80, 80, 80, 80, 80])
            print("  ✓ Created teleport")
        except:
            self.sounds['teleport'] = None
    
    def create_simple_beep(self, frequency, duration_ms):
        """Create a simple beep using pygame's built-in sound generation"""
        try:
            # Use a simpler approach - create raw audio data
            sample_rate = 22050
            frames = duration_ms * sample_rate // 1000
            
            # Create simple sine wave samples
            volume = int(self.sfx_volume * 16384)  # 16-bit audio range
            samples = []
            
            for i in range(frames):
                # Simple sine wave calculation
                angle = 2.0 * math.pi * frequency * i / sample_rate
                sample = int(volume * math.sin(angle))
                
                # Apply fade-out to prevent clicks
                fade_factor = 1.0 - (i / frames) * 0.5
                sample = int(sample * fade_factor)
                
                # Stereo samples (left, right)
                samples.extend([sample, sample])
            
            # Convert to bytes and create sound
            sound_buffer = bytes()
            for sample in samples:
                # Convert to 16-bit signed integer bytes
                if sample > 32767:
                    sample = 32767
                elif sample < -32768:
                    sample = -32768
                sound_buffer += sample.to_bytes(2, byteorder='little', signed=True)
            
            # Create pygame sound from raw buffer
            sound = pygame.mixer.Sound(buffer=sound_buffer)
            return sound
            
        except Exception as e:
            print(f"    Failed to create beep: {e}")
            return None
    
    def create_tone_sequence(self, frequencies, durations):
        """Create a sequence of tones"""
        try:
            sample_rate = 22050
            all_samples = []
            
            for freq, duration_ms in zip(frequencies, durations):
                frames = duration_ms * sample_rate // 1000
                volume = int(self.sfx_volume * 8192)  # Slightly quieter for sequences
                
                for i in range(frames):
                    angle = 2.0 * math.pi * freq * i / sample_rate
                    sample = int(volume * math.sin(angle))
                    
                    # Apply envelope
                    envelope = 1.0
                    if i < frames * 0.1:  # Fade in
                        envelope = i / (frames * 0.1)
                    elif i > frames * 0.8:  # Fade out
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
            print(f"    Failed to create tone sequence: {e}")
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
                # Random noise with decay
                noise = random.randint(-volume, volume)
                
                # Apply exponential decay
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
            print(f"    Failed to create noise burst: {e}")
            return None
    
    def start_menu_music(self):
        """Start menu music - create a simple looping melody"""
        try:
            print("WorkingSoundManager: Starting menu music...")
            # Create a simple melody that loops
            menu_melody = self.create_menu_melody()
            if menu_melody:
                # Play the melody on loop
                menu_melody.play(loops=-1)  # Loop forever
                print("  ✓ Menu music started")
            else:
                print("  ✗ Failed to create menu melody")
        except Exception as e:
            print(f"  ✗ Failed to start menu music: {e}")
    
    def create_menu_melody(self):
        """Create a simple looping menu melody"""
        try:
            # Simple chord progression: C-Am-F-G
            notes = [
                (523, 500),  # C
                (440, 500),  # A
                (349, 500),  # F
                (392, 500),  # G
                (523, 1000), # C (longer)
            ]
            
            sample_rate = 22050
            all_samples = []
            
            for freq, duration_ms in notes:
                frames = duration_ms * sample_rate // 1000
                volume = int(self.music_volume * 4096)  # Quieter for background music
                
                for i in range(frames):
                    angle = 2.0 * math.pi * freq * i / sample_rate
                    # Add some harmonics for richer sound
                    sample = int(volume * (
                        0.6 * math.sin(angle) +           # Fundamental
                        0.3 * math.sin(angle * 2) +       # Octave
                        0.1 * math.sin(angle * 3)         # Fifth
                    ))
                    
                    # Apply envelope
                    envelope = 1.0
                    if i < frames * 0.05:  # Quick fade in
                        envelope = i / (frames * 0.05)
                    elif i > frames * 0.9:  # Fade out
                        envelope = (frames - i) / (frames * 0.1)
                    
                    sample = int(sample * envelope)
                    all_samples.extend([sample, sample])
                
                # Add brief silence between notes
                silence_frames = sample_rate // 20  # 50ms silence
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
            print(f"    Failed to create menu melody: {e}")
            return None
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
                print(f"♪ Played: {sound_name}")
            except pygame.error as e:
                print(f"Failed to play {sound_name}: {e}")
        else:
            print(f"Sound {sound_name} not available")
    
    def play_music(self, music_name):
        """Play background music (simplified)"""
        print(f"♫ Would play music: {music_name}")
        # For now, menu music auto-starts and continues
        # You could implement different music tracks here
    
    def stop_music(self):
        """Stop all music"""
        pygame.mixer.stop()
        print("Music stopped")
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        print(f"SFX volume set to {self.sfx_volume}")
    
    def set_music_volume(self, volume):
        """Set music volume"""
        self.music_volume = max(0.0, min(1.0, volume))
        print(f"Music volume set to {self.music_volume}")


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
            'menu_select', 'teleport', 'heal'
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


class GameStateManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_state = GameState.MENU
        self.states = {}
        
        # Initialize sound manager - prioritize file loading first
        print("=== INITIALIZING SOUND SYSTEM ===")
        try:
            print("Attempting to load sound files first...")
            self.sound_manager = FileSoundManager()
            print("✓ FileSoundManager initialized successfully")
        except Exception as e:
            print(f"FileSoundManager failed: {e}")
            try:
                print("Falling back to procedural sounds...")
                self.sound_manager = WorkingSoundManager()
                print("✓ Fallback to WorkingSoundManager")
            except Exception as e2:
                print(f"WorkingSoundManager failed: {e2}")
                try:
                    print("Falling back to placeholder sounds...")
                    self.sound_manager = UltraSimpleSoundManager()
                    print("✓ Fallback to UltraSimpleSoundManager")
                except Exception as e3:
                    print(f"All sound managers failed: {e3}")
                    self.sound_manager = None
        
        # Initialize player (persistent across states)
        self.player = Player(400, 300, 0)
        
        # Initialize all game states
        self.states[GameState.MENU] = MenuState(screen, self)
        self.states[GameState.TOWN] = TownState(screen, self, self.player)
        self.states[GameState.ARENA] = ArenaState(screen, self, self.player)
        self.states[GameState.SHOP] = ShopState(screen, self, self.player)
        
        # Set sound manager for each state
        for state in self.states.values():
            if hasattr(state, 'sound_manager'):
                state.sound_manager = self.sound_manager
                print(f"Set sound manager for {type(state).__name__}")
        
        print("=== SOUND SYSTEM SETUP COMPLETE ===")
        
        # Mouse capture settings
        self.mouse_captured = False
        
        # Track arena wave progression
        self.came_from_arena_shop = False
        
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
        
        # Start appropriate background music
        if hasattr(self.sound_manager, 'play_music'):
            if new_state == GameState.MENU:
                self.sound_manager.play_music('menu')
            elif new_state == GameState.TOWN:
                self.sound_manager.play_music('town') 
            elif new_state == GameState.ARENA:
                self.sound_manager.play_music('arena')
            elif new_state == GameState.SHOP:
                self.sound_manager.play_music('shop')
        
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