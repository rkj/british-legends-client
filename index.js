document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const terminalScreen = document.getElementById("terminal-screen");
    const cmdInput = document.getElementById("cmd-input");
    const sendCmdBtn = document.getElementById("send-cmd-btn");
    const reconnectBtn = document.getElementById("reconnect-btn");
    const resetAgeVal = document.getElementById("reset-age-val");
    const latencyVal = document.getElementById("latency-val");
    
    const pulseIndicator = document.querySelector(".pulse-indicator");
    
    const statLevel = document.getElementById("stat-level");
    const charNameTitle = document.getElementById("char-name-title");
    const statStamina = document.getElementById("stat-stamina");
    const staminaProgress = document.getElementById("stamina-progress");
    
    // Tell Window DOM
    const tellList = document.getElementById("tell-list");
    const clearTellsBtn = document.getElementById("clear-tells-btn");
    let knownTellsCount = 0;
    

    // Macros DOM
    const macrosGrid = document.getElementById("macros-grid");
    const editMacrosBtn = document.getElementById("edit-macros-btn");
    let isEditingMacros = false;
    
    const onlinePlayersList = document.getElementById("online-players-list");
    const offlinePlayersList = document.getElementById("offline-players-list");
    const countOnline = document.getElementById("count-online");
    const countOffline = document.getElementById("count-offline");
    
    // Snoop elements
    const snoopPanel = document.getElementById("snoop-screen");
    const snoopContent = document.getElementById("snoop-content");
    const snoopResizer = document.getElementById("snoop-resizer");
    const closeSnoopBtn = document.getElementById("close-snoop-btn");
    const snoopTitleText = document.getElementById("snoop-title-text");
    let isSnoopingLine = false;

    // Advanced UI Tracking
    const sleepOverlay = document.getElementById("sleep-overlay");
    const combatHud = document.getElementById("combat-hud");
    const combatLogList = document.getElementById("combat-log-list");

    // State
    
    let commandHistory = [];
    let historyIndex = -1;
    let myName = "";
    let lastLoginPrompt = "";
    let cachedKnownPlayers = [];
    let currentSuggestion = "";
    let latencySamples = [];
    let resetAnchorElapsed = null;  // Server-reported elapsed seconds at anchor time
    let resetAnchorLocal = null;    // performance.now() when we anchored
    const ghostText = document.getElementById("ghost-text");
    let isConnected = false;

    // Smooth 1-second reset age timer using anchored elapsed time
    setInterval(() => {
        if (resetAnchorElapsed === null || !isConnected) return;
        const localDelta = (performance.now() - resetAnchorLocal) / 1000;
        const elapsed = Math.max(0, Math.floor(resetAnchorElapsed + localDelta));
        const h = Math.floor(elapsed / 3600);
        const m = Math.floor((elapsed % 3600) / 60);
        const s = elapsed % 60;
        if (h > 0) {
            resetAgeVal.innerText = `${h}h ${m}m ${s}s`;
        } else {
            resetAgeVal.innerText = `${m}m ${s}s`;
        }
    }, 1000);

    // Helper: HTML Escaper
    function escapeHtml(text) {
        if (!text) return "";
        return text.toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    class SessionLogger {
        constructor() {
            this.fileHandle = null;
            this.isLogging = false;
            this.writeQueue = [];
            this.isWriting = false;
            
            this.logBtn = document.getElementById('log-session-btn');
            this.logIndicator = document.getElementById('log-indicator');
            
            if (this.logBtn) {
                this.logBtn.addEventListener('click', () => this.toggleLogging());
            }
        }

        async toggleLogging() {
            if (this.isLogging) {
                await this.stopLogging();
            } else {
                await this.startLogging();
            }
        }

        async startLogging() {
            try {
                if (!window.showSaveFilePicker) {
                    alert("Your browser doesn't support the File System Access API. Please use a modern browser like Chrome or Edge.");
                    return;
                }
                
                const now = new Date();
                const timestamp = now.getFullYear().toString() + 
                                 (now.getMonth() + 1).toString().padStart(2, '0') + 
                                 now.getDate().toString().padStart(2, '0') + "_" + 
                                 now.getHours().toString().padStart(2, '0') + 
                                 now.getMinutes().toString().padStart(2, '0') + 
                                 now.getSeconds().toString().padStart(2, '0');
                
                const charName = typeof myName !== 'undefined' && myName ? myName : "Log";
                const dynamicSuggestedName = `${timestamp}_BritishLegends_${charName}.txt`;
                
                this.fileHandle = await window.showSaveFilePicker({
                    suggestedName: dynamicSuggestedName,
                    types: [{
                        description: 'Text Files',
                        accept: {'text/plain': ['.txt']}
                    }]
                });
                
                this.isLogging = true;
                
                this.logBtn.innerText = "Stop Logging";
                this.logIndicator.classList.remove('hidden');
                
                // Write a header
                this.logText(`--- Session Log Started: ${new Date().toLocaleString()} ---\n`);
            } catch (error) {
                console.error("Logging cancelled or failed:", error);
                this.isLogging = false;
                this.fileHandle = null;
            }
        }

        async stopLogging() {
            if (this.isLogging) {
                this.logText(`--- Session Log Ended: ${new Date().toLocaleString()} ---\n`);
            }
            
            this.isLogging = false;
            this.fileHandle = null;
            
            this.logBtn.innerText = "Log Session";
            this.logIndicator.classList.add('hidden');
        }

        logText(text) {
            if (!this.isLogging || !this.fileHandle) return;
            
            // Clean text for the file
            let cleanText = text.replace(/<[^>]*>?/gm, '');
            cleanText = cleanText.replace(/\x1b\[[0-9;]*[mK]/g, "");
            cleanText = cleanText.replace(/\r\n/g, "\n").replace(/\n/g, "\r\n"); // Ensure Windows-style newlines for local txt
            
            this.writeQueue.push(cleanText);
            this.processQueue();
        }

        async processQueue() {
            if (this.isWriting || this.writeQueue.length === 0) return;
            this.isWriting = true;
            
            try {
                const textToWrite = this.writeQueue.join("");
                this.writeQueue = [];
                
                const file = await this.fileHandle.getFile();
                const offset = file.size;
                
                const writable = await this.fileHandle.createWritable({keepExistingData: true});
                await writable.write({ type: "write", position: offset, data: textToWrite });
                await writable.close();
            } catch (error) {
                console.error("Error writing to log file:", error);
                // Stop logging if write fails (e.g., file was locked or deleted)
                this.isLogging = false;
                this.fileHandle = null;
                this.logBtn.innerText = "Log Session";
                this.logIndicator.classList.add('hidden');
            } finally {
                this.isWriting = false;
                if (this.writeQueue.length > 0 && this.isLogging) {
                    this.processQueue();
                }
            }
        }
    }

    const sessionLogger = new SessionLogger();

    // Helper: Append text to terminal and scroll
    function appendTerminalText(text) {
        if (!text) return;
        
        // Write to local session log if active
        sessionLogger.logText(text);
        
        // Check if user is scrolled near bottom (within 45px)
        const isNearBottom = terminalScreen.scrollHeight - terminalScreen.scrollTop - terminalScreen.clientHeight < 45;
        const snoopNearBottom = snoopContent.scrollHeight - snoopContent.scrollTop - snoopContent.clientHeight < 45;
        
        // Clean carriage returns
        let formatted = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
        // Strip ANSI escape sequences if any exist
        formatted = formatted.replace(/\x1b\[[0-9;]*[mK]/g, "");

        const lines = formatted.split("\n");
        lines.forEach((line, index) => {
            const isEndOfChunk = (index === lines.length - 1);
            
            // Determine if this line belongs to Snoop feed or Main terminal
            if (!isEndOfChunk || line.length > 0) {
                if (!isSnoopingLine && line.startsWith("|")) {
                    isSnoopingLine = true;
                    line = line.substring(1); // Remove the pipe character itself
                    snoopPanel.classList.add("active"); // Ensure panel is visible
                    snoopResizer.classList.add("active"); // Show the resizer
                }
            }

            const targetScreen = isSnoopingLine ? snoopContent : terminalScreen;

            const lineSpan = document.createElement("span");
            // Only append a newline if it was actually present in the original text chunk
            lineSpan.textContent = line + (!isEndOfChunk ? "\n" : "");
            targetScreen.appendChild(lineSpan);
            
            // If this line piece ended with a newline, reset the snoop tracking for the next line
            if (!isEndOfChunk) {
                isSnoopingLine = false;
            } else if (isSnoopingLine && (line.trim() === "*" || line.trim() === "(----*)")) {
                // BUGFIX: If the snooped player receives a prompt (* without a newline),
                // release the snoop lock so YOUR subsequent output/prompt doesn't get swallowed into the snoop feed!
                isSnoopingLine = false;
            }
        });
        
        // Auto scroll to bottom
        if (isNearBottom || terminalScreen.children.length <= 10) {
            terminalScreen.scrollTop = terminalScreen.scrollHeight;
        }
        if (snoopPanel.classList.contains("active") && (snoopNearBottom || snoopContent.children.length <= 10)) {
            snoopContent.scrollTop = snoopContent.scrollHeight;
        }
    }

    // Send Command to Backend
    async function sendCommand() {
        const command = cmdInput.value.trim();
        if (!command) return;
        
        // Force reset snoop tracking so user input/echo returns to main terminal
        isSnoopingLine = false;
        
        // Remember username or password
        if (lastLoginPrompt === "username") {
            localStorage.setItem("mud_username", command);
            lastLoginPrompt = "";
        } else if (lastLoginPrompt === "password") {
            localStorage.setItem("mud_password", command);
            lastLoginPrompt = "";
        }
        
        // Add to history
        commandHistory.push(command);
        if (commandHistory.length > 100) {
            commandHistory.shift();
        }
        historyIndex = -1;
        
        // Clear input field and ghost text
        cmdInput.value = "";
        ghostText.innerHTML = "";
        currentSuggestion = "";
        
        try {
            const response = await fetch("/command", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ command })
            });
            if (!response.ok) {
                console.error("Failed to send command:", response.statusText);
            }
        } catch (err) {
            console.error("Error sending command:", err);
            appendTerminalText(`\n[System Error: Connection to backend server failed while sending command.]\n`);
        }
    }
    // Reconnect to MUD
    async function reconnectMud() {
        appendTerminalText(`\n[System: Sending reconnect command to MUD server...]\n`);
        try {
            const response = await fetch("/reconnect", { method: "POST" });
            if (response.ok) {
                appendTerminalText(`[System: Reconnect request accepted by server. Reconnecting...]\n`);
            } else {
                appendTerminalText(`[System Error: Reconnect request failed: ${response.statusText}]\n`);
            }
        } catch (err) {
            console.error("Error reconnecting:", err);
            appendTerminalText(`[System Error: Network connection to web server failed during reconnect request.]\n`);
        }
    }

    reconnectBtn.addEventListener("click", reconnectMud);
    sendCmdBtn.addEventListener("click", sendCommand);
    
    if (clearTellsBtn) {
        clearTellsBtn.addEventListener("click", async () => {
            try {
                await fetch("/clear_tells", { method: "POST" });
                tellList.innerHTML = '<li class="empty-list">No tells received yet.</li>';
                knownTellsCount = 0;
            } catch (err) {
                console.error("Error clearing tells:", err);
            }
        });
    }
    
    closeSnoopBtn.addEventListener("click", () => {
        snoopPanel.classList.remove("active");
        snoopResizer.classList.remove("active");
        isSnoopingLine = false;
    });
    
    // Autocomplete: commands that take a player name as argument
    const playerCommands = ['snoop', 'tell', 'follow', 'summon', 'force', 'where', 'vis', 'invis', 'set', 'fod', 'finger', 'bug', 'proof'];

    function getAutocompleteSuggestion(text) {
        if (!text || cachedKnownPlayers.length === 0) return "";
        const parts = text.split(/\s+/);
        if (parts.length < 2) return "";
        const cmd = parts[0].toLowerCase();
        if (!playerCommands.some(pc => pc.startsWith(cmd))) return "";

        // Only autocomplete the last word (the player name fragment)
        const fragment = parts[parts.length - 1].toLowerCase();
        if (!fragment) return "";

        const match = cachedKnownPlayers.find(p =>
            p.toLowerCase().startsWith(fragment) && p.toLowerCase() !== fragment
        );

        if (match) {
            // Return the full line with the completed name
            const prefix = parts.slice(0, -1).join(' ') + ' ';
            return prefix + match;
        }
        return "";
    }

    function updateGhostText() {
        const text = cmdInput.value;
        currentSuggestion = getAutocompleteSuggestion(text);
        if (currentSuggestion) {
            // Split into typed part (transparent) and remaining part (visible)
            // to prevent overlapping character messiness (like lowercase 's' over uppercase 'S')
            const typedLength = text.length;
            const typedPart = currentSuggestion.substring(0, typedLength);
            const remainingPart = currentSuggestion.substring(typedLength);
            
            ghostText.innerHTML = `<span style="opacity: 0;">${escapeHtml(typedPart)}</span>${escapeHtml(remainingPart)}<span class="ghost-hint"> Tab</span>`;
        } else {
            ghostText.innerHTML = "";
        }
    }

    cmdInput.addEventListener("input", () => {
        updateGhostText();
    });

    cmdInput.addEventListener("keydown", (e) => {
        if (e.key === "Tab") {
            // Accept autocomplete suggestion
            if (currentSuggestion) {
                e.preventDefault();
                cmdInput.value = currentSuggestion;
                ghostText.innerHTML = "";
                currentSuggestion = "";
            }
        } else if (e.key === "Enter") {
            sendCommand();
        } else if (e.key === "ArrowUp") {
            // Traverse history backward
            if (commandHistory.length > 0) {
                if (historyIndex === -1) {
                    historyIndex = commandHistory.length - 1;
                } else if (historyIndex > 0) {
                    historyIndex--;
                }
                cmdInput.value = commandHistory[historyIndex];
                ghostText.innerHTML = "";
                currentSuggestion = "";
                setTimeout(() => {
                    cmdInput.setSelectionRange(cmdInput.value.length, cmdInput.value.length);
                }, 0);
            }
            e.preventDefault();
        } else if (e.key === "ArrowDown") {
            // Traverse history forward
            if (historyIndex !== -1) {
                if (historyIndex < commandHistory.length - 1) {
                    historyIndex++;
                    cmdInput.value = commandHistory[historyIndex];
                } else {
                    historyIndex = -1;
                    cmdInput.value = "";
                }
            }
            ghostText.innerHTML = "";
            currentSuggestion = "";
            e.preventDefault();
        } else if (e.key === "Escape") {
            cmdInput.value = "";
            ghostText.innerHTML = "";
            currentSuggestion = "";
            historyIndex = -1;
            e.preventDefault();
        }
    });

    // Make player lists clickable to easily target players
    document.addEventListener("click", (e) => {
        const playerItem = e.target.closest("li");
        if (playerItem && (onlinePlayersList.contains(playerItem) || offlinePlayersList.contains(playerItem))) {
            const nameSpan = playerItem.querySelector(".player-name");
            if (nameSpan) {
                const name = nameSpan.textContent;
                // Add a space after the name to make it easy to type "kill [name] " or just "[name] "
                cmdInput.value += (cmdInput.value && !cmdInput.value.endsWith(" ") ? " " : "") + name + " ";
                cmdInput.focus();
                updateGhostText();
            }
        }
    });
    // -----------------------------------------
    // Resizer Logic for Snoop Panel
    // -----------------------------------------
    let isResizing = false;

    snoopResizer.addEventListener("mousedown", (e) => {
        isResizing = true;
        snoopResizer.classList.add("dragging");
        document.body.style.userSelect = "none";
    });

    document.addEventListener("mousemove", (e) => {
        if (!isResizing) return;
        
        const containerRect = document.querySelector(".screens-container").getBoundingClientRect();
        let newWidth = containerRect.right - e.clientX;
        if (newWidth < 200) newWidth = 200;
        if (newWidth > containerRect.width - 300) newWidth = containerRect.width - 300;

        snoopPanel.style.flex = `0 0 ${newWidth}px`;
    });

    document.addEventListener("mouseup", () => {
        if (isResizing) {
            isResizing = false;
            snoopResizer.classList.remove("dragging");
            document.body.style.userSelect = "";
        }
    });

    // -----------------------------------------
    // Resizer Logic for Sidebar (Tell / Players)
    // -----------------------------------------
    const sidebarResizer = document.getElementById("sidebar-resizer");
    const tellCard = document.getElementById("tell-card");
    const playersCard = document.getElementById("players-card");
    let isSidebarResizing = false;

    sidebarResizer.addEventListener("mousedown", (e) => {
        isSidebarResizing = true;
        sidebarResizer.classList.add("dragging");
        document.body.style.userSelect = "none";
        e.preventDefault();
    });

    document.addEventListener("mousemove", (e) => {
        if (!isSidebarResizing) return;

        const area = document.querySelector(".sidebar-resizable-area");
        const areaRect = area.getBoundingClientRect();
        let tellHeight = e.clientY - areaRect.top;

        // Clamp: min 60px for each card
        const minCard = 60;
        const resizerHeight = 10;
        if (tellHeight < minCard) tellHeight = minCard;
        if (tellHeight > areaRect.height - resizerHeight - minCard) {
            tellHeight = areaRect.height - resizerHeight - minCard;
        }

        tellCard.style.flex = "none";
        tellCard.style.height = tellHeight + "px";
        playersCard.style.flex = "1";
    });

    document.addEventListener("mouseup", () => {
        if (isSidebarResizing) {
            isSidebarResizing = false;
            sidebarResizer.classList.remove("dragging");
            document.body.style.userSelect = "";
        }
    });

    // Update Player List UI Elements
    function updatePlayerLists(online, offline, levels) {
        // Online players
        countOnline.innerText = online.length;
        if (online.length === 0) {
            onlinePlayersList.innerHTML = `<li class="empty-list">No players detected yet. Type 'qu' to see who's online.</li>`;
        } else {
            // Sort case-insensitively
            const sorted = [...online].sort((a, b) => {
                return a.toLowerCase().localeCompare(b.toLowerCase());
            });
            
            onlinePlayersList.innerHTML = sorted.map(player => {
                const isMe = myName && player.toLowerCase() === myName.toLowerCase();
                let badge = '';
                if (isMe) {
                    badge = ' <span class="me-badge">(You)</span>';
                }
                const level = levels[player] ? ` <span class="player-level">[${escapeHtml(levels[player])}]</span>` : '';
                return `<li${isMe ? ' class="is-me"' : ''}><span class="status-dot"></span><span class="player-name">${escapeHtml(player)}</span>${badge}${level}</li>`;
            }).join('');
        }

        // Offline players
        countOffline.innerText = offline.length;
        if (offline.length === 0) {
            offlinePlayersList.innerHTML = `<li class="empty-list">No logged off players recorded yet.</li>`;
        } else {
            offlinePlayersList.innerHTML = offline.map(player => {
                const level = levels[player] ? ` <span class="player-level">[${escapeHtml(levels[player])}]</span>` : '';
                return `<li><span class="status-dot"></span><span class="player-name">${escapeHtml(player)}</span>${level}</li>`;
            }).join('');
        }
    }



    // Main Update Poller
    async function pollUpdates() {
        const startTime = performance.now();
        try {
            const response = await fetch("/updates");
            if (!response.ok) throw new Error(response.statusText);
            
            const data = await response.json();
            
            // Calculate and display rolling average latency
            const endTime = performance.now();
            const rawLatency = Math.round(endTime - startTime);
            
            if (data.is_connected) {
                isConnected = true;
                latencySamples.push(rawLatency);
                if (latencySamples.length > 10) latencySamples.shift(); // Keep last 10 samples
                const avgLatency = Math.round(latencySamples.reduce((a, b) => a + b, 0) / latencySamples.length);
                latencyVal.innerText = `${avgLatency}ms`;
                latencyVal.style.color = "var(--gold-highlight)";
                
                // Connection indicator glows green
                pulseIndicator.className = "pulse-indicator connected";
            } else {
                isConnected = false;
                // Leave latency at the last known value, just dim it
                pulseIndicator.className = "pulse-indicator";
                latencyVal.style.color = "var(--color-text-muted)";
            }
            
            // 1. Terminal screen output
            if (data.mud_output) {
                appendTerminalText(data.mud_output);
                
                // Detect login prompts for auto-fill
                if (data.mud_output.includes("By what name shall I call you?")) {
                    lastLoginPrompt = "username";
                    const savedName = localStorage.getItem("mud_username");
                    if (savedName && !cmdInput.value) {
                        cmdInput.value = savedName;
                    }
                } else if (/password/i.test(data.mud_output)) {
                    lastLoginPrompt = "password";
                    const savedPass = localStorage.getItem("mud_password");
                    if (savedPass && !cmdInput.value) {
                        cmdInput.value = savedPass;
                    }
                }
            }
            

            
            // Snoop Target
            if (data.snoop_target) {
                snoopTitleText.innerText = `SNOOP FEED: ${data.snoop_target}`;
            } else {
                snoopTitleText.innerText = `SNOOP FEED`;
            }
            
            // 4. Reset age - anchor elapsed time from server, tick locally
            if (data.reset_elapsed != null && data.is_connected) {
                if (resetAnchorElapsed === null || data.reset_elapsed < resetAnchorElapsed) {
                    resetAnchorElapsed = data.reset_elapsed;
                    resetAnchorLocal = performance.now();
                }
                const h = Math.floor(data.reset_elapsed / 3600);
                const m = Math.floor((data.reset_elapsed % 3600) / 60);
                const s = data.reset_elapsed % 60;
                resetAgeVal.innerText = `${h > 0 ? h + 'h ' : ''}${m}m ${s}s`;
                resetAgeVal.style.color = "var(--gold-highlight)";
            } else if (data.reset_elapsed === null && data.is_connected) {
                resetAgeVal.innerText = "--m --s";
                resetAnchorElapsed = null;
                resetAgeVal.style.color = "var(--gold-highlight)";
            } else if (!data.is_connected) {
                // Keep the last text value, dim it to show it's paused
                resetAgeVal.style.color = "var(--color-text-muted)";
            }
            // 5. Stats
            if (data.level) {
                statLevel.innerText = data.level;
            }
            if (data.stats) {
                statStamina.innerText = data.stats.stamina;
                
                // Stamina progress bar percentage
                if (data.stats.stamina_max > 0) {
                    const percent = Math.max(0, Math.min(100, Math.round((data.stats.stamina_val / data.stats.stamina_max) * 100)));
                    staminaProgress.style.width = `${percent}%`;
                    
                    // Adjust color gradient based on stamina level
                    if (percent < 25) {
                        staminaProgress.style.background = "linear-gradient(90deg, var(--neon-red), #ff7788)";
                        staminaProgress.style.boxShadow = "0 0 8px rgba(255, 51, 102, 0.6)";
                    } else if (percent < 50) {
                        staminaProgress.style.background = "linear-gradient(90deg, var(--neon-gold), #ffdd66)";
                        staminaProgress.style.boxShadow = "0 0 8px rgba(255, 170, 0, 0.6)";
                    } else {
                        staminaProgress.style.background = "linear-gradient(90deg, var(--neon-green), #99ffaa)";
                        staminaProgress.style.boxShadow = "0 0 8px rgba(0, 255, 102, 0.6)";
                    }
                } else {
                    staminaProgress.style.width = "0%";
                }
            }

            // Tell Window Updates
            if (data.tells && data.tells.length > knownTellsCount) {
                // If this is the first tell, clear the empty list placeholder
                if (knownTellsCount === 0) {
                    tellList.innerHTML = '';
                }
                
                // Append only the new tells
                for (let i = knownTellsCount; i < data.tells.length; i++) {
                    const tell = data.tells[i];
                    const li = document.createElement("li");
                    li.className = "tell-item";
                    
                    if (tell.type === "sent") {
                        li.innerHTML = `<span class="tell-prefix">To ${escapeHtml(tell.to)}:</span> <span class="tell-sent">${escapeHtml(tell.message)}</span>`;
                    } else if (tell.type === "received") {
                        li.innerHTML = `<span class="tell-prefix">From ${escapeHtml(tell.from)}:</span> <span class="tell-received">${escapeHtml(tell.message)}</span>`;
                    }
                    
                    tellList.appendChild(li);
                }
                
                knownTellsCount = data.tells.length;
                
                // Auto-scroll to bottom of tell list
                const tellContainer = tellList.parentElement;
                tellContainer.scrollTop = tellContainer.scrollHeight;
            }


            
            // 6. Player Lists
            if (data.my_name) {
                myName = data.my_name;
            }
            if (!myName) {
                myName = localStorage.getItem("mud_username") || "";
                if (myName) {
                    myName = myName.charAt(0).toUpperCase() + myName.slice(1).toLowerCase();
                }
            }
            if (myName) {
                charNameTitle.innerText = " - " + myName;
            } else {
                charNameTitle.innerText = "";
            }
            cachedKnownPlayers = [...(data.players_online || []), ...(data.players_offline || [])];
            updatePlayerLists(data.players_online || [], data.players_offline || [], data.player_levels || {});
            
            // 7. Advanced Trackers (Sleep & Combat)
            if (data.is_sleeping) {
                sleepOverlay.style.display = "flex";
            } else {
                sleepOverlay.style.display = "none";
            }

            if (data.in_combat) {
                combatHud.style.display = "block";
                if (data.combat_logs && data.combat_logs.length > 0) {
                    combatLogList.innerHTML = data.combat_logs.map(log => `<li>${escapeHtml(log)}</li>`).join('');
                    combatLogList.scrollTop = combatLogList.scrollHeight;
                }
            } else {
                combatHud.style.display = "none";
            }
        } catch (err) {
            console.error("Polling error:", err);
            
            // Only trigger the full disconnected UI state if we were previously connected
            if (pulseIndicator.className !== "pulse-indicator disconnected") {
                pulseIndicator.className = "pulse-indicator disconnected";
                latencyVal.innerText = "offline";
                latencyVal.style.color = "var(--neon-red)";
                
                // Clear UI state
                statStamina.innerText = "--/--";
                staminaProgress.style.width = "0%";
                updatePlayerLists([], [], {});
                
                // Print a visual warning in the terminal
                const sysLine = document.createElement("div");
                sysLine.style.color = "var(--neon-red)";
                sysLine.style.marginTop = "10px";
                sysLine.innerText = "\n[System: Lost connection to local Python backend (web_server.py).]";
                outputDiv.appendChild(sysLine);
                outputDiv.scrollTop = outputDiv.scrollHeight;
            }
        }
    }

    // Macros Logic
    let savedMacros = JSON.parse(localStorage.getItem('mudMacros'));
    let defaultMacros = [
        { label: "Exits", cmd: "exits" }, { label: "S", cmd: "s" }, { label: "Down", cmd: "d" },
        { label: "Score", cmd: "sc" }, { label: "Stats", cmd: "st" }, { label: "Who", cmd: "who" },
        { label: "Smile", cmd: "smile" }, { label: "Flee", cmd: "flee o" }, { label: "Quit", cmd: "quit" },
        { label: "M1", cmd: "" }, { label: "M2", cmd: "" }, { label: "M3", cmd: "" }
    ];
    if (savedMacros) {
        if (savedMacros.length === 18) {
            savedMacros = savedMacros.slice(6);
        }
        for (let i = 0; i < savedMacros.length && i < 12; i++) {
            defaultMacros[i] = savedMacros[i];
        }
    }
    let macros = defaultMacros;

    function renderMacros() {
        macrosGrid.innerHTML = '';
        macros.forEach((macro, index) => {
            const wrapper = document.createElement("div");
            wrapper.className = "macro-btn-wrapper";

            const btn = document.createElement("button");
            btn.className = "macro-btn";
            btn.innerText = macro.label;
            
            // Edit Panel
            const editPanel = document.createElement("div");
            editPanel.className = `macro-edit-panel ${isEditingMacros ? 'active' : ''}`;
            
            const labelInput = document.createElement("input");
            labelInput.type = "text";
            labelInput.value = macro.label;
            labelInput.placeholder = "Label";

            const cmdInput = document.createElement("input");
            cmdInput.type = "text";
            cmdInput.value = macro.cmd;
            cmdInput.placeholder = "Command";

            const saveBtn = document.createElement("button");
            saveBtn.innerText = "Save";

            saveBtn.onclick = () => {
                macros[index].label = labelInput.value.trim() || `Macro ${index+1}`;
                macros[index].cmd = cmdInput.value.trim();
                localStorage.setItem('mudMacros', JSON.stringify(macros));
                renderMacros();
            };

            editPanel.appendChild(labelInput);
            editPanel.appendChild(cmdInput);
            editPanel.appendChild(saveBtn);

            btn.onclick = () => {
                if (!isEditingMacros) {
                    // Send macro command
                    fetch("/command", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ command: macro.cmd })
                    }).catch(err => console.error("Error sending macro:", err));
                }
            };

            wrapper.appendChild(btn);
            wrapper.appendChild(editPanel);
            macrosGrid.appendChild(wrapper);
        });
    }

    editMacrosBtn.addEventListener("click", () => {
        isEditingMacros = !isEditingMacros;
        editMacrosBtn.style.color = isEditingMacros ? "var(--gold-highlight)" : "";
        if (isEditingMacros) {
            macrosGrid.classList.add("editing");
        } else {
            macrosGrid.classList.remove("editing");
        }
        renderMacros();
    });

    // Initial render
    renderMacros();

    // Run first poll instantly, then poll after each response completes
    // Using setTimeout (not setInterval) prevents request pileup when the server is slow
    function startPolling() {
        pollUpdates().finally(() => {
            setTimeout(startPolling, 500);
        });
    }
    // How to Play Guide Modal Logic
    const guideBtn = document.getElementById('guide-btn');
    const guideModalOverlay = document.getElementById('guide-modal-overlay');
    const closeGuideBtn = document.getElementById('close-guide-btn');

    if (guideBtn && guideModalOverlay && closeGuideBtn) {
        guideBtn.addEventListener('click', () => {
            guideModalOverlay.classList.remove('hidden');
        });

        closeGuideBtn.addEventListener('click', () => {
            guideModalOverlay.classList.add('hidden');
        });

        // Click outside to close
        guideModalOverlay.addEventListener('click', (e) => {
            if (e.target === guideModalOverlay) {
                guideModalOverlay.classList.add('hidden');
            }
        });
    }

    // Tips for Players Modal Logic
    const tipsBtn = document.getElementById('tips-btn');
    const tipsModalOverlay = document.getElementById('tips-modal-overlay');
    const closeTipsBtn = document.getElementById('close-tips-btn');

    if (tipsBtn && tipsModalOverlay && closeTipsBtn) {
        tipsBtn.addEventListener('click', () => {
            tipsModalOverlay.classList.remove('hidden');
        });

        closeTipsBtn.addEventListener('click', () => {
            tipsModalOverlay.classList.add('hidden');
        });

        // Click outside to close
        tipsModalOverlay.addEventListener('click', (e) => {
            if (e.target === tipsModalOverlay) {
                tipsModalOverlay.classList.add('hidden');
            }
        });
    }

    // FAQ Modal Logic
    const faqBtn = document.getElementById('faq-btn');
    const faqModalOverlay = document.getElementById('faq-modal-overlay');
    const closeFaqBtn = document.getElementById('close-faq-btn');

    if (faqBtn && faqModalOverlay && closeFaqBtn) {
        faqBtn.addEventListener('click', () => {
            faqModalOverlay.classList.remove('hidden');
        });

        closeFaqBtn.addEventListener('click', () => {
            faqModalOverlay.classList.add('hidden');
        });

        // Click outside to close
        faqModalOverlay.addEventListener('click', (e) => {
            if (e.target === faqModalOverlay) {
                faqModalOverlay.classList.add('hidden');
            }
        });
    }

    // Terms Modal Logic
    const termsBtn = document.getElementById('terms-btn');
    const termsModalOverlay = document.getElementById('terms-modal-overlay');
    const closeTermsBtn = document.getElementById('close-terms-btn');

    if (termsBtn && termsModalOverlay && closeTermsBtn) {
        termsBtn.addEventListener('click', () => {
            termsModalOverlay.classList.remove('hidden');
        });

        closeTermsBtn.addEventListener('click', () => {
            termsModalOverlay.classList.add('hidden');
        });

        // Click outside to close
        termsModalOverlay.addEventListener('click', (e) => {
            if (e.target === termsModalOverlay) {
                termsModalOverlay.classList.add('hidden');
            }
        });
    }

    // Tip Jar Modal Logic
    const tipBtn = document.getElementById('tip-btn');
    const tipModalOverlay = document.getElementById('tip-modal-overlay');
    const closeTipBtn = document.getElementById('close-tip-btn');

    if (tipBtn && tipModalOverlay && closeTipBtn) {
        tipBtn.addEventListener('click', () => {
            tipModalOverlay.classList.remove('hidden');
        });

        closeTipBtn.addEventListener('click', () => {
            tipModalOverlay.classList.add('hidden');
        });

        // Click outside to close
        tipModalOverlay.addEventListener('click', (e) => {
            if (e.target === tipModalOverlay) {
                tipModalOverlay.classList.add('hidden');
            }
        });
    }

    startPolling();
});
