import pygame
import sys
import random
import asyncio

# Initialize Pygame
pygame.init()

# -----------------------
# GAME CONSTANTS
# -----------------------
BAR_HEIGHT = 150
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
font = pygame.font.Font("PixelOperator-Bold.ttf", 50)
big_font = pygame.font.Font("PixelOperator-Bold.ttf", 150)
letter_font = pygame.font.Font("MomcakeBold-WyonA.otf", 26)
arrow_font = pygame.font.Font("Arrows.ttf", 30)

# Clock to control game speed
clock = pygame.time.Clock()

# A pool of possible keys to pick from: letters
KEY_POOL = [pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f,
            pygame.K_g, pygame.K_h, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l,
            pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r,
            pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x,
            pygame.K_y, pygame.K_z]

# Music
eat_sound = pygame.mixer.Sound("Nom.wav")
gameover_sound = pygame.mixer.Sound("GameOver.wav")

# Sprites
snake_sprite = pygame.transform.scale(pygame.image.load("nyan2.jpg"), (BLOCK_SIZE, BLOCK_SIZE))
food_sprite = pygame.transform.scale(pygame.image.load("greendonut.png"), (BLOCK_SIZE, BLOCK_SIZE))

def draw_bar(score, highScore, key_map):
    bar_rect = pygame.Rect(0, SCREEN_HEIGHT -150, SCREEN_WIDTH, BAR_HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), bar_rect)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    highScore_text = font.render(f"High Score: {highScore}", True, (255, 255, 0))
    screen.blit(score_text, (20, SCREEN_HEIGHT - 100))  # Draw score in the bottom-left corner of the bar
    screen.blit(highScore_text, (250, SCREEN_HEIGHT - 100))
    
    # Render key mappings
    center_x = 800
    direction_labels = {"c": (0, -1), "d": (0, 1), "b": (-1, 0), "a": (1, 0)}
    offset_x = 100  # Horizontal offset for each label
    
    for i, (label, direction) in enumerate(direction_labels.items()):
        key = next((k for k, v in key_map.items() if v == direction), None)
        key_name = pygame.key.name(key) if key else "None"
        key_name_text = key_name.capitalize()
        key_name_surface = letter_font.render(key_name_text, True, (255, 255, 0))
        
        label_text = f"{label}: "
        label_surface = arrow_font.render(label_text, True, (255, 255, 255))

        label_x = center_x + i * offset_x
        label_y = SCREEN_HEIGHT - 45

        key_name_x = label_x + label_surface.get_width()
        key_name_y = label_y

        screen.blit(label_surface, (label_x, label_y))
        screen.blit(key_name_surface, (key_name_x, key_name_y))

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
    screen.blit(food_sprite, rect.topleft)

def generate_food(snake_positions):
    while True:
        fx = random.randint(0, GRID_WIDTH - 1)
        fy = random.randint(0, GRID_HEIGHT_PLAYABLE - 1)
        if (fx, fy) not in snake_positions:
            return (fx, fy)

async def main():
    # Initial snake setup
    score = 0
    highScore = 0
    last_move_time = pygame.time.get_ticks()    
    snake_positions = [(GRID_WIDTH // 2, GRID_HEIGHT_PLAYABLE // 2)]
    snake_direction = (1, 0)  # start moving right
    snake_length = 6
    
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
                    if event.key == pygame.K_SPACE:
                        # Press space bar to restart
                        if score > highScore:
                            highScore = score
                        snake_positions = [(GRID_WIDTH // 2, GRID_HEIGHT_PLAYABLE // 2)]
                        snake_direction = (1, 0)
                        snake_length = 6
                        food_position = generate_food(snake_positions)
                        key_map = randomize_key_mapping()
                        game_over = False
                        score = 0
                        last_move_time = pygame.time.get_ticks()
                else:
                    # Check if the key is in our current mapping
                    if event.key in key_map:
                        proposed_direction = key_map[event.key]

                        # Check if the proposed direction is opposite to the current direction
                        if (snake_direction[0] + proposed_direction[0] == 0) and \
                        (snake_direction[1] + proposed_direction[1] == 0):
                            # If opposite, do nothing (ignore this input)
                            pass
                        else:
                            # Update the direction if valid
                            snake_direction = proposed_direction

                        # After processing the key, randomize key mapping
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
                    eat_sound.play()
                else:
                    # If we didn't eat, remove the tail
                    if len(snake_positions) > snake_length:
                        snake_positions.pop()
        
        # Drawing   
        screen.fill((0, 0, 0))  # black background

        draw_bar(score, highScore, key_map)
        
        if game_over:
            gameover_sound.play()
            game_over_surface = big_font.render("GAME OVER", True, (255, 255, 0))
            text_surface = font.render("Press space bar to restart.", True, (255, 255, 255))
            screen.blit(game_over_surface, ((GRID_WIDTH * BLOCK_SIZE) // 2 - 320, (GRID_HEIGHT * BLOCK_SIZE) // 2 - 150))
            screen.blit(text_surface, ((GRID_WIDTH * BLOCK_SIZE) // 2 - 300, (GRID_HEIGHT * BLOCK_SIZE) // 2))
        else:
            draw_snake(snake_positions)
            draw_food(food_position)

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
