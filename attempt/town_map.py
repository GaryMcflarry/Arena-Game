class TownMap:
    def __init__(self):
        self.width = 15  # Smaller, more dense
        self.height = 12  # Compact height
        
        # Create compact town layout
        # 0 = empty space (walkable)
        # 1 = wall/building exterior
        # 2 = house (non-interactive building)
        # 3 = weapon shop
        # 4 = magic shop  
        # 5 = healer
        # 6 = arena entrance
        
        self.collision_map = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 3, 3, 0, 2, 2, 0, 6, 6, 0, 2, 2, 0, 4, 1],
            [1, 3, 3, 0, 2, 2, 0, 6, 6, 0, 2, 2, 0, 4, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
            [1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 5, 5, 0, 2, 2, 0, 0, 0, 0, 2, 2, 0, 2, 1],
            [1, 5, 5, 0, 2, 2, 0, 0, 0, 0, 2, 2, 0, 2, 1],
            [1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1]   # Opening at bottom center
        ]
        
        # Building information for interaction system
        self.buildings = {
            "weapon_shop": {"name": "Blacksmith", "pos": (1, 1)},
            "magic_shop": {"name": "Mystic Arts", "pos": (13, 1)},
            "healer": {"name": "Temple of Healing", "pos": (1, 9)},
            "arena": {"name": "Arena Entrance", "pos": (7, 1)}
        }
        
    def get_tile(self, x, y):
        """Get tile type at given coordinates"""
        # Ensure coordinates are integers
        x = int(x)
        y = int(y)
        
        # Check bounds more carefully
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.collision_map[y][x]
        return 1 
        
    def is_walkable(self, x, y):
        """Check if a tile is walkable"""
        tile_type = self.get_tile(x, y)
        return tile_type == 0  # Only empty space is walkable
        
    def get_building_at(self, x, y):
        """Get building type at given coordinates"""
        tile_type = self.get_tile(x, y)
        if tile_type == 3:
            return "weapon_shop"
        elif tile_type == 4:
            return "magic_shop"
        elif tile_type == 5:
            return "healer"
        elif tile_type == 6:
            return "arena"
        return None