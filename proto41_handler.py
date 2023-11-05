import struct

class Proto41Handler:
    def register(self, client):
        client.register_handler(0x41, self.handle_proto41)
        
    def validate(self, packet):
        return True
    
    def decapsulate(self, packet):
        pass