import pygame
from constants import GameState
from player import Player
from town_state import TownState
from arena_state import ArenaState
from shop_state import ShopState
from menu_state import MenuState

class GameStateManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_state = GameState.MENU
        self.states = {}
        
        # Initialize player (persistent across states)
        self.player = Player(400, 300, 0)  # Start in town center
        
        # Initialize all game states
        self.states[GameState.MENU] = MenuState(screen, self)
        self.states[GameState.TOWN] = TownState(screen, self, self.player)
        self.states[GameState.ARENA] = ArenaState(screen, self, self.player)
        self.states[GameState.SHOP] = ShopState(screen, self, self.player)
        
        # Mouse capture settings
        self.mouse_captured = False
        
    def change_state(self, new_state, shop_type=None):
        """Change the current game state"""
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
            self.states[GameState.ARENA].initialize_arena()
        elif new_state == GameState.TOWN:
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
        # Global escape key to return to menu
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.current_state != GameState.MENU:
                self.change_state(GameState.MENU)
                return
                
        # Let current state handle the event
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
        
    def quit_game(self):
        """Quit the game"""
        pygame.quit()
        exit()