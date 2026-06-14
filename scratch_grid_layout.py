import json

def test_grid_layout():
    with open('world_map_static.json', 'r') as f:
        data = json.load(f)
        
    grid = {}
    coords = {}
    visited = set()
    
    dir_map = {
        'n': (0, -1), 's': (0, 1), 'e': (1, 0), 'w': (-1, 0),
        'ne': (1, -1), 'nw': (-1, -1), 'se': (1, 1), 'sw': (-1, 1),
        'u': (0, -1), 'd': (0, 1) # Treat up/down as north/south for 2D mapping
    }
    
    offset_x = 0
    for start_room in data.keys():
        if start_room in visited:
            continue
            
        queue = [(start_room, offset_x, 0)]
        while queue:
            curr, x, y = queue.pop(0)
            if curr in visited:
                continue
                
            visited.add(curr)
            
            # Find nearest empty spot if taken
            if (x, y) in grid:
                radius = 1
                found = False
                while not found:
                    for dx in range(-radius, radius + 1):
                        for dy in range(-radius, radius + 1):
                            if (x + dx, y + dy) not in grid:
                                x += dx
                                y += dy
                                found = True
                                break
                        if found: break
                    radius += 1
                    
            grid[(x, y)] = curr
            coords[curr] = (x, y)
            
            r_data = data.get(curr, {})
            for ex in r_data.get('exits', []):
                dest = ex['destination']
                dirs = ex['directions']
                if dest and dirs:
                    d = dirs[0].lower()
                    dx, dy = dir_map.get(d, (1, 1))
                    if dest not in visited:
                        queue.append((dest, x + dx, y + dy))
                        
        offset_x += 50 # Disconnected regions spaced out
        
    print(f"Total rooms mapped: {len(coords)}")
    print(f"Total grid slots used: {len(grid)}")
    
test_grid_layout()
