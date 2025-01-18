import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# -----------------------
# GAME CONSTANTS
# -----------------------
BAR_HEIGHT = 75
BLOCK_SIZE = 30  # Size of one grid block (in pixels)
GRID_WIDTH = 40  # Number of blocks horizontally
GRID_HEIGHT = 25 # Number of blocks vertically
GRID_HEIGHT_PLAYABLE = GRID_HEIGHT - BAR_HEIGHT // BLOCK_SIZE

SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
SCREEN_HEIGHT_TOTAL = GRID_HEIGHT_PLAYABLE * BLOCK_SIZE + BAR_HEIGHT

FPS = 60 # Game speed (frames per second)
MOVE_DELAY = 100

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Funny Snake")
snake_sprite = pygame.image.load("nyan2.jpg")
snake_sprite = pygame.transform.scale(snake_sprite, (BLOCK_SIZE, BLOCK_SIZE))

# Font for on-screen text
font = pygame.font.Font("PixelOperator-Bold.ttf", 24)
big_font = pygame.font.Font("PixelOperator-Bold.ttf", 70)
letter_font = pygame.font.Font("MomcakeBold-WyonA.otf", 26)

# Clock to control game speed
clock = pygame.time.Clock()

# A pool of possible keys to pick from: letters + digits
KEY_POOL = [pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f,
            pygame.K_g, pygame.K_h, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l,
            pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r,
            pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x,
            pygame.K_y, pygame.K_z]

def draw_bar(score, key_map):
    bar_rect = pygame.Rect(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, BAR_HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), bar_rect)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (20, SCREEN_HEIGHT - 45))  # Draw score in the top-left corner of the bar
    
    # Render key mappings
    center_x = 800
    direction_labels = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}
    offset_x = 100  # Horizontal offset for each label
    
    for i, (label, direction) in enumerate(direction_labels.items()):
        key = next((k for k, v in key_map.items() if v == direction), None)
        key_name = pygame.key.name(key) if key else "None"
        key_text = font.render(f"{label}: {key_name.capitalize()}", True, (255, 255, 255))
        screen.blit(key_text, (center_x + i * offset_x, SCREEN_HEIGHT - 45))

def randomize_key_mapping():
    chosen_keys = random.sample(KEY_POOL, 4)
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    # Shuffle directions so that every time the mapping might differ
    random.shuffle(directions)
    
    # Create a dictionary
    key_map = {}
    for i, k in enumerate(chosen_keys):
        key_map[k] = directions[i]
    return key_map

def randomize_pressed_key_mapping(key_map, pressed_key):
    """
    Randomize the key for the pressed direction while keeping other mappings unchanged.
    """
    if pressed_key in key_map:
        # Get the direction currently assigned to the pressed key
        direction = key_map[pressed_key]
        
        # Available keys are those not currently in use by the mapping
        used_keys = set(key_map.keys())
        available_keys = list(set(KEY_POOL) - used_keys)
        
        # Randomly pick a new key from the available keys
        new_key = random.choice(available_keys)
        
        # Update the mapping: Remove the old key and assign the new one
        del key_map[pressed_key]
        key_map[new_key] = direction
        
        return key_map

def draw_snake(snake_positions):
    """
    Draw each segment of the snake on the screen.
    """
    for (x, y) in snake_positions:
        rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        screen.blit(snake_sprite, rect.topleft)

def draw_food(food_position):
    (fx, fy) = food_position
    rect = pygame.Rect(fx * BLOCK_SIZE, fy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(screen, (255, 0, 0), rect)

def generate_food(snake_positions):
    while True:
        fx = random.randint(0, GRID_WIDTH - 1)
        fy = random.randint(0, GRID_HEIGHT_PLAYABLE - 1)
        if (fx, fy) not in snake_positions:
            return (fx, fy)

def main():
    # Initial snake setup
    score = 0
    last_move_time = pygame.time.get_ticks()
    snake_sprite = pygame.image.load("nyan2.jpg")
    snake_sprite = pygame.transform.scale(snake_sprite, (BLOCK_SIZE, BLOCK_SIZE))
    snake_positions = [(GRID_WIDTH // 2, GRID_HEIGHT_PLAYABLE // 2)]
    snake_direction = (1, 0)  # start moving right
    snake_length = 3
    
    # Generate initial food
    food_position = generate_food(snake_positions)
    
    # Random key mapping
    key_map = randomize_key_mapping()
    
    game_over = False
    
    while True:
        # Event processing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if game_over:
                    # Press any key to restart
                    snake_positions = [(GRID_WIDTH // 2, GRID_HEIGHT_PLAYABLE // 2)]
                    snake_direction = (1, 0)
                    snake_length = 3
                    food_position = generate_food(snake_positions)
                    key_map = randomize_key_mapping()
                    game_over = False
                    score = 0
                    last_move_time = pygame.time.get_ticks()
                else:
                    # Check if the key is in our current mapping
                    if event.key in key_map:
                        snake_direction = key_map[event.key]
                        # After pressing one of the keys, randomize again
                        key_map = randomize_pressed_key_mapping(key_map, event.key)

        current_time = pygame.time.get_ticks()
        if not game_over and current_time - last_move_time >= MOVE_DELAY:
            last_move_time = current_time
            # Update snake position
            head_x, head_y = snake_positions[0]
            dx, dy = snake_direction
            new_head = (head_x + dx, head_y + dy)
            print(GRID_HEIGHT, GRID_HEIGHT_PLAYABLE, BAR_HEIGHT, new_head)
            new_head = (new_head[0] % GRID_WIDTH,  new_head[1] % GRID_HEIGHT_PLAYABLE)

            # Collision check (with self)
            if (new_head in snake_positions):
                game_over = True
            else:
                # Place the new head at the front
                snake_positions.insert(0, new_head)

                # Check if we eat the food
                if new_head == food_position:
                    # Increase snake length, generate new food
                    snake_length += 1
                    food_position = generate_food(snake_positions)
                    score += 1
                else:
                    # If we didn't eat, remove the tail
                    if len(snake_positions) > snake_length:
                        snake_positions.pop()
        
        # Drawing   
        screen.fill((0, 0, 0))  # black background

        draw_bar(score, key_map)
        
        if game_over:
            game_over_surface = big_font.render("GAME OVER", True, (255, 255, 0))
            text_surface = font.render("Press any key to restart.", True, (255, 255, 255))
            screen.blit(game_over_surface, (150, 150))
            screen.blit(text_surface, (30, 350))
        else:
            draw_snake(snake_positions)
            draw_food(food_position)
            
            # Define the mapping from directions to (dx, dy) tuples
            # direction_labels = {
            #     "up": (0, -1),
            #     "down": (0, 1),
            #     "left": (-1, 0),
            #     "right": (1, 0)
            # }

            # center_x = 260
            # center_y = 60  # Distance from the top of the screen

            # # Offset distance from the center for text placement
            # offset = 50  # Adjust as needed for spacing

            # for label, direction in direction_labels.items():
            #     # Find the key mapped to the current direction
            #     key = next((k for k, v in key_map.items() if v == direction), None)
            #     # Get the name of the key (or display "None" if no key is mapped)
            #     key_name = pygame.key.name(key) if key is not None else "None"
                
            #     # Define text for the label and key_name
            #     label_text = f"{label.capitalize()}: "
            #     key_name_text = key_name.capitalize()

            #     # Render the label text (white)
            #     label_surface = font.render(label_text, True, (255, 255, 255))

            #     # Render the key_name text (bright yellow)
            #     key_name_surface = letter_font.render(key_name_text, True, (255, 255, 0))

            #     # Calculate the position for the label and key_name
            #     label_x = center_x + direction[0] * offset
            #     label_y = center_y + direction[1] * offset

            #     key_name_x = label_x + label_surface.get_width()  # Position the key_name text after the label
            #     key_name_y = label_y

            #     # Draw both parts of the text on the screen
            #     screen.blit(label_surface, (label_x, label_y))
            #     screen.blit(key_name_surface, (key_name_x, key_name_y))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()