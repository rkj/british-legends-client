import json
import os
import re
from collections import deque

class MUDWorldMap:
    def __init__(self, static_map_file="world_map_static.json"):
        self.static_map_file = static_map_file
        self.static_map = {}
        self.visited_rooms = set()
        self.room_items = {}  # { room_id: [item1, item2] }
        self.load_static_map()

    def load_static_map(self):
        if os.path.exists(self.static_map_file):
            try:
                with open(self.static_map_file, "r", encoding="utf-8") as f:
                    self.static_map = json.load(f)
                print(f"[Map System]: Loaded static map with {len(self.static_map)} rooms.")
            except Exception as e:
                print(f"[Error loading static map: {e}]")
                self.static_map = {}
        else:
            print("[Warning: Static map not found. Run parse_map.py first.]")
            self.static_map = {}

    def parse_room(self, text):
        """
        Parses room output and cross-references with the static map to find the room_id.
        Returns (room_id, description, items, npcs) or (None, None, [], []) if not a room.
        """
        text = text.strip()
        if not text:
            return None, None, [], []

        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if not lines:
            return None, None, [], []

        # Skip echoed commands (usually short lowercase strings like 'n', 'w')
        start_idx = 0
        while start_idx < len(lines) and (not lines[start_idx] or not lines[start_idx][0].isupper()):
            start_idx += 1
            
        if start_idx >= len(lines):
            return None, None, [], []
            
        first_line = lines[start_idx]
        room_name = first_line.rstrip(".")
        description_lines = lines[start_idx+1:]
        
        # Room name heuristics
        if not room_name or not room_name[0].isupper():
            return None, None, [], []
        if not re.match(r"^[A-Za-z0-9\s'\-]+$", room_name):
            return None, None, [], []
        if len(room_name.split()) > 5 or len(room_name) > 45:
            return None, None, [], []
            
        ignores = [
            "locked", "can't", "cannot", "berk", "shouts", "tells", "says", "score", "sta:", 
            "welcome", "persona", "initialising", "copyright", "valuable", "increased", "points", 
            "retaliate", "taken", "dropped", "carrying", "holding", "wielding", "wearing", 
            "attacks", "hits", "misses", "swipes", "shrugs", "parries", "dodges", "flee", "flees",
            "kills", "died", "dead", "invalid", "error", "what?", "pardon?", "direction", 
            "you ", "your ", "she ", "he ", "it ", "they ", "them ", "my ", "me ", "our ", "us ",
            "slides", "revealing", "opening", "door's", "shout", "tell", "say", "double dutch",
            "beggar", "zombie", "dwarf", "dragon", "wizard", "witch", "combat", "fight",
            "yes", "no", "ok", "true", "false", "password"
        ]
        lower_name = room_name.lower()
        if any(ignore in lower_name for ignore in ignores):
            return None, None, [], []

        description = "\n".join(description_lines)
        
        # Extract items
        items = []
        item_patterns = [
            r"There is a\s+(.*?)\s+here\.",
            r"There is an?\s+(.*?)\s+on the ground\.",
            r"A\s+(.*?)\s+lies strewn at your feet\.",
            r"An?\s+(.*?)\s+has been placed here\.",
            r"An?\s+(.*?)\s+is lying on the floor\.",
            r"There is a\s+(.*?)\s+lying around\."
        ]
        
        for p in item_patterns:
            matches = re.findall(p, description)
            for m in matches:
                if "door" not in m.lower() and "sign" not in m.lower():
                    items.append(m.strip())
                    
        # Extract NPCs
        npcs = []
        npc_patterns = [
            r"A[n]?\s+(.*?)\s+is (?:standing|sitting|hovering|sleeping|lying) here\.",
            r"The\s+(.*?)\s+is (?:standing|sitting|hovering|sleeping|lying) here\.",
            r"A[n]?\s+(.*?)\s+blocks your way!",
            r"The\s+(.*?)\s+blocks your way!",
            r"A[n]?\s+(.*?)\s+slithers by your feet",
            r"A[n]?\s+(.*?)\s+snuffles round your feet",
            r"A[n]?\s+(.*?)\s+is here\."
        ]
        for p in npc_patterns:
            matches = re.findall(p, description)
            for m in matches:
                if m.strip().lower() not in [i.lower() for i in items]:
                    npcs.append(m.strip())
                    
        # NOW, cross-reference with static map
        matched_room_id = None
        
        # 1. Exact match on name AND description (highest confidence)
        clean_desc = re.sub(r'\s+', ' ', description.strip())
        for r_id, r_data in self.static_map.items():
            if r_data["name"].rstrip('.') == room_name:
                static_desc = re.sub(r'\s+', ' ', r_data["description"].strip())
                if clean_desc.startswith(static_desc) or static_desc in clean_desc:
                    matched_room_id = r_id
                    break
                    
        # 2. Fallback: match just the name if unique
        if not matched_room_id:
            candidates = [r_id for r_id, r_data in self.static_map.items() if r_data["name"].rstrip('.') == room_name]
            if len(candidates) == 1:
                matched_room_id = candidates[0]
                
        if not matched_room_id:
            # Maybe brief mode? Return the raw name if we can't find an ID
            return room_name, description, items, npcs
            
        return matched_room_id, description, items, npcs

    def add_room(self, room_id, description, items):
        self.visited_rooms.add(room_id)
        if items:
            self.room_items[room_id] = list(set(items))

    def add_connection(self, source, target, direction):
        pass # No-op, map is static

    def mark_locked(self, source, direction):
        pass # No-op for now

    def clear_all_items(self, room_id):
        if room_id in self.room_items:
            self.room_items[room_id] = []

    def remove_item(self, room_id, item):
        if room_id in self.room_items:
            self.room_items[room_id] = [i for i in self.room_items[room_id] if item.lower() not in i.lower()]

    def find_path(self, start_id, goal_func):
        """BFS on static map"""
        if start_id not in self.static_map:
            return None
            
        queue = deque([(start_id, [])])
        visited = {start_id}
        
        while queue:
            curr_id, path = queue.popleft()
            
            if goal_func(curr_id):
                return curr_id, path
                
            node = self.static_map.get(curr_id, {})
            for exit in node.get("exits", []):
                # Only use "normal" connections to be safe
                if exit["condition"] == "n" and exit["directions"]:
                    dest = exit["destination"]
                    direction = exit["directions"][0]
                    
                    if dest not in visited and dest in self.static_map:
                        visited.add(dest)
                        queue.append((dest, path + [direction]))
        return None

    def get_summary(self, current_room_id):
        if not current_room_id:
            return "Map Status: Location unknown."
            
        # Is current_room_id in static map?
        if current_room_id not in self.static_map:
            # Fallback if using raw text name
            return f"Map Status: At '{current_room_id}'. Not synced with static map."
            
        r_data = self.static_map[current_room_id]
        name = r_data["name"]
        
        lines = [f"=== KNOWN MAP LAYOUT ==="]
        lines.append(f"Current Location: [{current_room_id}] {name}")
        
        items_here = self.room_items.get(current_room_id, [])
        if items_here:
            lines.append(f"Items Here: {', '.join(items_here)}")
            
        lines.append(f"\nExits from {current_room_id}:")
        for ex in r_data.get("exits", []):
            if ex["directions"]:
                d = ex["directions"][0]
                cond = ex["condition"]
                dest = ex["destination"]
                dest_name = self.static_map.get(dest, {}).get("name", "Unknown")
                cond_str = f" (requires {cond})" if cond != "n" else ""
                lines.append(f"  - {d.upper()}: [{dest}] {dest_name}{cond_str}")
                
        # Find path to nearest known item
        treasure_rooms = {rid for rid, items in self.room_items.items() if items}
        if treasure_rooms - {current_room_id}:
            goal = lambda rid: rid in treasure_rooms and rid != current_room_id
            res = self.find_path(current_room_id, goal)
            if res:
                target_id, path = res
                target_items = self.room_items[target_id]
                lines.append(f"\n[Path to Known Items]: [{target_id}] contains {', '.join(target_items)}")
                lines.append(f"Commands to reach: {', '.join(path)}")
        else:
            # Find path to nearest unvisited room
            goal = lambda rid: rid not in self.visited_rooms
            res = self.find_path(current_room_id, goal)
            if res:
                target_id, path = res
                target_name = self.static_map.get(target_id, {}).get("name", "Unknown")
                lines.append(f"\n[Path to Unvisited Room]: [{target_id}] {target_name}")
                lines.append(f"Commands to reach: {', '.join(path)}")
                
        return "\n".join(lines)
