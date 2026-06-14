class Client:
    def __init__(self, id):
        self.id = id
    def do_thing(self):
        print("doing thing with id", self.id)

client = Client(1)

def change_client():
    global client
    client = Client(2)

def use_client():
    client.do_thing()

use_client()
change_client()
use_client()
