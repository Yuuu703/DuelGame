import pygame
import sys
import time
import os
from fighter import Fighter
from character_select import CharacterSelect
from network_manager import NetworkManager
from sprite_loader import sprite_loader

pygame.init()

# Game constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Initialize display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Street Fighter Network")
clock = pygame.time.Clock()

class Game:
    def __init__(self):
        self.state = "menu"  # menu, lan_scan, ip_input, local_game, network_host, character_select, waiting, playing
        self.character_select = CharacterSelect(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.network_manager = None
        self.is_host = False
        self.is_network_game = False
        self.fighters = []
        self.background = None
        self.font = pygame.font.Font(None, 48)
        self.menu_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.available_hosts = []
        self.selected_host_index = 0
        self.host_scan_complete = False
        self.manual_ip = ""
        self.input_active = False
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == "menu":
                        if event.key == pygame.K_1:  # Local game
                            self.start_local_game()
                        elif event.key == pygame.K_2:  # Host network game
                            self.start_host()
                        elif event.key == pygame.K_3:  # Join network game
                            self.scan_for_hosts()
                        elif event.key == pygame.K_4:  # Connect to dedicated server
                            self.start_client_mode()
                    elif self.state == "lan_scan":
                        if event.key == pygame.K_UP and self.selected_host_index > 0:
                            self.selected_host_index -= 1
                        elif event.key == pygame.K_DOWN and self.selected_host_index < len(self.available_hosts) - 1:
                            self.selected_host_index += 1
                        elif event.key == pygame.K_RETURN and self.available_hosts:
                            self.join_selected_host()
                        elif event.key == pygame.K_m:  # Manual IP entry
                            self.state = "ip_input"
                            self.input_active = True
                        elif event.key == pygame.K_ESCAPE:
                            self.state = "menu"
                    elif self.state == "ip_input":
                        if event.key == pygame.K_RETURN:
                            self.join_manual_ip()
                        elif event.key == pygame.K_ESCAPE:
                            self.state = "lan_scan"
                        elif event.key == pygame.K_BACKSPACE:
                            self.manual_ip = self.manual_ip[:-1]
                        else:
                            if event.unicode.isprintable():
                                self.manual_ip += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "character_select":
                        self.character_select.handle_click(event.pos)
                        if self.character_select.is_selection_complete():
                            self.start_game()
            
            self.update()
            self.draw()
            clock.tick(FPS)
        
        if self.network_manager:
            self.network_manager.close()
        pygame.quit()
        sys.exit()
    
    def start_local_game(self):
        self.is_network_game = False
        self.state = "character_select"
    
    def start_host(self):
        self.is_host = True
        self.is_network_game = True
        self.network_manager = NetworkManager(is_host=True)
        print(f"Starting host on IP: {self.network_manager.host}")
        
        # Start hosting in a separate thread to avoid blocking UI
        import threading
        host_thread = threading.Thread(target=self._host_game)
        host_thread.daemon = True
        host_thread.start()
        
        self.state = "waiting"
    
    def _host_game(self):
        if self.network_manager.start_host():
            self.state = "character_select"
        else:
            self.state = "menu"
    
    def scan_for_hosts(self):
        self.state = "lan_scan"
        self.host_scan_complete = False
        self.available_hosts = []
        
        # Scan for hosts in a separate thread
        import threading
        scan_thread = threading.Thread(target=self._scan_hosts)
        scan_thread.daemon = True
        scan_thread.start()
    
    def _scan_hosts(self):
        temp_network = NetworkManager(is_host=False)
        self.available_hosts = temp_network.get_available_hosts()
        self.host_scan_complete = True
        print(f"Found {len(self.available_hosts)} available hosts")
    
    def join_selected_host(self):
        if self.available_hosts and self.selected_host_index < len(self.available_hosts):
            selected_ip = self.available_hosts[self.selected_host_index]
            self.join_game(selected_ip)
    
    def join_manual_ip(self):
        if self.manual_ip.strip():
            self.join_game(self.manual_ip.strip())
    
    def join_game(self, host_ip=None):
        self.is_host = False
        self.is_network_game = True
        self.network_manager = NetworkManager(is_host=False)
        
        if self.network_manager.connect_to_host(host_ip):
            self.state = "character_select"
        else:
            self.state = "menu"
    
    def start_client_mode(self):
        # Start the dedicated client
        import subprocess
        import os
        
        try:
            client_path = os.path.join(os.path.dirname(__file__), "client.py")
            subprocess.Popen([sys.executable, client_path])
            print("Started dedicated client")
        except Exception as e:
            print(f"Failed to start client: {e}")
    
    def start_game(self):
        if self.is_network_game and self.network_manager:
            # Send character selection to other player
            selection_data = {
                'characters': self.character_select.selected_chars,
                'background': self.character_select.selected_background
            }
            self.network_manager.send_data(selection_data)
        
        # Create fighters based on selection
        char1 = self.character_select.selected_chars[0]
        char2 = self.character_select.selected_chars[1]
        
        # Load character data and sprites using the new sprite loader
        char1_name = char1['name'] if char1 else 'Kunoichi'
        char2_name = char2['name'] if char2 else 'Lightning Mage'
        
        # Get character configurations
        fighter1_data = sprite_loader.get_character_data(char1_name)
        fighter2_data = sprite_loader.get_character_data(char2_name)
        
        # Load sprite sheets
        sprite_sheet1 = sprite_loader.create_sprite_sheet_from_animations(char1_name)
        sprite_sheet2 = sprite_loader.create_sprite_sheet_from_animations(char2_name)
        
        # Get frame counts for animations
        char1_sprite_data = sprite_loader.load_character_sprites(char1_name)
        char2_sprite_data = sprite_loader.load_character_sprites(char2_name)
        
        animation_steps1 = char1_sprite_data['frame_counts']
        animation_steps2 = char2_sprite_data['frame_counts']
        
        # Get special skills
        char1_skills = sprite_loader.get_character_skills(char1_name)
        char2_skills = sprite_loader.get_character_skills(char2_name)
        
        # Load attack sound (placeholder for now)
        attack_sound = None
        
        # Create fighters with proper sprites and skills
        fighter1 = Fighter(1, 200, 310, False, fighter1_data, sprite_sheet1, 
                          animation_steps1, attack_sound, char1_skills)
        fighter2 = Fighter(2, 700, 310, True, fighter2_data, sprite_sheet2, 
                          animation_steps2, attack_sound, char2_skills)
        
        self.fighters = [fighter1, fighter2]
        
        # Load background
        self.load_background(self.character_select.selected_background)
        
        self.state = "playing"
    
    def load_background(self, bg_name):
        try:
            # Try multiple possible paths for backgrounds
            possible_paths = [
                f"images/background/{bg_name}.png",
                f"images/background/{bg_name}.jpg", 
                f"images/background/{bg_name}",
                f"assets/backgrounds/{bg_name}.png",
                f"assets/backgrounds/{bg_name}.jpg"
            ]
            
            background_loaded = False
            for path in possible_paths:
                if os.path.exists(path):
                    self.background = pygame.image.load(path)
                    self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    background_loaded = True
                    print(f"Loaded background from: {path}")
                    break
            
            if not background_loaded:
                # Create a gradient background as fallback
                self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                for y in range(SCREEN_HEIGHT):
                    color_intensity = int(100 + (y / SCREEN_HEIGHT) * 100)
                    color = (color_intensity, color_intensity + 50, color_intensity + 100)
                    pygame.draw.line(self.background, color, (0, y), (SCREEN_WIDTH, y))
                print("Created gradient background (original files not found)")
                
        except Exception as e:
            print(f"Error loading background: {e}")
            # Fallback to solid color
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill((100, 150, 200))  # Default blue background
    
    def update(self):
        if self.state == "waiting" and self.network_manager and self.network_manager.connected:
            self.state = "character_select"
            
        if self.state == "playing" and self.fighters:
            if self.is_network_game and self.network_manager and self.network_manager.connected:
                # Network game logic with improved synchronization
                local_player = 0 if self.is_host else 1
                remote_player = 1 if self.is_host else 0
                
                # Get local input
                local_input = self.fighters[local_player].get_input_state()
                
                # Create game state data
                game_state = {
                    'type': 'game_state',
                    'input': local_input,
                    'player_data': {
                        'rect': [self.fighters[local_player].rect.x, self.fighters[local_player].rect.y],
                        'health': self.fighters[local_player].health,
                        'action': self.fighters[local_player].action,
                        'frame_index': self.fighters[local_player].frame_index,
                        'vel_y': self.fighters[local_player].vel_y,
                        'alive': self.fighters[local_player].alive,
                        'flip': self.fighters[local_player].flip
                    },
                    'timestamp': time.time()
                }
                
                # Send to other player
                self.network_manager.send_data(game_state)
                
                # Get remote data
                remote_data = self.network_manager.get_received_data()
                remote_input = {}
                
                if remote_data and remote_data.get('type') == 'game_state':
                    remote_input = remote_data.get('input', {})
                    
                    # Update remote player state for better synchronization
                    remote_player_data = remote_data.get('player_data', {})
                    if remote_player_data:
                        # Smooth interpolation for better network feel
                        current_x = self.fighters[remote_player].rect.x
                        target_x = remote_player_data.get('rect', [current_x, 0])[0]
                        
                        # Simple interpolation
                        if abs(target_x - current_x) > 5:  # Only interpolate if difference is significant
                            self.fighters[remote_player].rect.x = int(current_x * 0.8 + target_x * 0.2)
                        
                        # Update other critical state
                        self.fighters[remote_player].health = remote_player_data.get('health', 100)
                        self.fighters[remote_player].alive = remote_player_data.get('alive', True)
                
                # Update fighters with inputs
                self.fighters[local_player].move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, 
                                               self.fighters[remote_player], False, local_input)
                self.fighters[remote_player].move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, 
                                                self.fighters[local_player], False, remote_input)
            else:
                # Local game logic - both players on same machine
                self.fighters[0].move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, self.fighters[1], False)
                self.fighters[1].move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, self.fighters[0], False)
            
            # Update fighter animations
            for fighter in self.fighters:
                fighter.update()
    
    def draw(self):
        if self.state == "menu":
            screen.fill((0, 0, 0))
            title = self.font.render("Street Fighter - LAN Edition", True, (255, 255, 255))
            option1 = self.menu_font.render("1. Local Game (Same PC)", True, (255, 255, 255))
            option2 = self.menu_font.render("2. Host LAN Game", True, (255, 255, 255))
            option3 = self.menu_font.render("3. Join LAN Game", True, (255, 255, 255))
            option4 = self.menu_font.render("4. Connect to Dedicated Server", True, (255, 255, 255))
            
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
            screen.blit(option1, (SCREEN_WIDTH//2 - option1.get_width()//2, 250))
            screen.blit(option2, (SCREEN_WIDTH//2 - option2.get_width()//2, 300))
            screen.blit(option3, (SCREEN_WIDTH//2 - option3.get_width()//2, 350))
            screen.blit(option4, (SCREEN_WIDTH//2 - option4.get_width()//2, 400))
            
        elif self.state == "waiting":
            screen.fill((0, 0, 0))
            if self.is_host and self.network_manager:
                waiting_text = self.font.render("Waiting for player to connect...", True, (255, 255, 255))
                ip_text = self.menu_font.render(f"Your IP: {self.network_manager.host}", True, (0, 255, 0))
                port_text = self.menu_font.render(f"Port: {self.network_manager.port}", True, (0, 255, 0))
                
                screen.blit(waiting_text, (SCREEN_WIDTH//2 - waiting_text.get_width()//2, 250))
                screen.blit(ip_text, (SCREEN_WIDTH//2 - ip_text.get_width()//2, 300))
                screen.blit(port_text, (SCREEN_WIDTH//2 - port_text.get_width()//2, 330))
                
        elif self.state == "lan_scan":
            screen.fill((0, 0, 0))
            title = self.font.render("Available LAN Games", True, (255, 255, 255))
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
            
            if not self.host_scan_complete:
                scanning_text = self.menu_font.render("Scanning for games...", True, (255, 255, 0))
                screen.blit(scanning_text, (SCREEN_WIDTH//2 - scanning_text.get_width()//2, 200))
            else:
                if self.available_hosts:
                    instructions = self.small_font.render("Use UP/DOWN arrows to select, ENTER to join", True, (200, 200, 200))
                    screen.blit(instructions, (SCREEN_WIDTH//2 - instructions.get_width()//2, 150))
                    
                    for i, host_ip in enumerate(self.available_hosts):
                        color = (255, 255, 0) if i == self.selected_host_index else (255, 255, 255)
                        host_text = self.menu_font.render(f"{host_ip}", True, color)
                        y_pos = 200 + i * 40
                        screen.blit(host_text, (SCREEN_WIDTH//2 - host_text.get_width()//2, y_pos))
                else:
                    no_games_text = self.menu_font.render("No games found on LAN", True, (255, 100, 100))
                    screen.blit(no_games_text, (SCREEN_WIDTH//2 - no_games_text.get_width()//2, 200))
                
                manual_text = self.small_font.render("Press M for manual IP entry, ESC to go back", True, (150, 150, 150))
                screen.blit(manual_text, (SCREEN_WIDTH//2 - manual_text.get_width()//2, 450))
                
        elif self.state == "ip_input":
            screen.fill((0, 0, 0))
            title = self.font.render("Enter Host IP Address", True, (255, 255, 255))
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
            
            # Draw input box
            input_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 300, 300, 40)
            pygame.draw.rect(screen, (255, 255, 255), input_rect, 2)
            
            ip_text = self.menu_font.render(self.manual_ip, True, (255, 255, 255))
            screen.blit(ip_text, (input_rect.x + 10, input_rect.y + 10))
            
            instructions = self.small_font.render("Enter IP and press ENTER, or ESC to go back", True, (150, 150, 150))
            screen.blit(instructions, (SCREEN_WIDTH//2 - instructions.get_width()//2, 400))
            
        elif self.state == "character_select":
            self.character_select.draw(screen)
            
        elif self.state == "playing":
            # Draw background
            if self.background:
                screen.blit(self.background, (0, 0))
            
            # Draw fighters
            for fighter in self.fighters:
                fighter.draw(screen)
            
            # Draw UI elements (health bars, special skill cooldowns)
            self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        if not self.fighters:
            return
            
        # Health bars
        pygame.draw.rect(screen, (255, 0, 0), (20, 20, 400, 30))
        pygame.draw.rect(screen, (0, 255, 0), (20, 20, 4 * self.fighters[0].health, 30))
        
        pygame.draw.rect(screen, (255, 0, 0), (SCREEN_WIDTH - 420, 20, 400, 30))
        pygame.draw.rect(screen, (0, 255, 0), (SCREEN_WIDTH - 420, 20, 4 * self.fighters[1].health, 30))
        
        # Player names and controls
        name_font = pygame.font.Font(None, 24)
        control_font = pygame.font.Font(None, 18)
        
        # Player 1 info (left side)
        p1_name = name_font.render("Player 1", True, (255, 255, 255))
        screen.blit(p1_name, (20, 60))
        
        p1_controls = [
            "WASD: Movement", 
            "J/K: Attacks",
            "L/U/I/O: Special Skills"
        ]
        for i, control in enumerate(p1_controls):
            control_text = control_font.render(control, True, (200, 200, 200))
            screen.blit(control_text, (20, 85 + i * 20))
        
        # Player 2 info (right side)
        p2_name = name_font.render("Player 2", True, (255, 255, 255))
        p2_name_rect = p2_name.get_rect()
        p2_name_rect.topright = (SCREEN_WIDTH - 20, 60)
        screen.blit(p2_name, p2_name_rect)
        
        p2_controls = [
            "Arrows: Movement",
            "Num1/2: Attacks", 
            "Num4/5/6/8: Special Skills"
        ]
        for i, control in enumerate(p2_controls):
            control_text = control_font.render(control, True, (200, 200, 200))
            control_rect = control_text.get_rect()
            control_rect.topright = (SCREEN_WIDTH - 20, 85 + i * 20)
            screen.blit(control_text, control_rect)
        
        # Special skill cooldowns with key mappings
        font = pygame.font.Font(None, 20)
        
        # Player 1 special skills (left side)
        if self.fighters[0].special_skills:
            skill_keys = ['L', 'U', 'I', 'O']
            for i, skill in enumerate(self.fighters[0].special_skills[:4]):
                if i < len(skill_keys):
                    cooldown = self.fighters[0].special_cooldowns[i] if i < len(self.fighters[0].special_cooldowns) else 0
                    color = (100, 255, 100) if cooldown == 0 else (255, 100, 100)
                    
                    # Show skill name and key
                    skill_display = f"{skill_keys[i]}: {skill.replace('_', ' ').title()}"
                    cooldown_display = f" ({cooldown//60}s)" if cooldown > 0 else " Ready"
                    
                    skill_text = font.render(skill_display + cooldown_display, True, color)
                    screen.blit(skill_text, (20, 170 + i * 25))
        
        # Player 2 special skills (right side)
        if self.fighters[1].special_skills:
            skill_keys = ['Num4', 'Num5', 'Num6', 'Num8']
            for i, skill in enumerate(self.fighters[1].special_skills[:4]):
                if i < len(skill_keys):
                    cooldown = self.fighters[1].special_cooldowns[i] if i < len(self.fighters[1].special_cooldowns) else 0
                    color = (100, 255, 100) if cooldown == 0 else (255, 100, 100)
                    
                    # Show skill name and key
                    skill_display = f"{skill_keys[i]}: {skill.replace('_', ' ').title()}"
                    cooldown_display = f" ({cooldown//60}s)" if cooldown > 0 else " Ready"
                    
                    skill_text = font.render(skill_display + cooldown_display, True, color)
                    skill_rect = skill_text.get_rect()
                    skill_rect.topright = (SCREEN_WIDTH - 20, 170 + i * 25)
                    screen.blit(skill_text, skill_rect)
        
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()