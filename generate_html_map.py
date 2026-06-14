import json

def generate_map():
    with open('world_map_static.json', 'r') as f:
        data = json.load(f)
        
    with open('curated_map_layout.json', 'r') as f:
        curated_layout = json.load(f)

    nodes = []
    edges = []
    added_edges = set()
    
    # Grid multiplier determines pixel distance between rooms
    GRID_SIZE = 120
    
    for room_id, pos in curated_layout.items():
        r_data = data.get(room_id, {})
        name = r_data.get('name', room_id)
        nodes.append({
            'data': {
                'id': room_id,
                'name': name,
                'description': r_data.get('description', 'No description available.')
            },
            'position': {
                'x': pos['x'] * GRID_SIZE,
                'y': pos['y'] * GRID_SIZE
            }
        })
        
        for ex in r_data.get('exits', []):
            dest = ex['destination']
            # ONLY connect to rooms that are part of our curated historic layout
            if dest in curated_layout:
                edge_id = f"{room_id}-{dest}"
                if edge_id not in added_edges:
                    added_edges.add(edge_id)
                    edges.append({
                        'data': {
                            'id': edge_id,
                            'source': room_id,
                            'target': dest
                        }
                    })

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>MUD1 Historic Curated Map</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #e8dcc7; /* Parchment background */
            font-family: serif;
            overflow: hidden;
        }}
        #cy {{
            width: 100vw;
            height: 100vh;
            position: absolute;
            top: 0;
            left: 0;
        }}
        #hud {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(248, 244, 230, 0.9);
            padding: 20px;
            border-radius: 4px;
            border: 2px solid #2a2a2a;
            max-width: 400px;
            z-index: 10;
            pointer-events: none;
            box-shadow: 4px 4px 0px rgba(0,0,0,0.1);
        }}
        .room-title {{
            color: #2a2a2a;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .room-desc {{
            color: #4a4a4a;
            font-size: 16px;
            line-height: 1.4;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div id="cy"></div>
    <div id="hud">
        <div class="room-title">Historic Curated Map</div>
        <div class="room-desc">Hover over any room to see its description. Click and drag to pan, scroll to zoom. Map curated from Richard Bartle's original sketches.</div>
    </div>
    <script>
        var cy = cytoscape({{
            container: document.getElementById('cy'),
            autoungrabify: true, // Prevent nodes from being grabbed or dragged
            autolock: true, // Prevent nodes from being programmatically moved
            elements: {{
                nodes: {json.dumps(nodes)},
                edges: {json.dumps(edges)}
            }},
            style: [
                {{
                    selector: 'node',
                    style: {{
                        'shape': 'rectangle',
                        'background-color': '#f8f4e6',
                        'border-color': '#2a2a2a',
                        'border-width': 2,
                        'width': 60,
                        'height': 60,
                        'label': 'data(id)',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-size': 14,
                        'font-family': 'serif',
                        'color': '#2a2a2a'
                    }}
                }},
                {{
                    selector: 'edge',
                    style: {{
                        'width': 3,
                        'line-color': '#3a3a3a',
                        'target-arrow-shape': 'none',
                        'curve-style': 'straight',
                        'z-index': -1
                    }}
                }},
                {{
                    selector: 'node:selected',
                    style: {{
                        'border-color': '#ff4444',
                        'border-width': 4,
                        'background-color': '#fffafa'
                    }}
                }}
            ],
            layout: {{
                name: 'preset' // Uses the exact curated X,Y positions
            }},
            userZoomingEnabled: true,
            userPanningEnabled: true,
            boxSelectionEnabled: false
        }});

        // Hover events for HUD
        cy.on('mouseover', 'node', function(evt){{
            var node = evt.target;
            document.body.style.cursor = 'pointer';
            var hud = document.getElementById('hud');
            hud.innerHTML = `
                <div class="room-title">${{node.data('name')}}</div>
                <div class="room-desc">${{node.data('description')}}</div>
            `;
        }});

        cy.on('mouseout', 'node', function(evt){{
            document.body.style.cursor = 'default';
        }});
    </script>
</body>
</html>
"""
    with open('interactive_map.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Map generated: interactive_map.html")

if __name__ == "__main__":
    generate_map()
