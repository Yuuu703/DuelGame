#!/usr/bin/env python3
"""
Control Test Utility for Street Fighter
Test and learn the game controls in a safe environment
"""

import pygame
import sys
import os

pygame.init()

class ControlTester:
    def __init__(self):
        self.screen_width = 1000
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Street Fighter - Control Tester")
        
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Track pressed keys for visual feedback
        self.pressed_keys = set()
        self.key_press_times = {}
        
        # Control mappings
        self.p1_controls = {
            'Movement': {
                pygame.K_w: 'W - Jump',
                pygame.K_a: 'A - Move Left', 
                pygame.K_s: 'S - Down',
                pygame.K_d: 'D - Move Right'
            },
            'Combat': {
                pygame.K_j: 'J - Attack 1',
                pygame.K_k: 'K - Attack 2',
                pygame.K_l: 'L - Special 1',
                pygame.K_u: 'U - Special 2',
                pygame.K_i: 'I - Special 3', 
                pygame.K_o: 'O - Special 4'
            }
        }
        
        self.p2_controls = {
            'Movement': {
                pygame.K_UP: '↑ - Jump',
                pygame.K_LEFT: '← - Move Left',
                pygame.K_DOWN: '↓ - Down', 
                pygame.K_RIGHT: '→ - Move Right'
            },
            'Combat': {
                pygame.K_KP1: 'Num1 - Attack 1',
                pygame.K_KP2: 'Num2 - Attack 2',
                pygame.K_KP4: 'Num4 - Special 1',
                pygame.K_KP5: 'Num5 - Special 2',
                pygame.K_KP6: 'Num6 - Special 3',
                pygame.K_KP8: 'Num8 - Special 4'
            }
        }
        
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    else:
                        self.pressed_keys.add(event.key)
                        self.key_press_times[event.key] = pygame.time.get_ticks()
                elif event.type == pygame.KEYUP:
                    self.pressed_keys.discard(event.key)
            
            # Remove old key presses for visual effect
            current_time = pygame.time.get_ticks()
            keys_to_remove = []
            for key, press_time in self.key_press_times.items():
                if current_time - press_time > 500:  # 500ms highlight duration
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.key_press_times[key]
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def draw(self):
        self.screen.fill((30, 40, 60))
        
        # Title
        title = self.font_large.render("Street Fighter - Control Tester", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instruction = self.font_medium.render("Press keys to test controls - ESC to exit", True, (200, 200, 255))
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(instruction, instruction_rect)
        
        # Player 1 controls (left side)
        self.draw_player_controls(1, self.p1_controls, 50, 150)
        
        # Player 2 controls (right side)  
        self.draw_player_controls(2, self.p2_controls, self.screen_width // 2 + 50, 150)
        
        # Visual feedback area
        self.draw_key_feedback()
        
        pygame.display.flip()
    
    def draw_player_controls(self, player_num, controls, x_start, y_start):
        # Player header
        header = self.font_medium.render(f"Player {player_num}", True, (255, 255, 100))
        self.screen.blit(header, (x_start, y_start))
        
        y_offset = y_start + 40
        
        for category, keys in controls.items():
            # Category header
            category_text = self.font_small.render(f"{category}:", True, (200, 255, 200))
            self.screen.blit(category_text, (x_start, y_offset))
            y_offset += 25
            
            # Key mappings
            for key, description in keys.items():
                # Check if key is currently pressed
                color = (255, 255, 100) if key in self.pressed_keys else (255, 255, 255)
                recent_press = key in self.key_press_times
                if recent_press:
                    color = (100, 255, 100)  # Green for recent press
                
                key_text = self.font_small.render(f"  {description}", True, color)
                self.screen.blit(key_text, (x_start + 10, y_offset))
                y_offset += 22
            
            y_offset += 10  # Extra space between categories
    
    def draw_key_feedback(self):
        # Key press feedback area
        feedback_y = 450
        feedback_title = self.font_medium.render("Key Press Feedback:", True, (255, 200, 100))
        self.screen.blit(feedback_title, (50, feedback_y))
        
        if self.pressed_keys or self.key_press_times:
            y_pos = feedback_y + 35
            
            # Show currently pressed keys
            if self.pressed_keys:
                current_text = self.font_small.render("Currently Pressed:", True, (200, 200, 200))
                self.screen.blit(current_text, (50, y_pos))
                y_pos += 25
                
                for key in self.pressed_keys:
                    key_name = pygame.key.name(key)
                    key_text = self.font_small.render(f"  {key_name.upper()}", True, (100, 255, 100))
                    self.screen.blit(key_text, (70, y_pos))
                    y_pos += 20
            
            # Show recent key presses
            if self.key_press_times:
                recent_text = self.font_small.render("Recent Presses:", True, (200, 200, 200))
                self.screen.blit(recent_text, (300, feedback_y + 35))
                y_pos = feedback_y + 60
                
                sorted_keys = sorted(self.key_press_times.items(), key=lambda x: x[1], reverse=True)
                for key, press_time in sorted_keys[:5]:  # Show last 5 presses
                    key_name = pygame.key.name(key)
                    elapsed = (pygame.time.get_ticks() - press_time) / 1000
                    key_text = self.font_small.render(f"  {key_name.upper()} ({elapsed:.1f}s ago)", True, (255, 255, 100))
                    self.screen.blit(key_text, (320, y_pos))
                    y_pos += 20
        else:
            no_input = self.font_small.render("Press any key to see feedback...", True, (150, 150, 150))
            self.screen.blit(no_input, (50, feedback_y + 35))
        
        # Control combinations
        combo_title = self.font_small.render("Try these combinations:", True, (255, 200, 100))
        self.screen.blit(combo_title, (600, feedback_y))
        
        combos = [
            "W + J (Jump Attack)",
            "A/D + K (Moving Attack)", 
            "L/U/I/O (Special Skills)",
            "Arrow + Num1/2 (P2 Attack)"
        ]
        
        for i, combo in enumerate(combos):
            combo_text = self.font_small.render(combo, True, (200, 200, 255))
            self.screen.blit(combo_text, (600, feedback_y + 25 + i * 20))

def main():
    print("Starting Street Fighter Control Tester...")
    print("This will help you learn and test the game controls.")
    print()
    
    tester = ControlTester()
    tester.run()

if __name__ == "__main__":
    main()
