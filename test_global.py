import threading
l = threading.Lock()
def f():
    with l:
        global x
        x = 5
f()
print(x)
