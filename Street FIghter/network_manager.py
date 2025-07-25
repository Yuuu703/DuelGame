import socket
import threading
import pickle
import time
import struct
import json

class NetworkManager:
    def __init__(self, is_host=True, host=None, port=12345):
        self.is_host = is_host
        self.host = host or self.get_local_ip()
        self.port = port
        self.socket = None
        self.connection = None
        self.connected = False
        self.game_data = {}
        self.received_data = {}
        self.running = True
        self.receive_buffer = b''
        self.send_lock = threading.Lock()
        
    def get_local_ip(self):
        """Get the local IP address for LAN connectivity"""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return '127.0.0.1'
    
    def get_available_hosts(self):
        """Scan for available game hosts on LAN"""
        import subprocess
        import re
        
        base_ip = '.'.join(self.get_local_ip().split('.')[:-1]) + '.'
        available_hosts = []
        
        # Quick ping sweep (Windows compatible)
        for i in range(1, 255):
            ip = base_ip + str(i)
            try:
                # Quick socket test instead of ping for game port
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.settimeout(0.1)
                result = test_socket.connect_ex((ip, self.port))
                test_socket.close()
                
                if result == 0:
                    available_hosts.append(ip)
            except:
                continue
                
        return available_hosts
        
    def start_host(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            print(f"Hosting on {self.host}:{self.port}")
            print(f"Other players can connect to: {self.host}")
            
            # Set timeout for accept to allow checking for cancellation
            self.socket.settimeout(1.0)
            
            while self.running:
                try:
                    self.connection, addr = self.socket.accept()
                    print(f"Client connected from {addr}")
                    self.connected = True
                    
                    # Remove timeout for game communication
                    self.connection.settimeout(None)
                    
                    # Start receiving thread
                    receive_thread = threading.Thread(target=self.receive_data)
                    receive_thread.daemon = True
                    receive_thread.start()
                    
                    return True
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"Error accepting connection: {e}")
                    break
                    
        except Exception as e:
            print(f"Error starting host: {e}")
            return False
        
        return False
    
    def connect_to_host(self, host_ip=None):
        if host_ip:
            self.host = host_ip
            
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)  # 5 second timeout for connection
            self.socket.connect((self.host, self.port))
            self.connection = self.socket
            self.connected = True
            print(f"Connected to {self.host}:{self.port}")
            
            # Remove timeout for game communication
            self.socket.settimeout(None)
            
            # Start receiving thread
            receive_thread = threading.Thread(target=self.receive_data)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except Exception as e:
            print(f"Error connecting to host: {e}")
            return False
    
    def send_data(self, data):
        if self.connected and self.connection:
            try:
                with self.send_lock:
                    serialized_data = pickle.dumps(data)
                    # Send size first, then data (message framing)
                    message_size = len(serialized_data)
                    size_bytes = struct.pack('!I', message_size)
                    self.connection.send(size_bytes + serialized_data)
            except Exception as e:
                print(f"Error sending data: {e}")
                self.connected = False
    
    def receive_data(self):
        while self.running and self.connected:
            try:
                # First, get the message size (4 bytes)
                size_data = self._receive_exact(4)
                if not size_data:
                    break
                    
                message_size = struct.unpack('!I', size_data)[0]
                
                # Then receive the exact amount of data
                message_data = self._receive_exact(message_size)
                if not message_data:
                    break
                    
                self.received_data = pickle.loads(message_data)
                
            except Exception as e:
                print(f"Error receiving data: {e}")
                self.connected = False
                break
    
    def _receive_exact(self, size):
        """Receive exactly 'size' bytes from the socket"""
        data = b''
        while len(data) < size:
            chunk = self.connection.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def get_received_data(self):
        return self.received_data
    
    def close(self):
        self.running = False
        self.connected = False
        if self.connection:
            self.connection.close()
        if self.socket:
            self.socket.close()
