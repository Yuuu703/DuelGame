import socket
import threading
import pickle
import pygame
import sys
import random
from fighter import Fighter
from character_select import CharacterSelect

class GameClient:
    def __init__(self, server_host='localhost', server_port=12345):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.player_number = 0
        self.session_id = None
        self.received_data = {}
        self.game_state = 'connecting'  # connecting, waiting, character_select, playing
        self.running = True
        self.my_character = None
        self.opponent_character = None
        
    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            print(f"Connected to server at {self.server_host}:{self.server_port}")
            
            # Start receiving thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            self.game_state = 'waiting'
            return True
            
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    def receive_messages(self):
        while self.running and self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    self.connected = False
                    break
                    
                message = pickle.loads(data)
                self.handle_server_message(message)
                
            except Exception as e:
                if self.running:
                    print(f"Error receiving message: {e}")
                self.connected = False
                break
    
    def handle_server_message(self, message):
        msg_type = message.get('type')
        
        if msg_type == 'match_found':
            self.session_id = message['session_id']
            self.player_number = message['player_number']
            self.game_state = 'character_select'
            print(f"Match found! You are player {self.player_number}")
            
        elif msg_type == 'character_selected':
            # Opponent selected their character
            self.opponent_character = message.get('character')
            print(f"Opponent selected: {self.opponent_character['name']}")
            
        elif msg_type == 'game_start':
            self.received_data['game_start'] = message
            self.game_state = 'playing'
            print("Game starting!")
            
        elif msg_type == 'player_input':
            self.received_data['opponent_input'] = message['input']
            
        elif msg_type == 'sync_state':
            self.received_data['opponent_state'] = message['state']
            
        elif msg_type == 'opponent_disconnected':
            print("Opponent disconnected")
            self.game_state = 'waiting'
    
    def send_character_selection(self, character):
        if self.connected:
            # Add random background selection
            backgrounds = ['forest', 'desert', 'mountain', 'beach', 'city', 'temple']
            random_bg = random.choice(backgrounds)
            
            data = {
                'type': 'character_select',
                'character': character,
                'background': random_bg
            }
            try:
                serialized_data = pickle.dumps(data)
                self.socket.send(serialized_data)
                self.my_character = character
                print(f"Selected character: {character['name']}")
            except Exception as e:
                print(f"Failed to send character selection: {e}")
    
    def send_input(self, input_data):
        if self.connected:
            data = {
                'type': 'input',
                'input': input_data
            }
            try:
                serialized_data = pickle.dumps(data)
                self.socket.send(serialized_data)
            except Exception as e:
                print(f"Failed to send input: {e}")
    
    def send_game_state(self, state_data):
        if self.connected:
            data = {
                'type': 'game_state',
                'state': state_data
            }
            try:
                serialized_data = pickle.dumps(data)
                self.socket.send(serialized_data)
            except Exception as e:
                print(f"Failed to send game state: {e}")
    
    def get_opponent_input(self):
        return self.received_data.get('opponent_input', {})
    
    def get_opponent_state(self):
        return self.received_data.get('opponent_state', {})
    
    def close(self):
        self.running = False
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

class NetworkGame:
    def __init__(self, server_host='localhost', server_port=12345):
        pygame.init()
        self.screen_width = 1000
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Street Fighter Client")
        self.clock = pygame.time.Clock()
        
        self.client = GameClient(server_host, server_port)
        self.character_select = CharacterSelect(self.screen_width, self.screen_height)
        self.character_select.set_network_mode(True)  # Enable network mode
        self.fighters = []
        self.background = None
        self.font = pygame.font.Font(None, 36)
        self.selection_confirmed = False
        
    def run(self):
        if not self.client.connect_to_server():
            print("Failed to connect to server")
            return
            
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.client.game_state == 'character_select':
                        # Handle ENTER key to confirm selection
                        if self.character_select.handle_keypress(event.key) and not self.selection_confirmed:
                            selected_char = self.character_select.get_selected_character()
                            if selected_char:
                                self.client.send_character_selection(selected_char)
                                self.selection_confirmed = True
                                print(f"Character selection confirmed: {selected_char['name']}")
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.client.game_state == 'character_select' and not self.selection_confirmed:
                        self.character_select.handle_click(event.pos)
            
            self.update()
            self.draw()
            self.clock.tick(60)
            
        self.client.close()
        pygame.quit()
        sys.exit()
    
    def handle_character_selection(self, pos):
        # Modified to only allow selecting one character
        cols = 4
        start_x = (self.screen_width - (cols * 120)) // 2
        start_y = 150
        
        for i, char in enumerate(self.character_select.character_portraits):
            x = start_x + (i % cols) * 120
            y = start_y + (i // cols) * 120
            
            if x <= pos[0] <= x + 100 and y <= pos[1] <= y + 100:
                # Select character for this player only
                self.character_select.selected_chars[0] = char
                self.character_select.selected_chars[1] = None  # Clear second selection
                break

    def update(self):
        if self.client.game_state == 'playing':
            if not self.fighters and 'game_start' in self.client.received_data:
                self.setup_game()
            
            if self.fighters:
                # Get local input
                local_fighter = self.fighters[self.client.player_number - 1]
                opponent_fighter = self.fighters[2 - self.client.player_number]
                
                local_input = local_fighter.get_input_state()
                opponent_input = self.client.get_opponent_input()
                
                # Send input to server
                self.client.send_input(local_input)
                
                # Update fighters
                local_fighter.move(self.screen_width, self.screen_height, self.screen,
                                 opponent_fighter, False, local_input)
                opponent_fighter.move(self.screen_width, self.screen_height, self.screen,
                                    local_fighter, False, opponent_input)
                
                # Update animations
                for fighter in self.fighters:
                    fighter.update()
                
                # Send game state
                state_data = {
                    'rect': [local_fighter.rect.x, local_fighter.rect.y],
                    'health': local_fighter.health,
                    'action': local_fighter.action,
                    'frame_index': local_fighter.frame_index,
                    'flip': local_fighter.flip
                }
                self.client.send_game_state(state_data)
    
    def setup_game(self):
        game_data = self.client.received_data['game_start']
        players = game_data['players']
        
        # Create fighters
        fighter1_data = [162, 4, [72, 56]]
        fighter2_data = [162, 4, [72, 56]]
        
        # Create placeholder sprite sheets
        sprite_sheet1 = self.create_placeholder_sprite_sheet()
        sprite_sheet2 = self.create_placeholder_sprite_sheet()
        attack_sound = None
        
        animation_steps = [10, 8, 1, 7, 7, 3, 7, 12, 12]
        
        # Get character data from server
        player1_char = players.get('1', {})
        player2_char = players.get('2', {})
        
        fighter1 = Fighter(1, 200, 310, False, fighter1_data, sprite_sheet1,
                          animation_steps, attack_sound, player1_char.get('special_skills', []))
        fighter2 = Fighter(2, 700, 310, True, fighter2_data, sprite_sheet2,
                          animation_steps, attack_sound, player2_char.get('special_skills', []))
        
        self.fighters = [fighter1, fighter2]
        
        # Load random background
        self.load_random_background()
    
    def create_placeholder_sprite_sheet(self):
        # Create a placeholder sprite sheet with colored rectangles
        sprite_size = 162
        sheet_width = sprite_size * 10
        sheet_height = sprite_size * 9
        
        sprite_sheet = pygame.Surface((sheet_width, sheet_height))
        sprite_sheet.fill((100, 100, 100))  # Gray background
        
        # Add some colored rectangles to represent different animations
        colors = [
            (255, 100, 100),  # Red - idle
            (100, 255, 100),  # Green - run
            (100, 100, 255),  # Blue - jump
            (255, 255, 100),  # Yellow - attack1
            (255, 100, 255),  # Magenta - attack2
            (255, 150, 100),  # Orange - hit
            (150, 150, 150),  # Gray - death
            (255, 200, 100),  # Light orange - special1
            (200, 100, 255),  # Light purple - special2
        ]
        
        for y in range(9):  # 9 animation rows
            color = colors[y] if y < len(colors) else (100, 100, 100)
            for x in range(10):  # 10 frames per animation
                rect = pygame.Rect(x * sprite_size, y * sprite_size, sprite_size, sprite_size)
                pygame.draw.rect(sprite_sheet, color, rect)
                pygame.draw.rect(sprite_sheet, (255, 255, 255), rect, 2)  # White border
        
        return sprite_sheet
    
    def load_random_background(self):
        # Try to load your pixel village background first
        bg_paths = [
            "assets/backgrounds/pixel_village.png",
            "assets/backgrounds/village.png", 
            "assets/backgrounds/background.png"
        ]
        
        for bg_path in bg_paths:
            try:
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
                return
            except:
                continue
        
        # If not found, create pixel village style background
        self.background = self.create_pixel_village_background()
    
    def create_pixel_village_background(self):
        """Create a background similar to your pixel village image"""
        bg = pygame.Surface((self.screen_width, self.screen_height))
        
        # Sky (light blue like your image)
        bg.fill((135, 206, 235))
        
        # Ground
        ground_y = self.screen_height - 120
        pygame.draw.rect(bg, (101, 67, 33), (0, ground_y, self.screen_width, 120))
        
        # Simple pixel art style details
        # House
        pygame.draw.rect(bg, (139, 69, 19), (80, ground_y - 80, 60, 60))
        pygame.draw.polygon(bg, (178, 34, 34), [(80, ground_y - 80), (110, ground_y - 100), (140, ground_y - 80)])
        
        # Trees
        for x in [250, 400, 650]:
            pygame.draw.rect(bg, (101, 67, 33), (x, ground_y - 40, 10, 40))
            pygame.draw.circle(bg, (34, 139, 34), (x + 5, ground_y - 50), 20)
        
        # Simple patterns for visual interest
        for i in range(0, self.screen_width, 100):
            pygame.draw.line(bg, (120, 190, 250), (i, 0), (i, self.screen_height // 3), 1)
        
        return bg

    def draw(self):
        self.screen.fill((0, 0, 0))
        
        if self.client.game_state == 'connecting':
            text = self.font.render("Connecting to server...", True, (255, 255, 255))
            self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, self.screen_height//2))
            
        elif self.client.game_state == 'waiting':
            text = self.font.render("Waiting for opponent...", True, (255, 255, 255))
            self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, self.screen_height//2))
            
        elif self.client.game_state == 'character_select':
            self.draw_character_selection()
            
        elif self.client.game_state == 'playing':
            if self.background:
                self.screen.blit(self.background, (0, 0))
            
            if self.fighters:
                for fighter in self.fighters:
                    fighter.draw(self.screen)
                self.draw_ui()
        
        pygame.display.flip()
    
    def draw_character_selection(self):
        self.screen.fill((20, 20, 40))
        
        # Title
        title = self.font.render(f"SELECT YOUR CHARACTER (Player {self.client.player_number})", True, (255, 255, 255))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 20))
        
        # Status
        if self.selection_confirmed:
            status_text = f"Confirmed: {self.client.my_character['name']}"
            status_color = (0, 255, 0)
        elif self.character_select.get_selected_character():
            status_text = f"Selected: {self.character_select.get_selected_character()['name']} - Press ENTER to confirm"
            status_color = (255, 255, 0)
        else:
            status_text = "Click on a character to select"
            status_color = (255, 255, 255)
        
        status_surface = pygame.font.Font(None, 24).render(status_text, True, status_color)
        self.screen.blit(status_surface, (self.screen_width // 2 - status_surface.get_width() // 2, 50))
        
        # Opponent status
        if self.client.opponent_character:
            opp_text = f"Opponent selected: {self.client.opponent_character['name']}"
            opp_color = (100, 255, 100)
        else:
            opp_text = "Waiting for opponent..."
            opp_color = (200, 200, 200)
        
        opp_surface = pygame.font.Font(None, 24).render(opp_text, True, opp_color)
        self.screen.blit(opp_surface, (self.screen_width // 2 - opp_surface.get_width() // 2, 75))
        
        # Draw character selection interface
        self.character_select.draw_character_selection(self.screen)
        
        # Game start status
        if self.client.my_character and self.client.opponent_character:
            ready_text = "Both players ready! Game will start soon..."
            ready_surface = pygame.font.Font(None, 24).render(ready_text, True, (0, 255, 0))
            self.screen.blit(ready_surface, (self.screen_width // 2 - ready_surface.get_width() // 2, 100))

    def draw_ui(self):
        if not self.fighters:
            return
            
        # Health bars
        pygame.draw.rect(self.screen, (255, 0, 0), (20, 20, 400, 30))
        pygame.draw.rect(self.screen, (0, 255, 0), (20, 20, 4 * self.fighters[0].health, 30))
        
        pygame.draw.rect(self.screen, (255, 0, 0), (self.screen_width - 420, 20, 400, 30))
        pygame.draw.rect(self.screen, (0, 255, 0), (self.screen_width - 420, 20, 4 * self.fighters[1].health, 30))

if __name__ == "__main__":
    server_host = 'localhost'
    server_port = 12345
    
    if len(sys.argv) > 1:
        server_host = sys.argv[1]
    if len(sys.argv) > 2:
        server_port = int(sys.argv[2])
    
    game = NetworkGame(server_host, server_port)
    game.run()
