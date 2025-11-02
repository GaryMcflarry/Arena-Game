class TownMap:
    def __init__(self):
        self.width = 15  
        self.height = 12  
 
        
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
            [1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1]  
        ]
        
        self.buildings = {
            "weapon_shop": {"name": "Blacksmith", "pos": (1, 1)},
            "magic_shop": {"name": "Mystic Arts", "pos": (13, 1)},
            "healer": {"name": "Temple of Healing", "pos": (1, 9)},
            "arena": {"name": "Arena Entrance", "pos": (7, 1)}
        }
        
    def get_tile(self, x, y):
        """Get tile type at given coordinates"""
        x = int(x)
        y = int(y)
        
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.collision_map[y][x]
        return 1 
        
    def is_walkable(self, x, y):
        """Check if a tile is walkable"""
        tile_type = self.get_tile(x, y)
        return tile_type == 0  
        
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