import pygame
import math
import random

# === WINDOW SETTINGS ===
WIDTH, HEIGHT = 1200, 1000
CENTER = (WIDTH // 2, HEIGHT // 2 + 100)
SCALE = 350  # pixels per AU

# === PLANETARY DATA ===
# (name, semi-major axis (AU), eccentricity, period (days), color, radius px)
PLANETS = [
    ("Mercury", 0.387, 0.2056, 87.97, (200, 200, 200), 6),
    ("Venus",   0.723, 0.0067, 224.7, (255, 200, 100), 10),
    ("Earth",   1.000, 0.0167, 365.2, (100, 180, 255), 11),
    ("Mars",    1.524, 0.0934, 687.0, (255, 100, 100), 9),
]

omega_deg = 29.0  # argument of periapsis in degrees (same for all for simplicity)
omega = math.radians(omega_deg)

# === TIME SETTINGS ===
t = 0
dt = 0.5  # simulation time step (days per frame)
tau = 0  # time of perihelion

# === PYGAME INIT ===
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Beautiful Solar System Simulation")
font = pygame.font.SysFont(None, 28)
clock = pygame.time.Clock()
running = True

# === COLORS ===
BLACK = (10, 10, 30)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 100)
SUN_GLOW = (255, 255, 180, 40)

# === STAR BACKGROUND ===
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2)) for _ in range(200)]

def solve_kepler(M, e, tol=1e-6, max_iter=100):
    E = M if e < 0.8 else math.pi
    for _ in range(max_iter):
        delta = E - e * math.sin(E) - M
        if abs(delta) < tol:
            break
        E -= delta / (1 - e * math.cos(E))
    return E

def get_position(a, e, T, t):
    n = 2 * math.pi / T  # mean motion
    M = n * (t - tau)  # mean anomaly
    M = M % (2 * math.pi)  # keep M in [0, 2pi]
    E = solve_kepler(M, e)
    theta = 2 * math.atan2(math.sqrt(1 + e) * math.sin(E / 2),
                           math.sqrt(1 - e) * math.cos(E / 2))
    r = a * (1 - e * math.cos(E))
    # Polar to Cartesian in orbit frame
    x_orbit = r * math.cos(theta)
    y_orbit = r * math.sin(theta)
    # Rotate by omega (argument of periapsis)
    x = x_orbit * math.cos(omega) - y_orbit * math.sin(omega)
    y = x_orbit * math.sin(omega) + y_orbit * math.cos(omega)
    return x, y

def draw_sun():
    # Draw glow
    for r in range(80, 0, -10):
        s = pygame.Surface((2*r, 2*r), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 180, 18), (r, r), r)
        screen.blit(s, (CENTER[0]-r, CENTER[1]-r))
    pygame.draw.circle(screen, YELLOW, CENTER, 24)

def draw_orbit(a, e, color):
    # Draw ellipse for orbit
    points = []
    for deg in range(0, 360, 2):
        theta = math.radians(deg)
        r = a * (1 - e**2) / (1 + e * math.cos(theta))
        x_orbit = r * math.cos(theta)
        y_orbit = r * math.sin(theta)
        x = x_orbit * math.cos(omega) - y_orbit * math.sin(omega)
        y = x_orbit * math.sin(omega) + y_orbit * math.cos(omega)
        x_px = CENTER[0] + int(x * SCALE)
        y_px = CENTER[1] - int(y * SCALE)
        points.append((x_px, y_px))
    pygame.draw.aalines(screen, color, True, points, 1)

def draw_stars():
    for x, y, r in stars:
        pygame.draw.circle(screen, WHITE, (x, y), r)

# === TRAILS ===
trails = [[] for _ in PLANETS]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    t += dt

    # Draw background
    screen.fill(BLACK)
    draw_stars()
    draw_sun()

    # Draw orbits and planets
    for i, (name, a, e, T, color, radius) in enumerate(PLANETS):
        draw_orbit(a, e, color)
        x_au, y_au = get_position(a, e, T, t)
        x_px = CENTER[0] + int(x_au * SCALE)
        y_px = CENTER[1] - int(y_au * SCALE)
        trails[i].append((x_px, y_px))
        if len(trails[i]) > 800:
            trails[i].pop(0)
        # Draw trail
        for pos in trails[i]:
            pygame.draw.circle(screen, color, pos, 1)
        # Draw planet
        pygame.draw.circle(screen, color, (x_px, y_px), radius)
        # Draw name
        text = font.render(name, True, color)
        screen.blit(text, (x_px + 12, y_px - 12))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
