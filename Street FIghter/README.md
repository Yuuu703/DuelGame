# Street Fighter LAN Edition

A multiplayer Street Fighter game with enhanced LAN networking capabilities.

## Enhanced Sprite System

The game now features a completely rewritten sprite loading system that provides:

### 🎨 **Automatic Sprite Loading**
- **Smart Detection**: Automatically detects and loads character sprites from the `images/` folder
- **Multiple Formats**: Supports both individual sprite files and sprite sheets
- **Fallback System**: Creates placeholder sprites if original files are missing
- **Portrait Generation**: Automatically creates character portraits from idle animations

### 🎮 **Supported Characters**
The enhanced system includes configurations for:
- Kunoichi (shadow clone, ninja vanish)
- Lightning Mage (lightning bolt, chain lightning)  
- Ninja_Monk (meditation, spirit punch)
- Ninja_Peasant (farm tools, humble strike)
- Samurai (katana slash, honor guard)
- Fire Wizard (fireball, flame jet)
- Wanderer Magician (magic arrow, arcane sphere)

### 🔧 **Smart Sprite Loading**
- **Adaptive Sizing**: Automatically scales sprites based on character configuration
- **Animation Mapping**: Maps sprite files to proper animations (idle, run, jump, attacks, etc.)
- **Special Skills**: Each character has unique special moves with proper animations
- **Performance Caching**: Loaded sprites are cached for better performance

### 🎨 **Fallback Features**
- **Missing Sprites**: Creates colored placeholder sprites for missing characters
- **Portrait Generation**: Generates character portraits from sprites or creates colorful placeholders
- **Background Loading**: Enhanced background loading with multiple format support

### 📁 **File Structure Support**
The system handles various folder structures:
```
images/
  Character_Name/           # Individual sprite files
    Idle.png
    Run.png
    Attack_1.png
    ...
  Character_Name/Sprites/   # Organized in subfolder
    Idle.png
    Run.png
    ...
```

### 🛠 **Testing Tools**
- **Sprite Test Utility**: Run `python test_sprites.py` to test sprite loading
- **Visual Inspector**: Interactive sprite viewer to check animations
- **Loading Diagnostics**: Detailed logging of sprite loading process

## Quick Start

### Windows Users
1. Double-click `start_game.bat` to launch the game launcher
2. Or run `python launcher.py` from command line

### Manual Start
1. Make sure Python 3.x is installed
2. Install required dependencies: `pip install pygame`
3. Run `python main.py` to start the main game

## Game Modes

### 1. Local Game (Recommended for beginners)
- Both players use the same computer
- Player 1: WASD + JKLUIO keys
- Player 2: Arrow keys + Numpad

### 2. LAN Multiplayer
- Both players must be on the same local network
- One player hosts, the other joins
- Automatic host discovery available

### 3. Manual IP Connection
- For when automatic discovery fails
- Enter the host's IP address manually

## Network Setup

### Requirements
- Both computers on the same local network (Wi-Fi or Ethernet)
- Port 12345 must be available (not blocked by firewall)
- Python 3.x with pygame installed on both computers

### Firewall Configuration
If connection fails, you may need to:

**Windows:**
1. Open Windows Defender Firewall
2. Click "Allow an app or feature through Windows Defender Firewall"
3. Click "Change Settings" then "Allow another app..."
4. Browse to your Python installation (usually `python.exe`)
5. Check both "Private" and "Public" networks
6. Click OK

**Alternative:** Temporarily disable firewall for testing

### Finding Your IP Address
The game launcher shows your IP address, or you can:
- Windows: Open Command Prompt and type `ipconfig`
- Look for "IPv4 Address" under your network adapter

## Controls

### 🎮 **Player 1 (WASD + JKLUIO)**
**Movement:**
- **W** - Jump
- **A** - Move left  
- **S** - Down (currently unused)
- **D** - Move right

**Combat:**
- **J** - Attack 1 (light attack)
- **K** - Attack 2 (heavy attack)
- **L** - Special Skill 1
- **U** - Special Skill 2  
- **I** - Special Skill 3 (if character has 3+ skills)
- **O** - Special Skill 4 (if character has 4+ skills)

### 🎮 **Player 2 (Arrow Keys + Numpad)**
**Movement:**
- **↑** - Jump
- **←** - Move left
- **↓** - Down (currently unused)  
- **→** - Move right

**Combat:**
- **Num 1** - Attack 1 (light attack)
- **Num 2** - Attack 2 (heavy attack)
- **Num 4** - Special Skill 1
- **Num 5** - Special Skill 2
- **Num 6** - Special Skill 3 (if character has 3+ skills) 
- **Num 8** - Special Skill 4 (if character has 4+ skills)

### ⚡ **Special Skills by Character**
Each character has unique special abilities:

- **Kunoichi**: Shadow Clone, Ninja Vanish
- **Lightning Mage**: Lightning Bolt, Chain Lightning  
- **Ninja Monk**: Meditation, Spirit Punch
- **Ninja Peasant**: Farm Tools, Humble Strike
- **Samurai**: Katana Slash, Honor Guard
- **Fire Wizard**: Fireball, Flame Jet
- **Wanderer Magician**: Magic Arrow, Arcane Sphere

### 🔥 **Combat Tips**
- **Movement + Attack**: Move while attacking for combo attacks
- **Jump Attacks**: Press W/↑ + J/K or Num1/2 for aerial attacks
- **Special Skills**: Each has a cooldown period after use
- **Skill Display**: Available skills and cooldowns shown on screen during gameplay

### 🛠 **Control Testing**
Use the built-in control tester to practice:
```bash
python test_controls.py
# or through the launcher: Option 4
```

The tester shows:
- Real-time key press feedback
- Control mappings for both players
- Suggested key combinations to practice

## Troubleshooting

### Common Issues

**"No games found on LAN"**
- Ensure both computers are on the same network
- Check firewall settings
- Try manual IP connection
- Use the network test utility

**"Connection failed"**
- Verify the IP address is correct
- Check if port 12345 is available
- Ensure host computer is actually hosting
- Try restarting both games

**"Port in use"**
- Close other instances of the game
- Restart the application
- Check if another program is using port 12345

**Game runs but controls don't work**
- Make sure the game window has focus
- Check if another program is capturing keyboard input
- Try restarting the game

### Network Testing
Use the launcher's "Test Network Connection" option or run:
```bash
python network_test.py
```

This will:
- Show your IP address
- Test port availability
- Scan for available games
- Test connections

### Performance Tips
- Close unnecessary programs to improve performance
- Ensure stable network connection
- Both players should have similar hardware specs for best experience

## File Structure

- `main.py` - Main game file with enhanced LAN support
- `launcher.py` - User-friendly game launcher
- `network_manager.py` - Improved networking with LAN discovery
- `network_test.py` - Network diagnostic utility
- `start_game.bat` - Windows batch file for easy launching
- `fighter.py` - Fighter character logic
- `character_select.py` - Character selection screen

## Advanced Usage

### Hosting a Game
1. Launch the game
2. Select "Host LAN Game"
3. Wait for the other player to connect
4. Your IP will be displayed for manual connections

### Joining a Game
1. Launch the game
2. Select "Join LAN Game"
3. Choose from discovered hosts or enter IP manually
4. Select your character and start fighting!

### Network Diagnostics
Run `python network_test.py` for detailed network testing:
- IP detection
- Port availability check
- LAN game scanning
- Connection testing

## Development Notes

### Network Improvements Made
1. **Automatic LAN Discovery**: Scans local network for available games
2. **Proper Message Framing**: Prevents data corruption in network transmission
3. **Error Recovery**: Better handling of connection failures
4. **IP Detection**: Automatically detects local IP for hosting
5. **Timeout Handling**: Prevents hanging on failed connections
6. **Synchronization**: Improved game state synchronization between players

### Technical Details
- Uses TCP sockets for reliable communication
- Implements message framing with size prefixes
- Supports both automatic discovery and manual IP entry
- Includes network diagnostic tools
- Compatible with Windows firewalls and NAT

## License

This project is for educational purposes. Original Street Fighter assets belong to their respective owners.

## Support

If you encounter issues:
1. Try the network test utility first
2. Check firewall settings
3. Ensure both players have the same game version
4. Use manual IP connection if auto-discovery fails

For persistent issues, ensure:
- Python 3.x is properly installed
- pygame is installed (`pip install pygame`)
- Both computers can ping each other
- No antivirus software is blocking the connection
