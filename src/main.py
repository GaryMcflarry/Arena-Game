import pygame
import sys
from game_state_manager import GameStateManager
from constants import FPS, SCREEN_HEIGHT, SCREEN_WIDTH

def main():
    # Initialize pygame and create window
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Arena of Shadows")
    clock = pygame.time.Clock()
    
    game_manager = GameStateManager(screen)
    
    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game_manager.handle_event(event)
        
        # Update game state
        game_manager.update(dt)
        
        # Render current state
        game_manager.render()
        
        # Update display
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()