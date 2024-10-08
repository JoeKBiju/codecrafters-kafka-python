import socket
import threading


class Message:
    def __init__(self, id: int, api_key: int, api_version: int):
        self.supported_api_keys= 2
        self.min_version= 0
        self.max_version= 4
        self.throttle_time = 0
        self.tagged_fields = 0
        self.id = id
        self.api_key = api_key
        self.api_version = api_version
    
    def create_message(self):
        #Header
        response_bytes = self.id.to_bytes(4, 'big')

        #Body
        response_bytes += self.api_version.to_bytes(2, 'big')
        response_bytes += self.supported_api_keys.to_bytes(1, 'big')
        response_bytes += self.api_key.to_bytes(2, 'big')
        response_bytes += self.min_version.to_bytes(2, 'big')
        response_bytes += self.max_version.to_bytes(2, 'big')
        response_bytes += self.tagged_fields.to_bytes(1, 'big')
        response_bytes += self.throttle_time.to_bytes(4, 'big')
        response_bytes += self.tagged_fields.to_bytes(1, 'big')
    
        response_message = len(response_bytes).to_bytes(4, 'big') + response_bytes
        return response_message

def create_message(id: int, api_key: int, api_version: int):
    message = Message(id, api_key, api_version)
    return message.create_message()

def get_request_length(request):
    length = int.from_bytes(request[0:4], 'big')
    return length

def get_api_key(request):
    api_key = int.from_bytes(request[4:6], 'big')
    return api_key

def get_api_version(request):
    api_version = int.from_bytes(request[6:8], 'big')

    if(api_version < 0 or api_version > 4):
        return 35   # Error Code
    
    return 0        # No Error

def parse_correlation(request):
    correlation_id = int.from_bytes(request[8:12], 'big')
    return correlation_id

def handle_client(client_socket):
    while True:
        request = client_socket.recv(1024)
        correlation_id = parse_correlation(request)
        api_key = get_api_key(request)
        api_version = get_api_version(request)
        client_socket.sendall(create_message(correlation_id, api_key, api_version))
        #client_socket.close()

def main():
    server = socket.create_server(("localhost", 9092), reuse_port=True)
    while True:
        client_socket, client_addr = server.accept()
        t = threading.Thread(target=handle_client, args=(client_socket,))
        t.start()

if __name__ == "__main__":
    main()