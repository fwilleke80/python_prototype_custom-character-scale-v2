import pygame
import pygame.gfxdraw
import sys
import math
import random


# Settings
WIDTH, HEIGHT = 1280, 720 # Screen dimensions
DEFAULT_POINT_MIN_VALUE = 10 # Minimum value for random points
DEFAULT_POINT_MAX_VALUE = 150 # Maximum value for random points
DEFAULT_POINT_VALUE = 50 # Default point value for manually added points
INITIAL_NUM_POINTS = 3 # Number of initial points
FONT_SIZE = 24 # Font size
TOLERANCE_RADIUS = 10 # Tolerance for detecting clicks on existing points
DRAW_SHADED = True # Draw circles filled & shaded
DRAW_OUTLINES = True # Draw circle outlines (only has an effect if DRAW_SHADED == True)
DRAW_ANTIALIASED = True # Use antialising for text and lines


# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (160, 160, 160)
BACKGROUND = (24, 24, 64)
BACKGROUND_BRIGHT = (64, 64, 192)
CONTROLPOINT = (128, 0, 0)
CONTROLPOINT_RADIUS = (255, 160, 64)
MOUSE_CENTER = (0, 0, 0)
RESULT_RADIUS = (255, 255, 0)

# Initialize pygame
pygame.init()

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Weighted character scaling v2 - Prototype")

# Font setup
font = pygame.font.Font(None, FONT_SIZE)  # Default font, size 24

# Weighting modes
weighting_mode = 0
weighting_modes = [
    "Inverse Linear",
    "Inverse Square",
    "Exponential Decay",
    "Gaussian Weighting",
    "Max-Nearby Influence",
    "Weighted Median",
    "Harmonic Mean"
]

# Color remapping modes
remapping_mode = 0
remapping_modes = [
    "None",
    "Square",
    "Root"
]

# Generate random control points
def generate_random_point(width, height, scale_min, scale_max):
    x = random.randint(0, width - 1)
    y = random.randint(0, height - 1)
    scale_value = random.randint(scale_min, scale_max)
    return {"pos": (x, y), "value": scale_value}

# Generate initial control points
control_points = [generate_random_point(WIDTH, HEIGHT, DEFAULT_POINT_MIN_VALUE, DEFAULT_POINT_MAX_VALUE) for _ in range(INITIAL_NUM_POINTS)]

# Function to compute distance
def distance(point1, point2):
    dx = point1[0] - point2[0]
    dy = point1[1] - point2[1]
    return math.sqrt(dx ** 2 + dy ** 2)

# Inverse Linear
def get_object_scale_linear(control_points, object_pos):
    epsilon = 1e-8
    weighted_sum = 0.0
    total_weight = 0.0

    for point in control_points:
        dist = distance(point["pos"], object_pos)
        weight = 1.0 / (dist + epsilon)

        weighted_sum += weight * point["value"]
        total_weight += weight

    return (weighted_sum / total_weight) if total_weight > epsilon else 0.0

# Inverse Square
def get_object_scale_inverse_square(control_points, object_pos):
    epsilon = 1e-8
    weighted_sum = 0.0
    total_weight = 0.0

    for point in control_points:
        dist = distance(point["pos"], object_pos)
        weight = 1.0 / ((dist ** 2) + epsilon)

        weighted_sum += weight * point["value"]
        total_weight += weight

    return (weighted_sum / total_weight) if total_weight > epsilon else 0.0

# Exponential Decay
def get_object_scale_exponential(control_points, object_pos):
    epsilon = 1e-8
    decay_factor = 0.05
    weighted_sum = 0.0
    total_weight = 0.0

    for point in control_points:
        dist = distance(point["pos"], object_pos)
        weight = math.exp(-dist * decay_factor)

        weighted_sum += weight * point["value"]
        total_weight += weight

    return (weighted_sum / total_weight) if total_weight > epsilon else sum(p["value"] for p in control_points) / len(control_points)

# Gaussian Weighting
def get_object_scale_gaussian(control_points, object_pos):
    epsilon = 1e-8
    sigma = 100
    weighted_sum = 0.0
    total_weight = 0.0

    for point in control_points:
        dist = distance(point["pos"], object_pos)
        weight = math.exp(-((dist ** 2) / (2 * (sigma ** 2))))

        weighted_sum += weight * point["value"]
        total_weight += weight

    return (weighted_sum / total_weight) if total_weight > epsilon else sum(p["value"] for p in control_points) / len(control_points)

# Max-Nearby Influence
def get_object_scale_max_nearby(control_points, object_pos, k=3):
    epsilon = 1e-8
    distances = [
        (distance(point["pos"], object_pos), point["value"])
        for point in control_points
    ]
    distances = sorted(distances, key=lambda x: x[0])[:k]

    weighted_sum = 0.0
    total_weight = 0.0

    for dist, scale in distances:
        weight = 1.0 / (dist + epsilon)
        weighted_sum += weight * scale
        total_weight += weight

    return (weighted_sum / total_weight) if total_weight > epsilon else 0.0

# Weighted Median
def get_object_scale_weighted_median(control_points, object_pos):
    epsilon = 1e-8
    weighted_points = [
        (point["value"], 1.0 / (distance(point["pos"], object_pos) + epsilon))
        for point in control_points
    ]
    weighted_points = sorted(weighted_points, key=lambda x: x[0])

    total_weight = sum(w for _, w in weighted_points)
    cumulative_weight = 0.0

    for scale, weight in weighted_points:
        cumulative_weight += weight
        if cumulative_weight >= total_weight / 2:
            return scale

    return sum(p["value"] for p in control_points) / len(control_points)

# Harmonic Mean
def get_object_scale_harmonic_mean(control_points, object_pos):
    epsilon = 1e-8
    weighted_inverse = 0.0
    total_weight = 0.0

    for point in control_points:
        dist = distance(point["pos"], object_pos)
        weight = 1.0 / (dist + epsilon)

        weighted_inverse += weight / point["value"]
        total_weight += weight

    return (total_weight / weighted_inverse) if weighted_inverse > epsilon else sum(p["value"] for p in control_points) / len(control_points)

# Prompt user for a scale value (simple implementation)
def prompt_for_scale(defaultValue = DEFAULT_POINT_VALUE):
    running = True
    user_input = str(defaultValue)
    cursor_visible = True  # Cursor visibility toggle
    cursor_timer = 0  # Timer for blinking effect

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Confirm input
                    try:
                        return int(user_input)
                    except ValueError:
                        return None
                elif event.key == pygame.K_BACKSPACE:  # Delete last character
                    user_input = user_input[:-1]
                elif event.unicode.isdigit():  # Add digit to input
                    user_input += event.unicode
                elif event.key == pygame.K_ESCAPE:  # Cancel input
                    return None

        # Blinking cursor logic
        cursor_timer += 1
        if cursor_timer >= 30:  # Adjust blinking speed
            cursor_visible = not cursor_visible
            cursor_timer = 0

        # Calculate the size of the prompt and input text
        prompt_text = font.render("Enter point value (ESC to cancel):", True, WHITE)
        input_text = font.render(user_input, True, WHITE)
        input_with_cursor = user_input + "|" if cursor_visible else user_input
        input_text_with_cursor = font.render(input_with_cursor, True, WHITE)
        prompt_rect = pygame.Rect(5, 5, max(prompt_text.get_width(), input_text_with_cursor.get_width()) + 10, 80)

        # Draw a background rectangle for the prompt area
        pygame.draw.rect(screen, BACKGROUND_BRIGHT, prompt_rect)

        # Render prompt and input text
        screen.blit(prompt_text, (10, 10))
        screen.blit(input_text_with_cursor, (10, 50))
        pygame.display.flip()

# Handle mouse clicks
def handle_mouse_click(event, control_points, new_scale):
    if event.button == 1:  # Left click
        for point in control_points:
            if distance(event.pos, point["pos"]) <= TOLERANCE_RADIUS:
                control_points.remove(point)  # Remove point if near
                return
        # Otherwise, add a new point
        control_points.append({"pos": event.pos, "value": new_scale})
    elif event.button == 3:  # Right click
        for point in control_points:
            if distance(event.pos, point["pos"]) <= TOLERANCE_RADIUS:
                new_scale = prompt_for_scale(point["value"])
                if new_scale is not None:
                    point["value"] = new_scale
                    default_scale = new_scale
                break

# Blends two integer RGB colors, using t as blend factor (0.0 .. 1.0)
def blend_color(color1: tuple, color2: tuple, t: float) -> tuple:
    def blend(val1, val2, t: float):
        return val1 + t * (val2 - val1)

    r = round(blend(color1[0], color2[0], t))
    g = round(blend(color1[1], color2[1], t))
    b = round(blend(color1[2], color2[2], t))

    return (r, g, b)

# Maps a value from 0.0 .. 1.0 range to minimum .. maximum range.
def map_01_to_range(val: float, minimum: float, maximum: float) -> float:
    return minimum + val * (maximum - minimum)

# Apples value remapping (or not).
def remap_value(value, mode):
    if remapping_mode == 1:
        # Square value
        return value * value
    elif remapping_mode == 2:
        # Root value
        return math.sqrt(value)
    # Return unchanged value
    return value


# Main loop
clock = pygame.time.Clock()
current_scale = DEFAULT_POINT_VALUE
while True:
    # Handle events
    for event in pygame.event.get():
        # Quit
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Keyboard input
        if event.type == pygame.KEYDOWN:
            # Regenerate points
            if event.key == pygame.K_SPACE:
                control_points = [generate_random_point(WIDTH, HEIGHT, DEFAULT_POINT_MIN_VALUE, DEFAULT_POINT_MAX_VALUE) for _ in range(len(control_points))]
            # Add random point
            elif event.key == pygame.K_UP and len(control_points) < 100:
                control_points.append(generate_random_point(WIDTH, HEIGHT, DEFAULT_POINT_MIN_VALUE, DEFAULT_POINT_MAX_VALUE))
            # Remove point
            elif event.key == pygame.K_DOWN and len(control_points) > 1:
                control_points.pop()
            # Cycle interpolation mode forward
            elif event.key == pygame.K_b:
                weighting_mode = (weighting_mode + 1) % len(weighting_modes)
            # Cycle interpolation mode backward
            elif event.key == pygame.K_n:
                weighting_mode = (weighting_mode - 1) % len(weighting_modes)
            # Cycle color remapping mode
            elif event.key == pygame.K_y:
                remapping_mode = (remapping_mode + 1) % 3
            # Toggle outlines
            elif event.key == pygame.K_x:
                DRAW_OUTLINES = not DRAW_OUTLINES
            # Toggle shading
            elif event.key == pygame.K_c:
                DRAW_SHADED = not DRAW_SHADED
            # Toggle antialiasing
            elif event.key == pygame.K_a:
                DRAW_ANTIALIASED = not DRAW_ANTIALIASED
        # Mouse input
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_mouse_click(event, control_points, current_scale if current_scale != 0 else DEFAULT_POINT_VALUE)

    # Query mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pos = (mouse_x, mouse_y)

    # Compute radius based on control points and weighting mode
    weighting_mode_text = weighting_modes[weighting_mode]
    if weighting_mode == 0:
        mouse_circle_radius = get_object_scale_linear(control_points, mouse_pos)
    elif weighting_mode == 1:
        mouse_circle_radius = get_object_scale_inverse_square(control_points, mouse_pos)
    elif weighting_mode == 2:
        mouse_circle_radius = get_object_scale_exponential(control_points, mouse_pos)
    elif weighting_mode == 3:
        mouse_circle_radius = get_object_scale_gaussian(control_points, mouse_pos)
    elif weighting_mode == 4:
        mouse_circle_radius = get_object_scale_max_nearby(control_points, mouse_pos)
    elif weighting_mode == 5:
        mouse_circle_radius = get_object_scale_weighted_median(control_points, mouse_pos)
    elif weighting_mode == 6:
        mouse_circle_radius = get_object_scale_harmonic_mean(control_points, mouse_pos)
    current_scale = int(mouse_circle_radius)

    # Clear screen
    screen.fill(BACKGROUND)

    # Compute minimum and maximum point value
    if control_points:
        min_point_value = min(point["value"] for point in control_points)
        max_point_value = max(point["value"] for point in control_points)

    # Control points draw pass 1: Normalize point value and draw control points filled radius
    sorted_points = sorted(control_points, key=lambda p: p["value"]) # Sort by point value in ascending order
    for point in sorted_points:
        x, y = point["pos"]
        size = point["value"]

        if DRAW_SHADED:
            # Normalize the value
            if max_point_value > min_point_value:  # Avoid division by zero
                normalized_value = (size - min_point_value) / (max_point_value - min_point_value)
                normalized_value = remap_value(normalized_value, remapping_mode)
            else:
                normalized_value = 0.0

            # Adjust brightness based on normalized value
            radius_color = blend_color(BACKGROUND, CONTROLPOINT_RADIUS, map_01_to_range(normalized_value, 0.15, 1.0))

            # Draw circle filled with adjusted brightness
            if DRAW_ANTIALIASED:
                pygame.gfxdraw.filled_circle(screen, x, y, size, radius_color)
            else:
                pygame.draw.circle(screen, radius_color, (x, y), size)

    # Prettier: Draw circle around mouse cursor (filled with adjusted brightness)
    if control_points:
        if DRAW_SHADED:
            # Normalize the radius to compute the color
            if max_point_value > min_point_value:  # Avoid division by zero
                normalized_mouse_value = (mouse_circle_radius - min_point_value) / (max_point_value - min_point_value)
                normalized_mouse_value = remap_value(normalized_mouse_value, remapping_mode)
            else:
                normalized_mouse_value = 0.0

            # Adjust brightness based on normalized value
            mouse_color = blend_color(BACKGROUND, CONTROLPOINT_RADIUS, map_01_to_range(normalized_mouse_value, 0.15, 1.0))

            # Draw the filled circle
            if DRAW_ANTIALIASED:
                pygame.gfxdraw.filled_circle(screen, mouse_x, mouse_y, int(mouse_circle_radius), mouse_color)
            else:
                pygame.draw.circle(screen, mouse_color, mouse_pos, int(mouse_circle_radius))

            # Draw outline
            if DRAW_OUTLINES:
                if DRAW_ANTIALIASED:
                    pygame.gfxdraw.aacircle(screen, mouse_x, mouse_y, int(mouse_circle_radius), BLACK) # Antialiased outline
                else:
                    pygame.draw.circle(screen, BLACK, mouse_pos, int(mouse_circle_radius), 1)
        else:
            # Draw simple outline
            if DRAW_ANTIALIASED:
                pygame.gfxdraw.aacircle(screen, mouse_x, mouse_y, int(mouse_circle_radius), RESULT_RADIUS) # Antialiased outline
            else:
                pygame.draw.circle(screen, RESULT_RADIUS, mouse_pos, int(mouse_circle_radius), 1)
        pygame.draw.circle(screen, MOUSE_CENTER, (mouse_x, mouse_y), 2)

    # Control points draw pass 2: Draw control points center, outline, and text
    for point in control_points:
        x, y = point["pos"]
        size = point["value"]

        if DRAW_SHADED:
            # Draw circle outline
            if DRAW_OUTLINES:
                if DRAW_ANTIALIASED:
                    pygame.gfxdraw.aacircle(screen, x, y, size, BLACK) # Antialiased outline
                else:
                    pygame.draw.circle(screen, BLACK, (x, y), size, 1)
        else:
            # Draw simple circle outline
            if DRAW_ANTIALIASED:
                pygame.gfxdraw.aacircle(screen, x, y, size, CONTROLPOINT_RADIUS) # Antialiased outline
            else:
                pygame.draw.circle(screen, CONTROLPOINT_RADIUS, (x, y), size, 1)

        # Draw center point
        pygame.draw.circle(screen, CONTROLPOINT, (x, y), 2)
        size_text = font.render(str(size), DRAW_ANTIALIASED, WHITE)
        screen.blit(size_text, (x + 5, y - 10))

    # Display text at mouse cursor
    screen.blit(font.render(f"Scale: {mouse_circle_radius:.2f}", DRAW_ANTIALIASED, WHITE), (mouse_x + int(mouse_circle_radius) + 10, mouse_y - 10))
    screen.blit(font.render(f"{weighting_mode_text}", DRAW_ANTIALIASED, WHITE), (mouse_x + int(mouse_circle_radius) + 10, mouse_y + 10))

    # Display top text
    screen.blit(font.render(f"Number of points: {len(control_points)}", DRAW_ANTIALIASED, GREY), (10, 10))
    screen.blit(font.render(f"Weighting mode: {weighting_mode_text}", DRAW_ANTIALIASED, GREY), (10, 30))
    screen.blit(font.render(f"Remapping mode: {remapping_modes[remapping_mode]}", DRAW_ANTIALIASED, GREY), (10, 50))

    # Display bottom text
    screen.blit(font.render("Display: Y=Cycle color remapping, X=Toggle outlines, C=Toggle shading, A=Toggle antialiasing", DRAW_ANTIALIASED, GREY), (10, 660))
    screen.blit(font.render("Interpolation: B=Next weighting mode, N=Previous weighting mode", DRAW_ANTIALIASED, GREY), (10, 680))
    screen.blit(font.render("Point management: SPACE=Regenerate points, UP=Add point, DOWN=Remove point, Left click: Add/Remove point, Right click: Set point value", DRAW_ANTIALIASED, GREY), (10, 700))

    pygame.display.flip()
    clock.tick(60)
