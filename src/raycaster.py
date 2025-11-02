import pygame
import math
from typing import List, Tuple
from constants import *

class RayCaster:
    def __init__(self, screen):
        self.screen = screen
        
        self.textures = {}
        self.load_textures()

    def load_textures(self):
        """Load all texture assets"""
        import os
        
        print("=== TEXTURE LOADING DEBUG ===")
        print(f"Current working directory: {os.getcwd()}")
        
        arena_textures = {
            'arena_wall': "../assets/textures/arena/arena_wall.jpg",
            'arena_pillar': "../assets/textures/arena/arena_pillar.jpg", 
            'arena_floor': "../assets/textures/arena/arena_floor.png",
            'arena_ceiling': "../assets/textures/arena/arena_ceiling.jpg"
        }
        
        print("\n--- Loading Arena Textures ---")
        for texture_name, texture_path in arena_textures.items():
            try:
                print(f"Checking path: {texture_path}")
                if os.path.exists(texture_path):
                    print(f"  File exists: YES")
                    file_size = os.path.getsize(texture_path)
                    print(f"  File size: {file_size} bytes")
                    
                    self.textures[texture_name] = pygame.image.load(texture_path).convert()
                    width = self.textures[texture_name].get_width()
                    height = self.textures[texture_name].get_height()
                    print(f"  ✓ {texture_name} loaded successfully ({width}x{height})")
                else:
                    print(f"  File exists: NO")
                    print(f"  ERROR: File not found at {texture_path}")
                    
            except pygame.error as e:
                print(f"  ERROR loading {texture_name}: {e}")
            except Exception as e:
                print(f"  UNEXPECTED ERROR loading {texture_name}: {e}")
        
        town_textures = {
            'town_wall': "../assets/textures/town/town_wall.jpeg",
            'town_house': "../assets/textures/town/town_house.png",
            
            'weapon_shop': "../assets/textures/town/weapon_shop.png",
            'magic_shop': "../assets/textures/town/magic_shop.png",
            'healer_shop': "../assets/textures/town/healer_shop.png",
            'arena_entrance': "../assets/textures/town/arena_entrance.png",
        }
        
        npc_textures = {
            'gareth': "../assets/textures/npcs/gareth_merchant.png",
            'evangeline': "../assets/textures/npcs/evangeline_sister.png", 
            'aldric': "../assets/textures/npcs/aldric_captain.png",
            'elara': "../assets/textures/npcs/elara_seamstress.png",
            'finn': "../assets/textures/npcs/finn_apprentice.png",
            'willem': "../assets/textures/npcs/willem_storyteller.png",
            'meredith': "../assets/textures/npcs/meredith_herbalist.png",
            'roderick': "../assets/textures/npcs/roderick_knight.png",
            'tobias': "../assets/textures/npcs/tobias_crier.png",
            'margot': "../assets/textures/npcs/margot_flowergirl.png",
            'bran': "../assets/textures/npcs/bran_baker.png",
            'clara': "../assets/textures/npcs/clara_scribe.png",
            'tom': "../assets/textures/npcs/tom_stable.png",
            'luna': "../assets/textures/npcs/luna_minstrel.png",
            'erik': "../assets/textures/npcs/erik_guard.png"
        }
        
        print("\n--- Loading Town Textures ---")
        for texture_name, texture_path in town_textures.items():
            try:
                print(f"Checking path: {texture_path}")
                if os.path.exists(texture_path):
                    print(f"  File exists: YES")
                    file_size = os.path.getsize(texture_path)
                    print(f"  File size: {file_size} bytes")
                    
                    self.textures[texture_name] = pygame.image.load(texture_path).convert()
                    width = self.textures[texture_name].get_width()
                    height = self.textures[texture_name].get_height()
                    print(f"  ✓ {texture_name} loaded successfully ({width}x{height})")
                else:
                    print(f"  File exists: NO")
                    print(f"  Will use fallback for {texture_name}")
                    
            except pygame.error as e:
                print(f"  ERROR loading {texture_name}: {e}")
            except Exception as e:
                print(f"  UNEXPECTED ERROR loading {texture_name}: {e}")

        print("\n--- Loading NPC Textures ---")
        for texture_name, texture_path in npc_textures.items():
            try:
                print(f"Checking path: {texture_path}")
                if os.path.exists(texture_path):
                    print(f"  File exists: YES")
                    file_size = os.path.getsize(texture_path)
                    print(f"  File size: {file_size} bytes")
                    
                    self.textures[texture_name] = pygame.image.load(texture_path).convert_alpha()
                    width = self.textures[texture_name].get_width()
                    height = self.textures[texture_name].get_height()
                    print(f"  ✓ {texture_name} loaded successfully ({width}x{height})")
                else:
                    print(f"  File exists: NO")
                    print(f"  Will use fallback for {texture_name}")
                    
            except pygame.error as e:
                print(f"  ERROR loading {texture_name}: {e}")
            except Exception as e:
                print(f"  UNEXPECTED ERROR loading {texture_name}: {e}")
        
        print(f"\n--- Final Texture Inventory ---")
        print(f"Total textures loaded: {len(self.textures)}")
        for name, texture in self.textures.items():
            if texture:
                print(f"  ✓ {name}: {texture.get_width()}x{texture.get_height()}")
            else:
                print(f"  ✗ {name}: FAILED")
        
        print(f"\n--- Creating Fallback Textures ---")
        self.create_fallback_textures()
        print("=== END TEXTURE LOADING DEBUG ===\n")

    def create_fallback_textures(self):
        """Create simple colored textures if image files aren't found"""
        print("--- Creating Fallback Textures ---")
        texture_size = 64
        
        SANDY_FLOOR = (194, 178, 128) 
        
        SKY_BLUE_CEILING = (135, 206, 235)
        
        if 'arena_wall' not in self.textures or self.textures['arena_wall'] is None:
            self.textures['arena_wall'] = pygame.Surface((texture_size, texture_size))
            self.textures['arena_wall'].fill(DARK_BROWN)
            print("  Created fallback: arena_wall (dark brown)")
        
        if 'arena_pillar' not in self.textures or self.textures['arena_pillar'] is None:
            self.textures['arena_pillar'] = pygame.Surface((texture_size, texture_size))
            self.textures['arena_pillar'].fill(GRAY)
            print("  Created fallback: arena_pillar (gray)")
        
       
        self.textures['arena_floor'] = self.create_sandy_texture(texture_size)
        print("  Created/Overrode: arena_floor (sandy texture)")
        
        self.textures['arena_ceiling'] = pygame.Surface((texture_size, texture_size))
        self.textures['arena_ceiling'].fill(SKY_BLUE_CEILING)
        print("  Created/Overrode: arena_ceiling (sky blue)")
        
        if 'town_wall' not in self.textures or self.textures['town_wall'] is None:
            self.textures['town_wall'] = pygame.Surface((texture_size, texture_size))
            self.textures['town_wall'].fill(BROWN)
            print("  Created fallback: town_wall (brown)")
        
        if 'town_house' not in self.textures or self.textures['town_house'] is None:
            self.textures['town_house'] = pygame.Surface((texture_size, texture_size))
            self.textures['town_house'].fill(GRAY)
            print("  Created fallback: town_house (gray)")
        
        if 'weapon_shop' not in self.textures or self.textures['weapon_shop'] is None:
            self.textures['weapon_shop'] = pygame.Surface((texture_size, texture_size))
            self.textures['weapon_shop'].fill(DARK_RED)  
            print("  Created fallback: weapon_shop (dark red)")
        
        if 'magic_shop' not in self.textures or self.textures['magic_shop'] is None:
            self.textures['magic_shop'] = pygame.Surface((texture_size, texture_size))
            self.textures['magic_shop'].fill(PURPLE)  
            print("  Created fallback: magic_shop (purple)")
        
        if 'healer_shop' not in self.textures or self.textures['healer_shop'] is None:
            self.textures['healer_shop'] = pygame.Surface((texture_size, texture_size))
            self.textures['healer_shop'].fill(WHITE)  
            print("  Created fallback: healer_shop (white)")
        
        if 'arena_entrance' not in self.textures or self.textures['arena_entrance'] is None:
            self.textures['arena_entrance'] = pygame.Surface((texture_size, texture_size))
            self.textures['arena_entrance'].fill(GOLD)  
            print("  Created fallback: arena_entrance (gold)")
        
        npc_info = {
            'gareth': GREEN,
            'evangeline': WHITE, 
            'aldric': BROWN,
            'elara': PURPLE,
            'finn': (255, 165, 0),  
            'willem': GRAY,
            'meredith': (0, 100, 0),  
            'roderick': (192, 192, 192),  
            'tobias': YELLOW,
            'margot': (173, 216, 230), 
            'bran': (139, 69, 19),  
            'clara': (128, 0, 128),  
            'tom': (205, 133, 63),  
            'luna': (255, 20, 147),  
            'erik': (47, 79, 79)  
        }
        
        for npc_name, color in npc_info.items():
            if npc_name not in self.textures or self.textures[npc_name] is None:
                npc_texture = pygame.Surface((texture_size, texture_size))
                npc_texture.fill(color)
                
                eye_size = texture_size // 8
                left_eye_x = texture_size // 4
                right_eye_x = texture_size * 3 // 4
                eye_y = texture_size // 3
                
                pygame.draw.circle(npc_texture, WHITE, (left_eye_x, eye_y), eye_size)
                pygame.draw.circle(npc_texture, WHITE, (right_eye_x, eye_y), eye_size)
                
                self.textures[npc_name] = npc_texture
                print(f"  Created fallback: {npc_name} ({color})")
        
       
        self.textures['town_ground'] = self.create_sandy_texture(texture_size)
        print("  Created/Overrode: town_ground (sandy texture)")
        
        self.textures['sky'] = pygame.Surface((texture_size, texture_size))
        self.textures['sky'].fill(SKY_BLUE_CEILING)
        print("  Created/Overrode: sky (sky blue)")
        
        print("--- Fallback Creation Complete ---")

    def create_sandy_texture(self, size):
        """Create a sandy-looking texture with some variation"""
        texture = pygame.Surface((size, size))
        
        base_sandy = (194, 178, 128)
        
        texture.fill(base_sandy)
        
        import random
        for _ in range(size * size // 4):  
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)
            
            r_var = random.randint(-20, 20)
            g_var = random.randint(-15, 15)
            b_var = random.randint(-10, 10)
            
            new_color = (
                max(0, min(255, base_sandy[0] + r_var)),
                max(0, min(255, base_sandy[1] + g_var)),
                max(0, min(255, base_sandy[2] + b_var))
            )
            
            texture.set_at((x, y), new_color)
        
        return texture

    def render_textured_floor_ceiling(self, player, view_bob, is_arena=True):
        """Render floor and ceiling with textures"""
        if is_arena:
            floor_texture = self.textures.get('arena_floor')
            ceiling_texture = self.textures.get('arena_ceiling')
        else:
            floor_texture = self.textures.get('town_ground')
            ceiling_texture = self.textures.get('sky')
        
        if not floor_texture or not ceiling_texture:
            sandy_color = (194, 178, 128)  
            sky_blue = (135, 206, 235)     
            
            if is_arena:
                pygame.draw.rect(self.screen, sky_blue, (0, 0 + view_bob, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
                pygame.draw.rect(self.screen, sandy_color, (0, SCREEN_HEIGHT // 2 + view_bob, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            else:
                pygame.draw.rect(self.screen, sky_blue, (0, 0 + view_bob, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
                pygame.draw.rect(self.screen, sandy_color, (0, SCREEN_HEIGHT // 2 + view_bob, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            return

        texture_width = floor_texture.get_width()
        texture_height = floor_texture.get_height()
        
        offset_x = int(player.x * 0.5) % texture_width
        offset_y = int(player.y * 0.5) % texture_height
        
        for x in range(0, SCREEN_WIDTH, texture_width):
            for y in range(0, SCREEN_HEIGHT // 2, texture_height):
                tex_x = (x - offset_x) % texture_width
                tex_y = (y - offset_y) % texture_height
                self.screen.blit(ceiling_texture, (x, y + view_bob))
        
        for x in range(0, SCREEN_WIDTH, texture_width):
            for y in range(SCREEN_HEIGHT // 2, SCREEN_HEIGHT, texture_height):
                tex_x = (x - offset_x) % texture_width
                tex_y = (y - offset_y) % texture_height
                self.screen.blit(floor_texture, (x, y + view_bob))

    def cast_rays(self, player, collision_map, map_width, map_height) -> List[Tuple[float, float, int, float, float]]:
        """Enhanced ray casting that also returns hit coordinates for texture mapping"""
        rays = []
        ray_angle = player.angle - HALF_FOV

        for ray in range(NUM_RAYS):
            depth = 0
            wall_type = 1
            hit_x, hit_y = 0, 0
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            for depth in range(0, MAX_DEPTH * TILE_SIZE, 4):
                target_x = player.x + cos_a * depth
                target_y = player.y + sin_a * depth
                map_x = int(target_x // TILE_SIZE)
                map_y = int(target_y // TILE_SIZE)

                if map_x < 0 or map_x >= map_width or map_y < 0 or map_y >= map_height:
                    wall_type = 1
                    hit_x, hit_y = target_x, target_y
                    break

                wall_type = collision_map[map_y][map_x]
                if wall_type != 0:
                    hit_x, hit_y = target_x, target_y
                    break

            depth *= math.cos(player.angle - ray_angle)  
            rays.append((depth, ray_angle, wall_type, hit_x, hit_y))
            ray_angle += DELTA_ANGLE

        return rays

    def render_3d_town(self, rays: List[Tuple[float, float, int, float, float]], player):
        """Render 3D town environment with simple texture tiling - FIXED VERSION"""
        view_bob = int(player.z * 0.3)

        self.render_textured_floor_ceiling(player, view_bob, is_arena=False)

        for i, (depth, ray_angle, wall_type, hit_x, hit_y) in enumerate(rays):
            if wall_type != 0:
                wall_height = min(SCREEN_HEIGHT, 21000 / max(depth, 1))
                wall_y = (SCREEN_HEIGHT - wall_height) // 2 + view_bob
                wall_x = i * 2  

                texture = None
                if wall_type == 1:  
                    texture = self.textures.get('town_wall')
                elif wall_type == 2:  
                    texture = self.textures.get('town_house')
                elif wall_type == 3: 
                    texture = self.textures.get('weapon_shop')
                elif wall_type == 4:  
                    texture = self.textures.get('magic_shop')
                elif wall_type == 5:  
                    texture = self.textures.get('healer_shop')
                elif wall_type == 6: 
                    texture = self.textures.get('arena_entrance')
                
                if texture and wall_height > 0:
                    stretched_texture = pygame.transform.scale(texture, (2, int(wall_height)))
                    
                    color_intensity = max(50, 255 - int(depth * 4))
                    if color_intensity < 255:
                        dark_overlay = pygame.Surface((2, int(wall_height)))
                        dark_overlay.fill((color_intensity, color_intensity, color_intensity))
                        
                        stretched_texture.blit(dark_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                    
                    self.screen.blit(stretched_texture, (wall_x, wall_y))
                    
                else:
                    colors = {
                        1: BROWN,     
                        2: GRAY,      
                        3: DARK_RED, 
                        4: PURPLE,   
                        5: WHITE,    
                        6: GOLD       
                    }
                    base_color = colors.get(wall_type, GRAY)
                    
                    color_intensity = max(50, 255 - int(depth * 4))
                    wall_color = tuple(int(c * color_intensity / 255) for c in base_color)
                    
                    pygame.draw.rect(self.screen, wall_color, (wall_x, wall_y, 2, wall_height))

    def render_3d_arena(self, rays: List[Tuple[float, float, int, float, float]], enemies, spells, player):
        """Render 3D arena environment with simple texture tiling"""
        view_bob = int(player.z * 0.3)

        self.render_textured_floor_ceiling(player, view_bob, is_arena=True)

        for i, (depth, ray_angle, wall_type, hit_x, hit_y) in enumerate(rays):
            if wall_type != 0:
                wall_height = min(SCREEN_HEIGHT, 21000 / max(depth, 1))
                wall_y = max(0, (SCREEN_HEIGHT - wall_height) // 2 + view_bob)
                wall_x = i * 2
                actual_wall_height = min(wall_height, SCREEN_HEIGHT - wall_y)

                if wall_type == 1:
                    texture = self.textures.get('arena_wall')
                elif wall_type == 2:
                    texture = self.textures.get('arena_pillar')
                else:
                    texture = self.textures.get('arena_wall')

                if texture and actual_wall_height > 0:
                    stretched_texture = pygame.transform.scale(texture, (2, int(actual_wall_height)))
                    
                    color_intensity = max(30, 255 - int(depth * 6))
                    if color_intensity < 255:
                        dark_overlay = pygame.Surface((2, int(actual_wall_height)))
                        dark_overlay.fill((color_intensity, color_intensity, color_intensity))
                        stretched_texture.blit(dark_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                    
                    self.screen.blit(stretched_texture, (wall_x, wall_y))
                    
                else:
                    if wall_type == 1:
                        base_color = DARK_BROWN
                    elif wall_type == 2:
                        base_color = GRAY
                    else:
                        base_color = GRAY

                    color_intensity = max(30, 255 - int(depth * 6))
                    wall_color = tuple(int(c * color_intensity / 255) for c in base_color)

                    if actual_wall_height > 0:
                        pygame.draw.rect(self.screen, wall_color, (wall_x, wall_y, 2, actual_wall_height))

        self.render_spells(spells, view_bob)
        self.render_enemies(player, enemies, view_bob)

    def render_spells(self, spells, view_bob: int = 0):
        for spell in spells:
            if not spell.alive:
                continue
            screen_x = int(spell.x * 0.5)
            screen_y = int(spell.y * 0.5) + view_bob
            if 0 <= screen_x < SCREEN_WIDTH and 0 <= screen_y < SCREEN_HEIGHT:
                pygame.draw.circle(self.screen, spell.color, (screen_x, screen_y), spell.size)

    def render_enemies(self, player, enemies, view_bob: int = 0):
        for enemy in enemies:
            if not enemy.alive:
                continue

            dx = enemy.x - player.x
            dy = enemy.y - player.y
            enemy_distance = math.sqrt(dx * dx + dy * dy)
            if enemy_distance < 1:
                continue

            enemy_angle = math.atan2(dy, dx)
            angle_diff = enemy_angle - player.angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi

            if abs(angle_diff) < HALF_FOV:
                screen_x = (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2) + (SCREEN_WIDTH // 2)

                enemy_scale = max(4, int(enemy.size * 1000 / enemy_distance))
                enemy_width = enemy_scale
                enemy_height = enemy_scale

                scaled_image = pygame.transform.scale(enemy.image, (enemy_width, enemy_height))
                enemy_y = (SCREEN_HEIGHT // 2 - enemy_height // 2) + view_bob
                enemy_rect = scaled_image.get_rect(center=(int(screen_x), int(enemy_y + enemy_height // 2)))

                self.screen.blit(scaled_image, enemy_rect)

    def render_bosses(self, player, bosses, view_bob: int = 0):
        """Render boss sprites"""
        for boss in bosses:
            if not boss.alive:
                continue

            dx = boss.x - player.x
            dy = boss.y - player.y
            boss_distance = math.sqrt(dx * dx + dy * dy)
            if boss_distance < 1:
                continue

            boss_angle = math.atan2(dy, dx)
            angle_diff = boss_angle - player.angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi

            if abs(angle_diff) < HALF_FOV:
                screen_x = (angle_diff / HALF_FOV) * (SCREEN_WIDTH // 2) + (SCREEN_WIDTH // 2)

                boss_scale = max(8, int(boss.size * 1200 / boss_distance)) 
                boss_width = boss_scale
                boss_height = boss_scale

                if hasattr(boss, 'image') and boss.image:
                    scaled_image = pygame.transform.scale(boss.image, (boss_width, boss_height))
                    boss_y = (SCREEN_HEIGHT // 2 - boss_height // 2) + view_bob
                    boss_rect = scaled_image.get_rect(center=(int(screen_x), int(boss_y + boss_height // 2)))
                    self.screen.blit(scaled_image, boss_rect)