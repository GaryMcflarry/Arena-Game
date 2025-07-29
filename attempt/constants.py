import math

# Screen constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Raycasting constants
FOV = math.pi / 3  # 60 degrees
HALF_FOV = FOV / 2
NUM_RAYS = SCREEN_WIDTH // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20

# Map constants
TILE_SIZE = 64

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 128, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
DARK_RED = (139, 0, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_GREEN = (0, 100, 0)

# Game states
class GameState:
    MENU = "menu"
    TOWN = "town"
    ARENA = "arena"
    SHOP = "shop"
    GAME_OVER = "game_over"

# Enemy types
class EnemyType:
    SKELETON = "skeleton"
    ORC = "orc"
    TROLL = "troll"
    DEMON = "demon"

# Boss types
class BossType:
    NECROMANCER = "necromancer"
    ORC_CHIEFTAIN = "orc_chieftain"
    ANCIENT_TROLL = "ancient_troll"
    DEMON_LORD = "demon_lord"

# Shop types
class ShopType:
    WEAPON = "weapon"
    MAGIC = "magic"
    HEALER = "healer"

# Spell types
SPELL_TYPES = ["fireball", "lightning", "ice"]