import json

def generate_map():
    with open('world_map_static.json', 'r') as f:
        data = json.load(f)
        
    nodes = []
    edges = []
    added_edges = set()
    
    for room_id, r_data in data.items():
        name = r_data.get('name', 'Unknown')
        nodes.append({
            'id': room_id,
            'label': f"{room_id}\n{name}",
            'title': r_data.get('description', ''),
            'font': {'size': 14}
        })
        
        for ex in r_data.get('exits', []):
            dest = ex['destination']
            dirs = ex['directions']
            if dirs and dest in data:
                direction = dirs[0]
                edge_id = f"{room_id}-{dest}-{direction}"
                if edge_id not in added_edges:
                    added_edges.add(edge_id)
                    edges.append({
                        'from': room_id,
                        'to': dest,
                        'label': direction,
                        'arrows': 'to',
                        'font': {'size': 10, 'align': 'middle'},
                        'color': {'color': '#848484'} if ex['condition'] == 'n' else {'color': '#ff4444'}
                    })
                    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>MUD1 Org Chart Fisheye</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        body {{ margin: 0; padding: 0; background-color: #1a1a1a; overflow: hidden; }}
        #mynetwork {{ width: 100vw; height: 100vh; border: none; }}
    </style>
</head>
<body>
    <div id="mynetwork"></div>
    <script type="text/javascript">
        var nodes = new vis.DataSet({json.dumps(nodes)});
        var edges = new vis.DataSet({json.dumps(edges)});
        
        var container = document.getElementById('mynetwork');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            nodes: {{
                shape: 'box',
                color: {{ background: '#2b2b2b', border: '#555555' }},
                font: {{ color: '#eeeeee', multi: true }}
            }},
            layout: {{
                hierarchical: {{
                    enabled: true,
                    direction: 'UD',
                    sortMethod: 'directed',
                    nodeSpacing: 250,
                    levelSeparation: 200
                }}
            }},
            physics: {{ enabled: false }}
        }};
        var network = new vis.Network(container, data, options);

        function updateFisheye() {{
            var center = network.getViewPosition();
            var allNodes = nodes.get();
            var updates = [];
            var posDict = network.getPositions(); // Very fast, gets all current positions
            
            for (var i = 0; i < allNodes.length; i++) {{
                var node = allNodes[i];
                var pos = posDict[node.id];
                if (!pos) continue;
                
                var dx = pos.x - center.x;
                var dy = pos.y - center.y;
                var dist = Math.sqrt(dx*dx + dy*dy);
                
                var scale = 1;
                if (dist < 400) {{
                    scale = 1 + (2.0 * (1 - (dist / 400))); // Max 3.0 scale at dead center
                }}
                
                var newSize = Math.round(14 * scale);
                if (node._currentSize !== newSize) {{
                    updates.push({{
                        id: node.id,
                        font: {{ size: newSize }},
                        _currentSize: newSize
                    }});
                }}
            }}
            
            if (updates.length > 0) {{
                nodes.update(updates);
            }}
        }}

        // Run continuous polling for fisheye 
        // This captures canvas panning effortlessly
        setInterval(updateFisheye, 30);
    </script>
</body>
</html>
"""
    with open('test_org_fisheye.html', 'w') as f:
        f.write(html_content)

generate_map()
