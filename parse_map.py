import json
import os

def tokenize_line(line):
    parts = line.strip().split()
    tokens = []
    in_group = False
    group = []
    for p in parts:
        if p.startswith('<') and p.endswith('>'):
            tokens.append(p)
        elif p.startswith('<'):
            in_group = True
            group.append(p)
        elif p.endswith('>'):
            group.append(p)
            tokens.append(" ".join(group))
            in_group = False
            group = []
        elif in_group:
            group.append(p)
        else:
            tokens.append(p)
    return tokens

def parse_mud_txt(filepath="MUD.TXT", outpath="world_map_static.json"):
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    rooms = {}
    
    # 1. Parse @txtrms
    in_txtrms = False
    current_room = None
    desc_phase = 0 # 0=waiting for short, 1=waiting for long, 2=in long
    
    for line in lines:
        if line.startswith('@txtrms'):
            in_txtrms = True
            continue
        if in_txtrms and line.startswith('@'):
            in_txtrms = False
            continue
            
        if in_txtrms:
            stripped = line.strip()
            if not stripped:
                continue
                
            # If line has no leading whitespace, it's a new room definition
            if not line[0].isspace():
                parts = stripped.split()
                current_room = parts[0]
                flags = parts[1:]
                rooms[current_room] = {
                    "id": current_room,
                    "flags": flags,
                    "name": "",
                    "description": "",
                    "exits": []
                }
                desc_phase = 0
            elif current_room:
                if desc_phase == 0:
                    rooms[current_room]["name"] = stripped
                    desc_phase = 1
                else:
                    if rooms[current_room]["description"]:
                        rooms[current_room]["description"] += " " + stripped
                    else:
                        rooms[current_room]["description"] = stripped

    # Resolve %macros in short descriptions
    for r_id, r_data in rooms.items():
        if r_data["name"].startswith("%"):
            macro_room = r_data["name"][1:]
            if macro_room in rooms:
                r_data["name"] = rooms[macro_room]["name"]
                
    # 2. Parse *travel go
    in_travel = False
    current_src = None
    
    for line in lines:
        if line.startswith('*travel'):
            in_travel = True
            continue
        if in_travel and line.startswith('*'):
            in_travel = False
            break
            
        if in_travel:
            if not line.strip():
                continue
                
            tokens = tokenize_line(line)
            if not tokens:
                continue
                
            if not line[0].isspace():
                current_src = tokens[0]
                rule_parts = tokens[1:]
            else:
                rule_parts = tokens
                
            if not rule_parts or not current_src:
                continue
                
            if len(rule_parts) >= 2:
                condition = rule_parts[0]
                destination = rule_parts[1]
                directions = rule_parts[2:]
                
                if current_src in rooms:
                    rooms[current_src]["exits"].append({
                        "condition": condition,
                        "destination": destination,
                        "directions": directions,
                        "raw_line": line.strip()
                    })
                else:
                    # In case the source room wasn't declared in @txtrms (unlikely, but safe to handle)
                    rooms[current_src] = {
                        "id": current_src,
                        "flags": [],
                        "name": "Unknown Room",
                        "description": "",
                        "exits": [{
                            "condition": condition,
                            "destination": destination,
                            "directions": directions,
                            "raw_line": line.strip()
                        }]
                    }

    # Save to JSON
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(rooms, f, indent=2)

    print(f"Parsed {len(rooms)} rooms.")
    
    # Calculate some stats
    total_exits = sum(len(r["exits"]) for r in rooms.values())
    print(f"Total exits found: {total_exits}")

if __name__ == "__main__":
    parse_mud_txt()
