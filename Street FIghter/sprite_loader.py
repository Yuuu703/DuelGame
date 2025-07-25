import pygame
import os
import json

class SpriteLoader:
    """Enhanced sprite loading system for Street Fighter characters"""
    
    def __init__(self):
        self.loaded_sprites = {}  # Cache for loaded sprites
        self.character_configs = self._load_character_configs()
        
    def _load_character_configs(self):
        """Load character configuration data"""
        configs = {
            'Kunoichi': {
                'folder': 'Kunoichi',
                'size': 64,
                'scale': 3,
                'offset': [32, 32],
                'animations': {
                    'idle': 'Idle.png',
                    'run': 'Run.png', 
                    'jump': 'Jump.png',
                    'attack1': 'Attack_1.png',
                    'attack2': 'Attack_2.png',
                    'hurt': 'Hurt.png',
                    'dead': 'Dead.png',
                    'special1': 'Cast.png',
                    'special2': 'Spine.png'
                },
                'frame_counts': [8, 8, 2, 6, 6, 4, 6, 6, 8],  # frames per animation
                'special_skills': ['shadow_clone', 'ninja_vanish']
            },
            'Lightning Mage': {
                'folder': 'Lightning Mage',
                'size': 64,
                'scale': 3,
                'offset': [32, 32],
                'animations': {
                    'idle': 'Idle.png',
                    'run': 'Run.png',
                    'jump': 'Jump.png', 
                    'attack1': 'Attack_1.png',
                    'attack2': 'Attack_2.png',
                    'hurt': 'Hurt.png',
                    'dead': 'Dead.png',
                    'special1': 'Charge.png',
                    'special2': 'Light_ball.png'
                },
                'frame_counts': [6, 8, 2, 7, 7, 4, 6, 8, 6],
                'special_skills': ['lightning_bolt', 'chain_lightning']
            },
            'Ninja_Monk': {
                'folder': 'Ninja_Monk',
                'size': 64,
                'scale': 3,
                'offset': [32, 32],
                'animations': {
                    'idle': 'Idle.png',
                    'run': 'Run.png',
                    'jump': 'Jump.png',
                    'attack1': 'Attack_1.png', 
                    'attack2': 'Attack_2.png',
                    'hurt': 'Hurt.png',
                    'dead': 'Dead.png',
                    'special1': 'Cast.png',
                    'special2': 'Blade.png'
                },
                'frame_counts': [6, 8, 2, 6, 6, 4, 6, 8, 6],
                'special_skills': ['meditation', 'spirit_punch']
            },
            'Ninja_Peasant': {
                'folder': 'Ninja_Peasant',
                'size': 64,
                'scale': 3,
                'offset': [32, 32],
                'animations': {
                    'idle': 'Idle.png',
                    'run': 'Run.png',
                    'jump': 'Jump.png',
                    'attack1': 'Attack_1.png',
                    'attack2': 'Attack_2.png',
                    'hurt': 'Hurt.png',
                    'dead': 'Dead.png',
                    'special1': 'Disguise.png',
                    'special2': 'Shot.png'
                },
                'frame_counts': [6, 8, 2, 6, 6, 4, 6, 8, 6],
                'special_skills': ['farm_tools', 'humble_strike']
            },
            'Samurai': {
                'folder': 'Samurai/Sprites',
                'size': 200,
                'scale': 2,
                'offset': [100, 100],
                'animations': {
                    'idle': 'Idle.png',
                    'run': 'Run.png',
                    'jump': 'Jump.png',
                    'attack1': 'Attack_1.png',
                    'attack2': 'Attack_2.png',
                    'attack3': 'Attack_3.png',
                    'hurt': 'Hurt.png',
                    'dead': 'Dead.png',
                    'special1': 'Shield.png'
                },
                'frame_counts': [8, 8, 2, 6, 6, 6, 4, 6, 8],
                'special_skills': ['katana_slash', 'honor_guard']
            },
            'Fire Wizard': {
                'folder': 'Fire Wizard',
                'size': 64,
                'scale': 3,
                'offset': [32, 32],
                'animations': {
                    'idle': 'Idle.png',
                    'run': 'Run.png',
                    'jump': 'Jump.png',
                    'attack1': 'Attack_1.png',
                    'attack2': 'Attack_2.png',
                    'hurt': 'Hurt.png',
                    'dead': 'Dead.png',
                    'special1': 'Charge.png',
                    'special2': 'Fireball.png'
                },
                'frame_counts': [6, 8, 2, 7, 7, 4, 6, 8, 6],
                'special_skills': ['fireball', 'flame_jet']
            },
            'Wanderer Magican': {
                'folder': 'Wanderer Magican',
                'size': 64,
                'scale': 3,
                'offset': [32, 32],
                'animations': {
                    'idle': 'Idle.png',
                    'run': 'Run.png',
                    'jump': 'Jump.png',
                    'attack1': 'Attack_1.png',
                    'attack2': 'Attack_2.png',
                    'hurt': 'Hurt.png',
                    'dead': 'Dead.png',
                    'special1': 'Charge_1.png',
                    'special2': 'Magic_sphere.png'
                },
                'frame_counts': [6, 8, 2, 7, 7, 4, 6, 8, 6],
                'special_skills': ['magic_arrow', 'arcane_sphere']
            }
        }
        return configs
    
    def load_character_sprites(self, character_name):
        """Load all sprites for a character"""
        if character_name in self.loaded_sprites:
            return self.loaded_sprites[character_name]
        
        if character_name not in self.character_configs:
            print(f"Warning: Character '{character_name}' not found in configs")
            return self._create_placeholder_sprites(character_name)
        
        config = self.character_configs[character_name]
        base_path = os.path.join("images", config['folder'])
        
        try:
            sprite_data = self._load_sprites_from_folder(base_path, config)
            self.loaded_sprites[character_name] = sprite_data
            return sprite_data
        except Exception as e:
            print(f"Error loading sprites for {character_name}: {e}")
            return self._create_placeholder_sprites(character_name)
    
    def _load_sprites_from_folder(self, folder_path, config):
        """Load sprites from character folder"""
        animations = config['animations']
        frame_counts = config['frame_counts']
        size = config['size']
        scale = config['scale']
        
        animation_list = []
        
        # Animation order: idle, run, jump, attack1, attack2, hurt, dead, special1, special2
        animation_order = ['idle', 'run', 'jump', 'attack1', 'attack2', 'hurt', 'dead', 'special1', 'special2']
        
        for i, anim_type in enumerate(animation_order):
            frames = []
            
            if anim_type in animations:
                sprite_file = animations[anim_type]
                sprite_path = os.path.join(folder_path, sprite_file)
                
                if os.path.exists(sprite_path):
                    try:
                        # Load the sprite image
                        sprite_img = pygame.image.load(sprite_path).convert_alpha()
                        
                        # Determine if it's a sprite sheet or single frame
                        img_width = sprite_img.get_width()
                        frame_count = frame_counts[i] if i < len(frame_counts) else 1
                        
                        if img_width > size * 1.5:  # Likely a sprite sheet
                            frame_width = img_width // frame_count
                            for frame_idx in range(frame_count):
                                frame_rect = pygame.Rect(frame_idx * frame_width, 0, frame_width, sprite_img.get_height())
                                frame_surface = pygame.Surface((frame_width, sprite_img.get_height()), pygame.SRCALPHA)
                                frame_surface.blit(sprite_img, (0, 0), frame_rect)
                                scaled_frame = pygame.transform.scale(frame_surface, (frame_width * scale, sprite_img.get_height() * scale))
                                frames.append(scaled_frame)
                        else:  # Single frame, duplicate for animation
                            scaled_sprite = pygame.transform.scale(sprite_img, (size * scale, size * scale))
                            for _ in range(frame_count):
                                frames.append(scaled_sprite.copy())
                                
                    except Exception as e:
                        print(f"Error loading {sprite_file}: {e}")
                        frames = self._create_placeholder_frames(size * scale, frame_counts[i] if i < len(frame_counts) else 1)
                else:
                    print(f"Sprite file not found: {sprite_path}")
                    frames = self._create_placeholder_frames(size * scale, frame_counts[i] if i < len(frame_counts) else 1)
            else:
                frames = self._create_placeholder_frames(size * scale, frame_counts[i] if i < len(frame_counts) else 1)
            
            animation_list.append(frames)
        
        return {
            'animations': animation_list,
            'config': config,
            'frame_counts': frame_counts
        }
    
    def _create_placeholder_frames(self, size, count):
        """Create placeholder frames for missing sprites"""
        frames = []
        colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
        
        for i in range(count):
            frame = pygame.Surface((size, size), pygame.SRCALPHA)
            color = colors[i % len(colors)]
            pygame.draw.rect(frame, color, frame.get_rect())
            pygame.draw.rect(frame, (255, 255, 255), frame.get_rect(), 3)
            frames.append(frame)
        
        return frames
    
    def _create_placeholder_sprites(self, character_name):
        """Create placeholder sprite data for unknown characters"""
        size = 64 * 3  # 64 base size * 3 scale
        frame_counts = [6, 8, 2, 6, 6, 4, 6, 6, 6]
        
        animation_list = []
        for count in frame_counts:
            frames = self._create_placeholder_frames(size, count)
            animation_list.append(frames)
        
        config = {
            'size': 64,
            'scale': 3,
            'offset': [32, 32],
            'special_skills': ['placeholder_skill_1', 'placeholder_skill_2']
        }
        
        return {
            'animations': animation_list,
            'config': config,
            'frame_counts': frame_counts
        }
    
    def get_character_data(self, character_name):
        """Get character configuration data"""
        if character_name in self.character_configs:
            config = self.character_configs[character_name]
            return [config['size'], config['scale'], config['offset']]
        else:
            return [64, 3, [32, 32]]  # Default values
    
    def get_character_skills(self, character_name):
        """Get character special skills"""
        if character_name in self.character_configs:
            return self.character_configs[character_name]['special_skills']
        else:
            return ['unknown_skill_1', 'unknown_skill_2']
    
    def get_available_characters(self):
        """Get list of available characters"""
        return list(self.character_configs.keys())
    
    def create_sprite_sheet_from_animations(self, character_name):
        """Create a traditional sprite sheet from loaded animations for compatibility"""
        sprite_data = self.load_character_sprites(character_name)
        animations = sprite_data['animations']
        config = sprite_data['config']
        
        # Calculate sprite sheet dimensions
        max_frames = max(len(anim) for anim in animations)
        frame_size = config['size'] * config['scale']
        
        sheet_width = max_frames * frame_size
        sheet_height = len(animations) * frame_size
        
        # Create sprite sheet surface
        sprite_sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
        
        # Blit animations onto sprite sheet
        for y, animation in enumerate(animations):
            for x, frame in enumerate(animation):
                pos = (x * frame_size, y * frame_size)
                # Scale frame to match expected size
                scaled_frame = pygame.transform.scale(frame, (frame_size, frame_size))
                sprite_sheet.blit(scaled_frame, pos)
        
        return sprite_sheet

# Global sprite loader instance
sprite_loader = SpriteLoader()
