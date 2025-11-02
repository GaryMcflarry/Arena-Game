import pygame

from constants import GameState, ShopType
from constants import *

class ShopState:
    def __init__(self, screen, game_manager, player):
        self.screen = screen
        self.game_manager = game_manager
        self.player = player
        
        self.sound_manager = None
        
        self.shop_type = None
        self.selected_item = 0
        self.items = []
        
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 48)
        self.info_font = pygame.font.Font(None, 24)
        
        self.weapon_items = [
        ]
        
        self.magic_items = [
            {"name": "Apprentice Robes", "level": 2, "cost": 400, "description": "Increases mana and spell power"},
            {"name": "Journeyman Robes", "level": 3, "cost": 800, "description": "Further increases magical abilities"},
            {"name": "Expert Robes", "level": 4, "cost": 1300, "description": "High-level magical enhancement"},
            {"name": "Master Robes", "level": 5, "cost": 2000, "description": "Ultimate magical power"},
        ]
        
        self.spell_items = [
            {"name": "Lightning Bolt", "spell": "lightning", "cost": 200, "description": "Fast, low-cost electric attack"},
            {"name": "Ice Shard", "spell": "ice", "cost": 300, "description": "Powerful ice projectile"},
            {"name": "Healing Light", "spell": "heal", "cost": 500, "description": "Restore health with magic"},
        ]
        
        self.armor_items = [
            {"name": "Leather Armor", "level": 2, "cost": 350, "description": "Basic protection and health"},
            {"name": "Chain Mail", "level": 3, "cost": 700, "description": "Improved protection and health"},
            {"name": "Plate Armor", "level": 4, "cost": 1100, "description": "Heavy protection and health"},
            {"name": "Enchanted Armor", "level": 5, "cost": 1700, "description": "Maximum protection and health"},
        ]
        
        self.healing_items = [
            {"name": "Minor Healing Potion", "heal": 30, "cost": 50, "description": "Restores 30 health"},
            {"name": "Healing Potion", "heal": 60, "cost": 90, "description": "Restores 60 health"},
            {"name": "Greater Healing Potion", "heal": 100, "cost": 150, "description": "Restores 100 health"},
            {"name": "Minor Mana Potion", "mana": 40, "cost": 60, "description": "Restores 40 mana"},
            {"name": "Mana Potion", "mana": 80, "cost": 110, "description": "Restores 80 mana"},
            {"name": "Full Restore", "heal": 999, "mana": 999, "cost": 300, "description": "Fully restores health and mana"},
        ]
        
    def set_shop_type(self, shop_type):
        """Set the current shop type and update items"""
        self.shop_type = shop_type
        self.selected_item = 0
        
        if shop_type == ShopType.WEAPON:
            self.items = []
            for item in self.armor_items:
                if item["level"] == self.player.armor_level + 1:
                    self.items.append(item)
                    
        elif shop_type == ShopType.MAGIC:
            self.items = []
            for item in self.magic_items:
                if item["level"] == self.player.spell_level + 1:
                    self.items.append(item)
            
            for spell_item in self.spell_items:
                if spell_item["spell"] not in self.player.known_spells:
                    self.items.append(spell_item)
                    
        elif shop_type == ShopType.HEALER:
            self.items = self.healing_items.copy()
            
        self.items.append({"name": "Leave Shop", "cost": 0, "description": "Return to town"})
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.items)
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.items)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.purchase_item()
                
    def purchase_item(self):
        """Handle item purchase"""
        if not self.items:
            return
            
        item = self.items[self.selected_item]
        
        if item["name"] == "Leave Shop":
            self.game_manager.change_state(GameState.TOWN)
            return
            
        if not self.player.spend_gold(item["cost"]):
            return  
            
        if self.sound_manager:
            self.sound_manager.play_sound('shop_buy')
        
        if "level" in item:
            if "Sword" in item["name"]:
                self.player.weapon_level = item["level"]
            elif "Robes" in item["name"]:
                self.player.spell_level = item["level"]
                self.player.mana = self.player.get_max_mana()
            elif "Armor" in item["name"]:
                self.player.armor_level = item["level"]
                self.player.health = self.player.get_max_health()
                
        elif "spell" in item:
            self.player.learn_spell(item["spell"])
            
        elif "heal" in item:
            self.player.heal(item["heal"])
            
        elif "mana" in item:
            self.player.restore_mana(item["mana"])
            
        if self.shop_type != ShopType.HEALER:
            self.set_shop_type(self.shop_type)
            
    def update(self, dt):
        pass 
        
    def render(self):
        self.screen.fill(BLACK)
        
        shop_names = {
            ShopType.WEAPON: "Blacksmith - Weapons & Armor",
            ShopType.MAGIC: "Mystic Arts - Magical Equipment & Spells", 
            ShopType.HEALER: "Temple of Healing - Potions & Services"
        }
        
        title_text = self.title_font.render(shop_names.get(self.shop_type, "Shop"), True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        gold_text = self.font.render(f"Gold: {self.player.gold}", True, YELLOW)
        self.screen.blit(gold_text, (50, 100))
        
        stats_y = 130
        stats = []
        if self.shop_type == ShopType.WEAPON:
            stats = [
                f"Weapon Level: {self.player.weapon_level}/5",
                f"Armor Level: {self.player.armor_level}/5",
                f"Health: {int(self.player.health)}/{self.player.get_max_health()}"
            ]
        elif self.shop_type == ShopType.MAGIC:
            stats = [
                f"Magic Level: {self.player.spell_level}/5",
                f"Mana: {int(self.player.mana)}/{self.player.get_max_mana()}",
                f"Known Spells: {len(self.player.known_spells)}"
            ]
        elif self.shop_type == ShopType.HEALER:
            stats = [
                f"Health: {int(self.player.health)}/{self.player.get_max_health()}",
                f"Mana: {int(self.player.mana)}/{self.player.get_max_mana()}"
            ]
            
        for i, stat in enumerate(stats):
            stat_text = self.info_font.render(stat, True, WHITE)
            self.screen.blit(stat_text, (50, stats_y + i * 25))
        
        if self.shop_type == ShopType.MAGIC:
            spells_text = "Known: " + ", ".join([s.title() for s in self.player.known_spells])
            spells_surface = self.info_font.render(spells_text, True, LIGHT_BLUE)
            self.screen.blit(spells_surface, (50, stats_y + len(stats) * 25))
        
        if not self.items:
            no_items_text = self.font.render("No items available", True, GRAY)
            no_items_rect = no_items_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
            self.screen.blit(no_items_text, no_items_rect)
        else:
            start_y = 250
            for i, item in enumerate(self.items):
                color = YELLOW if i == self.selected_item else WHITE
                
                if item["cost"] > self.player.gold and item["name"] != "Leave Shop":
                    color = GRAY
                
                if "spell" in item:
                    if i == self.selected_item:
                        color = (255, 100, 255) 
                    else:
                        color = PURPLE
                
                item_text = f"{item['name']} - {item['cost']} gold"
                if item["name"] == "Leave Shop":
                    item_text = item["name"]
                    
                text_surface = self.font.render(item_text, True, color)
                self.screen.blit(text_surface, (100, start_y + i * 40))
                
                desc_text = self.info_font.render(item["description"], True, GRAY)
                self.screen.blit(desc_text, (120, start_y + i * 40 + 25))
                
        controls = [
            "UP/DOWN: Navigate",
            "ENTER/SPACE: Purchase",
        ]
        
        controls_y = SCREEN_HEIGHT - 100
        for i, control in enumerate(controls):
            control_text = self.info_font.render(control, True, GRAY)
            self.screen.blit(control_text, (50, controls_y + i * 20))
            
        if self.items and self.selected_item < len(self.items):
            item = self.items[self.selected_item]
            if ("level" in item or "spell" in item) and item["name"] != "Leave Shop":
                benefits_x = SCREEN_WIDTH - 350
                benefits_y = 200
                
                benefit_text = "Item Benefits:"
                benefit_surface = self.font.render(benefit_text, True, GOLD)
                self.screen.blit(benefit_surface, (benefits_x, benefits_y))
                
                benefits = []
                if "level" in item:
                    if "Sword" in item["name"]:
                        current_dmg = self.player.get_weapon_damage()
                        new_dmg = 30 + (item["level"] - 1) * 15
                        benefits.append(f"Damage: {current_dmg} + {new_dmg}")
                    elif "Robes" in item["name"]:
                        current_mult = self.player.get_spell_damage_multiplier()
                        new_mult = 1.0 + (item["level"] - 1) * 0.25
                        benefits.append(f"Spell Power: x{current_mult:.2f} + x{new_mult:.2f}")
                        current_mana = self.player.get_max_mana()
                        new_mana = 100 + (item["level"] - 1) * 15
                        benefits.append(f"Max Mana: {current_mana} + {new_mana}")
                    elif "Armor" in item["name"]:
                        current_def = self.player.get_armor_defense()
                        new_def = (item["level"] - 1) * 0.1
                        benefits.append(f"Damage Reduction: {current_def:.0%} + {new_def:.0%}")
                        current_hp = self.player.get_max_health()
                        new_hp = 100 + (item["level"] - 1) * 20
                        benefits.append(f"Max Health: {current_hp} + {new_hp}")
                elif "spell" in item:
                    spell_name = item["spell"]
                    mana_cost = self.player.spell_costs.get(spell_name, 0)
                    benefits.append(f"Spell: {spell_name.title()}")
                    benefits.append(f"Mana Cost: {mana_cost}")
                    
                    spell_effects = {
                        "lightning": "Fast, low-cost attack",
                        "ice": "High damage ice projectile", 
                        "heal": "Restores health instantly",
                        "shield": "Temporary damage protection",
                        "teleport": "Instant movement ability"
                    }
                    effect = spell_effects.get(spell_name, "Unknown effect")
                    benefits.append(f"Effect: {effect}")
                
                for j, benefit in enumerate(benefits):
                    benefit_surface = self.info_font.render(benefit, True, WHITE)
                    self.screen.blit(benefit_surface, (benefits_x, benefits_y + 30 + j * 20))