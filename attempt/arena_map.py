import math

class ArenaMap:
    def __init__(self):
        self.width = 20
        self.height = 20

        self.collision_map = self.create_arena_map()
        
    def create_arena_map(self):
        """Create the smaller circular arena without pillars"""
        arena_map = [[1 for _ in range(self.width)] for _ in range(self.height)]
        
        center_x, center_y = self.width // 2, self.height // 2
        arena_radius = 6  
        
        for y in range(self.height):
            for x in range(self.width):
                distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                if distance < arena_radius:
                    arena_map[y][x] = 0
        
        return arena_map
        
    def get_tile(self, x, y):
        """Get tile type at given coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.collision_map[y][x]
        return 1 
        
    def is_walkable(self, x, y):
        """Check if a tile is walkable"""
        return self.get_tile(x, y) == 0