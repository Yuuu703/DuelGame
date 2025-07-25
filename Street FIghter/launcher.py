#!/usr/bin/env python3
"""
Street Fighter LAN Game Launcher
Enhanced launcher with network testing and LAN discovery
"""
import sys
import subprocess
import os
import time
import threading

def print_menu():
    print("=" * 60)
    print("Street Fighter LAN Game Launcher")
    print("=" * 60)
    print("1. Launch Main Game (Recommended)")
    print("2. Test Network Connection")
    print("3. Scan for LAN Games")
    print("4. Test Controls")
    print("5. Test Sprites")
    print("6. Start Room-Based Server")
    print("7. Start Room Client")
    print("8. Start Dedicated Server")
    print("9. Help & Troubleshooting")
    print("10. Exit")
    print("=" * 60)

def get_local_ip():
    """Get local IP address"""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def test_network():
    """Test network connectivity"""
    print("\n" + "=" * 40)
    print("Network Test")
    print("=" * 40)
    
    local_ip = get_local_ip()
    print(f"Your IP Address: {local_ip}")
    
    # Test port availability
    import socket
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.bind(('', 12345))
        test_socket.close()
        print("Port 12345: Available ✓")
    except:
        print("Port 12345: In use or blocked ✗")
    
    print("\nPress Enter to continue...")
    input()

def test_controls():
    """Launch control testing utility"""
    print("\n" + "=" * 40)
    print("Launching Control Tester...")
    print("=" * 40)
    
    try:
        script_path = os.path.join(os.path.dirname(__file__), "test_controls.py")
        if os.path.exists(script_path):
            subprocess.run([sys.executable, script_path])
        else:
            print("Control test utility not found")
    except Exception as e:
        print(f"Error during control test: {e}")
    
    print("\nPress Enter to continue...")
    input()

def test_sprites():
    """Launch sprite testing utility"""
    print("\n" + "=" * 40)
    print("Launching Sprite Tester...")
    print("=" * 40)
    
    try:
        script_path = os.path.join(os.path.dirname(__file__), "test_sprites.py")
        if os.path.exists(script_path):
            subprocess.run([sys.executable, script_path])
        else:
            print("Sprite test utility not found")
    except Exception as e:
        print(f"Error during sprite test: {e}")
    
    print("\nPress Enter to continue...")
    input()

def launch_main_game():
    """Launch the main game"""
    try:
        game_path = os.path.join(os.path.dirname(__file__), "main.py")
        print(f"\nLaunching main game from: {game_path}")
        subprocess.Popen([sys.executable, game_path])
        print("Game launched successfully!")
        return True
    except Exception as e:
        print(f"Failed to launch game: {e}")
        return False

def show_help():
    """Show help and troubleshooting information"""
    print("\n" + "=" * 60)
    print("Help & Troubleshooting")
    print("=" * 60)
    print("""
NETWORK SETUP:
• Both players must be on the same local network (LAN)
• Port 12345 must be available and not blocked
• Windows Firewall may need to allow Python/the game

GAME MODES:
1. Main Game - Full featured game with LAN support
2. Room Server/Client - Alternative networking approach
3. Dedicated Server - For multiple game sessions

TROUBLESHOOTING:
• If LAN scan finds no games, try manual IP entry
• Check firewall settings if connection fails
• Use 'Test Network Connection' to diagnose issues
• Make sure both players use the same game version

LAN CONNECTION:
• Host player: Select 'Host LAN Game' in main game
• Joining player: Select 'Join LAN Game' and pick host
• If auto-discovery fails, use manual IP entry

def scan_lan_games():
    """Scan for available LAN games"""
    print("\n" + "=" * 40)
    print("Scanning for LAN Games...")
    print("=" * 40)
    
    try:
        # Use the network test utility
        script_path = os.path.join(os.path.dirname(__file__), "network_test.py")
        if os.path.exists(script_path):
            subprocess.run([sys.executable, script_path, "scan"])
        else:
            print("Network test utility not found")
    except Exception as e:
        print(f"Error during scan: {e}")
    
    print("\nPress Enter to continue...")
    input()

def start_room_server():
    host = input("Enter host IP (default: localhost): ").strip() or "localhost"
    port = input("Enter port (default: 12345): ").strip() or "12345"
    
    try:
        port = int(port)
        server_path = os.path.join(os.path.dirname(__file__), "room_server.py")
        subprocess.run([sys.executable, server_path, host, str(port)])
    except ValueError:
        print("Invalid port number!")
    except Exception as e:
        print(f"Error starting room server: {e}")

def start_room_client():
    host = input("Enter server IP (default: localhost): ").strip() or "localhost"
    port = input("Enter port (default: 12345): ").strip() or "12345"
    
    try:
        port = int(port)
        client_path = os.path.join(os.path.dirname(__file__), "room_client.py")
        subprocess.run([sys.executable, client_path, host, str(port)])
    except ValueError:
        print("Invalid port number!")
    except Exception as e:
        print(f"Error starting room client: {e}")

def start_server():
    host = input("Enter host IP (default: localhost): ").strip() or "localhost"
    port = input("Enter port (default: 12345): ").strip() or "12345"
    
    try:
        port = int(port)
        server_path = os.path.join(os.path.dirname(__file__), "server.py")
        subprocess.run([sys.executable, server_path, host, str(port)])
    except ValueError:
        print("Invalid port number!")
    except Exception as e:
        print(f"Error starting server: {e}")

def start_client():
    host = input("Enter server IP (default: localhost): ").strip() or "localhost"
    port = input("Enter port (default: 12345): ").strip() or "12345"
    
    try:
        port = int(port)
        client_path = os.path.join(os.path.dirname(__file__), "client.py")
        subprocess.run([sys.executable, client_path, host, str(port)])
    except ValueError:
        print("Invalid port number!")
    except Exception as e:
        print(f"Error starting client: {e}")

def start_local_game():
    main_path = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.run([sys.executable, main_path])

def print_help():
    print("\nRoom System Features:")
    print("- Create named rooms with unique codes")
    print("- Browse public rooms")
    print("- Join rooms by 6-digit code")
    print("- In-room chat system")
    print("- Host can control room settings")
    print("\nHow to use:")
    print("1. Start the room server on one machine")
    print("2. Players connect using room client")
    print("3. Create or join rooms to find opponents")
    print("4. Use room codes to invite specific friends")

def main():
    while True:
        print_menu()
        print(f"Your IP: {get_local_ip()}")
        choice = input("\nEnter your choice (1-10): ").strip()
        
        if choice == "1":
            if launch_main_game():
                break  # Exit launcher after successful game launch
        elif choice == "2":
            test_network()
        elif choice == "3":
            scan_lan_games()
        elif choice == "4":
            test_controls()
        elif choice == "5":
            test_sprites()
        elif choice == "6":
            start_room_server()
        elif choice == "7":
            start_room_client()
        elif choice == "8":
            start_dedicated_server()
        elif choice == "9":
            show_help()
        elif choice == "10":
            print("Goodbye!")
            break
        elif choice.lower() == "help":
            show_help()
        else:
            print("Invalid choice! Please select 1-10. Type 'help' for more info.")
        
        print("\n")

if __name__ == "__main__":
    main()
