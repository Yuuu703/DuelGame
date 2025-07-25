import socket
import threading
import pickle
import time
import json

class GameSession:
    def __init__(self, session_id, player1_conn, player2_conn):
        self.session_id = session_id
        self.players = {
            1: {'conn': player1_conn, 'ready': False, 'character': None, 'input': {}},
            2: {'conn': player2_conn, 'ready': False, 'character': None, 'input': {}}
        }
        self.game_state = {
            'phase': 'character_select',  # character_select, playing, finished
            'background': None,
            'round_over': False,
            'winner': None
        }
        self.running = True
        
    def broadcast_to_players(self, data, exclude_player=None):
        for player_id, player in self.players.items():
            if exclude_player and player_id == exclude_player:
                continue
            try:
                serialized_data = pickle.dumps(data)
                player['conn'].send(serialized_data)
            except:
                print(f"Failed to send data to player {player_id}")
    
    def handle_player_data(self, player_id, data):
        if data['type'] == 'character_select':
            self.players[player_id]['character'] = data['character']
            self.players[player_id]['ready'] = True
            
            # Check if both players are ready
            if all(p['ready'] for p in self.players.values()):
                self.game_state['phase'] = 'playing'
                self.broadcast_to_players({
                    'type': 'game_start',
                    'players': {
                        1: self.players[1]['character'],
                        2: self.players[2]['character']
                    },
                    'background': data.get('background', 'default')
                })
        
        elif data['type'] == 'input':
            self.players[player_id]['input'] = data['input']
            
            # Broadcast input to other player
            other_player = 2 if player_id == 1 else 1
            self.broadcast_to_players({
                'type': 'player_input',
                'player_id': player_id,
                'input': data['input']
            }, exclude_player=player_id)
        
        elif data['type'] == 'game_state':
            # Broadcast game state to other player
            other_player = 2 if player_id == 1 else 1
            self.broadcast_to_players({
                'type': 'sync_state',
                'player_id': player_id,
                'state': data['state']
            }, exclude_player=player_id)

class GameServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = None
        self.clients = {}
        self.waiting_clients = []
        self.game_sessions = {}
        self.session_counter = 0
        self.running = True
        
    def start(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(10)
            print(f"Game server started on {self.host}:{self.port}")
            
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
        client_id = f"{client_address[0]}:{client_address[1]}"
        self.clients[client_id] = {
            'socket': client_socket,
            'address': client_address,
            'session': None
        }
        
        # Add to waiting list for matchmaking
        self.waiting_clients.append(client_id)
        self.try_matchmaking()
        
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
    
    def try_matchmaking(self):
        if len(self.waiting_clients) >= 2:
            player1_id = self.waiting_clients.pop(0)
            player2_id = self.waiting_clients.pop(0)
            
            self.session_counter += 1
            session_id = f"session_{self.session_counter}"
            
            player1_conn = self.clients[player1_id]['socket']
            player2_conn = self.clients[player2_id]['socket']
            
            session = GameSession(session_id, player1_conn, player2_conn)
            self.game_sessions[session_id] = session
            
            # Assign clients to session
            self.clients[player1_id]['session'] = session_id
            self.clients[player2_id]['session'] = session_id
            
            # Notify players about match found
            match_data = {
                'type': 'match_found',
                'session_id': session_id,
                'player_number': 1
            }
            self.send_to_client(player1_id, match_data)
            
            match_data['player_number'] = 2
            self.send_to_client(player2_id, match_data)
            
            print(f"Created game session {session_id} for {player1_id} vs {player2_id}")
    
    def process_client_message(self, client_id, message):
        client = self.clients.get(client_id)
        if not client:
            return
            
        session_id = client['session']
        if not session_id or session_id not in self.game_sessions:
            return
            
        session = self.game_sessions[session_id]
        
        # Determine player number
        player_number = 1 if session.players[1]['conn'] == client['socket'] else 2
        
        session.handle_player_data(player_number, message)
    
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
            session_id = client['session']
            
            # Remove from waiting list
            if client_id in self.waiting_clients:
                self.waiting_clients.remove(client_id)
            
            # Handle session cleanup
            if session_id and session_id in self.game_sessions:
                session = self.game_sessions[session_id]
                session.running = False
                
                # Notify other player
                for player_id, player in session.players.items():
                    if player['conn'] != client['socket']:
                        try:
                            self.send_to_client(client_id, {'type': 'opponent_disconnected'})
                        except:
                            pass
                
                del self.game_sessions[session_id]
            
            # Close socket
            try:
                client['socket'].close()
            except:
                pass
                
            del self.clients[client_id]
            print(f"Client {client_id} disconnected")
    
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
    
    server = GameServer(host, port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.close()
