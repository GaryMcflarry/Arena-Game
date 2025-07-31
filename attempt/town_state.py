import pygame
import math
from constants import *
from raycaster import RayCaster
from town_map import TownMap

class NPC:
    """Simple NPC that wanders around town"""
    def __init__(self, x, y, name, color=BLUE, dialogue=None):
        self.x = x
        self.y = y
        self.name = name
        self.color = color
        self.size = 12
        self.speed = 15
        
        # Dialogue system
        self.dialogue = dialogue or [f"Greetings, traveler! I am {name}."]
        self.has_talked = False
        self.is_being_talked_to = False  # New: Track if player is talking to this NPC
        
        # Dialogue choices for interactive conversations
        self.dialogue_choices = {
            "greet": ["Hello there!", "Nice to meet you.", "Good day!"],
            "ask_about": ["Tell me about yourself.", "What do you do here?", "Any interesting stories?"],
            "ask_town": ["What's happening in town?", "Any news?", "Tell me about this place."],
            "goodbye": ["I must be going.", "Farewell!", "See you around."]
        }
        
        # Wandering behavior
        self.target_x = x
        self.target_y = y
        self.wander_radius = 80
        self.home_x = x
        self.home_y = y
        self.target_reached_time = 0
        self.wait_time = 3000  # Wait 3 seconds before moving to new target
        
    def update(self, dt, current_time):
        """Update NPC movement"""
        # Don't move if being talked to
        if self.is_being_talked_to:
            return
            
        # Check if we've reached our target
        distance_to_target = math.sqrt((self.x - self.target_x)**2 + (self.y - self.target_y)**2)
        
        if distance_to_target < 20:  # Close enough to target
            if current_time - self.target_reached_time > self.wait_time:
                self.set_new_target()
                self.target_reached_time = current_time
        else:
            # Move toward target
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            if distance_to_target > 0:
                dx /= distance_to_target
                dy /= distance_to_target
                
                self.x += dx * self.speed * dt
                self.y += dy * self.speed * dt
                
    def set_new_target(self):
        """Set a new random target within wander radius"""
        import random
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(30, self.wander_radius)
        
        self.target_x = self.home_x + math.cos(angle) * distance
        self.target_y = self.home_y + math.sin(angle) * distance
        
        # Keep within town bounds (20x20 map = 1280x1280 world coordinates)
        self.target_x = max(100, min(1180, self.target_x))  # Stay within map
        self.target_y = max(100, min(1180, self.target_y))  # Stay within map

class TownState:
    def __init__(self, screen, game_manager, player):
        self.screen = screen
        self.game_manager = game_manager
        self.player = player
        
        # Initialize town map
        self.town_map = TownMap()
        self.raycaster = RayCaster(screen)
        
        # Interaction system
        self.interaction_range = 80
        self.show_interaction_prompt = False
        self.current_interaction = None
        self.current_npc = None  # Fixed: Initialize this variable
        
        # Dialogue system - Enhanced for choices
        self.show_dialogue = False
        self.dialogue_text = ""
        self.dialogue_timer = 0
        self.dialogue_duration = 5000  # Show dialogue for 5 seconds
        self.show_dialogue_choices = False
        self.dialogue_choices = []
        self.selected_choice = 0
        
        # Initialize 10 walking NPCs spread across town (using tile coordinates * TILE_SIZE)
        self.npcs = [
            NPC(2 * TILE_SIZE, 4 * TILE_SIZE, "Gareth the Merchant", GREEN, [
                "Ah, a fellow trader! I deal in only the finest goods.",
                "These silk scarves came all the way from the eastern kingdoms!",
                "Business has been good - the townsfolk appreciate quality.",
                "Have you seen the prices at the weapon shop? Outrageous!",
                "I've got connections in every major city, you know."
            ]),
            NPC(16 * TILE_SIZE, 3 * TILE_SIZE, "Sister Evangeline", WHITE, [
                "May the light bless your journey, child.",
                "I tend to the sick and weary at the temple.",
                "Prayer and meditation bring peace to troubled souls.",
                "The healer's shop works wonders, but faith works miracles.",
                "Have you come seeking spiritual guidance, traveler?"
            ]),
            NPC(10 * TILE_SIZE, 8 * TILE_SIZE, "Captain Aldric", BROWN, [
                "Hold there, citizen! State your business in our town.",
                "The streets are safe under my watch, I assure you.",
                "That arena sees some fierce battles - are you warrior material?",
                "I've served this town for twenty years without incident.",
                "Keep your weapons sheathed while in town, understand?"
            ]),
            NPC(4 * TILE_SIZE, 14 * TILE_SIZE, "Elara the Seamstress", PURPLE, [
                "Your clothes look travel-worn, dear. Need repairs?",
                "I can mend tears and patch holes better than anyone!",
                "This fabric is imported - feel how soft it is!",
                "Fashion may change, but quality stitching is eternal.",
                "The merchant Gareth brings me the finest materials."
            ]),
            NPC(17 * TILE_SIZE, 10 * TILE_SIZE, "Finn the Blacksmith's Apprentice", (255, 165, 0), [  # Orange
                "Master says I'm getting better with the hammer!",
                "Someday I'll forge weapons as fine as his.",
                "These calluses on my hands are badges of honor!",
                "The forge fire burns hottest just before dawn.",
                "Want to see the sword I'm working on? It's almost finished!"
            ]),
            NPC(7 * TILE_SIZE, 15 * TILE_SIZE, "Old Willem the Storyteller", GRAY, [
                "Gather 'round, I've tales that'll curl your toes!",
                "Did I ever tell you about the dragon of Thornwood Keep?",
                "In my day, adventurers were made of sterner stuff...",
                "Every scar has a story, every story has a lesson.",
                "The young ones don't appreciate a good tale anymore."
            ]),
            NPC(14 * TILE_SIZE, 7 * TILE_SIZE, "Meredith the Herbalist", (0, 100, 0), [  # Dark Green
                "These healing herbs grow wild in the forest nearby.",
                "Mix three parts willowbark with one part moonbell for headaches.",
                "Potions are alchemy, but herbs are nature's own magic.",
                "The healer buys my finest remedies for his shop.",
                "Careful with that mushroom - it's more dangerous than it looks!"
            ]),
            NPC(3 * TILE_SIZE, 9 * TILE_SIZE, "Sir Roderick the Retired Knight", (192, 192, 192), [  # Silver
                "These old bones have seen their share of battles.",
                "I was arena champion for seven consecutive years!",
                "Honor and valor - that's what knighthood truly means.",
                "Young fighters today rely too much on magic, not skill.",
                "My sword arm may be slower, but my wisdom is sharper than ever."
            ]),
            NPC(12 * TILE_SIZE, 2 * TILE_SIZE, "Tobias the Town Crier", YELLOW, [
                "Hear ye, hear ye! Fresh news from the capital!",
                "The harvest festival is but a fortnight away!",
                "Royal decree: all citizens must register their magical items!",
                "Breaking news: dragon sighted three leagues to the north!",
                "Town meeting tonight at the square - attendance mandatory!"
            ]),
            NPC(8 * TILE_SIZE, 12 * TILE_SIZE, "Little Margot the Flower Girl", (173, 216, 230), [  # Light Blue
                "Pretty flowers bring good luck to brave adventurers!",
                "These daisies were picked fresh this morning!",
                "Mama says flowers make everything more beautiful.",
                "The roses are for lovers, but the lilies are for warriors!",
                "Would you like a flower crown? Only two copper pieces!"
            ])
        ]
        
        self.font = pygame.font.Font(None, 24)
        self.dialogue_font = pygame.font.Font(None, 20)
        
    def initialize_town(self):
        """Initialize/reset town state"""
        # Place player at town entrance (bottom center opening)
        self.player.x = 9 * TILE_SIZE + TILE_SIZE // 2  # Center of opening
        self.player.y = 18 * TILE_SIZE + TILE_SIZE // 2  # Just inside the opening
        self.player.angle = math.pi / 2  # Facing north
        
        # Reset dialogue state
        self.show_dialogue = False
        self.show_dialogue_choices = False
        self.dialogue_text = ""
        self.dialogue_timer = 0
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                if self.show_dialogue_choices:
                    # Handle dialogue choice selection
                    self.handle_dialogue_choice()
                elif self.current_interaction:
                    self.interact_with_building()
                elif self.current_npc:
                    self.start_dialogue_with_npc()
            elif event.key == pygame.K_1 and self.show_dialogue_choices:
                self.selected_choice = 0
                self.handle_dialogue_choice()
            elif event.key == pygame.K_2 and self.show_dialogue_choices:
                self.selected_choice = 1
                self.handle_dialogue_choice()
            elif event.key == pygame.K_3 and self.show_dialogue_choices:
                self.selected_choice = 2
                self.handle_dialogue_choice()
            elif event.key == pygame.K_UP and self.show_dialogue_choices:
                self.selected_choice = (self.selected_choice - 1) % len(self.dialogue_choices)
            elif event.key == pygame.K_DOWN and self.show_dialogue_choices:
                self.selected_choice = (self.selected_choice + 1) % len(self.dialogue_choices)
            elif event.key == pygame.K_ESCAPE and self.show_dialogue_choices:
                self.end_dialogue()
            elif event.key == pygame.K_m:
                pass  # Could toggle minimap
        elif event.type == pygame.MOUSEMOTION:
            self.player.handle_mouse_look(event.rel)
            
    def start_dialogue_with_npc(self):
        """Start dialogue choice menu with NPC"""
        if self.current_npc:
            self.show_dialogue_choices = True
            self.selected_choice = 0
            self.dialogue_timer = pygame.time.get_ticks()  # Reset timer when starting dialogue
            self.current_npc.is_being_talked_to = True
            
            # Create dialogue choices based on NPC type
            npc_name = self.current_npc.name.lower()
            if "merchant" in npc_name or "gareth" in npc_name:
                self.dialogue_choices = [
                    "What goods do you have for sale?",
                    "Tell me about your trade routes.",
                    "Any rare items available?"
                ]
            elif "sister" in npc_name or "evangeline" in npc_name:
                self.dialogue_choices = [
                    "I seek spiritual guidance.",
                    "Can you bless my journey?",
                    "Tell me about the temple."
                ]
            elif "captain" in npc_name or "aldric" in npc_name:
                self.dialogue_choices = [
                    "Is the town safe?",
                    "Tell me about the arena.",
                    "Any threats I should know about?"
                ]
            elif "seamstress" in npc_name or "elara" in npc_name:
                self.dialogue_choices = [
                    "Can you repair my equipment?",
                    "What fabrics do you work with?",
                    "Any fashion advice?"
                ]
            elif "apprentice" in npc_name or "finn" in npc_name:
                self.dialogue_choices = [
                    "How's your training going?",
                    "Can you show me your work?",
                    "What's it like being an apprentice?"
                ]
            elif "storyteller" in npc_name or "willem" in npc_name:
                self.dialogue_choices = [
                    "Tell me a story!",
                    "What adventures have you heard about?",
                    "Any local legends?"
                ]
            elif "herbalist" in npc_name or "meredith" in npc_name:
                self.dialogue_choices = [
                    "What herbs do you recommend?",
                    "Can you teach me about potions?",
                    "Where do you find your ingredients?"
                ]
            elif "knight" in npc_name or "roderick" in npc_name:
                self.dialogue_choices = [
                    "Tell me about your battles.",
                    "Any advice for a warrior?",
                    "What was the arena like in your day?"
                ]
            elif "crier" in npc_name or "tobias" in npc_name:
                self.dialogue_choices = [
                    "What's the latest news?",
                    "Any important announcements?",
                    "Tell me about upcoming events."
                ]
            elif "flower" in npc_name or "margot" in npc_name:
                self.dialogue_choices = [
                    "Your flowers are beautiful!",
                    "Do they really bring luck?",
                    "Can I buy some flowers?"
                ]
            else:
                # Default choices
                self.dialogue_choices = [
                    "Hello there!",
                    "Tell me about yourself.",
                    "What's happening around here?"
                ]
    
    def handle_dialogue_choice(self):
        """Handle player's dialogue choice selection"""
        if not self.show_dialogue_choices or not self.current_npc:
            return
            
        if 0 <= self.selected_choice < len(self.dialogue_choices):
            # Get the chosen question
            chosen_question = self.dialogue_choices[self.selected_choice]
            
            # Generate NPC response based on choice and NPC type
            response = self.get_npc_response(self.current_npc, self.selected_choice)
            
            # Show the dialogue
            self.dialogue_text = f"You: {chosen_question}\n\n{self.current_npc.name}: {response}"
            self.show_dialogue = True
            self.show_dialogue_choices = False
            self.dialogue_timer = pygame.time.get_ticks()
            self.current_npc.has_talked = True
    
    def get_npc_response(self, npc, choice_index):
        """Get NPC response based on dialogue choice"""
        npc_name = npc.name.lower()
        
        if "gareth" in npc_name:  # Merchant responses
            responses = [
                "I have silk, spices, and fine jewelry from distant lands!",
                "My caravans travel the Great Trade Road - dangerous but profitable!",
                "Ah yes, I have a magical compass that never lies. Interested?"
            ]
        elif "evangeline" in npc_name:  # Sister responses
            responses = [
                "Find peace within yourself, and the path will become clear.",
                "May your steps be light and your heart be pure, traveler.",
                "Our temple has stood for centuries, a beacon of hope and healing."
            ]
        elif "aldric" in npc_name:  # Captain responses
            responses = [
                "Aye, I keep the peace here. No bandits dare trouble this town!",
                "The arena tests true warriors. Many enter, fewer leave victorious.",
                "Watch for wolves on the northern road, and goblins in the caves."
            ]
        elif "elara" in npc_name:  # Seamstress responses
            responses = [
                "Of course! I can mend tears and reinforce weak spots for a fair price.",
                "I work with everything from common wool to enchanted silks!",
                "Darker colors hide stains better - practical for adventurers like you."
            ]
        elif "finn" in npc_name:  # Apprentice responses
            responses = [
                "Master says I'm improving! Yesterday I made a horseshoe without help!",
                "Look at this blade - still needs tempering, but the edge is true!",
                "It's hard work, but someday I'll be the finest smith in the land!"
            ]
        elif "willem" in npc_name:  # Storyteller responses
            responses = [
                "Long ago, a great dragon slept beneath these very hills...",
                "I heard tell of a lost treasure in the Whispering Woods nearby.",
                "They say this town was built on an ancient battlefield..."
            ]
        elif "meredith" in npc_name:  # Herbalist responses
            responses = [
                "Red moss for strength, blue sage for wisdom, white willow for pain.",
                "The secret is in the preparation - timing and temperature matter!",
                "I forage at dawn when the dew holds the plants' full potency."
            ]
        elif "roderick" in npc_name:  # Knight responses
            responses = [
                "I once faced three ogres single-handed and lived to tell the tale!",
                "Keep your guard up, strike true, and never fight angry.",
                "The arena was more honorable then - real skill, not just flashy magic."
            ]
        elif "tobias" in npc_name:  # Town Crier responses
            responses = [
                "A merchant caravan was attacked on the east road this morning!",
                "The harvest festival begins at sunset - there'll be dancing and contests!",
                "Strange lights were seen over the old ruins last night..."
            ]
        elif "margot" in npc_name:  # Flower Girl responses
            responses = [
                "Thank you! Mama taught me to pick only the prettiest ones!",
                "Oh yes! Papa says flowers carry the forest's magic with them!",
                "Two copper for a daisy, five for a lucky four-leaf clover!"
            ]
        else:
            responses = npc.dialogue  # Fallback to original dialogue
            
        return responses[choice_index % len(responses)]
    
    def end_dialogue(self):
        """End current dialogue and reset state"""
        self.show_dialogue = False
        self.show_dialogue_choices = False
        self.dialogue_text = ""
        if self.current_npc:
            self.current_npc.is_being_talked_to = False
            
    def interact_with_building(self):
        """Handle interaction with buildings"""
        try:
            if self.current_interaction == "weapon_shop":
                # Import GameState to use proper enum values
                from constants import GameState
                self.game_manager.change_state(GameState.SHOP, "weapon")
            elif self.current_interaction == "magic_shop":
                from constants import GameState
                self.game_manager.change_state(GameState.SHOP, "magic")
            elif self.current_interaction == "healer":
                from constants import GameState
                self.game_manager.change_state(GameState.SHOP, "healer")
            elif self.current_interaction == "arena":
                from constants import GameState
                self.game_manager.change_state(GameState.ARENA)
        except Exception as e:
            print(f"Error changing state: {e}")
            # Show message instead of crashing
            self.dialogue_text = f"The {self.current_interaction.replace('_', ' ')} is currently closed."
            self.show_dialogue = True
            self.dialogue_timer = pygame.time.get_ticks()
            
    def check_interactions(self):
        """Check for nearby interactive objects and NPCs"""
        self.show_interaction_prompt = False
        self.current_interaction = None
        
        # Reset all NPCs' talking state first
        for npc in self.npcs:
            npc.is_being_talked_to = False
        
        self.current_npc = None
        
        # Check for NPCs first
        for npc in self.npcs:
            distance = math.sqrt(
                (self.player.x - npc.x) ** 2 + 
                (self.player.y - npc.y) ** 2
            )
            
            if distance < self.interaction_range:
                self.show_interaction_prompt = True
                self.current_npc = npc
                # Stop NPC movement whenever player is near them
                npc.is_being_talked_to = True
                return  # Priority to NPCs over buildings
        
        # Check for buildings if no NPC nearby
        player_map_x = int(self.player.x // TILE_SIZE)
        player_map_y = int(self.player.y // TILE_SIZE)
        
        # Check for interactive tiles around player
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                check_x = player_map_x + dx
                check_y = player_map_y + dy
                
                if (0 <= check_x < self.town_map.width and 
                    0 <= check_y < self.town_map.height):
                    
                    tile_type = self.town_map.get_tile(check_x, check_y)
                    
                    # Calculate distance to tile center
                    tile_center_x = check_x * TILE_SIZE + TILE_SIZE // 2
                    tile_center_y = check_y * TILE_SIZE + TILE_SIZE // 2
                    
                    distance = math.sqrt(
                        (self.player.x - tile_center_x) ** 2 + 
                        (self.player.y - tile_center_y) ** 2
                    )
                    
                    if distance < self.interaction_range:
                        if tile_type == 3:  # Weapon shop
                            self.show_interaction_prompt = True
                            self.current_interaction = "weapon_shop"
                        elif tile_type == 4:  # Magic shop
                            self.show_interaction_prompt = True
                            self.current_interaction = "magic_shop"
                        elif tile_type == 5:  # Healer
                            self.show_interaction_prompt = True
                            self.current_interaction = "healer"
                        elif tile_type == 6:  # Arena entrance
                            self.show_interaction_prompt = True
                            self.current_interaction = "arena"
                            
    def update(self, dt):
        current_time = pygame.time.get_ticks()
        
        # Update player with proper collision detection
        keys = pygame.key.get_pressed()
        
        # Store old position for collision rollback
        old_x, old_y = self.player.x, self.player.y
        
        # Move player
        self.player.move(keys, dt, self.town_map.collision_map, 
                        self.town_map.width, self.town_map.height)
        
        # Check if player moved into a wall and rollback if necessary
        player_tile_x = int(self.player.x // TILE_SIZE)
        player_tile_y = int(self.player.y // TILE_SIZE)
        
        # Check collision with walls (tile type 1) and buildings (tile types 2-6)
        if (player_tile_x < 0 or player_tile_x >= self.town_map.width or
            player_tile_y < 0 or player_tile_y >= self.town_map.height or
            not self.town_map.is_walkable(player_tile_x, player_tile_y)):
            # Rollback movement
            self.player.x, self.player.y = old_x, old_y
        
        self.player.update(dt)
        
        # Update NPCs
        for npc in self.npcs:
            npc.update(dt, current_time)
        
        # Check for interactions
        self.check_interactions()
        
        # Update dialogue timer
        if self.show_dialogue:
            if current_time - self.dialogue_timer > self.dialogue_duration:
                self.end_dialogue()
        
        # Auto-hide dialogue choices after 10 seconds of inactivity
        if self.show_dialogue_choices:
            if current_time - self.dialogue_timer > 10000:
                self.end_dialogue()
        
    def render(self):
        self.screen.fill(BLACK)
        
        # Cast rays and render 3D view
        rays = self.raycaster.cast_rays(self.player, self.town_map.collision_map,
                                       self.town_map.width, self.town_map.height)
        self.raycaster.render_3d_town(rays, self.player)
        
        # Render NPCs in 3D space
        self.render_npcs()
        
        # Draw UI
        self.draw_ui()
        
    def render_npcs(self):
        """Render NPCs in 3D space"""
        view_bob = int(self.player.z * 0.3)
        
        for npc in self.npcs:
            dx = npc.x - self.player.x
            dy = npc.y - self.player.y
            npc_distance = math.sqrt(dx * dx + dy * dy)
            
            if npc_distance < 0.1:
                continue
                
            npc_angle = math.atan2(dy, dx)
            angle_diff = npc_angle - self.player.angle
            
            # Normalize angle difference
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
                
            # Check if NPC is in FOV
            if abs(angle_diff) < HALF_FOV:
                screen_x = (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2) + (SCREEN_WIDTH // 2)
                
                npc_size = npc.size * 800 / (npc_distance + 0.1)
                npc_height = npc_size * 1.5  # NPCs are taller than wide
                
                # Draw NPC with jump bob effect
                npc_rect = (
                    screen_x - npc_size // 2,
                    (SCREEN_HEIGHT - npc_height) // 2 + view_bob,
                    npc_size,
                    npc_height
                )
                pygame.draw.rect(self.screen, npc.color, npc_rect)
                
                # Draw simple face
                if npc_size > 10:
                    # Eyes
                    eye_size = max(1, int(npc_size // 8))
                    left_eye_x = int(screen_x - npc_size // 4)
                    right_eye_x = int(screen_x + npc_size // 4)
                    eye_y = int((SCREEN_HEIGHT - npc_height) // 2 + npc_height // 3 + view_bob)
                    
                    pygame.draw.circle(self.screen, WHITE, (left_eye_x, eye_y), eye_size)
                    pygame.draw.circle(self.screen, WHITE, (right_eye_x, eye_y), eye_size)
                
                # Draw name above NPC if close enough
                if npc_distance < 150 and npc_size > 15:
                    name_font = pygame.font.Font(None, max(12, int(npc_size // 3)))
                    name_text = name_font.render(npc.name, True, WHITE)
                    name_rect = name_text.get_rect(center=(screen_x, npc_rect[1] - 15))
                    
                    # Draw background for name
                    bg_rect = name_rect.inflate(4, 2)
                    pygame.draw.rect(self.screen, BLACK, bg_rect)
                    pygame.draw.rect(self.screen, WHITE, bg_rect, 1)
                    
                    self.screen.blit(name_text, name_rect)
        
    def draw_ui(self):
        # Draw player stats
        stats_y = 10
        stats = [
            f"Gold: {self.player.gold}",
            f"Health: {int(self.player.health)}/{self.player.get_max_health()}",
            f"Mana: {int(self.player.mana)}/{self.player.get_max_mana()}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.font.render(stat, True, WHITE)
            self.screen.blit(stat_text, (10, stats_y + i * 25))
            
        # Draw interaction prompt
        if self.show_interaction_prompt and not self.show_dialogue_choices:
            if self.current_npc:
                prompt_text = f"Press E to talk to {self.current_npc.name.split()[0]}"
                prompt_color = self.current_npc.color
            else:
                interaction_names = {
                    "weapon_shop": "Weapon Shop",
                    "magic_shop": "Magic Shop", 
                    "healer": "Healer",
                    "arena": "Arena Entrance"
                }
                prompt_text = f"Press E to enter {interaction_names.get(self.current_interaction, 'building')}"
                prompt_color = YELLOW
            
            text_surface = self.font.render(prompt_text, True, prompt_color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            
            # Draw background for better visibility
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            pygame.draw.rect(self.screen, prompt_color, bg_rect, 2)
            
            self.screen.blit(text_surface, text_rect)
        
        # Draw dialogue choices menu
        if self.show_dialogue_choices:
            self.draw_dialogue_choices()
            
        # Draw dialogue if active
        elif self.show_dialogue and self.dialogue_text:  # Fixed: Check if dialogue_text exists
            dialogue_y = SCREEN_HEIGHT - 120
            dialogue_rect = pygame.Rect(50, dialogue_y, SCREEN_WIDTH - 100, 60)
            
            # Draw dialogue background
            pygame.draw.rect(self.screen, BLACK, dialogue_rect)
            pygame.draw.rect(self.screen, WHITE, dialogue_rect, 2)
            
            # Draw dialogue text (word wrap)
            words = self.dialogue_text.split(' ')
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                text_width = self.dialogue_font.size(test_line)[0]
                
                if text_width < dialogue_rect.width - 20:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw lines
            for i, line in enumerate(lines[:2]):  # Max 2 lines
                line_y = dialogue_y + 15 + i * 20
                line_surface = self.dialogue_font.render(line, True, WHITE)
                self.screen.blit(line_surface, (dialogue_rect.x + 10, line_y))
            
        # Draw minimap with NPCs
        self.draw_minimap()
    
    def draw_dialogue_choices(self):
        """Draw the dialogue choice menu"""
        if not self.current_npc:
            return
            
        # Menu dimensions
        menu_width = SCREEN_WIDTH - 100
        menu_height = 200
        menu_x = 50
        menu_y = SCREEN_HEIGHT - menu_height - 20
        
        # Draw menu background
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(self.screen, BLACK, menu_rect)
        pygame.draw.rect(self.screen, self.current_npc.color, menu_rect, 3)
        
        # Draw NPC name header
        header_text = f"Talking to {self.current_npc.name}"
        header_surface = self.font.render(header_text, True, WHITE)
        header_rect = header_surface.get_rect(center=(SCREEN_WIDTH // 2, menu_y + 20))
        self.screen.blit(header_surface, header_rect)
        
        # Draw choices
        choice_y_start = menu_y + 50
        choice_spacing = 35
        
        for i, choice in enumerate(self.dialogue_choices):
            choice_y = choice_y_start + i * choice_spacing
            
            # Highlight selected choice
            if i == self.selected_choice:
                choice_bg = pygame.Rect(menu_x + 10, choice_y - 5, menu_width - 20, 25)
                pygame.draw.rect(self.screen, self.current_npc.color, choice_bg)
                choice_color = BLACK
            else:
                choice_color = WHITE
                
            # Draw choice number and text
            choice_text = f"{i + 1}. {choice}"
            choice_surface = self.dialogue_font.render(choice_text, True, choice_color)
            self.screen.blit(choice_surface, (menu_x + 15, choice_y))
        
        # Draw instructions
        instruction_text = "Use 1-3 or Arrow Keys, then E to select • ESC to cancel"
        instruction_surface = pygame.font.Font(None, 18).render(instruction_text, True, GRAY)
        instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, menu_y + menu_height - 15))
        self.screen.blit(instruction_surface, instruction_rect)
        
    def draw_minimap(self):
        """Draw a minimap with NPCs"""
        map_scale = 6
        map_size = 120
        map_x = SCREEN_WIDTH - map_size - 10
        map_y = 10
        
        # Draw map background
        pygame.draw.rect(self.screen, DARK_GRAY, (map_x, map_y, map_size, map_size))
        pygame.draw.rect(self.screen, WHITE, (map_x, map_y, map_size, map_size), 2)
        
        # Draw map tiles
        for y in range(min(20, self.town_map.height)):
            for x in range(min(20, self.town_map.width)):
                if x < self.town_map.width and y < self.town_map.height:
                    tile_type = self.town_map.get_tile(x, y)
                    
                    if tile_type != 0:  # Not empty space
                        color = WHITE
                        if tile_type == 1:  # Wall
                            color = BROWN
                        elif tile_type == 2:  # House
                            color = GRAY
                        elif tile_type in [3, 4, 5]:  # Shops
                            color = BLUE
                        elif tile_type == 6:  # Arena
                            color = RED
                            
                        tile_x = map_x + x * map_scale
                        tile_y = map_y + y * map_scale
                        pygame.draw.rect(self.screen, color, 
                                       (tile_x, tile_y, map_scale, map_scale))
                    
        # Draw NPCs on minimap
        for npc in self.npcs:
            npc_map_x = int(map_x + (npc.x / TILE_SIZE) * map_scale)
            npc_map_y = int(map_y + (npc.y / TILE_SIZE) * map_scale)
            
            if (map_x <= npc_map_x <= map_x + map_size and 
                map_y <= npc_map_y <= map_y + map_size):
                pygame.draw.circle(self.screen, npc.color, (npc_map_x, npc_map_y), 2)
                    
        # Draw player position
        player_map_x = int(self.player.x // TILE_SIZE)
        player_map_y = int(self.player.y // TILE_SIZE)
        
        if (0 <= player_map_x < 20 and 0 <= player_map_y < 20):
            player_x = map_x + player_map_x * map_scale
            player_y = map_y + player_map_y * map_scale
            
            pygame.draw.circle(self.screen, YELLOW, (player_x, player_y), 3)
            
            # Draw player direction
            end_x = player_x + int(math.cos(self.player.angle) * 8)
            end_y = player_y + int(math.sin(self.player.angle) * 8)
            pygame.draw.line(self.screen, YELLOW, (player_x, player_y), (end_x, end_y), 2)