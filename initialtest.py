import pygame
import math

# === WINDOW SETTINGS ===
WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH // 2, HEIGHT // 2)
SCALE = 400  # pixels per AU

# === ORBIT PARAMETERS FOR MERCURY ===
a = 0.387  # semi-major axis in AU
e = 0.2056  # eccentricity
T = 87.97  # orbital period in days
omega_deg = 29.0  # argument of periapsis in degrees
omega = math.radians(omega_deg)

# === TIME SETTINGS ===
t = 0
dt = 0.1  # simulation time step (days per frame)
tau = 0  # time of perihelion

# === PYGAME INIT ===
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

# === COLORS ===
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

def solve_kepler(M, e, tol=1e-6, max_iter=100):
    E = M if e < 0.8 else math.pi
    for _ in range(max_iter):
        delta = E - e * math.sin(E) - M
        if abs(delta) < tol:
            break
        E -= delta / (1 - e * math.cos(E))
    return E

def get_position(t):
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

# === TRAIL ===
trail = []

# === MAIN LOOP ===
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update time and get new position
    t += dt
    x_au, y_au = get_position(t)
    x_px = CENTER[0] + int(x_au * SCALE)
    y_px = CENTER[1] - int(y_au * SCALE)

    trail.append((x_px, y_px))
    if len(trail) > 1000:
        trail.pop(0)

    # Draw
    screen.fill(BLACK)
    pygame.draw.circle(screen, YELLOW, CENTER, 8)  # Sun
    for pos in trail:
        pygame.draw.circle(screen, GRAY, pos, 1)
    pygame.draw.circle(screen, WHITE, (x_px, y_px), 5)  # Mercury

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
