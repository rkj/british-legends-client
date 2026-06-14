import json

def generate_explorer():
    with open('world_map_static.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Serialize JSON for embedding
    map_data_json = json.dumps(data)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MUD1 Interactive Explorer</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        :root {{
            --bg-dark: #121212;
            --bg-panel: #1e1e1e;
            --bg-hover: #2c2c2c;
            --text-main: #e0e0e0;
            --text-muted: #888888;
            --accent: #4caf50;
            --accent-hover: #45a049;
            --border: #333333;
        }}
        
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}

        /* Sidebar */
        #sidebar {{
            width: 300px;
            background-color: var(--bg-panel);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            height: 100%;
        }}
        
        #search-container {{
            padding: 15px;
            border-bottom: 1px solid var(--border);
        }}
        
        #search {{
            width: 100%;
            padding: 10px;
            box-sizing: border-box;
            background-color: var(--bg-dark);
            border: 1px solid var(--border);
            color: var(--text-main);
            border-radius: 4px;
        }}
        
        #room-list {{
            list-style: none;
            padding: 0;
            margin: 0;
            overflow-y: auto;
            flex-grow: 1;
        }}
        
        #room-list li {{
            padding: 10px 15px;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            transition: background 0.2s;
        }}
        
        #room-list li:hover, #room-list li.active {{
            background-color: var(--bg-hover);
            border-left: 4px solid var(--accent);
            padding-left: 11px;
        }}
        
        .room-id {{
            font-size: 0.8em;
            color: var(--text-muted);
            margin-bottom: 4px;
            font-family: monospace;
        }}
        
        .room-title {{
            font-weight: bold;
        }}

        /* Main Area */
        #main {{
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
        }}
        
        #content {{
            padding: 30px;
            background-color: var(--bg-dark);
            border-bottom: 1px solid var(--border);
            flex-shrink: 0;
        }}
        
        #content h1 {{
            margin-top: 0;
            color: var(--accent);
        }}
        
        #room-desc {{
            line-height: 1.6;
            font-size: 1.1em;
            margin-bottom: 25px;
            white-space: pre-wrap;
        }}
        
        .exit-btn {{
            display: inline-block;
            background-color: var(--bg-panel);
            color: var(--text-main);
            border: 1px solid var(--border);
            padding: 8px 16px;
            margin: 5px 5px 5px 0;
            border-radius: 4px;
            cursor: pointer;
            text-transform: uppercase;
            font-weight: bold;
            font-size: 0.9em;
            transition: all 0.2s;
        }}
        
        .exit-btn:hover {{
            background-color: var(--accent);
            border-color: var(--accent);
            color: white;
        }}
        
        .exit-condition {{
            font-size: 0.8em;
            color: #ff9800;
            text-transform: none;
            display: block;
            margin-top: 2px;
            font-weight: normal;
        }}

        /* Minimap */
        #minimap-container {{
            flex-grow: 1;
            position: relative;
            background-color: #0a0a0a;
        }}
        
        #minimap {{
            width: 100%;
            height: 100%;
        }}
        
        .minimap-title {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0,0,0,0.7);
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.9em;
            color: var(--text-muted);
            pointer-events: none;
            z-index: 10;
        }}
    </style>
</head>
<body>

    <div id="sidebar">
        <div id="search-container">
            <input type="text" id="search" placeholder="Search rooms..." onkeyup="filterRooms()">
        </div>
        <ul id="room-list"></ul>
    </div>
    
    <div id="main">
        <div id="content">
            <h1 id="room-name">Select a room</h1>
            <div id="room-meta" style="color: var(--text-muted); font-family: monospace; margin-bottom: 15px;"></div>
            <p id="room-desc">Welcome to the MUD Interactive Explorer. Use the sidebar to find a room, or click on a starting location to begin exploring.</p>
            <div id="exits"></div>
        </div>
        <div id="minimap-container">
            <div class="minimap-title">Local Area Radar (Depth: 1)</div>
            <div id="minimap"></div>
        </div>
    </div>

    <script>
        const mapData = {map_data_json};
        const roomListEl = document.getElementById('room-list');
        let currentRoomId = null;
        let network = null;
        
        // Initialize room list
        function initList() {{
            const sortedRooms = Object.keys(mapData).sort((a, b) => {{
                return mapData[a].name.localeCompare(mapData[b].name);
            }});
            
            sortedRooms.forEach(roomId => {{
                const room = mapData[roomId];
                const li = document.createElement('li');
                li.id = 'list-' + roomId;
                li.onclick = () => loadRoom(roomId);
                
                li.innerHTML = `
                    <div class="room-id">[${{roomId}}]</div>
                    <div class="room-title">${{room.name || 'Unknown'}}</div>
                `;
                roomListEl.appendChild(li);
            }});
        }}
        
        function filterRooms() {{
            const query = document.getElementById('search').value.toLowerCase();
            const items = roomListEl.getElementsByTagName('li');
            
            for (let i = 0; i < items.length; i++) {{
                const text = items[i].textContent || items[i].innerText;
                if (text.toLowerCase().indexOf(query) > -1) {{
                    items[i].style.display = "";
                }} else {{
                    items[i].style.display = "none";
                }}
            }}
        }}
        
        function loadRoom(roomId) {{
            if (!mapData[roomId]) return;
            
            const room = mapData[roomId];
            currentRoomId = roomId;
            
            // Update UI list selection
            const items = roomListEl.getElementsByTagName('li');
            for(let i=0; i<items.length; i++) items[i].classList.remove('active');
            const activeLi = document.getElementById('list-' + roomId);
            if(activeLi) activeLi.classList.add('active');
            
            // Update Content
            document.getElementById('room-name').innerText = room.name || 'Unknown Room';
            document.getElementById('room-meta').innerText = `ID: ${{roomId}} | Flags: ${{room.flags ? room.flags.join(', ') : 'none'}}`;
            document.getElementById('room-desc').innerText = room.description || '';
            
            // Update Exits
            const exitsEl = document.getElementById('exits');
            exitsEl.innerHTML = '';
            
            if (room.exits && room.exits.length > 0) {{
                room.exits.forEach(ex => {{
                    if (ex.directions && ex.directions.length > 0) {{
                        const dir = ex.directions[0]; // Just use the first alias
                        const dest = ex.destination;
                        const destName = mapData[dest] ? mapData[dest].name : 'Unknown';
                        
                        const btn = document.createElement('div');
                        btn.className = 'exit-btn';
                        btn.onclick = () => loadRoom(dest);
                        
                        let html = `${{dir}} &rarr; ${{destName}}`;
                        if (ex.condition !== 'n') {{
                            html += `<span class="exit-condition">Requires: ${{ex.condition}}</span>`;
                        }}
                        btn.innerHTML = html;
                        exitsEl.appendChild(btn);
                    }}
                }});
            }} else {{
                exitsEl.innerHTML = '<span style="color: var(--text-muted)">No obvious exits.</span>';
            }}
            
            drawMiniMap(roomId);
        }}
        
        function drawMiniMap(centerId) {{
            const container = document.getElementById('minimap');
            
            let visNodes = [];
            let visEdges = [];
            let addedNodes = new Set();
            let addedEdges = new Set();
            
            // Helper to add node
            const addNode = (id, level) => {{
                if (addedNodes.has(id)) return;
                addedNodes.add(id);
                
                const r = mapData[id];
                const isCenter = (id === centerId);
                
                visNodes.push({{
                    id: id,
                    label: r ? `${{r.name}}\\n[${{id}}]` : `[${{id}}]`,
                    color: isCenter ? {{ background: '#4caf50', border: '#81c784' }} : {{ background: '#2b2b2b', border: '#555555' }},
                    font: {{ color: isCenter ? '#ffffff' : '#eeeeee', multi: true }},
                    shape: 'box'
                }});
            }};
            
            // Add center node
            addNode(centerId, 0);
            
            // Find neighbors (depth 1)
            const room = mapData[centerId];
            if (room && room.exits) {{
                room.exits.forEach(ex => {{
                    const dest = ex.destination;
                    if (ex.directions && ex.directions.length > 0) {{
                        addNode(dest, 1);
                        
                        const edgeId = `${{centerId}}-${{dest}}-${{ex.directions[0]}}`;
                        if (!addedEdges.has(edgeId)) {{
                            addedEdges.add(edgeId);
                            visEdges.push({{
                                from: centerId,
                                to: dest,
                                label: ex.directions[0],
                                arrows: 'to',
                                color: ex.condition === 'n' ? '#888888' : '#ff9800',
                                font: {{size: 10, align: 'middle', color: '#aaaaaa'}}
                            }});
                        }}
                    }}
                }});
            }}
            
            // Find incoming neighbors (nodes that link TO centerId)
            Object.keys(mapData).forEach(id => {{
                const r = mapData[id];
                if (r.exits) {{
                    r.exits.forEach(ex => {{
                        if (ex.destination === centerId && ex.directions && ex.directions.length > 0) {{
                            addNode(id, 1);
                            const edgeId = `${{id}}-${{centerId}}-${{ex.directions[0]}}`;
                            if (!addedEdges.has(edgeId)) {{
                                addedEdges.add(edgeId);
                                visEdges.push({{
                                    from: id,
                                    to: centerId,
                                    label: ex.directions[0],
                                    arrows: 'to',
                                    color: ex.condition === 'n' ? '#555555' : '#ff9800',
                                    font: {{size: 10, align: 'middle', color: '#666666'}},
                                    dashes: true
                                }});
                            }}
                        }}
                    }});
                }}
            }});

            const data = {{
                nodes: new vis.DataSet(visNodes),
                edges: new vis.DataSet(visEdges)
            }};
            
            const options = {{
                physics: {{
                    stabilization: false,
                    barnesHut: {{
                        springLength: 100
                    }}
                }},
                interaction: {{
                    hover: true
                }}
            }};
            
            if (network !== null) {{
                network.destroy();
            }}
            network = new vis.Network(container, data, options);
            
            network.on("click", function (params) {{
                if (params.nodes.length > 0) {{
                    const clickedId = params.nodes[0];
                    if (clickedId !== centerId) {{
                        loadRoom(clickedId);
                    }}
                }}
            }});
        }}
        
        // Init
        initList();
        // Load default start room if exists
        if(mapData['start']) loadRoom('start');
        else loadRoom(Object.keys(mapData)[0]);

    </script>
</body>
</html>
"""
    with open('mud_explorer.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Explorer generated: mud_explorer.html")

if __name__ == "__main__":
    generate_explorer()
