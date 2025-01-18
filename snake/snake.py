import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# -----------------------
# GAME CONSTANTS
# -----------------------
BLOCK_SIZE = 20  # Size of one grid block (in pixels)
GRID_WIDTH = 30  # Number of blocks horizontally
GRID_HEIGHT = 20 # Number of blocks vertically

SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

FPS = 10  # Game speed (frames per second)

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game with Random Keys")

# Font for on-screen text
font = pygame.font.SysFont("arial", 24)

# Clock to control game speed
clock = pygame.time.Clock()

# A pool of possible keys to pick from: letters + digits
KEY_POOL = [pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f,
            pygame.K_g, pygame.K_h, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l,
            pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r,
            pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x,
            pygame.K_y, pygame.K_z,
            pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, 
            pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]

def randomize_key_mapping():
    """
    Return a dict mapping random keys to directions.
    Directions are represented as (dx, dy), 
    where dx=1 means moving right, dx=-1 means left, etc.
    """
    chosen_keys = random.sample(KEY_POOL, 4)
    # Directions: UP, DOWN, LEFT, RIGHT in some order
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    # Shuffle directions so that every time the mapping might differ
    random.shuffle(directions)
    
    # Create a dictionary
    key_map = {}
    for i, k in enumerate(chosen_keys):
        key_map[k] = directions[i]
    return key_map

def draw_snake(snake_positions):
    """
    Draw each segment of the snake on the screen.
    """
    for (x, y) in snake_positions:
        rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(screen, (0, 255, 0), rect)

def draw_food(food_position):
    """
    Draw the food as a simple red block.
    """
    (fx, fy) = food_position
    rect = pygame.Rect(fx * BLOCK_SIZE, fy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(screen, (255, 0, 0), rect)

def generate_food(snake_positions):
    """
    Return a new (x, y) for the food that isn't occupied by the snake.
    """
    while True:
        fx = random.randint(0, GRID_WIDTH - 1)
        fy = random.randint(0, GRID_HEIGHT - 1)
        if (fx, fy) not in snake_positions:
            return (fx, fy)

def main():
    # Initial snake setup
    snake_positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
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
                    snake_positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
                    snake_direction = (1, 0)
                    snake_length = 3
                    food_position = generate_food(snake_positions)
                    key_map = randomize_key_mapping()
                    game_over = False
                else:
                    # Check if the key is in our current mapping
                    if event.key in key_map:
                        snake_direction = key_map[event.key]
                        # After pressing one of the keys, randomize again
                        key_map = randomize_key_mapping()

        if not game_over:
            # Update snake position
            head_x, head_y = snake_positions[0]
            dx, dy = snake_direction
            new_head = (head_x + dx, head_y + dy)
            
            # Collision check (with boundaries or self)
            if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
                new_head in snake_positions):
                game_over = True
            else:
                # Place the new head at the front
                snake_positions.insert(0, new_head)

                # Check if we eat the food
                if new_head == food_position:
                    # Increase snake length, generate new food
                    snake_length += 1
                    food_position = generate_food(snake_positions)
                else:
                    # If we didn't eat, remove the tail
                    if len(snake_positions) > snake_length:
                        snake_positions.pop()
        
        # Drawing
        screen.fill((0, 0, 0))  # black background
        
        if game_over:
            text_surface = font.render("Game Over! Press any key to restart.", True, (255, 255, 255))
            screen.blit(text_surface, (40, SCREEN_HEIGHT // 2))
        else:
            draw_snake(snake_positions)
            draw_food(food_position)
            
            # Display the current random key mapping for convenience
            # We’ll show which keys map to up/down/left/right
            # (Because directions is not strictly in that order, we label them by (dx, dy))
            info_y = 10
            for k in key_map:
                direction_str = f"{key_map[k]}"
                key_name = pygame.key.name(k)
                text_surface = font.render(f"Key '{key_name}' -> {direction_str}", True, (255, 255, 255))
                screen.blit(text_surface, (10, info_y))
                info_y += 25
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()