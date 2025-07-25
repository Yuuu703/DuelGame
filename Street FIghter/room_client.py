import pygame
import socket
import threading
import pickle
import sys
import time
import os
import random
from fighter import Fighter
from character_select import CharacterSelect

class RoomBrowser:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.rooms = []
        self.selected_room = None
        self.scroll_offset = 0
        self.background_image = None
        self.background_loaded = False
        
    def draw(self, screen):
        # Load background image only once
        if not self.background_loaded:
            try:
                # Get the directory of the current script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                bg_path = os.path.join(script_dir, "images", "background", "Home.jpg")
                print(f"RoomBrowser: Script directory: {script_dir}")
                print(f"RoomBrowser: Trying to load: {bg_path}")
                print(f"RoomBrowser: File exists: {os.path.exists(bg_path)}")
                
                if os.path.exists(bg_path):
                    self.background_image = pygame.image.load(bg_path)
                    self.background_image = pygame.transform.scale(self.background_image, (self.screen_width, self.screen_height))
                    print(f"RoomBrowser: Successfully loaded background: {bg_path}")
                else:
                    print(f"RoomBrowser: File does not exist: {bg_path}")
                    self.background_image = self.create_pixel_village_background()
                    print("RoomBrowser: Using fallback background")
            except Exception as e:
                print(f"RoomBrowser: Failed to load Home.jpg: {e}")
                self.background_image = self.create_pixel_village_background()
                print("RoomBrowser: Using fallback background")
            
            self.background_loaded = True
        
        # Draw the cached background
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        
        # Add semi-transparent overlay for better text visibility
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Title with outline for better visibility
        title = self.font.render("Room Browser", True, (255, 255, 255))
        title_outline = self.font.render("Room Browser", True, (0, 0, 0))
        
        # Draw title with outline
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    screen.blit(title_outline, (20 + dx, 20 + dy))
        screen.blit(title, (20, 20))
        
        # Instructions with better styling
        instructions = [
            "Click on a room to join",
            "Press 'C' to create room",
            "Press 'J' to join by code",
            "Press 'R' to refresh",
            "Press 'ESC' to return to menu"
        ]
        
        for i, instruction in enumerate(instructions):
            # Create background for each instruction
            text = self.small_font.render(instruction, True, (255, 255, 255))
            text_bg = pygame.Surface((text.get_width() + 10, text.get_height() + 5))
            text_bg.set_alpha(180)
            text_bg.fill((0, 0, 0))
            
            y_pos = 60 + i * 25
            screen.blit(text_bg, (15, y_pos - 2))
            screen.blit(text, (20, y_pos))
        
        # Room list with better styling
        start_y = 180
        room_height = 60
        visible_rooms = (self.screen_height - start_y - 20) // room_height
        
        for i, room in enumerate(self.rooms[self.scroll_offset:self.scroll_offset + visible_rooms]):
            y = start_y + i * room_height
            
            # Room background with better styling
            room_bg = pygame.Surface((self.screen_width - 40, room_height - 5))
            if room == self.selected_room:
                room_bg.set_alpha(200)
                room_bg.fill((100, 150, 255))  # Highlight color
            else:
                room_bg.set_alpha(180)
                room_bg.fill((60, 60, 80))
            
            screen.blit(room_bg, (20, y))
            
            # Room border
            border_color = (255, 255, 255) if room == self.selected_room else (150, 150, 150)
            pygame.draw.rect(screen, border_color, (20, y, self.screen_width - 40, room_height - 5), 2)
            
            # Room info with outlines for better visibility
            room_text = f"{room['room_name']} ({room['player_count']}/{room['max_players']})"
            host_text = f"Host: {room['host_nickname']}"
            code_text = f"Code: {room['room_code']}"
            
            text_color = (255, 255, 255) if not room['is_full'] else (200, 200, 200)
            
            # Draw text with subtle outlines
            for text, y_offset, color in [(room_text, 5, text_color), (host_text, 25, (200, 200, 200)), (code_text, 40, (150, 200, 255))]:
                text_surface = self.small_font.render(text, True, color)
                text_outline = self.small_font.render(text, True, (0, 0, 0))
                
                # Draw outline
                screen.blit(text_outline, (31, y + y_offset + 1))
                screen.blit(text_outline, (29, y + y_offset + 1))
                screen.blit(text_outline, (30, y + y_offset + 2))
                screen.blit(text_outline, (30, y + y_offset))
                
                # Draw main text
                screen.blit(text_surface, (30, y + y_offset))

    def create_pixel_village_background(self):
        """Create a pixel village background matching the style"""
        bg = pygame.Surface((self.screen_width, self.screen_height))
        
        # Sky gradient
        for y in range(self.screen_height // 2):
            color_intensity = 235 - (y * 30 // (self.screen_height // 2))
            color = (135, 206, max(200, color_intensity))
            pygame.draw.line(bg, color, (0, y), (self.screen_width, y))
        
        # Ground
        ground_y = self.screen_height - 150
        pygame.draw.rect(bg, (101, 67, 33), (0, ground_y, self.screen_width, 150))
        pygame.draw.rect(bg, (34, 139, 34), (0, ground_y, self.screen_width, 20))
        
        # Simple house
        house_x, house_y = 100, ground_y - 120
        pygame.draw.rect(bg, (139, 69, 19), (house_x, house_y, 80, 80))
        pygame.draw.polygon(bg, (178, 34, 34), [(house_x, house_y), (house_x + 40, house_y - 30), (house_x + 80, house_y)])
        
        # Trees
        tree_positions = [(300, ground_y - 40), (500, ground_y - 30), (750, ground_y - 50)]
        for tree_x, tree_y in tree_positions:
            pygame.draw.rect(bg, (101, 67, 33), (tree_x, tree_y, 15, 60))
            pygame.draw.circle(bg, (34, 139, 34), (tree_x + 7, tree_y - 10), 25)
        
        # Clouds
        cloud_positions = [(150, 80), (400, 60), (700, 90)]
        for cloud_x, cloud_y in cloud_positions:
            pygame.draw.circle(bg, (255, 255, 255), (cloud_x, cloud_y), 20)
            pygame.draw.circle(bg, (255, 255, 255), (cloud_x + 20, cloud_y), 25)
            pygame.draw.circle(bg, (255, 255, 255), (cloud_x + 40, cloud_y), 20)
        
        return bg

    def handle_click(self, pos):
        """Handle mouse clicks on room list"""
        start_y = 180
        room_height = 60
        visible_rooms = (self.screen_height - start_y - 20) // room_height
        
        for i, room in enumerate(self.rooms[self.scroll_offset:self.scroll_offset + visible_rooms]):
            y = start_y + i * room_height
            if y <= pos[1] <= y + room_height - 5:
                self.selected_room = room
                return room
        return None

class RoomClient:
    def __init__(self, server_host='localhost', server_port=12345):
        pygame.init()
        self.screen_width = 1000
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Street Fighter - Room System")
        self.clock = pygame.time.Clock()
        
        # Network
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.running = True
        
        # UI
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.room_browser = RoomBrowser(self.screen_width, self.screen_height)
        
        # Initialize character select with error handling
        try:
            self.character_select = CharacterSelect(self.screen_width, self.screen_height)
            print("Character selection initialized successfully")
        except Exception as e:
            print(f"Error initializing character selection: {e}")
            # Create a minimal character select if there's an error
            self.character_select = CharacterSelect(self.screen_width, self.screen_height)
        
        # Game state
        self.state = 'connecting'  # connecting, menu, room_browser, in_room, character_select, playing, local_fight
        self.nickname = f"Player_{int(time.time()) % 10000}"
        self.current_room = None
        self.role = None
        self.chat_messages = []
        self.chat_input = ""
        self.input_active = False
        self.both_players_ready = False
        self.fighters = []
        self.background = None
        
        # Local fighting variables
        self.local_fight_background = None
        self.round_over = False
        self.round_over_time = 0
        
        # Input boxes
        self.room_name_input = ""
        self.room_code_input = ""
        self.nickname_input = self.nickname
        self.input_mode = None  # 'room_name', 'room_code', 'nickname'
        
        # Background caching
        self.menu_background = None
        self.connecting_background = None
        self.dialog_background = None
        self.backgrounds_loaded = False

    def load_backgrounds(self):
        """Load all backgrounds once at startup"""
        if self.backgrounds_loaded:
            return
            
        try:
            # Get the directory of the current script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            bg_path = os.path.join(script_dir, "images", "background", "Home.jpg")
            print(f"Loading backgrounds from: {bg_path}")
            
            if os.path.exists(bg_path):
                bg_image = pygame.image.load(bg_path)
                # Scale once and reuse for all screens
                self.menu_background = pygame.transform.scale(bg_image.copy(), (self.screen_width, self.screen_height))
                self.connecting_background = pygame.transform.scale(bg_image.copy(), (self.screen_width, self.screen_height))
                self.dialog_background = pygame.transform.scale(bg_image.copy(), (self.screen_width, self.screen_height))
                print(f"Successfully loaded Home.jpg background")
            else:
                print(f"Home.jpg not found, using fallback backgrounds")
                self.menu_background = self.create_pixel_village_background()
                self.connecting_background = self.create_pixel_village_background()
                self.dialog_background = self.create_pixel_village_background()
        except Exception as e:
            print(f"Failed to load backgrounds: {e}")
            self.menu_background = self.create_pixel_village_background()
            self.connecting_background = self.create_pixel_village_background()
            self.dialog_background = self.create_pixel_village_background()
        
        self.backgrounds_loaded = True

    def connect_to_server(self):
        try:
            print(f"Attempting to connect to {self.server_host}:{self.server_port}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            print(f"Connected to server at {self.server_host}:{self.server_port}")
            
            # Start receiving thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Set nickname
            self.send_message({'type': 'set_nickname', 'nickname': self.nickname})
            
            self.state = 'menu'
            print(f"State changed to: {self.state}")
            return True
            
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            # If can't connect to server, go directly to menu for testing
            print("Going to menu anyway for testing...")
            self.state = 'menu'
            self.connected = False
            return True  # Return True anyway to allow testing without server
    
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
        
        if msg_type == 'nickname_set':
            self.nickname = message['nickname']
            
        elif msg_type == 'room_created':
            self.current_room = message['room_info']
            self.role = message['role']
            self.state = 'in_room'
            self.chat_messages = []
            
        elif msg_type == 'room_joined':
            self.current_room = message['room_info']
            self.role = message['role']
            self.state = 'in_room'
            self.chat_messages = []
            
        elif msg_type == 'room_list':
            self.room_browser.rooms = message['rooms']
            
        elif msg_type == 'player_joined':
            if self.current_room:
                self.current_room = message['room_info']
                self.chat_messages.append({
                    'sender': 'System',
                    'message': f"Player joined the room",
                    'timestamp': time.time()
                })
                
        elif msg_type == 'player_left':
            if self.current_room:
                self.current_room = message['room_info']
                self.chat_messages.append({
                    'sender': 'System',
                    'message': f"{message['left_player']} left the room",
                    'timestamp': time.time()
                })
                
        elif msg_type == 'room_chat':
            self.chat_messages.append(message)
            
        elif msg_type == 'character_selected':
            # Handle when opponent selects a character
            if self.state == 'character_select' and self.character_select.network_mode:
                opponent_role = message.get('role')
                opponent_char = message.get('character')
                
                if opponent_role != self.role:  # It's the opponent's selection
                    self.character_select.set_opponent_selection(opponent_char)
                    
                    # Check if both players have selected
                    if (self.character_select.is_ready_for_network_play() and 
                        self.character_select.opponent_selection):
                        self.character_select.set_both_players_ready(True)
                        # Send ready signal to server
                        if self.connected:
                            self.send_message({'type': 'player_ready', 'ready': True})
                        
            self.chat_messages.append({
                'sender': 'System',
                'message': f"{message['role']} selected {message['character']['name']}",
                'timestamp': time.time()
            })
            
        elif msg_type == 'game_start':
            # Transition to playing state with synchronized background
            self.setup_game(message)
            self.state = 'playing'
            
        elif msg_type == 'opponent_input':
            if hasattr(self, 'opponent_input'):
                self.opponent_input = message['input']
            
        elif msg_type == 'error':
            print(f"Server error: {message['message']}")
            self.chat_messages.append({
                'sender': 'System',
                'message': f"Error: {message['message']}",
                'timestamp': time.time()
            })

    def send_message(self, message):
        if self.connected:
            try:
                serialized_data = pickle.dumps(message)
                self.socket.send(serialized_data)
            except Exception as e:
                print(f"Failed to send message: {e}")
    
    def run(self):
        # Load backgrounds once before starting
        self.load_backgrounds()
        
        if not self.connect_to_server():
            print("Failed to connect to server")
            return
            
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        self.close()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if self.input_mode:
                    self.handle_text_input(event)
                elif self.state == 'menu':
                    if event.key == pygame.K_1:  # Browse rooms
                        self.state = 'room_browser'
                        self.send_message({'type': 'get_room_list'})
                    elif event.key == pygame.K_2:  # Create room
                        self.input_mode = 'room_name'
                        self.room_name_input = f"{self.nickname}'s Room"
                    elif event.key == pygame.K_3:  # Join by code
                        self.input_mode = 'room_code'
                        self.room_code_input = ""
                    elif event.key == pygame.K_4:  # Local Fight
                        self.character_select.set_network_mode(False)
                        self.character_select.reset_selection()
                        self.state = 'character_select'
                    elif event.key == pygame.K_5:  # Change nickname
                        self.input_mode = 'nickname'
                        self.nickname_input = self.nickname
                        
                elif self.state == 'room_browser':
                    if event.key == pygame.K_c:  # Create room
                        self.input_mode = 'room_name'
                        self.room_name_input = f"{self.nickname}'s Room"
                    elif event.key == pygame.K_j:  # Join by code
                        self.input_mode = 'room_code'
                        self.room_code_input = ""
                    elif event.key == pygame.K_r:  # Refresh
                        self.send_message({'type': 'get_room_list'})
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                        
                elif self.state == 'in_room':
                    if event.key == pygame.K_ESCAPE:
                        self.send_message({'type': 'leave_room'})
                        self.state = 'menu'
                        self.current_room = None
                        self.chat_messages = []
                    elif event.key == pygame.K_RETURN:
                        if self.chat_input.strip():
                            self.send_message({
                                'type': 'room_chat',
                                'message': self.chat_input.strip()
                            })
                            self.chat_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.chat_input = self.chat_input[:-1]
                    elif event.key == pygame.K_SPACE and self.current_room['player_count'] == 2:
                        # Start character selection for network play
                        self.character_select.set_network_mode(True, self.role)
                        self.character_select.reset_selection()
                        self.state = 'character_select'
                    else:
                        if len(self.chat_input) < 100:
                            self.chat_input += event.unicode
                            
                elif self.state == 'character_select':
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'in_room' if self.connected else 'menu'
                    elif event.key == pygame.K_RETURN:
                        # For network play - send character selection when player selects
                        if (self.character_select.network_mode and 
                            self.character_select.is_ready_for_network_play()):
                            char = self.character_select.selected_chars[0]
                            if self.connected:
                                # Send only serializable character data (no pygame surfaces)
                                char_data = {
                                    'name': char['name'],
                                    'special_skills': char.get('special_skills', [])
                                }
                                self.send_message({
                                    'type': 'character_select',
                                    'character': char_data
                                })
                        # Check if selection is complete for local play
                        elif (not self.character_select.network_mode and 
                            self.character_select.is_selection_complete()):
                            self.start_local_fight()
                            
                elif self.state == 'local_fight':
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                        self.cleanup_local_fight()
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == 'menu':
                    # Handle menu button clicks
                    self.handle_menu_click(event.pos)
                elif self.state == 'room_browser':
                    selected_room = self.room_browser.handle_click(event.pos)
                    if selected_room and not selected_room['is_full']:
                        self.send_message({
                            'type': 'join_room',
                            'room_id': selected_room['room_id']
                        })
                elif self.state == 'character_select':
                    self.character_select.handle_click(event.pos)
                    # Check if both characters are selected for local play
                    if (not self.character_select.network_mode and 
                        self.character_select.is_selection_complete()):
                        self.start_local_fight()
                    # For network mode - send selection immediately when character is clicked
                    elif (self.character_select.network_mode and 
                          self.character_select.is_ready_for_network_play()):
                        char = self.character_select.selected_chars[0]
                        if self.connected:
                            # Send only serializable character data (no pygame surfaces)
                            char_data = {
                                'name': char['name'],
                                'special_skills': char.get('special_skills', [])
                            }
                            self.send_message({
                                'type': 'character_select',
                                'character': char_data
                            })
                            # If opponent already selected, send ready signal
                            if self.character_select.opponent_selection:
                                self.character_select.set_both_players_ready(True)
                                self.send_message({'type': 'player_ready', 'ready': True})
    
    def handle_text_input(self, event):
        if event.key == pygame.K_RETURN:
            if self.input_mode == 'room_name' and self.room_name_input.strip():
                self.send_message({
                    'type': 'create_room',
                    'room_name': self.room_name_input.strip(),
                    'is_private': False
                })
                self.input_mode = None
            elif self.input_mode == 'room_code' and self.room_code_input.strip():
                self.send_message({
                    'type': 'join_by_code',
                    'room_code': self.room_code_input.strip().upper()
                })
                self.input_mode = None
            elif self.input_mode == 'nickname' and self.nickname_input.strip():
                self.nickname = self.nickname_input.strip()
                self.send_message({'type': 'set_nickname', 'nickname': self.nickname})
                self.input_mode = None
        elif event.key == pygame.K_ESCAPE:
            self.input_mode = None
        elif event.key == pygame.K_BACKSPACE:
            if self.input_mode == 'room_name':
                self.room_name_input = self.room_name_input[:-1]
            elif self.input_mode == 'room_code':
                self.room_code_input = self.room_code_input[:-1]
            elif self.input_mode == 'nickname':
                self.nickname_input = self.nickname_input[:-1]
        else:
            if self.input_mode == 'room_name' and len(self.room_name_input) < 30:
                self.room_name_input += event.unicode
            elif self.input_mode == 'room_code' and len(self.room_code_input) < 6 and event.unicode.isalnum():
                self.room_code_input += event.unicode.upper()
            elif self.input_mode == 'nickname' and len(self.nickname_input) < 20:
                self.nickname_input += event.unicode

    def handle_menu_click(self, pos):
        """Handle mouse clicks on menu buttons"""
        print(f"Menu click detected at: {pos}")
        # Menu options positions (calculated the same way as in draw_menu)
        options = [
            "1. Browse Rooms",
            "2. Create Room", 
            "3. Join by Code",
            "4. Local Fight",
            "5. Change Nickname"
        ]
        
        for i, option in enumerate(options):
            text = self.font.render(option, True, (255, 255, 255))
            y_pos = 250 + i * 70
            x_pos = self.screen_width//2 - text.get_width()//2
            
            # Check if click is within button bounds
            button_rect = pygame.Rect(x_pos - 20, y_pos - 10, text.get_width() + 40, text.get_height() + 20)
            print(f"Button {i} rect: {button_rect}")
            if button_rect.collidepoint(pos):
                print(f"Button {i} clicked: {option}")
                if i == 0:  # Browse Rooms
                    self.state = 'room_browser'
                    if self.connected:
                        self.send_message({'type': 'get_room_list'})
                elif i == 1:  # Create Room
                    self.input_mode = 'room_name'
                    self.room_name_input = f"{self.nickname}'s Room"
                elif i == 2:  # Join by Code
                    self.input_mode = 'room_code'
                    self.room_code_input = ""
                elif i == 3:  # Local Fight
                    self.character_select.set_network_mode(False)
                    self.character_select.reset_selection()
                    self.state = 'character_select'
                elif i == 4:  # Change Nickname
                    self.input_mode = 'nickname'
                    self.nickname_input = self.nickname
                break

    def start_local_fight(self):
        """Start local fighting mode with selected characters"""
        print("Starting local fight!")
        
        # Set up character selection for network mode to prevent further changes
        self.character_select.set_network_mode(False)
        
        # Get selected characters and background
        char1 = self.character_select.selected_chars[0]
        char2 = self.character_select.selected_chars[1]
        background = self.character_select.get_random_background()
        
        # Load the background for fighting
        self.load_fight_background(background)
        
        # Create fighters with character data
        self.create_local_fighters(char1, char2)
        
        # Switch to fighting state
        self.state = 'local_fight'
        self.round_over = False
        self.round_over_time = 0
        
        print(f"Fight: {char1['name']} vs {char2['name']} on {background['name']}")

    def load_fight_background(self, background):
        """Load the background for fighting"""
        try:
            if background.get('path') and os.path.exists(background['path']):
                self.local_fight_background = pygame.image.load(background['path'])
                self.local_fight_background = pygame.transform.scale(
                    self.local_fight_background, 
                    (self.screen_width, self.screen_height)
                )
                print(f"Loaded fight background: {background['name']}")
            else:
                # Use fallback background
                self.local_fight_background = self.create_pixel_village_background()
                print("Using fallback background for fight")
        except Exception as e:
            print(f"Error loading fight background: {e}")
            self.local_fight_background = self.create_pixel_village_background()

    def create_local_fighters(self, char1, char2):
        """Create fighter objects for local play using exact test game approach"""
        # Exact fighter data from test game
        WARRIOR_SIZE = 162
        WARRIOR_SCALE = 4
        WARRIOR_OFFSET = [72, 56]
        fighter_data = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
        
        # Exact animation steps from test game
        animation_steps = [10, 8, 1, 7, 7, 3, 7]
        
        # Try to load actual character sprites first
        sprite_sheet1 = self.load_character_sprite_sheet(char1['name']) or self.create_placeholder_sprite_sheet((100, 100, 255), animation_steps, fighter_data[0])
        sprite_sheet2 = self.load_character_sprite_sheet(char2['name']) or self.create_placeholder_sprite_sheet((255, 100, 100), animation_steps, fighter_data[0])
        
        # Position fighters exactly like in test game
        fighter1 = Fighter(1, 200, 310, False, fighter_data, sprite_sheet1,
                          animation_steps, None, char1.get('special_skills', []))
        fighter2 = Fighter(2, 700, 310, True, fighter_data, sprite_sheet2,
                          animation_steps, None, char2.get('special_skills', []))
        
        self.fighters = [fighter1, fighter2]
        print(f"Created local fighters: {char1['name']} vs {char2['name']}")
        print(f"Fighter 1 position: ({fighter1.rect.x}, {fighter1.rect.y})")
        print(f"Fighter 2 position: ({fighter2.rect.x}, {fighter2.rect.y})")
        print(f"Using fighter data: {fighter_data}")
        print(f"Using animation steps: {animation_steps}")

    def cleanup_local_fight(self):
        """Clean up local fight resources"""
        self.fighters = []
        self.local_fight_background = None
        self.round_over = False
        self.round_over_time = 0
        self.character_select.reset_selection()

    def update(self):
        # Check for automatic game start in character selection (network mode)
        if (self.state == 'character_select' and 
            self.character_select.network_mode and 
            self.character_select.both_players_ready):
            # Wait a moment before transitioning to show both selections 
            if not hasattr(self, 'ready_time'):
                self.ready_time = time.time()
                print("Both players ready! Starting game in 2 seconds...")
            elif time.time() - self.ready_time > 2:  # Wait 2 seconds
                # Both players ready, transition to game
                print("Transitioning to game state...")
                # Create a mock game start message for local transition
                mock_game_data = {
                    'players': {
                        'host': {'character': self.character_select.selected_chars[0]},
                        'guest': {'character': self.character_select.opponent_selection or self.character_select.selected_chars[0]}
                    }
                }
                self.setup_game(mock_game_data)
                self.state = 'playing'
                # Reset the ready time for next use
                delattr(self, 'ready_time')
        
        if self.state == 'playing' and self.fighters:
            # Network game logic
            # Get local input
            local_fighter = self.fighters[0] if self.role == 'host' else self.fighters[1]
            opponent_fighter = self.fighters[1] if self.role == 'host' else self.fighters[0]
            
            local_input = local_fighter.get_input_state()
            opponent_input = getattr(self, 'opponent_input', {})
            
            # Send input to server
            if self.connected:
                self.send_message({
                    'type': 'game_input',
                    'input': local_input,
                    'game_state': {
                        'rect': [local_fighter.rect.x, local_fighter.rect.y],
                        'health': local_fighter.health,
                        'action': local_fighter.action,
                        'frame_index': local_fighter.frame_index,
                        'flip': local_fighter.flip
                    }
                })
            
            # Update fighters
            local_fighter.move(self.screen_width, self.screen_height, self.screen,
                             opponent_fighter, False, local_input)
            opponent_fighter.move(self.screen_width, self.screen_height, self.screen,
                                local_fighter, False, opponent_input)
            
            # Update animations
            for fighter in self.fighters:
                fighter.update()
                
        elif self.state == 'local_fight' and self.fighters:
            # Local fight logic
            if not self.round_over:
                # Update both fighters
                self.fighters[0].move(self.screen_width, self.screen_height, self.screen,
                                    self.fighters[1], self.round_over)
                self.fighters[1].move(self.screen_width, self.screen_height, self.screen,
                                    self.fighters[0], self.round_over)
                
                # Update animations
                for fighter in self.fighters:
                    fighter.update()
                
                # Check for round over
                if not self.fighters[0].alive or not self.fighters[1].alive:
                    self.round_over = True
                    self.round_over_time = pygame.time.get_ticks()
            
            else:
                # Handle round over state
                if pygame.time.get_ticks() - self.round_over_time > 3000:  # 3 seconds
                    # Reset for next round or return to menu
                    self.state = 'menu'
                    self.cleanup_local_fight()

    def setup_game(self, game_data):
        players = game_data['players']
        
        # Use exact fighter data from test game
        WARRIOR_SIZE = 162
        WARRIOR_SCALE = 4
        WARRIOR_OFFSET = [72, 56]
        fighter_data = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
        
        # Use exact animation steps from test game  
        animation_steps = [10, 8, 1, 7, 7, 3, 7]  # Test game animation steps
        
        host_char = players['host']['character']
        guest_char = players['guest']['character']
        
        # Try to load actual character sprites, fallback to placeholders
        sprite_sheet1 = self.load_character_sprite_sheet(host_char['name']) or self.create_placeholder_sprite_sheet((100, 100, 255), animation_steps, fighter_data[0])
        sprite_sheet2 = self.load_character_sprite_sheet(guest_char['name']) or self.create_placeholder_sprite_sheet((255, 100, 100), animation_steps, fighter_data[0])
        attack_sound = None
        
        # Position fighters like in the test game
        fighter1 = Fighter(1, 200, 310, False, fighter_data, sprite_sheet1,
                          animation_steps, attack_sound, host_char.get('special_skills', []))
        fighter2 = Fighter(2, 700, 310, True, fighter_data, sprite_sheet2,
                          animation_steps, attack_sound, guest_char.get('special_skills', []))
        
        self.fighters = [fighter1, fighter2]
        self.opponent_input = {}
        
        # Load synchronized background from server
        if 'background' in game_data:
            self.load_synchronized_background(game_data['background'])
        else:
            self.load_randomized_background()
        
        print(f"Network game started: {host_char['name']} vs {guest_char['name']}")
        print(f"Background: {game_data.get('background', 'Random')}")
        print(f"Fighter 1 position: ({fighter1.rect.x}, {fighter1.rect.y})")
        print(f"Fighter 2 position: ({fighter2.rect.x}, {fighter2.rect.y})")
        print(f"Using fighter data: {fighter_data}")
        print(f"Using animation steps: {animation_steps}")
    
    def load_character_sprite_sheet(self, character_name):
        """Load actual character sprite sheet exactly like the test game"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Try to load sprite sheet exactly like the test game does
            sprite_path = os.path.join(script_dir, "images", character_name, "Sprites", f"{character_name.lower()}.png")
            print(f"Attempting to load sprite sheet: {sprite_path}")
            
            if os.path.exists(sprite_path):
                sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
                print(f"Successfully loaded sprite sheet for {character_name}: {sprite_sheet.get_size()}")
                return sprite_sheet
            
            # If specific file doesn't exist, try other common names
            sprites_folder = os.path.join(script_dir, "images", character_name, "Sprites")
            if os.path.exists(sprites_folder):
                sprite_files = [f for f in os.listdir(sprites_folder) if f.endswith('.png')]
                print(f"Found sprite files in {character_name}/Sprites: {sprite_files}")
                
                if sprite_files:
                    # Use the first PNG file found
                    sprite_path = os.path.join(sprites_folder, sprite_files[0])
                    sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
                    print(f"Loaded sprite sheet for {character_name}: {sprite_files[0]} (size: {sprite_sheet.get_size()})")
                    return sprite_sheet
            
            # If no Sprites folder, try the main character folder
            char_folder = os.path.join(script_dir, "images", character_name)
            if os.path.exists(char_folder):
                png_files = [f for f in os.listdir(char_folder) if f.endswith('.png')]
                if png_files:
                    # Try to find a file that looks like a sprite sheet (larger file)
                    largest_file = None
                    largest_size = 0
                    
                    for png_file in png_files:
                        file_path = os.path.join(char_folder, png_file)
                        try:
                            img = pygame.image.load(file_path)
                            size = img.get_width() * img.get_height()
                            if size > largest_size:
                                largest_size = size
                                largest_file = png_file
                        except:
                            continue
                    
                    if largest_file:
                        sprite_path = os.path.join(char_folder, largest_file)
                        sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
                        print(f"Loaded largest sprite file for {character_name}: {largest_file} (size: {sprite_sheet.get_size()})")
                        return sprite_sheet
                        
        except Exception as e:
            print(f"Error loading sprite sheet for {character_name}: {e}")
        
        print(f"Failed to load sprites for {character_name}, using placeholder")
        return None
    
    def create_sprite_sheet_from_individual_sprites(self, char_folder, character_name):
        """Create a sprite sheet from individual sprite files"""
        try:
            print(f"Creating sprite sheet from individual sprites for {character_name}")
            
            # Map sprite files to animation rows
            sprite_files = {
                'Idle.png': 0,
                'Run.png': 1, 
                'Jump.png': 2,
                'Attack_1.png': 3,
                'Attack_2.png': 4,
                'Hurt.png': 5,
                'Dead.png': 6,
                'Cast.png': 7,  # Special attack 1
                'Charge.png': 7,  # Alternative special
                'Blade.png': 8,  # Special attack 2
                'Fireball.png': 8,  # Alternative special
                'Walk.png': 1,  # Fallback to run if no run sprite
            }
            
            animation_steps = [10, 8, 1, 7, 7, 3, 7, 12, 12]
            sprite_size = 162
            max_frames = max(animation_steps)
            
            sheet_width = sprite_size * max_frames
            sheet_height = sprite_size * len(animation_steps)
            sprite_sheet = pygame.Surface((sheet_width, sheet_height))
            sprite_sheet.fill((50, 50, 50))  # Dark gray background
            
            # Get list of available files
            available_files = os.listdir(char_folder)
            print(f"Available sprite files: {available_files}")
            
            sprites_loaded = 0
            
            # Load and place individual sprites
            for filename, anim_row in sprite_files.items():
                if filename in available_files:
                    sprite_path = os.path.join(char_folder, filename)
                    try:
                        sprite_img = pygame.image.load(sprite_path)
                        print(f"Loaded {filename} for animation row {anim_row}")
                        
                        # Resize to expected size if needed
                        if sprite_img.get_width() != sprite_size or sprite_img.get_height() != sprite_size:
                            sprite_img = pygame.transform.scale(sprite_img, (sprite_size, sprite_size))
                        
                        # Place the sprite across multiple frames for that animation
                        frames_for_anim = animation_steps[anim_row] if anim_row < len(animation_steps) else 1
                        for frame in range(frames_for_anim):
                            x_pos = frame * sprite_size
                            y_pos = anim_row * sprite_size
                            sprite_sheet.blit(sprite_img, (x_pos, y_pos))
                        
                        sprites_loaded += 1
                        
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
                else:
                    print(f"Sprite file {filename} not found")
            
            if sprites_loaded > 0:
                print(f"Successfully created sprite sheet with {sprites_loaded} different sprites for {character_name}")
                return sprite_sheet
            else:
                print(f"No valid sprite files found, trying fallback method for {character_name}")
                return self.create_fallback_sprite_sheet(char_folder, character_name)
            
        except Exception as e:
            print(f"Error creating sprite sheet from individual sprites for {character_name}: {e}")
            return None
    
    def create_fallback_sprite_sheet(self, char_folder, character_name):
        """Create sprite sheet using any available images as fallback"""
        try:
            available_files = [f for f in os.listdir(char_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
            print(f"Fallback: Found {len(available_files)} image files for {character_name}")
            
            if not available_files:
                return None
            
            animation_steps = [10, 8, 1, 7, 7, 3, 7, 12, 12]
            sprite_size = 162
            max_frames = max(animation_steps)
            
            sheet_width = sprite_size * max_frames
            sheet_height = sprite_size * len(animation_steps)
            sprite_sheet = pygame.Surface((sheet_width, sheet_height))
            sprite_sheet.fill((50, 50, 50))
            
            # Use the first available image for all animations
            first_image_path = os.path.join(char_folder, available_files[0])
            base_sprite = pygame.image.load(first_image_path)
            
            # Handle different source image sizes
            if base_sprite.get_width() > sprite_size * 2 or base_sprite.get_height() > sprite_size * 2:
                # Looks like a sprite sheet, extract first frame
                base_sprite = base_sprite.subsurface(0, 0, min(sprite_size, base_sprite.get_width()), 
                                                   min(sprite_size, base_sprite.get_height()))
            
            base_sprite = pygame.transform.scale(base_sprite, (sprite_size, sprite_size))
            
            # Fill all animation frames with this sprite
            for y in range(len(animation_steps)):
                frames_for_anim = animation_steps[y]
                for x in range(frames_for_anim):
                    sprite_sheet.blit(base_sprite, (x * sprite_size, y * sprite_size))
            
            print(f"Fallback: Created sprite sheet using {available_files[0]} for {character_name}")
            return sprite_sheet
            
        except Exception as e:
            print(f"Error in fallback sprite sheet creation for {character_name}: {e}")
            return None
    
    def load_synchronized_background(self, background_filename):
        """Load the synchronized background specified by the server"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            bg_path = os.path.join(script_dir, "images", "background", background_filename)
            
            if os.path.exists(bg_path):
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
                print(f"Loaded synchronized background: {background_filename}")
                return
                
        except Exception as e:
            print(f"Error loading synchronized background {background_filename}: {e}")
        
        # Fallback to default background
        print("Using fallback background")
        self.background = self.create_pixel_village_background()
    
    def create_placeholder_sprite_sheet(self, base_color=(100, 100, 255), animation_steps=None, sprite_size=162):
        """Create a placeholder sprite sheet matching the test game's exact format"""
        if animation_steps is None:
            animation_steps = [10, 8, 1, 7, 7, 3, 7]  # Exact test game animation steps
        
        max_frames = max(animation_steps)
        num_animations = len(animation_steps)
        
        sheet_width = sprite_size * max_frames
        sheet_height = sprite_size * num_animations
        
        sprite_sheet = pygame.Surface((sheet_width, sheet_height))
        sprite_sheet.fill((50, 50, 50))  # Dark gray background
        
        print(f"Creating placeholder sprite sheet: {sheet_width}x{sheet_height}, base_color: {base_color}")
        print(f"Animation count: {num_animations}, Animation steps: {animation_steps}")
        
        # Colors for each animation type (7 animations like test game)
        colors = [
            base_color,  # Idle
            (base_color[0], min(255, base_color[1] + 50), base_color[2]),  # Run
            (base_color[0], base_color[1], min(255, base_color[2] + 50)),  # Jump
            (min(255, base_color[0] + 50), base_color[1], base_color[2]),  # Attack1
            (min(255, base_color[0] + 80), base_color[1], base_color[2]),  # Attack2
            (max(0, base_color[0] - 50), max(0, base_color[1] - 50), max(0, base_color[2] - 50)),  # Hit
            (80, 20, 20),  # Death
        ]
        
        for y in range(num_animations):
            color = colors[y] if y < len(colors) else base_color
            frames_for_this_animation = animation_steps[y]
            
            for x in range(frames_for_this_animation):
                rect = pygame.Rect(x * sprite_size, y * sprite_size, sprite_size, sprite_size)
                
                # Fill background
                pygame.draw.rect(sprite_sheet, color, rect)
                
                # Draw a better character figure proportional to the sprite size
                center_x = rect.centerx
                center_y = rect.centery
                scale = sprite_size / 162  # Scale relative to standard size
                
                # Character proportions
                head_radius = int(15 * scale)
                body_width = int(25 * scale)
                body_height = int(50 * scale)
                arm_width = int(20 * scale)
                arm_height = int(8 * scale)
                leg_width = int(10 * scale)
                leg_height = int(35 * scale)
                
                # Draw character
                # Head
                head_y = center_y - int(45 * scale)
                pygame.draw.circle(sprite_sheet, (255, 255, 255), (center_x, head_y), head_radius)
                
                # Body
                body_y = center_y - int(20 * scale)
                pygame.draw.rect(sprite_sheet, (255, 255, 255), 
                               (center_x - body_width//2, body_y, body_width, body_height))
                
                # Arms
                arm_y = center_y - int(10 * scale)
                pygame.draw.rect(sprite_sheet, (255, 255, 255), 
                               (center_x - body_width//2 - arm_width, arm_y, arm_width, arm_height))
                pygame.draw.rect(sprite_sheet, (255, 255, 255), 
                               (center_x + body_width//2, arm_y, arm_width, arm_height))
                
                # Legs
                leg_y = center_y + int(30 * scale)
                pygame.draw.rect(sprite_sheet, (255, 255, 255), 
                               (center_x - leg_width - 2, leg_y, leg_width, leg_height))
                pygame.draw.rect(sprite_sheet, (255, 255, 255), 
                               (center_x + 2, leg_y, leg_width, leg_height))
                
                # Border
                pygame.draw.rect(sprite_sheet, (255, 255, 255), rect, 2)
        
        print(f"Created placeholder sprite sheet with {num_animations} animations")
        return sprite_sheet
    
    def load_randomized_background(self):
        """Load a random background from the available backgrounds for network play"""
        
        try:
            # Get the directory of the current script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            bg_folder = os.path.join(script_dir, "images", "background")
            
            if os.path.exists(bg_folder):
                # Get all background files
                bg_files = [f for f in os.listdir(bg_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
                if bg_files:
                    # Select a random background
                    selected_bg = random.choice(bg_files)
                    bg_path = os.path.join(bg_folder, selected_bg)
                    
                    self.background = pygame.image.load(bg_path)
                    self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
                    print(f"Network game: Loaded random background: {selected_bg}")
                    return
                    
        except Exception as e:
            print(f"Error loading random background: {e}")
        
        # If no background found or error, create a pixel-village style background
        print("Network game: Using fallback pixel village background")
        self.background = self.create_pixel_village_background()
    
    def load_pixel_village_background(self):
        """Load your actual Home.jpg background for the game"""
        try:
            # Get the directory of the current script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            bg_path = os.path.join(script_dir, "images", "background", "Home.jpg")
            print(f"Game: Trying to load: {bg_path}")
            if os.path.exists(bg_path):
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
                print(f"Game: Successfully loaded background: {bg_path}")
                return
            else:
                print(f"Game: File does not exist: {bg_path}")
        except Exception as e:
            print(f"Game: Failed to load Home.jpg: {e}")
        
        # If no background found, create a pixel-village style background
        print("Game: Creating fallback pixel village background")
        self.background = self.create_pixel_village_background()

    def draw(self):
        if self.input_mode:
            self.draw_input_dialog()
        elif self.state == 'connecting':
            self.draw_connecting()
        elif self.state == 'menu':
            self.draw_menu()
        elif self.state == 'room_browser':
            self.room_browser.draw(self.screen)  # This line is working correctly
        elif self.state == 'in_room':
            self.draw_room()
        elif self.state == 'character_select':
            self.character_select.draw(self.screen)
        elif self.state == 'playing':
            self.draw_game()
        elif self.state == 'local_fight':
            self.draw_local_fight()
            
        pygame.display.flip()
    
    def draw_menu(self):
        # Use cached background
        if self.menu_background:
            self.screen.blit(self.menu_background, (0, 0))
        
        # Add a semi-transparent overlay for better text readability
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(120)  # Semi-transparent
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Title with better styling
        title = self.font.render("Street Fighter - Room System", True, (255, 255, 255))
        title_outline = self.font.render("Street Fighter - Room System", True, (0, 0, 0))
        
        # Draw title with outline effect
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    self.screen.blit(title_outline, (self.screen_width//2 - title.get_width()//2 + dx, 100 + dy))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 100))
        
        # Nickname with background box
        nickname_text = self.small_font.render(f"Nickname: {self.nickname}", True, (255, 255, 255))
        nickname_bg = pygame.Surface((nickname_text.get_width() + 20, nickname_text.get_height() + 10))
        nickname_bg.set_alpha(180)
        nickname_bg.fill((0, 0, 0))
        
        nickname_x = self.screen_width//2 - nickname_text.get_width()//2
        self.screen.blit(nickname_bg, (nickname_x - 10, 145))
        self.screen.blit(nickname_text, (nickname_x, 150))
        
        # Menu options with styled boxes
        options = [
            "1. Browse Rooms",
            "2. Create Room", 
            "3. Join by Code",
            "4. Local Fight",
            "5. Change Nickname"
        ]
        
        for i, option in enumerate(options):
            text = self.font.render(option, True, (255, 255, 255))
            text_outline = self.font.render(option, True, (0, 0, 0))
            
            # Create background box for each option
            option_bg = pygame.Surface((text.get_width() + 40, text.get_height() + 20))
            option_bg.set_alpha(150)
            option_bg.fill((50, 50, 100))
            
            y_pos = 250 + i * 70
            x_pos = self.screen_width//2 - text.get_width()//2
            
            # Draw option background
            self.screen.blit(option_bg, (x_pos - 20, y_pos - 10))
            
            # Draw border
            pygame.draw.rect(self.screen, (255, 255, 255), (x_pos - 20, y_pos - 10, text.get_width() + 40, text.get_height() + 20), 2)
            
            # Draw text with outline
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        self.screen.blit(text_outline, (x_pos + dx, y_pos + dy))
            self.screen.blit(text, (x_pos, y_pos))

    def draw_connecting(self):
        # Use cached background
        if self.connecting_background:
            self.screen.blit(self.connecting_background, (0, 0))
        
        # Add overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Connecting text with style
        text = self.font.render("Connecting to server...", True, (255, 255, 255))
        text_outline = self.font.render("Connecting to server...", True, (0, 0, 0))
        
        # Create background box
        text_bg = pygame.Surface((text.get_width() + 40, text.get_height() + 20))
        text_bg.set_alpha(180)
        text_bg.fill((0, 0, 0))
        
        x_pos = self.screen_width//2 - text.get_width()//2
        y_pos = self.screen_height//2 - text.get_height()//2
        
        self.screen.blit(text_bg, (x_pos - 20, y_pos - 10))
        pygame.draw.rect(self.screen, (255, 255, 255), (x_pos - 20, y_pos - 10, text.get_width() + 40, text.get_height() + 20), 2)
        
        # Draw text with outline
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    self.screen.blit(text_outline, (x_pos + dx, y_pos + dy))
        self.screen.blit(text, (x_pos, y_pos))

    def draw_input_dialog(self):
        # Use cached background
        if self.dialog_background:
            self.screen.blit(self.dialog_background, (0, 0))
        
        # Dialog rendering code...
        if self.input_mode == 'room_name':
            title = "Create Room"
            prompt = "Enter room name:"
            current_input = self.room_name_input
        elif self.input_mode == 'room_code':
            title = "Join by Code"
            prompt = "Enter 6-digit room code:"
            current_input = self.room_code_input
        elif self.input_mode == 'nickname':
            title = "Change Nickname"
            prompt = "Enter new nickname:"
            current_input = self.nickname_input
        
        # Create styled dialog box
        dialog_width = 500
        dialog_height = 300
        dialog_x = (self.screen_width - dialog_width) // 2
        dialog_y = (self.screen_height - dialog_height) // 2
        
        # Dialog background
        dialog_bg = pygame.Surface((dialog_width, dialog_height))
        dialog_bg.set_alpha(220)
        dialog_bg.fill((40, 40, 80))
        self.screen.blit(dialog_bg, (dialog_x, dialog_y))
        
        # Dialog border
        pygame.draw.rect(self.screen, (255, 255, 255), (dialog_x, dialog_y, dialog_width, dialog_height), 3)
        
        # Title
        title_surface = self.font.render(title, True, (255, 255, 255))
        title_x = dialog_x + (dialog_width - title_surface.get_width()) // 2
        self.screen.blit(title_surface, (title_x, dialog_y + 30))
        
        # Prompt
        prompt_surface = self.small_font.render(prompt, True, (200, 200, 200))
        prompt_x = dialog_x + (dialog_width - prompt_surface.get_width()) // 2
        self.screen.blit(prompt_surface, (prompt_x, dialog_y + 80))
        
        # Input box
        input_rect = pygame.Rect(dialog_x + 50, dialog_y + 120, dialog_width - 100, 40)
        pygame.draw.rect(self.screen, (60, 60, 80), input_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), input_rect, 2)
        
        input_surface = self.font.render(current_input + "_", True, (255, 255, 255))
        self.screen.blit(input_surface, (input_rect.x + 10, input_rect.y + 8))
        
        # Instructions
        instructions = self.small_font.render("Press ENTER to confirm, ESC to cancel", True, (150, 150, 150))
        instructions_x = dialog_x + (dialog_width - instructions.get_width()) // 2
        self.screen.blit(instructions, (instructions_x, dialog_y + 200))

    def draw_room(self):
        self.screen.fill((30, 30, 50))
        
        if not self.current_room:
            return
            
        # Room header
        room_title = f"Room: {self.current_room['room_name']}"
        code_text = f"Code: {self.current_room['room_code']}"
        
        title_surface = self.font.render(room_title, True, (255, 255, 255))
        code_surface = self.small_font.render(code_text, True, (150, 200, 255))
        
        self.screen.blit(title_surface, (20, 20))
        self.screen.blit(code_surface, (20, 60))
        
        # Player info
        players_text = f"Players: {self.current_room['player_count']}/{self.current_room['max_players']}"
        role_text = f"Role: {self.role.capitalize()}"
        
        players_surface = self.small_font.render(players_text, True, (200, 200, 200))
        role_surface = self.small_font.render(role_text, True, (200, 200, 200))
        
        self.screen.blit(players_surface, (20, 100))
        self.screen.blit(role_surface, (20, 120))
        
        # Start game button (if room is full)
        if self.current_room['player_count'] == 2:
            start_text = "Press SPACE to start character selection"
            start_surface = self.small_font.render(start_text, True, (0, 255, 0))
            self.screen.blit(start_surface, (20, 140))
        
        # Chat area
        chat_y = 180
        chat_height = 300
        pygame.draw.rect(self.screen, (40, 40, 60), (20, chat_y, self.screen_width - 40, chat_height))
        
        # Chat messages
        for i, msg in enumerate(self.chat_messages[-10:]):  # Show last 10 messages
            msg_text = f"{msg['sender']}: {msg['message']}"
            msg_surface = self.small_font.render(msg_text, True, (255, 255, 255))
            self.screen.blit(msg_surface, (30, chat_y + 10 + i * 25))
        
        # Chat input
        input_y = chat_y + chat_height + 10
        pygame.draw.rect(self.screen, (60, 60, 80), (20, input_y, self.screen_width - 40, 30))
        
        input_text = f"Chat: {self.chat_input}"
        input_surface = self.small_font.render(input_text, True, (255, 255, 255))
        self.screen.blit(input_surface, (30, input_y + 5))
        
        # Instructions
        instructions = [
            "Enter - Send message",
            "ESC - Leave room"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, (150, 150, 150))
            self.screen.blit(text, (20, self.screen_height - 60 + i * 20))
    
    def draw_game(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((50, 50, 100))  # Blue background if no image
        
        if self.fighters:
            for i, fighter in enumerate(self.fighters):
                # Draw each fighter
                fighter.draw(self.screen)
                
                # Minimal debug info - just show position and health
                info_text = self.small_font.render(f"P{fighter.player}: H{fighter.health}", 
                                                 True, (255, 255, 255))
                # Create background for text
                text_bg = pygame.Surface((info_text.get_width() + 6, info_text.get_height() + 2))
                text_bg.fill((0, 0, 0))
                text_bg.set_alpha(150)
                self.screen.blit(text_bg, (fighter.rect.x - 3, fighter.rect.y - 25))
                self.screen.blit(info_text, (fighter.rect.x, fighter.rect.y - 23))
                
            self.draw_game_ui()
        else:
            # Show a message if no fighters
            text = self.font.render("No fighters loaded", True, (255, 255, 255))
            self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, self.screen_height//2))
    
    def draw_game_ui(self):
        if not self.fighters:
            return
            
        # Health bars
        pygame.draw.rect(self.screen, (255, 0, 0), (20, 20, 400, 30))
        pygame.draw.rect(self.screen, (0, 255, 0), (20, 20, 4 * self.fighters[0].health, 30))
        
        pygame.draw.rect(self.screen, (255, 0, 0), (self.screen_width - 420, 20, 400, 30))
        pygame.draw.rect(self.screen, (0, 255, 0), (self.screen_width - 420, 20, 4 * self.fighters[1].health, 30))

    def draw_local_fight(self):
        # Draw fight background
        if self.local_fight_background:
            self.screen.blit(self.local_fight_background, (0, 0))
        else:
            self.screen.fill((50, 50, 100))
        
        # Draw fighters
        if self.fighters:
            for i, fighter in enumerate(self.fighters):
                # Draw each fighter
                fighter.draw(self.screen)
                
                # Draw debug visualization
                debug_rect = pygame.Rect(fighter.rect.x - 10, fighter.rect.y - 10, 
                                       fighter.rect.width + 20, fighter.rect.height + 20)
                pygame.draw.rect(self.screen, (255, 255, 0), debug_rect, 3)  # Yellow border
                
                # Draw fighter collision rect in red
                pygame.draw.rect(self.screen, (255, 0, 0), fighter.rect, 2)  # Red collision box
                
                # Draw fighter info with background
                info_text = self.small_font.render(f"P{fighter.player}: ({fighter.rect.x}, {fighter.rect.y}) H:{fighter.health}", 
                                                 True, (255, 255, 255))
                # Create background for text
                text_bg = pygame.Surface((info_text.get_width() + 10, info_text.get_height() + 4))
                text_bg.fill((0, 0, 0))
                text_bg.set_alpha(180)
                self.screen.blit(text_bg, (fighter.rect.x - 5, fighter.rect.y - 35))
                self.screen.blit(info_text, (fighter.rect.x, fighter.rect.y - 30))
                
                # Draw a large colored circle to show fighter position
                center_x = fighter.rect.centerx
                center_y = fighter.rect.centery
                color = (0, 100, 255) if fighter.player == 1 else (255, 100, 0)
                pygame.draw.circle(self.screen, color, (center_x, center_y), 30, 3)
            
            # Draw health bars
            self.draw_local_fight_ui()
        
        # Draw round over screen
        if self.round_over:
            self.draw_round_over()

    def draw_local_fight_ui(self):
        if not self.fighters:
            return
        
        # Player 1 health bar (left side)
        pygame.draw.rect(self.screen, (255, 0, 0), (20, 20, 400, 30))
        if self.fighters[0].health > 0:
            pygame.draw.rect(self.screen, (0, 255, 0), (20, 20, 4 * self.fighters[0].health, 30))
        
        # Player 2 health bar (right side)
        pygame.draw.rect(self.screen, (255, 0, 0), (self.screen_width - 420, 20, 400, 30))
        if self.fighters[1].health > 0:
            pygame.draw.rect(self.screen, (0, 255, 0), (self.screen_width - 420, 20, 4 * self.fighters[1].health, 30))
        
        # Player names/controls
        p1_text = self.small_font.render("Player 1 (WASD + JKLUIO)", True, (255, 255, 255))
        self.screen.blit(p1_text, (20, 60))
        
        p2_text = self.small_font.render("Player 2 (Arrows + Numpad)", True, (255, 255, 255))
        p2_rect = p2_text.get_rect()
        p2_rect.topright = (self.screen_width - 20, 60)
        self.screen.blit(p2_text, p2_rect)
        
        # Special skills display
        if self.fighters[0].special_skills:
            skills_text = f"P1 Skills: {', '.join(self.fighters[0].special_skills)}"
            skills_surface = self.small_font.render(skills_text, True, (200, 200, 255))
            self.screen.blit(skills_surface, (20, 80))
            
        if self.fighters[1].special_skills:
            skills_text = f"P2 Skills: {', '.join(self.fighters[1].special_skills)}"
            skills_surface = self.small_font.render(skills_text, True, (255, 200, 200))
            skills_rect = skills_surface.get_rect()
            skills_rect.topright = (self.screen_width - 20, 80)
            self.screen.blit(skills_surface, skills_rect)

    def draw_round_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Determine winner
        if self.fighters[0].alive:
            winner_text = "Player 1 Wins!"
            color = (0, 255, 0)
        elif self.fighters[1].alive:
            winner_text = "Player 2 Wins!"
            color = (0, 255, 0)
        else:
            winner_text = "Draw!"
            color = (255, 255, 0)
        
        # Draw winner text
        winner_surface = self.font.render(winner_text, True, color)
        winner_rect = winner_surface.get_rect(center=(self.screen_width//2, self.screen_height//2))
        self.screen.blit(winner_surface, winner_rect)
        
        # Instructions
        instruction = "Returning to menu in 3 seconds... (ESC to return now)"
        inst_surface = self.small_font.render(instruction, True, (255, 255, 255))
        inst_rect = inst_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 + 50))
        self.screen.blit(inst_surface, inst_rect)

    def close(self):
        self.running = False
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        pygame.quit()

    def create_pixel_village_background(self):
        """Create a pixel village background matching the style"""
        bg = pygame.Surface((self.screen_width, self.screen_height))
        
        # Sky gradient
        for y in range(self.screen_height // 2):
            color_intensity = 235 - (y * 30 // (self.screen_height // 2))
            color = (135, 206, max(200, color_intensity))
            pygame.draw.line(bg, color, (0, y), (self.screen_width, y))
        
        # Ground
        ground_y = self.screen_height - 150
        pygame.draw.rect(bg, (101, 67, 33), (0, ground_y, self.screen_width, 150))
        pygame.draw.rect(bg, (34, 139, 34), (0, ground_y, self.screen_width, 20))
        
        # Simple house
        house_x, house_y = 100, ground_y - 120
        pygame.draw.rect(bg, (139, 69, 19), (house_x, house_y, 80, 80))
        pygame.draw.polygon(bg, (178, 34, 34), [(house_x, house_y), (house_x + 40, house_y - 30), (house_x + 80, house_y)])
        
        # Trees
        tree_positions = [(300, ground_y - 40), (500, ground_y - 30), (750, ground_y - 50)]
        for tree_x, tree_y in tree_positions:
            pygame.draw.rect(bg, (101, 67, 33), (tree_x, tree_y, 15, 60))
            pygame.draw.circle(bg, (34, 139, 34), (tree_x + 7, tree_y - 10), 25)
        
        # Clouds
        cloud_positions = [(150, 80), (400, 60), (700, 90)]
        for cloud_x, cloud_y in cloud_positions:
            pygame.draw.circle(bg, (255, 255, 255), (cloud_x, cloud_y), 20)
            pygame.draw.circle(bg, (255, 255, 255), (cloud_x + 20, cloud_y), 25)
            pygame.draw.circle(bg, (255, 255, 255), (cloud_x + 40, cloud_y), 20)
        
        return bg

if __name__ == "__main__":
    server_host = 'localhost'
    server_port = 12345
    
    if len(sys.argv) > 1:
        server_host = sys.argv[1]
    if len(sys.argv) > 2:
        server_port = int(sys.argv[2])
    
    client = RoomClient(server_host, server_port)
    client.run()
