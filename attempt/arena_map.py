import math

class ArenaMap:
    def __init__(self):
        self.width = 20
        self.height = 20
        
        # Create arena layout - circular arena with pillars
        # 0 = empty space (walkable)
        # 1 = wall
        # 2 = pillar
        self.collision_map = self.create_arena_map()
        
    def create_arena_map(self):
        """Create the circular arena with pillars"""
        arena_map = [[1 for _ in range(self.width)] for _ in range(self.height)]
        
        center_x, center_y = self.width // 2, self.height // 2
        arena_radius = 8
        
        # Create circular arena
        for y in range(self.height):
            for x in range(self.width):
                distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                if distance < arena_radius:
                    arena_map[y][x] = 0  # Open space
        
        # Add pillars for cover
        pillar_positions = [
            (center_x - 3, center_y - 3),
            (center_x + 3, center_y - 3),
            (center_x - 3, center_y + 3),
            (center_x + 3, center_y + 3),
            (center_x, center_y - 5),
            (center_x, center_y + 5),
            (center_x - 5, center_y),
            (center_x + 5, center_y),
        ]
        
        for px, py in pillar_positions:
            if 0 <= px < self.width and 0 <= py < self.height:
                arena_map[py][px] = 2  # Pillar
        
        return arena_map
        
    def get_tile(self, x, y):
        """Get tile type at given coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.collision_map[y][x]
        return 1  # Return wall for out of bounds
        
    def is_walkable(self, x, y):
        """Check if a tile is walkable"""
        return self.get_tile(x, y) == 0