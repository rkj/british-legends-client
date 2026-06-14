import json

def calculate_xy():
    with open('world_map_static.json', 'r') as f:
        data = json.load(f)
        
    coords = {}
    visited = set()
    queue = [('nfrst1', 0, 0)] # START room
    
    # N -> y-1, S -> y+1, E -> x+1, W -> x-1
    # NE -> x+1, y-1, NW -> x-1, y-1
    # SE -> x+1, y+1, SW -> x-1, y+1
    # U, D -> z-axis (maybe ignore or offset slightly in xy)
    
    dir_map = {
        'n': (0, -1), 's': (0, 1), 'e': (1, 0), 'w': (-1, 0),
        'ne': (1, -1), 'nw': (-1, -1), 'se': (1, 1), 'sw': (-1, 1),
        'u': (0.5, -0.5), 'd': (-0.5, 0.5), 'in': (0, 0), 'out': (0, 0)
    }
    
    overlaps = 0
    while queue:
        curr, x, y = queue.pop(0)
        if curr in visited:
            # Check if coords are totally conflicting
            continue
        
        visited.add(curr)
        # If position is already taken, shift it slightly to avoid exact overlap
        while (x, y) in coords.values():
            x += 0.2
            y += 0.2
            overlaps += 1
            
        coords[curr] = (x, y)
        
        r_data = data.get(curr, {})
        for ex in r_data.get('exits', []):
            dest = ex['destination']
            dirs = ex['directions']
            if dest and dirs:
                direction = dirs[0].lower()
                dx, dy = dir_map.get(direction, (0, 0))
                if dest not in visited:
                    queue.append((dest, x + dx, y + dy))
                    
    print(f"Total rooms mapped: {len(coords)}")
    print(f"Total overlapping shifts needed: {overlaps}")
    
calculate_xy()
