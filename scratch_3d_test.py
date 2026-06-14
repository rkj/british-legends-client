import json
def test_map():
    with open('world_map_static.json', 'r') as f:
        data = json.load(f)
    
    nodes = []
    edges = []
    for room_id, r_data in data.items():
        nodes.append({"id": room_id, "name": r_data.get("name", "")})
        for ex in r_data.get("exits", []):
            edges.append({"source": room_id, "target": ex["destination"], "label": ex["directions"][0] if ex["directions"] else ""})
            
    html = f"""
    <html>
    <head>
        <script src="https://unpkg.com/3d-force-graph"></script>
        <script src="https://unpkg.com/d3-force-3d"></script>
    </head>
    <body style="margin: 0; background: #111;">
        <div id="3d-graph"></div>
        <script>
            const gData = {{
                nodes: {json.dumps(nodes)},
                links: {json.dumps(edges)}
            }};
            
            const Graph = ForceGraph3D()
                (document.getElementById('3d-graph'))
                .graphData(gData)
                .nodeLabel('name')
                .enableNodeDrag(false)
                .nodeColor(() => '#00f2fe')
                .linkColor(() => 'rgba(255,255,255,0.2)');
                
            // Apply sphere constraint
            Graph.d3Force('collide', d3.forceCollide(5));
            Graph.d3Force('charge').strength(-20);
            Graph.d3Force('radial', d3.forceRadial(300, 0, 0, 0).strength(1.0));
        </script>
    </body>
    </html>
    """
    with open('test_3d_map.html', 'w') as f:
        f.write(html)

test_map()
