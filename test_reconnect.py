import socket, time
def test_connect(delay):
    print(f"Testing delay {delay}s...")
    s1 = socket.socket()
    s1.connect(("british-legends.com", 27750))
    time.sleep(0.5)
    print("s1 recv:", len(s1.recv(1024)))
    s1.close()
    
    time.sleep(delay)
    
    s2 = socket.socket()
    s2.connect(("british-legends.com", 27750))
    time.sleep(0.5)
    print("s2 recv:", len(s2.recv(1024)))
    s2.settimeout(3.0)
    try:
        data = s2.recv(1024)
        if not data:
            print("Dropped!")
        else:
            print("Kept alive!")
    except Exception as e:
        print("Exception:", e)
    s2.close()

test_connect(0.5)
test_connect(2.0)
test_connect(5.0)
