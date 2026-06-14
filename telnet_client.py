import socket
import re
import threading
import time

class MUDTelnetClient:
    def __init__(self, host="british-legends.com", port=27750):
        self.host = host
        self.port = port
        self.sock = None
        self.buffer = ""
        self.lock = threading.Lock()
        self.running = False
        self.read_thread = None

    def connect(self):
        """Establish connection to the MUD server."""
        print(f"Connecting to {self.host}:{self.port}...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(None)
        self.running = True
        
        # Start background reader thread
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.read_thread.start()
        print("Connected successfully!")

    def _clean_ansi(self, text):
        """Remove ANSI escape sequences from text."""
        ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
        return ansi_escape.sub('', text)

    def _process_telnet_data(self, data):
        """Parse incoming data, filter out Telnet IAC commands, and decode to text."""
        cleaned_bytes = bytearray()
        i = 0
        n = len(data)
        
        while i < n:
            byte = data[i]
            if byte == 255:  # IAC (Interpret As Command)
                if i + 1 < n:
                    cmd = data[i + 1]
                    if cmd in (251, 252, 253, 254):  # WILL, WONT, DO, DONT
                        # These are 3-byte commands, skip the option byte too
                        i += 3
                    elif cmd == 250:  # SB (Subnegotiation)
                        # Skip until SE (Subnegotiation End, 240)
                        i += 2
                        while i < n and data[i] != 240:
                            i += 1
                        i += 1
                    else:
                        # Other 2-byte commands
                        i += 2
                else:
                    i += 1
            else:
                cleaned_bytes.append(byte)
                i += 1
                
        # Decode bytes to text, ignoring errors
        text = cleaned_bytes.decode('utf-8', errors='ignore')
        # Also clean carriage returns and normalize newlines
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        return self._clean_ansi(text)

    def _read_loop(self):
        """Background thread to read from socket and fill the buffer."""
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data:
                    print("\n[Connection closed by server]")
                    self.running = False
                    break
                
                cleaned_text = self._process_telnet_data(data)
                with self.lock:
                    self.buffer += cleaned_text
            except Exception as e:
                print(f"\n[Read error: {e}]")
                self.running = False
                break

    def read_buffer(self):
        """Retrieve and clear the accumulated text buffer."""
        with self.lock:
            data = self.buffer
            self.buffer = ""
            return data

    def send_command(self, cmd):
        """Send a text command to the MUD."""
        if not self.running or not self.sock:
            raise ConnectionError("Not connected to MUD server.")
        
        # Append CRLF (standard telnet line ending) and send
        full_cmd = (cmd + "\r\n").encode('utf-8')
        with open("telnet_debug.txt", "a", encoding="utf-8") as f:
            f.write(f"SENDING: {repr(full_cmd)}\n")
        self.sock.sendall(full_cmd)

    def close(self):
        """Close connection."""
        self.running = False
        if self.sock:
            self.sock.close()
        print("Connection closed.")

if __name__ == "__main__":
    # Quick manual test to verify connection
    client = MUDTelnetClient()
    client.connect()
    
    try:
        # Give it a moment to show welcome message
        time.sleep(2)
        print("--- Server Output ---")
        print(client.read_buffer())
        print("---------------------")
        
        # Send a blank line to prompt
        client.send_command("")
        time.sleep(1)
        print("--- Server Output after prompt ---")
        print(client.read_buffer())
        print("---------------------")
    finally:
        client.close()
