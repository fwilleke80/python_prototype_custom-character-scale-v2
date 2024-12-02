import pygame
import sys
import math
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1280, 720

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Mouse Circle with Random Points")

# Font setup
font = pygame.font.Font(None, 24)  # Default font, size 24

# Number of points
num_points = 8

# Generate 10 random control points
def generate_random_points(num_points, width, height, scale_min, scale_max):
    points = []
    for _ in range(num_points):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        scale_value = random.randint(scale_min, scale_max)
        points.append({"pos": (x, y), "scaleValue": scale_value})
    return points

# Generate control points
control_points = generate_random_points(num_points, WIDTH, HEIGHT, 10, 150)

# Function to compute distance
def distance(point1, point2):
    dx = point1[0] - point2[0]
    dy = point1[1] - point2[1]
    return math.sqrt(dx ** 2 + dy ** 2)

# Computes a scale from the participating points.
def get_object_scale(control_points, object_pos):
    epsilon = 1e-6  # Small value to prevent division by zero
    weighted_sum = 0.0
    total_weight = 0.0

    for point in control_points:
        dist = distance(point["pos"], object_pos)
        weight = 1.0 / (dist + epsilon)

        weighted_sum += weight * point["scaleValue"]
        total_weight += weight

    return (weighted_sum / total_weight) if total_weight > epsilon else 0.0

# Main loop
clock = pygame.time.Clock()
while True:
    # Handle events
    for event in pygame.event.get():
        # Quit
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Handle key presses
        if event.type == pygame.KEYDOWN:
            # SPACE key
            if event.key == pygame.K_SPACE:
                # Generate a new set of control points
                control_points = generate_random_points(10, WIDTH, HEIGHT, 10, 150)

    # Query mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pos = (mouse_x, mouse_y)

    # Compute radius based on control points
    mouse_circle_radius = get_object_scale(control_points, mouse_pos)

    # Clear screen
    screen.fill(BLACK)

    # Draw control points, circles, and sizes
    for point in control_points:
        x, y = point["pos"]
        size = point["scaleValue"]
        pygame.draw.circle(screen, WHITE, (x, y), size, 1)  # Circle
        pygame.draw.circle(screen, RED, (x, y), 2)         # Point

        # Render size as text
        size_text = font.render(str(size), True, WHITE)
        screen.blit(size_text, (x + size + 5, y - 10))  # Offset text slightly to the right and up

    # Draw circle around the mouse cursor
    pygame.draw.circle(screen, YELLOW, mouse_pos, int(mouse_circle_radius), 1)

    # Display mouse circle size as text
    radius_text = font.render(f"{mouse_circle_radius:.2f}", True, WHITE)
    screen.blit(radius_text, (mouse_x + int(mouse_circle_radius) + 10, mouse_y - 10))  # Offset text to the right

    # Update the display
    pygame.display.flip()
    clock.tick(60)
