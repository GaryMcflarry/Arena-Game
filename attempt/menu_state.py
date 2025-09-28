import pygame
from constants import GameState
from constants import *

class MenuState:
    def __init__(self, screen, game_manager):
        self.screen = screen
        self.game_manager = game_manager
        
        # Menu options
        self.menu_options = [
            ("Enter Town", GameState.TOWN),
            ("Enter Arena", GameState.ARENA),
            ("Quit Game", "quit")
        ]
        
        self.selected_option = 0
        self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 72)
        self.info_font = pygame.font.Font(None, 24)
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.select_option()
                
    def select_option(self):
        option_text, option_action = self.menu_options[self.selected_option]
        
        if option_action == "quit":
            self.game_manager.quit_game()
        else:
            self.game_manager.change_state(option_action)
            
    def update(self, dt):
        pass  # No updates needed for menu
        
    def render(self):
        self.screen.fill(BLACK)
        
        # Draw title
        title_text = self.title_font.render("ARENA OF SHADOWS", True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.info_font.render("An Elder Scrolls Inspired Adventure", True, SILVER)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 190))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw menu options
        start_y = 280
        for i, (option_text, _) in enumerate(self.menu_options):
            color = YELLOW if i == self.selected_option else WHITE
            option_surface = self.font.render(option_text, True, color)
            option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 60))
            self.screen.blit(option_surface, option_rect)
            
        # Draw player stats
        player = self.game_manager.player
        stats_y = 450
        stats = [
            f"Gold: {player.gold}",
            f"Weapon Level: {player.weapon_level}",
            f"Armor Level: {player.armor_level}",
            f"Magic Level: {player.spell_level}",
            f"Highest Wave: {player.highest_wave}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.info_font.render(stat, True, WHITE)
            self.screen.blit(stat_text, (50, stats_y + i * 25))
            
        # Draw controls
        controls = [
            "UP/DOWN: Navigate Menu",
            "ENTER/SPACE: Select",
        ]
        
        for i, control in enumerate(controls):
            control_text = self.info_font.render(control, True, GRAY)
            control_rect = control_text.get_rect(right=SCREEN_WIDTH - 50)
            self.screen.blit(control_text, (control_rect.x, stats_y + i * 25))