# Shadow Arena

A 3D first-person dungeon crawlerb built with Python and Pygame.

## Game Structure

### Files Overview

- **main.py** - Entry point and main game loop
- **game_state_manager.py** - Manages different game states (menu, town, arena, shop)
- **constants.py** - Game constants, colors, and enums
- **player.py** - Player class with movement, combat, and progression
- **town_state.py** - Town exploration with 3D raycasting
- **town_map.py** - Town layout and building definitions
- **arena_state.py** - Arena combat system with waves
- **arena_map.py** - Circular arena layout with pillars
- **shop_state.py** - Equipment upgrade and healing shops
- **raycaster.py** - 3D rendering engine for both town and arena
- **enemy.py** - Regular enemy types (Skeleton, Orc, Troll, Demon)
- **boss.py** - Boss enemies with special abilities
- **spell.py** - Magic projectile system

### Game Flow

1. **Main Menu** - Start game, view stats, quit
2. **Town** - 3D exploration hub with shops and arena entrance
3. **Shops** - Upgrade weapons, armor, magic, or buy healing items
4. **Arena** - 20-wave survival mode with bosses every 5 waves
5. **Progression** - Earn gold to buy upgrades between arena runs

## Controls

### Town & Arena (3D Mode)
- **WASD** - Move
- **Mouse** - Look around
- **Left Click** - Cast spell (arena only)
- **Right Click** - Cycle spells (arena only)
- **E** - Interact with buildings (town only)
- **ESC** - Return to main menu

### Menus & Shops
- **UP/DOWN** - Navigate options
- **ENTER/SPACE** - Select
- **ESC** - Return to previous screen

## Features

### Town System
- 3D first-person exploration
- Interactive buildings (weapon shop, magic shop, healer, arena entrance)
- Minimap display
- Seamless transitions between areas

### Arena Combat
- 20 progressive waves of enemies
- 4 enemy types with different strengths
- 4 unique bosses with special abilities
- 3 spell types (Fireball, Lightning, Ice)
- Real-time 3D combat

### Progression System
- Weapon upgrades (1-5 levels)
- Armor upgrades (1-5 levels) 
- Magic upgrades (1-5 levels)
- Gold economy
- Equipment affects stats (damage, health, mana, spell power)

### Bosses & Special Abilities
- **Wave 5 - Necromancer**: Summons skeleton minions
- **Wave 10 - Orc Chieftain**: Berserker rage mode
- **Wave 15 - Ancient Troll**: Health regeneration
- **Wave 20 - Demon Lord**: Teleport attacks

## Installation & Running

1. Ensure Python 3.7+ is installed
2. Install Pygame: `pip install pygame`
3. Run the game: `python main.py`
