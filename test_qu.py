import socket, time
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('british-legends.com', 27750))
time.sleep(1)
s.recv(4096)
s.sendall(b'Sunset\r\n')
time.sleep(1)
s.recv(4096)
s.sendall(b'XqduDLeDZ\r\n')
time.sleep(1)
res = s.recv(4096).decode('ascii', errors='replace')
if "Eh? Yes or no?" in res or "already" in res:
    s.sendall(b'y\r\n')
    time.sleep(1)
    s.recv(4096)
s.sendall(b'qu\r\n')
time.sleep(2)  # Wait longer to get all qu output
out = b""
s.setblocking(False)
end_time = time.time() + 2
while time.time() < end_time:
    try:
        out += s.recv(4096)
    except:
        time.sleep(0.1)

with open('out.txt', 'w', encoding='utf-8') as f:
    f.write(out.decode('ascii', errors='replace'))
s.sendall(b'qq\r\n')
s.close()
