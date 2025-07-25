import pygame
import os

class Fighter():
  def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound, special_skills=None):
    self.player = player
    self.size = data[0]
    self.image_scale = data[1]
    self.offset = data[2]
    self.flip = flip
    self.animation_list = self.load_images(sprite_sheet, animation_steps)
    self.action = 0#0:idle #1:run #2:jump #3:attack1 #4: attack2 #5:hit #6:death #7:special1 #8:special2
    self.frame_index = 0
    self.image = self.animation_list[self.action][self.frame_index]
    self.update_time = pygame.time.get_ticks()
    self.rect = pygame.Rect((x, y, 80, 180))
    self.vel_y = 0
    self.running = False
    self.jump = False
    self.attacking = False
    self.attack_type = 0
    self.attack_cooldown = 0
    self.attack_sound = sound
    self.hit = False
    self.health = 100
    self.alive = True
    self.special_skills = special_skills or []
    self.special_cooldowns = [0, 0, 0, 0]  # Cooldowns for up to 4 special skills
    self.using_special = False
    self.special_type = 0

  def get_input_state(self):
    """Convert pygame key state to dictionary format"""
    keys = pygame.key.get_pressed()
    
    # Player 1 controls: WASD (movement) + JKLUIO (attacks/skills)
    if self.player == 1:
      return {
        # Movement keys
        'w': keys[pygame.K_w],        # Jump
        'a': keys[pygame.K_a],        # Move left 
        's': keys[pygame.K_s],        # Down/Block (unused currently)
        'd': keys[pygame.K_d],        # Move right
        # Attack/skill keys
        'j': keys[pygame.K_j],        # Attack 1
        'k': keys[pygame.K_k],        # Attack 2
        'l': keys[pygame.K_l],        # Special skill 1
        'u': keys[pygame.K_u],        # Special skill 2
        'i': keys[pygame.K_i],        # Special skill 3
        'o': keys[pygame.K_o]         # Special skill 4
      }
    # Player 2 controls: Arrow keys (movement) + Numpad (attacks/skills)
    else:
      return {
        # Movement keys
        'UP': keys[pygame.K_UP],      # Jump
        'LEFT': keys[pygame.K_LEFT],  # Move left
        'DOWN': keys[pygame.K_DOWN],  # Down/Block (unused currently)
        'RIGHT': keys[pygame.K_RIGHT], # Move right
        # Attack/skill keys
        'KP1': keys[pygame.K_KP1],    # Attack 1
        'KP2': keys[pygame.K_KP2],    # Attack 2
        'KP4': keys[pygame.K_KP4],    # Special skill 1
        'KP5': keys[pygame.K_KP5],    # Special skill 2
        'KP6': keys[pygame.K_KP6],    # Special skill 3
        'KP8': keys[pygame.K_KP8]     # Special skill 4
      }


  def load_images(self, sprite_sheet, animation_steps):
    #extract images from spritesheet
    animation_list = []
    for y, animation in enumerate(animation_steps):
      temp_img_list = []
      for x in range(animation):
        temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
        temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
      animation_list.append(temp_img_list)
    return animation_list


  def move(self, screen_width, screen_height, surface, target, round_over, network_input=None):
    SPEED = 10
    GRAVITY = 2
    dx = 0
    dy = 0
    self.running = False
    self.attack_type = 0

    # Get input state
    if network_input:
      key_state = network_input
    else:
      key_state = self.get_input_state()

    #can only perform other actions if not currently attacking
    if self.attacking == False and self.alive == True and round_over == False and self.using_special == False:
      #check player 1 controls (WASD + JKLUIO)
      if self.player == 1:
        #movement
        if key_state.get('a', False):
          dx = -SPEED
          self.running = True
        if key_state.get('d', False):
          dx = SPEED
          self.running = True
        #jump
        if key_state.get('w', False) and self.jump == False:
          self.vel_y = -30
          self.jump = True
        #basic attacks
        if key_state.get('j', False) or key_state.get('k', False):
          self.attack(target)
          if key_state.get('j', False):
            self.attack_type = 1
          if key_state.get('k', False):
            self.attack_type = 2
        #special skills (dynamically assign based on available skills)
        # L key - First special skill
        if key_state.get('l', False) and len(self.special_skills) > 0:
          self.use_special_skill(target, 0)
        # U key - Second special skill  
        if key_state.get('u', False) and len(self.special_skills) > 1:
          self.use_special_skill(target, 1)
        # I key - Third special skill
        if key_state.get('i', False) and len(self.special_skills) > 2:
          self.use_special_skill(target, 2)
        # O key - Fourth special skill
        if key_state.get('o', False) and len(self.special_skills) > 3:
          self.use_special_skill(target, 3)

      #check player 2 controls (Arrow keys + Numpad)
      if self.player == 2:
        #movement
        if key_state.get('LEFT', False):
          dx = -SPEED
          self.running = True
        if key_state.get('RIGHT', False):
          dx = SPEED
          self.running = True
        #jump
        if key_state.get('UP', False) and self.jump == False:
          self.vel_y = -30
          self.jump = True
        #basic attacks
        if key_state.get('KP1', False) or key_state.get('KP2', False):
          self.attack(target)
          if key_state.get('KP1', False):
            self.attack_type = 1
          if key_state.get('KP2', False):
            self.attack_type = 2
        #special skills (dynamically assign based on available skills)
        # KP4 - First special skill
        if key_state.get('KP4', False) and len(self.special_skills) > 0:
          self.use_special_skill(target, 0)
        # KP5 - Second special skill
        if key_state.get('KP5', False) and len(self.special_skills) > 1:
          self.use_special_skill(target, 1)
        # KP6 - Third special skill
        if key_state.get('KP6', False) and len(self.special_skills) > 2:
          self.use_special_skill(target, 2)
        # KP8 - Fourth special skill
        if key_state.get('KP8', False) and len(self.special_skills) > 3:
          self.use_special_skill(target, 3)


    #apply gravity
    self.vel_y += GRAVITY
    dy += self.vel_y

    #ensure player stays on screen
    if self.rect.left + dx < 0:
      dx = -self.rect.left
    if self.rect.right + dx > screen_width:
      dx = screen_width - self.rect.right
    if self.rect.bottom + dy > screen_height - 110:
      self.vel_y = 0
      self.jump = False
      dy = screen_height - 110 - self.rect.bottom

    #ensure players face each other
    if target.rect.centerx > self.rect.centerx:
      self.flip = False
    else:
      self.flip = True

    #apply attack cooldown
    if self.attack_cooldown > 0:
      self.attack_cooldown -= 1
    
    #apply special skill cooldowns
    for i in range(len(self.special_cooldowns)):
      if self.special_cooldowns[i] > 0:
        self.special_cooldowns[i] -= 1

    #update player position
    self.rect.x += dx
    self.rect.y += dy

  def use_special_skill(self, target, skill_index):
    if (skill_index < len(self.special_skills) and 
        self.special_cooldowns[skill_index] == 0 and 
        not self.using_special):
      
      self.using_special = True
      self.special_type = skill_index + 1
      if self.attack_sound:
        self.attack_sound.play()
      
      # Special skill effects based on character skills
      skill_name = self.special_skills[skill_index]
      
      # Kunoichi skills
      if skill_name == 'shadow_clone':
        self.special_attack(target, 30, 140)
      elif skill_name == 'ninja_vanish':
        self.special_attack(target, 25, 120)
      elif skill_name == 'shadow_strike':
        self.special_attack(target, 25, 150)
      elif skill_name == 'invisibility':
        self.special_attack(target, 15, 100)
      elif skill_name == 'smoke_bomb':
        self.special_attack(target, 20, 120)
      
      # Lightning Mage skills
      elif skill_name == 'lightning_bolt':
        self.special_attack(target, 35, 200)
      elif skill_name == 'chain_lightning':
        self.special_attack(target, 30, 180)
      
      # Ninja Monk skills
      elif skill_name == 'meditation':
        self.special_attack(target, 15, 80)  # Healing/defense skill
      elif skill_name == 'spirit_punch':
        self.special_attack(target, 28, 160)
      
      # Ninja Peasant skills
      elif skill_name == 'farm_tools':
        self.special_attack(target, 20, 110)
      elif skill_name == 'humble_strike':
        self.special_attack(target, 25, 130)
      
      # Samurai skills
      elif skill_name == 'katana_slash':
        self.special_attack(target, 32, 110)
      elif skill_name == 'honor_guard':
        self.special_attack(target, 18, 90)
      
      # Fire Wizard skills
      elif skill_name == 'fireball':
        self.special_attack(target, 28, 170)
      elif skill_name == 'flame_jet':
        self.special_attack(target, 26, 160)
      
      # Wanderer Magician skills
      elif skill_name == 'magic_arrow':
        self.special_attack(target, 24, 140)
      elif skill_name == 'arcane_sphere':
        self.special_attack(target, 30, 180)
      
      # Generic/fallback skills
      elif skill_name == 'magic_missile':
        self.special_attack(target, 25, 160)
      elif skill_name == 'teleport':
        self.special_attack(target, 20, 100)
      elif skill_name == 'ice_shard':
        self.special_attack(target, 22, 150)
      elif skill_name == 'blade_fury':
        self.special_attack(target, 40, 130)
      elif skill_name == 'warrior_spirit':
        self.special_attack(target, 25, 120)
      elif skill_name == 'battle_cry':
        self.special_attack(target, 22, 140)
      elif skill_name == 'tactical_strike':
        self.special_attack(target, 28, 125)
      
      # Default skill for unknown skills
      else:
        self.special_attack(target, 25, 130)
        print(f"Unknown skill: {skill_name} - using default effect")
      
      # Archer skills
      elif skill_name == 'arrow_rain':
        self.special_attack(target, 24, 200)
      elif skill_name == 'precision_shot':
        self.special_attack(target, 35, 250)
      
      # Monk skills
      elif skill_name == 'meditation':
        self.special_attack(target, 15, 80)
      elif skill_name == 'spirit_punch':
        self.special_attack(target, 30, 100)
      
      # Peasant skills
      elif skill_name == 'farm_tools':
        self.special_attack(target, 18, 90)
      elif skill_name == 'humble_strike':
        self.special_attack(target, 20, 95)
      
      # Warrior skills
      elif skill_name == 'sword_slash':
        self.special_attack(target, 26, 115)
      elif skill_name == 'shield_bash':
        self.special_attack(target, 22, 105)
      
      else:
        self.special_attack(target, 15, 120)  # Default special
      
      self.special_cooldowns[skill_index] = 300  # 5 second cooldown

  def special_attack(self, target, damage, range_width):
    attacking_rect = pygame.Rect(
      self.rect.centerx - (range_width * self.flip), 
      self.rect.y, 
      range_width, 
      self.rect.height
    )
    if attacking_rect.colliderect(target.rect):
      target.health -= damage
      target.hit = True

  #handle animation updates
  def update(self):
    #check what action the player is performing
    if self.health <= 0:
      self.health = 0
      self.alive = False
      self.update_action(6)#6:death
    elif self.hit == True:
      self.update_action(5)#5:hit
    elif self.using_special == True:
      if self.special_type == 1:
        self.update_action(7)#7:special1
      elif self.special_type == 2:
        self.update_action(8)#8:special2
    elif self.attacking == True:
      if self.attack_type == 1:
        self.update_action(3)#3:attack1
      elif self.attack_type == 2:
        self.update_action(4)#4:attack2
    elif self.jump == True:
      self.update_action(2)#2:jump
    elif self.running == True:
      self.update_action(1)#1:run
    else:
      self.update_action(0)#0:idle

    animation_cooldown = 50
    #update image
    self.image = self.animation_list[self.action][self.frame_index]
    #check if enough time has passed since the last update
    if pygame.time.get_ticks() - self.update_time > animation_cooldown:
      self.frame_index += 1
      self.update_time = pygame.time.get_ticks()
    #check if the animation has finished
    if self.frame_index >= len(self.animation_list[self.action]):
      #if the player is dead then end the animation
      if self.alive == False:
        self.frame_index = len(self.animation_list[self.action]) - 1
      else:
        self.frame_index = 0
        #check if an attack was executed
        if self.action == 3 or self.action == 4:
          self.attacking = False
          self.attack_cooldown = 20
        #check if special skill was executed
        if self.action == 7 or self.action == 8:
          self.using_special = False
        #check if damage was taken
        if self.action == 5:
          self.hit = False
          #if the player was in the middle of an attack, then the attack is stopped
          self.attacking = False
          self.using_special = False
          self.attack_cooldown = 20


  def attack(self, target):
    if self.attack_cooldown == 0:
      #execute attack
      self.attacking = True
      if self.attack_sound:  # Only play if sound exists
        self.attack_sound.play()
      attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
      if attacking_rect.colliderect(target.rect):
        target.health -= 10
        target.hit = True


  def update_action(self, new_action):
    #check if the new action is different to the previous one
    if new_action != self.action:
      self.action = new_action
      #update the animation settings
      self.frame_index = 0
      self.update_time = pygame.time.get_ticks()

  def draw(self, surface):
    img = pygame.transform.flip(self.image, self.flip, False)
    draw_x = self.rect.x - (self.offset[0] * self.image_scale)
    draw_y = self.rect.y - (self.offset[1] * self.image_scale)
    
    # Debug: Print fighter draw info occasionally
    if hasattr(self, '_debug_counter'):
      self._debug_counter += 1
    else:
      self._debug_counter = 0
    
    if self._debug_counter % 60 == 0:  # Print every 60 frames (1 second at 60 FPS)
      print(f"Fighter {self.player}: Drawing at ({draw_x}, {draw_y}), image size: {img.get_size()}, action: {self.action}")
    
    surface.blit(img, (draw_x, draw_y))

  def get_input_state(self):
    """Get current input state for network transmission"""
    key = pygame.key.get_pressed()
    if self.player == 1:
      return {
        'a': key[pygame.K_a],
        'd': key[pygame.K_d],
        'w': key[pygame.K_w],
        's': key[pygame.K_s],
        'j': key[pygame.K_j],
        'k': key[pygame.K_k],
        'l': key[pygame.K_l],
        'u': key[pygame.K_u],
        'i': key[pygame.K_i],
        'o': key[pygame.K_o]
      }
    else:
      return {
        'LEFT': key[pygame.K_LEFT],
        'RIGHT': key[pygame.K_RIGHT],
        'UP': key[pygame.K_UP],
        'DOWN': key[pygame.K_DOWN],
        'KP1': key[pygame.K_KP1],
        'KP2': key[pygame.K_KP2],
        'KP4': key[pygame.K_KP4],
        'KP5': key[pygame.K_KP5],
        'KP7': key[pygame.K_KP7],
        'KP8': key[pygame.K_KP8]
      }

  def load_character_sprite_sheet(self, character_name):
    """Load sprite sheet for the specific character from your folder structure"""
    sprite_paths = [
        f"images/{character_name}/spritesheet.png",
        f"images/{character_name}/sprite_sheet.png",
        f"images/{character_name}/{character_name}.png",
        f"images/{character_name}/{character_name.lower()}.png"
    ]
    
    # Also try to find any large image that could be a sprite sheet
    character_folder = f"images/{character_name}/"
    if os.path.exists(character_folder):
        for file in os.listdir(character_folder):
            if file.endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(character_folder, file)
                try:
                    test_img = pygame.image.load(file_path)
                    # If image is large enough to be a sprite sheet
                    if test_img.get_width() >= 500 and test_img.get_height() >= 500:
                        sprite_paths.insert(0, file_path)  # Add to front of list
                except:
                    continue
    
    for path in sprite_paths:
        try:
            sprite_sheet = pygame.image.load(path)
            print(f"Loaded sprite sheet: {path}")
            return sprite_sheet
        except:
            continue
    
    # If no sprite sheet found, create placeholder
    print(f"No sprite sheet found for {character_name}, creating placeholder")
    return self.create_placeholder_sprite_sheet()

  def create_placeholder_sprite_sheet(self):
    """Create a placeholder sprite sheet with colored rectangles"""
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