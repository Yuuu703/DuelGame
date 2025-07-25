import pygame
import os
from sprite_loader import sprite_loader

class CharacterSelect:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.selected_chars = [None, None]  # Player 1, Player 2
        self.selected_background = None
        self.character_portraits = self.load_character_portraits()
        self.backgrounds = self.load_backgrounds()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.selection_phase = "characters"
        self.current_player = 0
        self.network_mode = False  # Set to True for network play
        self.role = None  # 'host' or 'guest' for network play
        self.my_role = None  # Same as role, for consistency
        self.both_players_ready = False
        self.opponent_selection = None  # Store opponent's character selection
        self.background_image = None
        self.background_loaded = False
        
        # Background caching
        self.background_image = None
        self.background_loaded = False
        
    def load_character_portraits(self):
        portraits = []
        portrait_path = "images/"
        loaded_names = []
        
        # Your exact 12 character folder names
        character_folders = [
            'Kunoichi', 'Lightning_Mage', 'Ninja_Monk', 'Ninja_Peasant',
            'Samurai', 'Samurai_Archer', 'Samurai_Commander', 'Samurai_Warrior', 
            'Shinobi', 'Wanderer_Magican', 'warrior', 'wizard'
        ]
        
        # Load portraits from your character folders
        if os.path.exists(portrait_path):
            for folder_name in character_folders:
                folder_path = os.path.join(portrait_path, folder_name)
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    # Look for any image file that could be a portrait
                    portrait_found = False
                    for file in os.listdir(folder_path):
                        if file.endswith(('.png', '.jpg', '.jpeg')):
                            # Try files that might be portraits first
                            if any(word in file.lower() for word in ['portrait', 'face', 'head', 'icon']):
                                try:
                                    img = pygame.image.load(os.path.join(folder_path, file))
                                    img = pygame.transform.scale(img, (100, 100))
                                    
                                    portraits.append({
                                        'image': img,
                                        'name': folder_name,
                                        'special_skills': self.get_character_skills(folder_name)
                                    })
                                    loaded_names.append(folder_name)
                                    portrait_found = True
                                    print(f"Loaded portrait for {folder_name}: {file}")
                                    break
                                except Exception as e:
                                    print(f"Error loading {file}: {e}")
                                    continue
                    
                    # If no portrait found, try the first image in the folder
                    if not portrait_found:
                        for file in os.listdir(folder_path):
                            if file.endswith(('.png', '.jpg', '.jpeg')):
                                try:
                                    img = pygame.image.load(os.path.join(folder_path, file))
                                    # Extract a portion of the sprite sheet as portrait if it's large
                                    if img.get_width() > 200 or img.get_height() > 200:
                                        # Assume it's a sprite sheet, extract top-left portion
                                        portrait_rect = pygame.Rect(0, 0, min(162, img.get_width()), min(162, img.get_height()))
                                        img = img.subsurface(portrait_rect)
                                    
                                    img = pygame.transform.scale(img, (100, 100))
                                    
                                    portraits.append({
                                        'image': img,
                                        'name': folder_name,
                                        'special_skills': self.get_character_skills(folder_name)
                                    })
                                    loaded_names.append(folder_name)
                                    print(f"Loaded sprite as portrait for {folder_name}: {file}")
                                    break
                                except Exception as e:
                                    print(f"Error loading {file}: {e}")
                                    continue
        
        # Create placeholders for any missing characters
        for folder_name in character_folders:
            if folder_name not in loaded_names and len(portraits) < 12:
                placeholder_img = self.create_placeholder_portrait(folder_name)
                portraits.append({
                    'image': placeholder_img,
                    'name': folder_name,
                    'special_skills': self.get_character_skills(folder_name)
                })
                print(f"Created placeholder for {folder_name}")
        
        return portraits[:12]

    def create_placeholder_portrait(self, name):
        # Create a colored placeholder portrait
        img = pygame.Surface((100, 100))
        colors = [
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green
            (100, 100, 255),  # Blue
            (255, 255, 100),  # Yellow
            (255, 100, 255),  # Magenta
            (100, 255, 255),  # Cyan
            (255, 150, 100),  # Orange
            (150, 100, 255),  # Purple
            (200, 100, 100),  # Dark Red
            (100, 200, 100),  # Dark Green
            (100, 100, 200),  # Dark Blue
            (200, 200, 100),  # Dark Yellow
        ]
        color_index = abs(hash(name)) % len(colors)
        img.fill(colors[color_index])
        
        # Add border
        pygame.draw.rect(img, (255, 255, 255), img.get_rect(), 3)
        
        # Add character name (first 3 letters)
        font = pygame.font.Font(None, 24)
        text = font.render(name[:3].upper(), True, (255, 255, 255))
        text_rect = text.get_rect(center=(50, 40))
        img.blit(text, text_rect)
        
        # Add character icon/initial
        icon_font = pygame.font.Font(None, 48)
        icon_text = icon_font.render(name[0].upper(), True, (255, 255, 255))
        icon_rect = icon_text.get_rect(center=(50, 70))
        img.blit(icon_text, icon_rect)
        
        return img
    
    def get_character_skills(self, char_name):
        # Updated to match your exact character names
        special_chars = {
            'kunoichi': ['shadow_strike', 'invisibility'],
            'lightning_mage': ['lightning_bolt', 'chain_lightning'],
            'ninja_monk': ['meditation', 'spirit_punch'],
            'ninja_peasant': ['farm_tools', 'humble_strike'],
            'samurai': ['katana_slash', 'honor_guard'],
            'samurai_archer': ['arrow_rain', 'precision_shot'],
            'samurai_commander': ['battle_cry', 'tactical_strike'],
            'samurai_warrior': ['blade_fury', 'warrior_spirit'],
            'shinobi': ['smoke_bomb', 'shadow_clone'],
            'wanderer_magican': ['magic_missile', 'teleport'],
            'warrior': ['sword_slash', 'shield_bash'],
            'wizard': ['fireball', 'ice_shard']
        }
        return special_chars.get(char_name.lower(), ['basic_attack', 'power_strike'])
    
    def load_backgrounds(self):
        backgrounds = []
        bg_path = "images/background/"
        loaded_backgrounds = []
        
        if os.path.exists(bg_path):
            for file in os.listdir(bg_path):
                if file.endswith(('.png', '.jpg', '.jpeg')):
                    try:
                        img = pygame.image.load(os.path.join(bg_path, file))
                        preview_img = pygame.transform.scale(img, (200, 150))
                        bg_name = file.split('.')[0]
                        
                        backgrounds.append({
                            'image': preview_img,
                            'name': bg_name,
                            'path': os.path.join(bg_path, file),
                            'full_image': img
                        })
                        loaded_backgrounds.append(bg_name)
                        print(f"Loaded background: {bg_name}")
                        
                    except Exception as e:
                        print(f"Error loading background {file}: {e}")
                        continue
        
        # If no backgrounds found, create placeholders
        if not backgrounds:
            default_bg = self.create_placeholder_background('default_stage')
            backgrounds.append({
                'image': default_bg,
                'name': 'default_stage',
                'path': None,
                'full_image': None
            })
        
        return backgrounds
    
    def create_placeholder_background(self, name):
        img = pygame.Surface((200, 150))
        
        # Enhanced background colors to match pixel art style
        bg_colors = {
            'pixel_village': (135, 206, 235),  # Sky blue like your image
            'forest_stage': (34, 139, 34),
            'desert_arena': (238, 203, 173),
            'mountain_peak': (139, 137, 137),
            'beach_shore': (135, 206, 235),
            'city_street': (105, 105, 105),
            'temple_grounds': (160, 82, 45),
            'castle_courtyard': (112, 128, 144)
        }
        
        primary_color = bg_colors.get(name, (100, 150, 200))
        img.fill(primary_color)
        
        # Add some pixel-art style details
        if name == 'pixel_village':
            # Create a simple village-like placeholder
            # Ground
            pygame.draw.rect(img, (101, 67, 33), (0, 120, 200, 30))  # Brown ground
            # Simple house shape
            pygame.draw.rect(img, (139, 69, 19), (50, 80, 40, 40))  # House
            pygame.draw.polygon(img, (178, 34, 34), [(50, 80), (70, 60), (90, 80)])  # Roof
            # Simple tree
            pygame.draw.rect(img, (101, 67, 33), (120, 90, 8, 30))  # Trunk
            pygame.draw.circle(img, (34, 139, 34), (124, 85), 15)  # Leaves
        elif name == 'forest_stage':
            # Forest details
            for i in range(3):
                x = 30 + i * 60
                pygame.draw.rect(img, (101, 67, 33), (x, 100, 12, 50))  # Tree trunks
                pygame.draw.circle(img, (0, 100, 0), (x + 6, 90), 20)  # Tree tops
        
        # Add border and text
        pygame.draw.rect(img, (255, 255, 255), img.get_rect(), 2)
        font = pygame.font.Font(None, 18)
        
        # Split long names into two lines
        if len(name) > 12:
            words = name.replace('_', ' ').split()
            if len(words) > 1:
                line1 = words[0]
                line2 = ' '.join(words[1:])
                text1 = font.render(line1, True, (255, 255, 255))
                text2 = font.render(line2, True, (255, 255, 255))
                img.blit(text1, (100 - text1.get_width()//2, 65))
                img.blit(text2, (100 - text2.get_width()//2, 85))
            else:
                text = font.render(name.replace('_', ' '), True, (255, 255, 255))
                img.blit(text, (100 - text.get_width()//2, 75))
        else:
            text = font.render(name.replace('_', ' '), True, (255, 255, 255))
            img.blit(text, (100 - text.get_width()//2, 75))
        
        return img
    
    def draw(self, surface):
        # Load background image only once
        if not self.background_loaded:
            try:
                # Get the directory of the current script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                bg_path = os.path.join(script_dir, "images", "background", "Home.jpg")
                print(f"CharacterSelect: Trying to load: {bg_path}")
                
                if os.path.exists(bg_path):
                    self.background_image = pygame.image.load(bg_path)
                    self.background_image = pygame.transform.scale(self.background_image, (self.screen_width, self.screen_height))
                    print(f"CharacterSelect: Successfully loaded background: {bg_path}")
                else:
                    print(f"CharacterSelect: File does not exist: {bg_path}")
                    self.background_image = self.create_pixel_village_background()
                    print("CharacterSelect: Using fallback background")
            except Exception as e:
                print(f"CharacterSelect: Failed to load Home.jpg: {e}")
                self.background_image = self.create_pixel_village_background()
                print("CharacterSelect: Using fallback background")
            
            self.background_loaded = True
        
        # Draw the cached background
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        
        # Add semi-transparent overlay for better text visibility
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        if self.selection_phase == "characters":
            self.draw_character_selection(surface)
        else:
            self.draw_background_selection(surface)

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

    def draw_character_selection(self, surface):
        title = self.font.render("SELECT CHARACTER", True, (255, 255, 255))
        surface.blit(title, (self.screen_width // 2 - title.get_width() // 2, 30))
        
        # Show current player selecting
        if self.network_mode:
            if self.my_role:
                if not self.selected_chars[0]:
                    status_text = f"You ({self.my_role}): Select your character"
                    color = (255, 255, 0)
                else:
                    if self.both_players_ready:
                        status_text = "Both players ready! Starting game..."
                        color = (0, 255, 0)
                    elif self.opponent_selection:
                        status_text = f"Waiting for opponent to confirm..."
                        color = (255, 200, 0)
                    else:
                        status_text = f"Waiting for opponent selection..."
                        color = (255, 255, 100)
                        
                status_surface = self.small_font.render(status_text, True, color)
                surface.blit(status_surface, (self.screen_width // 2 - status_surface.get_width() // 2, 70))
        else:
            # Local play
            if self.current_player < 2:
                player_text = f"Player {self.current_player + 1} selecting..."
                player_surface = self.small_font.render(player_text, True, (255, 255, 0))
                surface.blit(player_surface, (self.screen_width // 2 - player_surface.get_width() // 2, 70))
            else:
                player_text = "Both players selected!"
                player_surface = self.small_font.render(player_text, True, (0, 255, 0))
                surface.blit(player_surface, (self.screen_width // 2 - player_surface.get_width() // 2, 70))
        
        # Draw character grid (4x3 for 12 characters)
        cols = 4
        rows = 3
        char_width = 110
        char_height = 130
        start_x = (self.screen_width - (cols * char_width)) // 2
        start_y = 120
        
        for i, char in enumerate(self.character_portraits):
            if i >= 12:  # Only show first 12 characters
                break
                
            x = start_x + (i % cols) * char_width
            y = start_y + (i // cols) * char_height
            
            # Highlight selected characters
            if self.network_mode:
                # In network mode, show both yours and opponent's selection
                if self.selected_chars[0] and char['name'] == self.selected_chars[0]['name']:
                    # Your selection - bright yellow
                    pygame.draw.rect(surface, (255, 255, 0), (x-5, y-5, 110, 125), 4)
                    # Add "YOU" label
                    you_text = self.small_font.render("YOU", True, (255, 255, 0))
                    surface.blit(you_text, (x + 5, y + 5))
                elif self.opponent_selection and char['name'] == self.opponent_selection['name']:
                    # Opponent's selection - red
                    pygame.draw.rect(surface, (255, 100, 100), (x-5, y-5, 110, 125), 4)
                    # Add "OPPONENT" label
                    opp_text = self.small_font.render("OPP", True, (255, 100, 100))
                    surface.blit(opp_text, (x + 5, y + 5))
            else:
                # In local mode, show both player selections
                if self.selected_chars[0] and char['name'] == self.selected_chars[0]['name']:
                    pygame.draw.rect(surface, (0, 255, 0), (x-5, y-5, 110, 125), 3)
                    # Add "P1" label
                    p1_text = self.small_font.render("P1", True, (0, 255, 0))
                    surface.blit(p1_text, (x + 5, y + 5))
                elif len(self.selected_chars) > 1 and self.selected_chars[1] and char['name'] == self.selected_chars[1]['name']:
                    pygame.draw.rect(surface, (0, 0, 255), (x-5, y-5, 110, 125), 3)
                    # Add "P2" label
                    p2_text = self.small_font.render("P2", True, (0, 0, 255))
                    surface.blit(p2_text, (x + 5, y + 5))
            
            # Draw character portrait
            surface.blit(char['image'], (x, y))
            
            # Draw character name
            name_text = self.small_font.render(char['name'], True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(x + 50, y + 110))
            surface.blit(name_text, name_rect)
        
        # Show selection status
        if self.network_mode:
            # Network mode - show both players' selections
            my_text = f"Your choice: {self.selected_chars[0]['name'] if self.selected_chars[0] else 'None'}"
            my_surface = self.small_font.render(my_text, True, (255, 255, 0))
            surface.blit(my_surface, (50, self.screen_height - 80))
            
            opp_text = f"Opponent: {self.opponent_selection['name'] if self.opponent_selection else 'None'}"
            opp_surface = self.small_font.render(opp_text, True, (255, 100, 100))
            surface.blit(opp_surface, (50, self.screen_height - 50))
        else:
            # Local mode
            p1_text = f"Player 1: {self.selected_chars[0]['name'] if self.selected_chars[0] else 'None'}"
            p1_surface = self.small_font.render(p1_text, True, (0, 255, 0))
            surface.blit(p1_surface, (50, self.screen_height - 80))
            
            if len(self.selected_chars) > 1:
                p2_text = f"Player 2: {self.selected_chars[1]['name'] if self.selected_chars[1] else 'None'}"
                p2_surface = self.small_font.render(p2_text, True, (0, 0, 255))
                surface.blit(p2_surface, (50, self.screen_height - 50))
        
        # Instructions
        if self.network_mode:
            if self.both_players_ready:
                instruction = "Starting game..."
            elif self.selected_chars[0]:
                instruction = "Waiting for opponent to select character"
            else:
                instruction = "Click on a character to select"
        else:
            if self.current_player == 0:
                instruction = "Player 1: Click on a character to select"
            elif self.current_player == 1:
                instruction = "Player 2: Click on a character to select"
            else:
                instruction = "Press SPACE to continue to background selection"
        
        inst_surface = self.small_font.render(instruction, True, (200, 200, 200))
        surface.blit(inst_surface, (self.screen_width // 2 - inst_surface.get_width() // 2, self.screen_height - 20))

    def draw_background_selection(self, surface):
        title = self.font.render("SELECT BACKGROUND", True, (255, 255, 255))
        surface.blit(title, (self.screen_width // 2 - title.get_width() // 2, 50))
        
        cols = 3
        start_x = (self.screen_width - (cols * 220)) // 2
        start_y = 150
        
        for i, bg in enumerate(self.backgrounds):
            x = start_x + (i % cols) * 220
            y = start_y + (i // cols) * 170
            
            if self.selected_background == bg['name']:
                pygame.draw.rect(surface, (255, 255, 0), (x-5, y-5, 210, 160), 3)
            
            surface.blit(bg['image'], (x, y))
            
            name_text = self.small_font.render(bg['name'], True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(x + 100, y + 165))
            surface.blit(name_text, name_rect)
        
        # Instructions
        instruction = "Click on a background to select, then press ENTER to confirm"
        inst_surface = self.small_font.render(instruction, True, (200, 200, 200))
        surface.blit(inst_surface, (self.screen_width // 2 - inst_surface.get_width() // 2, self.screen_height - 30))
    
    def handle_click(self, pos):
        if self.selection_phase == "characters":
            return self.handle_character_click(pos)
        else:
            return self.handle_background_click(pos)
    
    def handle_character_click(self, pos):
        cols = 4
        char_width = 110
        char_height = 130
        start_x = (self.screen_width - (cols * char_width)) // 2
        start_y = 120
        
        for i, char in enumerate(self.character_portraits):
            if i >= 12:  # Only check first 12 characters
                break
                
            x = start_x + (i % cols) * char_width
            y = start_y + (i // cols) * char_height
            
            if x <= pos[0] <= x + 100 and y <= pos[1] <= y + 100:
                if self.network_mode:
                    # Network mode - only select for this player
                    self.selected_chars[0] = char
                else:
                    # Local mode - select for current player
                    if self.current_player == 0:
                        self.selected_chars[0] = char
                        self.current_player = 1
                    elif self.current_player == 1:
                        self.selected_chars[1] = char
                        self.current_player = 2  # Both players selected
                        # Auto-select a random background for fighting
                        self.auto_select_background()
                return True
        return False
    
    def handle_background_click(self, pos):
        cols = 3
        start_x = (self.screen_width - (cols * 220)) // 2
        start_y = 150
        
        for i, bg in enumerate(self.backgrounds):
            x = start_x + (i % cols) * 220
            y = start_y + (i // cols) * 170
            
            if x <= pos[0] <= x + 200 and y <= pos[1] <= y + 150:
                self.selected_background = bg['name']
                return True
        return False
    
    def handle_keypress(self, key):
        if self.network_mode:
            # Network mode - ENTER to confirm character selection
            if key == pygame.K_RETURN and self.selected_chars[0]:
                return True  # Character selection confirmed
        else:
            # Local mode - SPACE to move to background selection
            if key == pygame.K_SPACE and self.current_player >= 2:
                self.selection_phase = "background"
                if not self.selected_background and self.backgrounds:
                    self.selected_background = self.backgrounds[0]['name']
            elif key == pygame.K_RETURN and self.selection_phase == "background" and self.selected_background:
                return True  # Selection complete
        return False

    def set_network_mode(self, network_mode=True, role=None):
        """Set whether this is for network play (single selection) or local play (dual selection)"""
        self.network_mode = network_mode
        self.role = role
        self.my_role = role
        self.both_players_ready = False
        self.opponent_selection = None
        
        if network_mode:
            self.selected_chars = [None]  # Only one selection for network
            self.current_player = 0  # Reset to 0 for network mode
        else:
            self.selected_chars = [None, None]  # Two selections for local
            self.current_player = 0

    def set_opponent_selection(self, opponent_character):
        """Set the opponent's character selection"""
        if self.network_mode:
            self.opponent_selection = opponent_character
            
    def set_both_players_ready(self, ready=True):
        """Set the state when both players are ready"""
        self.both_players_ready = ready

    def is_selection_complete(self):
        if self.network_mode:
            # In network mode, complete when this player has selected and both are ready
            return (self.selected_chars[0] is not None and self.both_players_ready)
        else:
            # In local mode, need both characters (background auto-selected)
            return (self.selected_chars[0] is not None and 
                    len(self.selected_chars) > 1 and
                    self.selected_chars[1] is not None and 
                    self.selected_background is not None)
    
    def is_ready_for_network_play(self):
        """Check if this player is ready for network play (character selected)"""
        return self.network_mode and self.selected_chars[0] is not None
    
    def reset_selection(self):
        self.selected_chars = [None, None] if not self.network_mode else [None]
        self.selected_background = None
        self.selection_phase = "characters"
        self.current_player = 0
        self.both_players_ready = False
        self.opponent_selection = None
    
    def reset_for_network_play(self):
        """Reset for network play where each player selects only their character"""
        self.selected_chars = [None, None]
        self.selected_background = None
        self.selection_phase = "characters"
        self.current_player = 0
    
    def is_character_selected(self):
        """Check if this player has selected a character"""
        return self.selected_chars[0] is not None

    def get_selected_character(self):
        """Get the selected character for network play"""
        return self.selected_chars[0] if self.selected_chars[0] else None
    
    def set_network_mode(self, network_mode=True, role=None):
        """Set whether this is for network play (single selection) or local play (dual selection)"""
        self.network_mode = network_mode
        self.role = role
        if network_mode:
            self.selected_chars = [None]  # Only one selection for network
            self.current_player = 0  # Reset to 0 for network mode
        else:
            self.selected_chars = [None, None]  # Two selections for local
            self.current_player = 0
    
    def reset_selection(self):
        """Reset character selection"""
        if self.network_mode:
            self.selected_chars = [None]
        else:
            self.selected_chars = [None, None]
        self.selected_background = None
        self.selection_phase = "characters"
        self.current_player = 0
        self.both_players_ready = False
        self.opponent_selection = None
    
    def is_ready_for_network_play(self):
        """Check if this player has selected a character for network play"""
        return self.network_mode and self.selected_chars[0] is not None
    
    def set_opponent_selection(self, opponent_char):
        """Set the opponent's character selection"""
        self.opponent_selection = opponent_char
    
    def set_both_players_ready(self, ready):
        """Set the both players ready state"""
        self.both_players_ready = ready
    
    def reset_for_network_play(self):
        """Reset for network play where each player selects only their character"""
        self.selected_chars = [None, None]
        self.selected_background = None
        self.selection_phase = "characters"
        self.current_player = 0

    def get_random_background(self):
        """Get a random background from available backgrounds"""
        import random
        if self.backgrounds:
            return random.choice(self.backgrounds)
        else:
            # Return a default background if none available
            return {
                'name': 'default_stage',
                'path': None,
                'full_image': None
            }

    def auto_select_background(self):
        """Auto-select a random background when both characters are chosen"""
        random_bg = self.get_random_background()
        self.selected_background = random_bg['name']
        return random_bg

    def both_characters_selected(self):
        """Check if both characters have been selected (for local play)"""
        return (self.selected_chars[0] is not None and 
                len(self.selected_chars) > 1 and 
                self.selected_chars[1] is not None)
