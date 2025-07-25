#!/usr/bin/env python3
"""
Test script for the new sprite loading system
"""

import pygame
import sys
import os

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Sprite Loader Test")
clock = pygame.time.Clock()

# Import our sprite loader
try:
    from sprite_loader import sprite_loader
    print("✓ Sprite loader imported successfully")
except ImportError as e:
    print(f"✗ Failed to import sprite loader: {e}")
    sys.exit(1)

def test_character_loading():
    """Test loading all available characters"""
    print("\n=== Testing Character Loading ===")
    
    available_chars = sprite_loader.get_available_characters()
    print(f"Available characters: {available_chars}")
    
    test_results = {}
    
    for char_name in available_chars[:3]:  # Test first 3 characters
        print(f"\nTesting {char_name}:")
        
        try:
            # Test sprite loading
            sprite_data = sprite_loader.load_character_sprites(char_name)
            print(f"  ✓ Sprite data loaded: {len(sprite_data['animations'])} animations")
            
            # Test character data
            char_data = sprite_loader.get_character_data(char_name)
            print(f"  ✓ Character data: size={char_data[0]}, scale={char_data[1]}")
            
            # Test skills
            skills = sprite_loader.get_character_skills(char_name)
            print(f"  ✓ Special skills: {skills}")
            
            # Test sprite sheet creation
            sprite_sheet = sprite_loader.create_sprite_sheet_from_animations(char_name)
            print(f"  ✓ Sprite sheet: {sprite_sheet.get_width()}x{sprite_sheet.get_height()}")
            
            test_results[char_name] = "PASS"
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            test_results[char_name] = f"FAIL: {e}"
    
    return test_results

def visualize_character_sprites(char_name):
    """Visualize a character's sprites"""
    print(f"\n=== Visualizing {char_name} ===")
    
    try:
        sprite_data = sprite_loader.load_character_sprites(char_name)
        animations = sprite_data['animations']
        
        animation_names = ['Idle', 'Run', 'Jump', 'Attack1', 'Attack2', 'Hurt', 'Dead', 'Special1', 'Special2']
        current_anim = 0
        current_frame = 0
        frame_timer = 0
        
        font = pygame.font.Font(None, 36)
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        current_anim = (current_anim - 1) % len(animations)
                        current_frame = 0
                    elif event.key == pygame.K_RIGHT:
                        current_anim = (current_anim + 1) % len(animations)
                        current_frame = 0
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            # Update animation frame
            frame_timer += 1
            if frame_timer >= 10:  # Change frame every 10 ticks
                frame_timer = 0
                if animations[current_anim]:
                    current_frame = (current_frame + 1) % len(animations[current_anim])
            
            # Draw
            screen.fill((50, 50, 50))
            
            # Draw current animation frame
            if animations[current_anim] and animations[current_anim]:
                sprite = animations[current_anim][current_frame]
                sprite_rect = sprite.get_rect(center=(400, 300))
                screen.blit(sprite, sprite_rect)
            
            # Draw UI
            anim_text = font.render(f"Animation: {animation_names[current_anim]}", True, (255, 255, 255))
            frame_text = font.render(f"Frame: {current_frame + 1}/{len(animations[current_anim]) if animations[current_anim] else 0}", True, (255, 255, 255))
            help_text = font.render("Left/Right: Change animation, ESC: Exit", True, (200, 200, 200))
            
            screen.blit(anim_text, (20, 20))
            screen.blit(frame_text, (20, 60))
            screen.blit(help_text, (20, 550))
            
            pygame.display.flip()
            clock.tick(60)
            
    except Exception as e:
        print(f"Error visualizing {char_name}: {e}")

def main():
    print("Street Fighter Sprite Loader Test")
    print("=" * 40)
    
    # Test character loading
    results = test_character_loading()
    
    print("\n=== Test Results ===")
    for char, result in results.items():
        print(f"{char}: {result}")
    
    # Interactive visualization
    print("\n=== Interactive Visualization ===")
    print("Choose a character to visualize:")
    
    available_chars = sprite_loader.get_available_characters()
    for i, char in enumerate(available_chars):
        print(f"{i+1}. {char}")
    
    try:
        choice = input("\nEnter character number (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            return
        
        char_index = int(choice) - 1
        if 0 <= char_index < len(available_chars):
            char_name = available_chars[char_index]
            visualize_character_sprites(char_name)
        else:
            print("Invalid choice")
            
    except (ValueError, KeyboardInterrupt):
        print("\nExiting...")
    
    pygame.quit()

if __name__ == "__main__":
    main()
