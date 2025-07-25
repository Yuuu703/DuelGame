import socket
import threading
import pickle
import time
import random
import string

class Room:
    def __init__(self, room_id, room_name, host_conn, room_code=None, max_players=2):
        self.room_id = room_id
        self.room_name = room_name
        self.room_code = room_code or self.generate_room_code()
        self.max_players = max_players
        self.host_conn = host_conn
        self.players = {
            'host': {'conn': host_conn, 'ready': False, 'character': None, 'nickname': 'Host'},
            'guest': {'conn': None, 'ready': False, 'character': None, 'nickname': None}
        }
        self.game_state = {
            'phase': 'waiting',  # waiting, character_select, playing, finished
            'background': None,
            'round_over': False,
            'winner': None
        }
        self.created_time = time.time()
        self.is_private = False
        
    def generate_room_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def add_player(self, conn, nickname):
        if self.players['guest']['conn'] is None:
            self.players['guest']['conn'] = conn
            self.players['guest']['nickname'] = nickname
            return True
        return False
    
    def remove_player(self, conn):
        if self.players['guest']['conn'] == conn:
            self.players['guest'] = {'conn': None, 'ready': False, 'character': None, 'nickname': None}
            return True
        elif self.players['host']['conn'] == conn:
            # Host left, promote guest to host if exists
            if self.players['guest']['conn']:
                self.players['host'] = self.players['guest'].copy()
                self.players['guest'] = {'conn': None, 'ready': False, 'character': None, 'nickname': None}
                self.host_conn = self.players['host']['conn']
                return True
            else:
                return False  # Room should be deleted
        return False
    
    def is_full(self):
        return self.players['guest']['conn'] is not None
    
    def get_player_count(self):
        count = 1 if self.players['host']['conn'] else 0
        count += 1 if self.players['guest']['conn'] else 0
        return count
    
    def broadcast_to_room(self, data, exclude_conn=None):
        for role, player in self.players.items():
            if player['conn'] and player['conn'] != exclude_conn:
                try:
                    serialized_data = pickle.dumps(data)
                    player['conn'].send(serialized_data)
                except Exception as e:
                    print(f"Failed to send data to {role}: {e}")
    
    def get_room_info(self):
        return {
            'room_id': self.room_id,
            'room_name': self.room_name,
            'room_code': self.room_code,
            'host_nickname': self.players['host']['nickname'],
            'player_count': self.get_player_count(),
            'max_players': self.max_players,
            'is_full': self.is_full(),
            'is_private': self.is_private,
            'phase': self.game_state['phase']
        }

class RoomServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = None
        self.clients = {}
        self.rooms = {}
        self.room_counter = 0
        self.running = True
        
    def start(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(20)
            print(f"Room server started on {self.host}:{self.port}")
            
            # Start room cleanup thread
            cleanup_thread = threading.Thread(target=self.cleanup_empty_rooms)
            cleanup_thread.daemon = True
            cleanup_thread.start()
            
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    print(f"New client connected: {client_address}")
                    
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:
                        print(f"Error accepting connection: {e}")
                        
        except Exception as e:
            print(f"Error starting server: {e}")
        finally:
            self.close()
    
    def handle_client(self, client_socket, client_address):
        client_id = f"{client_address[0]}:{client_address[1]}:{time.time()}"
        self.clients[client_id] = {
            'socket': client_socket,
            'address': client_address,
            'room_id': None,
            'nickname': f"Player_{client_id[-4:]}"
        }
        
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                    
                try:
                    message = pickle.loads(data)
                    self.process_client_message(client_id, message)
                except Exception as e:
                    print(f"Error processing message from {client_id}: {e}")
                    
        except Exception as e:
            print(f"Error handling client {client_id}: {e}")
        finally:
            self.disconnect_client(client_id)
    
    def process_client_message(self, client_id, message):
        msg_type = message.get('type')
        client = self.clients.get(client_id)
        
        if not client:
            return
            
        if msg_type == 'set_nickname':
            client['nickname'] = message.get('nickname', client['nickname'])
            self.send_to_client(client_id, {'type': 'nickname_set', 'nickname': client['nickname']})
            
        elif msg_type == 'create_room':
            self.create_room(client_id, message)
            
        elif msg_type == 'join_room':
            self.join_room(client_id, message)
            
        elif msg_type == 'leave_room':
            self.leave_room(client_id)
            
        elif msg_type == 'get_room_list':
            self.send_room_list(client_id)
            
        elif msg_type == 'join_by_code':
            self.join_room_by_code(client_id, message)
            
        elif msg_type == 'room_chat':
            self.handle_room_chat(client_id, message)
            
        elif msg_type == 'character_select':
            self.handle_character_select(client_id, message)
            
        elif msg_type == 'player_ready':
            self.handle_player_ready(client_id, message)
            
        elif msg_type == 'game_input':
            self.handle_game_input(client_id, message)
    
    def create_room(self, client_id, message):
        client = self.clients[client_id]
        
        # Leave current room if in one
        if client['room_id']:
            self.leave_room(client_id)
        
        self.room_counter += 1
        room_id = f"room_{self.room_counter}"
        
        room_name = message.get('room_name', f"{client['nickname']}'s Room")
        room = Room(room_id, room_name, client['socket'])
        room.players['host']['nickname'] = client['nickname']
        room.is_private = message.get('is_private', False)
        
        self.rooms[room_id] = room
        client['room_id'] = room_id
        
        self.send_to_client(client_id, {
            'type': 'room_created',
            'room_info': room.get_room_info(),
            'role': 'host'
        })
        
        print(f"Room {room_id} created by {client['nickname']} (Code: {room.room_code})")
    
    def join_room(self, client_id, message):
        room_id = message.get('room_id')
        client = self.clients[client_id]
        
        if room_id not in self.rooms:
            self.send_to_client(client_id, {'type': 'error', 'message': 'Room not found'})
            return
        
        room = self.rooms[room_id]
        
        if room.is_full():
            self.send_to_client(client_id, {'type': 'error', 'message': 'Room is full'})
            return
        
        # Leave current room if in one
        if client['room_id']:
            self.leave_room(client_id)
        
        if room.add_player(client['socket'], client['nickname']):
            client['room_id'] = room_id
            
            # Notify both players
            room.broadcast_to_room({
                'type': 'player_joined',
                'room_info': room.get_room_info(),
                'players': {
                    'host': room.players['host']['nickname'],
                    'guest': room.players['guest']['nickname']
                }
            })
            
            self.send_to_client(client_id, {
                'type': 'room_joined',
                'room_info': room.get_room_info(),
                'role': 'guest'
            })
            
            print(f"{client['nickname']} joined room {room_id}")
    
    def join_room_by_code(self, client_id, message):
        room_code = message.get('room_code', '').upper()
        
        for room in self.rooms.values():
            if room.room_code == room_code:
                self.join_room(client_id, {'room_id': room.room_id})
                return
        
        self.send_to_client(client_id, {'type': 'error', 'message': 'Invalid room code'})
    
    def leave_room(self, client_id):
        client = self.clients[client_id]
        room_id = client['room_id']
        
        if not room_id or room_id not in self.rooms:
            return
        
        room = self.rooms[room_id]
        
        if room.remove_player(client['socket']):
            client['room_id'] = None
            
            # Notify remaining players
            room.broadcast_to_room({
                'type': 'player_left',
                'room_info': room.get_room_info(),
                'left_player': client['nickname']
            })
            
            print(f"{client['nickname']} left room {room_id}")
        else:
            # Host left and no guest, delete room
            del self.rooms[room_id]
            client['room_id'] = None
            print(f"Room {room_id} deleted (host left)")
    
    def send_room_list(self, client_id):
        room_list = []
        for room in self.rooms.values():
            if not room.is_private and room.game_state['phase'] == 'waiting':
                room_list.append(room.get_room_info())
        
        self.send_to_client(client_id, {
            'type': 'room_list',
            'rooms': room_list
        })
    
    def handle_room_chat(self, client_id, message):
        client = self.clients[client_id]
        room_id = client['room_id']
        
        if room_id and room_id in self.rooms:
            room = self.rooms[room_id]
            chat_data = {
                'type': 'room_chat',
                'sender': client['nickname'],
                'message': message.get('message', ''),
                'timestamp': time.time()
            }
            room.broadcast_to_room(chat_data)
    
    def handle_character_select(self, client_id, message):
        client = self.clients[client_id]
        room_id = client['room_id']
        
        if room_id and room_id in self.rooms:
            room = self.rooms[room_id]
            
            # Find player role
            role = 'host' if room.players['host']['conn'] == client['socket'] else 'guest'
            room.players[role]['character'] = message.get('character')
            
            # Broadcast character selection
            room.broadcast_to_room({
                'type': 'character_selected',
                'role': role,
                'character': message.get('character')
            })
    
    def handle_player_ready(self, client_id, message):
        client = self.clients[client_id]
        room_id = client['room_id']
        
        if room_id and room_id in self.rooms:
            room = self.rooms[room_id]
            
            # Find player role
            role = 'host' if room.players['host']['conn'] == client['socket'] else 'guest'
            room.players[role]['ready'] = message.get('ready', False)
            
            # Check if both players are ready
            if (room.players['host']['ready'] and room.players['guest']['ready'] and
                room.players['host']['character'] and room.players['guest']['character']):
                
                room.game_state['phase'] = 'playing'
                
                # Select a random background for all players
                available_backgrounds = [
                    'Home.jpg', 'Dawn.png', 'Forest.png', 'Jungle.png', 'Jungle2.png',
                    'NightForest.png', 'postapocalypse1.png', 'postapocalypse2.png',
                    'postapocalypse3.png', 'postapocalypse4.png'
                ]
                selected_background = random.choice(available_backgrounds)
                print(f"Server: Selected synchronized background: {selected_background}")
                
                room.broadcast_to_room({
                    'type': 'game_start',
                    'background': selected_background,
                    'players': {
                        'host': room.players['host'],
                        'guest': room.players['guest']
                    }
                })
    
    def handle_game_input(self, client_id, message):
        client = self.clients[client_id]
        room_id = client['room_id']
        
        if room_id and room_id in self.rooms:
            room = self.rooms[room_id]
            
            # Find player role
            role = 'host' if room.players['host']['conn'] == client['socket'] else 'guest'
            
            # Broadcast input to other player
            room.broadcast_to_room({
                'type': 'opponent_input',
                'role': role,
                'input': message.get('input', {}),
                'game_state': message.get('game_state', {})
            }, exclude_conn=client['socket'])
    
    def send_to_client(self, client_id, data):
        client = self.clients.get(client_id)
        if client:
            try:
                serialized_data = pickle.dumps(data)
                client['socket'].send(serialized_data)
            except Exception as e:
                print(f"Failed to send data to {client_id}: {e}")
    
    def disconnect_client(self, client_id):
        if client_id in self.clients:
            client = self.clients[client_id]
            
            # Leave room if in one
            if client['room_id']:
                self.leave_room(client_id)
            
            try:
                client['socket'].close()
            except:
                pass
                
            del self.clients[client_id]
            print(f"Client {client_id} disconnected")
    
    def cleanup_empty_rooms(self):
        while self.running:
            time.sleep(30)  # Check every 30 seconds
            empty_rooms = []
            
            for room_id, room in self.rooms.items():
                if room.get_player_count() == 0:
                    empty_rooms.append(room_id)
                elif time.time() - room.created_time > 3600:  # 1 hour timeout
                    empty_rooms.append(room_id)
            
            for room_id in empty_rooms:
                if room_id in self.rooms:
                    del self.rooms[room_id]
                    print(f"Cleaned up empty room: {room_id}")
    
    def close(self):
        self.running = False
        for client in self.clients.values():
            try:
                client['socket'].close()
            except:
                pass
        if self.socket:
            self.socket.close()

if __name__ == "__main__":
    import sys
    
    host = 'localhost'
    port = 12345
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    server = RoomServer(host, port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.close()
