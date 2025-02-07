import pygame
import numpy as np
import random

# Inicializar pygame
pygame.init()
pygame.mixer.init()  # Inicializar el mezclador de Pygame

# Cargar sonidos
level_up_sound = pygame.mixer.Sound('sounds/level_up.wav')
move_sound = pygame.mixer.Sound('sounds/move.wav')
lose_sound = pygame.mixer.Sound('sounds/lose_sound.wav')

# Configuración de la pantalla
WIDTH, HEIGHT = 500, 700  # Aumentar la altura para los botones
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vector Quest")
clock = pygame.time.Clock()

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (169, 169, 169)

# Centro del plano cartesiano
CENTER = (WIDTH // 2, HEIGHT // 2)

# Tamaño de la cuadrícula
GRID_SIZE = 40

# Límites del mapa
MAP_LIMIT = 9

# Posición inicial del jugador
player_pos = np.array([0, 0])

# Nivel actual y número máximo de niveles
level = 1
max_levels = 5
show_intro = True

# Variables para el ejercicio
exercise_text = ""
solution = np.array([0, 0])
show_goal = False  # Asegúrate de que esta variable esté definida

# Tamaño de los botones (definirlo antes de usarlo)
button_size = 70  # Puedes ajustar el tamaño según necesites

# Botones de control
left_button = pygame.Rect(50, HEIGHT - button_size - 50, button_size, button_size)
right_button = pygame.Rect(200, HEIGHT - button_size - 50, button_size, button_size)
up_button = pygame.Rect(125, HEIGHT - button_size * 2 - 50, button_size, button_size)
down_button = pygame.Rect(125, HEIGHT - 50, button_size, button_size)

def generate_exercise():
    global exercise_text, solution
    operation = random.choice(['suma', 'resta', 'escalar', 'magnitud', 'producto'])
    a, b = random.randint(-5, 5), random.randint(-5, 5)
    c, d = random.randint(-5, 5), random.randint(-5, 5)
    
    if operation == 'suma':
        solution = np.array([a + c, b + d])
    elif operation == 'resta':
        solution = np.array([a - c, b - d])
    elif operation == 'escalar':
        k = random.randint(1, 5)
        solution = np.array([k * a, k * b])
    elif operation == 'magnitud':
        solution = np.array([np.sqrt(a**2 + b**2), 0])  # Solo la magnitud en x
    elif operation == 'producto':
        solution = np.array([a * c + b * d, 0])  # Solo el resultado en x

    # Asegurarse de que la solución esté dentro de los límites
    solution = np.clip(solution, -MAP_LIMIT, MAP_LIMIT)

    # Generar el texto del ejercicio
    if operation == 'suma':
        exercise_text = f"Resuelve: ({a}, {b}) + ({c}, {d}) = ?"
    elif operation == 'resta':
        exercise_text = f"Resuelve: ({a}, {b}) - ({c}, {d}) = ?"
    elif operation == 'escalar':
        exercise_text = f"Resuelve: {k} * ({a}, {b}) = ?"
    elif operation == 'magnitud':
        exercise_text = f"Resuelve: |({a}, {b})| = ?"
    elif operation == 'producto':
        exercise_text = f"Resuelve: ({a}, {b}) · ({c}, {d}) = ?"

def show_start_screen():
    global show_intro
    generate_exercise()  # Generar un nuevo ejercicio al inicio del nivel
    
    while show_intro:
        screen.fill(WHITE)
        font = pygame.font.Font(None, 40)  # Tamaño adecuado de fuente
        
        # Texto en dos líneas
        level_text = font.render(f"Nivel {level}/{max_levels}", True, BLACK)
        vector_text = font.render(exercise_text, True, BLACK)
        button_text1 = font.render("Presiona ENTER o toca la pantalla", True, BLACK)
        button_text2 = font.render("para continuar", True, BLACK)

        # Posicionamiento
        screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 4))
        screen.blit(vector_text, (WIDTH // 2 - vector_text.get_width() // 2, HEIGHT // 3))
        screen.blit(button_text1, (WIDTH // 2 - button_text1.get_width() // 2, HEIGHT // 2))
        screen.blit(button_text2, (WIDTH // 2 - button_text2.get_width() // 2, HEIGHT // 2 + 40))  # Segunda línea

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            # Permitir continuar con ENTER o toque en pantalla
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                show_intro = False
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Si toca la pantalla, también avanza
                show_intro = False



def smooth_move(target_pos):
    global player_pos
    steps = 10  # Aumentamos los pasos para una animación más fluida
    diff = (target_pos - player_pos) / steps

    for _ in range(steps):
        player_pos = player_pos + diff  # Movimiento más gradual
        render_game()  # Dibujar la pantalla en cada paso
        pygame.display.flip()
        pygame.time.delay(20)  # Pequeña pausa para suavizar el movimiento
    
    player_pos = target_pos  # Asegurar que el jugador termine en la posición exacta


def generate_obstacles():
    num_obstacles = 5 + (level * 2)
    obstacles = set()
    while len(obstacles) < num_obstacles:
        x, y = random.randint(-MAP_LIMIT, MAP_LIMIT), random.randint(-MAP_LIMIT, MAP_LIMIT)
        if (x, y) != (0, 0):
            obstacles.add((x, y))
    return obstacles

obstacles = generate_obstacles()

def move_player(vector):
    global player_pos
    new_pos = player_pos + vector

    # Si el jugador choca con un obstáculo, pierde
    if tuple(new_pos) in obstacles:
        print("¡Chocaste con un obstáculo!")  # Debugging en consola
        show_game_over()
        return  # Detener ejecución para evitar que se mueva

    # Si no choca, moverse normalmente dentro de los límites del mapa
    if -MAP_LIMIT <= new_pos[0] <= MAP_LIMIT and -MAP_LIMIT <= new_pos[1] <= MAP_LIMIT:
        smooth_move(new_pos)
        move_sound.play()  # Reproducir sonido al moverse



def check_win():
    global show_intro, level, show_goal
    if np.array_equal(player_pos, solution):
        show_goal = True  # Mostrar la meta solo si el jugador ha alcanzado la solución
        level_up_sound.play()

        # 💥 Efecto de "explosión de luz" al ganar
        for i in range(10):
            screen.fill((255, 255 - i * 25, 255 - i * 25))  # Cambio de color a blanco brillante
            render_game()
            pygame.display.flip()
            pygame.time.delay(50)  # Pequeña pausa para el efecto

        # ✨ Parpadeo del jugador antes de desaparecer
        for _ in range(5):  # Parpadeo rápido
            render_game()
            pygame.display.flip()
            pygame.time.delay(100)
            screen.fill(WHITE)
            pygame.display.flip()
            pygame.time.delay(100)

        # 🌟 Efecto de fade-out y zoom-out
        for scale in range(1, 11):
            screen.fill(WHITE)
            scaled_surface = pygame.transform.smoothscale(screen, (WIDTH // scale, HEIGHT // scale))
            screen.blit(scaled_surface, ((WIDTH - WIDTH // scale) // 2, (HEIGHT - HEIGHT // scale) // 2))
            pygame.display.flip()
            pygame.time.delay(30)

        # 🔥 Cambio de nivel después de la animación
        level += 1
        if level > max_levels:
            return True  # Fin del juego

        show_intro = True
        player_pos[:] = [0, 0]  # Resetear posición
        obstacles = generate_obstacles()
        show_start_screen()
    
    return False

def show_game_over():
    lose_sound.play()  # Reproducir sonido al perder
    screen.fill(WHITE)
    font = pygame.font.Font(None, 50)
    text = font.render("¡Has perdido!", True, RED)
    restart_text1 = font.render("Presiona ENTER o toca", True, BLACK)
    restart_text2 = font.render("la pantalla para reiniciar", True, BLACK)

    # Animación de parpadeo del jugador
    for _ in range(5):  # Parpadear 5 veces
        render_game()
        pygame.display.flip()
        pygame.time.delay(200)  # Pequeña pausa
        screen.fill(WHITE)  # Borrar todo
        pygame.display.flip()
        pygame.time.delay(200)

    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))
    screen.blit(restart_text1, (WIDTH // 2 - restart_text1.get_width() // 2, HEIGHT // 2))
    screen.blit(restart_text2, (WIDTH // 2 - restart_text2.get_width() // 2, HEIGHT // 2 + 40))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                restart_game()
                waiting = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                restart_game()
                waiting = False


def restart_game():
    global level, player_pos, solution, obstacles, show_intro, show_goal
    level = 1
    player_pos = np.array([0, 0])
    generate_exercise()
    obstacles = generate_obstacles()
    show_intro = True
    show_goal = False  # Asegurarse de que el cubo verde no se muestre al reiniciar
    show_start_screen()

def render_game():
    screen.fill(WHITE)
    draw_grid()
    if show_goal and level == 1:  # Solo dibujar la meta si es visible y estamos en el primer nivel
        draw_goal()
    draw_obstacles()
    draw_player()
    display_info()
    draw_buttons()  # Dibuja los botones de control

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y), 1)

def draw_player():
    x, y = player_pos * GRID_SIZE + CENTER
    pygame.draw.circle(screen, BLUE, (int(x), int(y)), 10)

def draw_goal():
    x, y = solution * GRID_SIZE + CENTER
    pygame.draw.rect(screen, GREEN, (x - 10, y - 10, 20, 20))

def draw_obstacles():
    for obs in obstacles:
        x, y = np.array(obs) * GRID_SIZE + CENTER
        pygame.draw.rect(screen, GRAY, (x - 10, y - 10, 20, 20))

def draw_buttons():
    """ Dibuja las flechas dentro de los botones sin redefinir las hitboxes """
    arrow_size = 20  # Tamaño de las flechas

    # Flecha izquierda (◀)
    pygame.draw.polygon(screen, BLACK, [
        (left_button.centerx - arrow_size // 2, left_button.centery),
        (left_button.centerx + arrow_size // 2, left_button.centery - arrow_size // 2),
        (left_button.centerx + arrow_size // 2, left_button.centery + arrow_size // 2)
    ])

    # Flecha derecha (▶)
    pygame.draw.polygon(screen, BLACK, [
        (right_button.centerx + arrow_size // 2, right_button.centery),
        (right_button.centerx - arrow_size // 2, right_button.centery - arrow_size // 2),
        (right_button.centerx - arrow_size // 2, right_button.centery + arrow_size // 2)
    ])

    # Flecha arriba (▲)
    pygame.draw.polygon(screen, BLACK, [
        (up_button.centerx, up_button.centery - arrow_size // 2),
        (up_button.centerx - arrow_size // 2, up_button.centery + arrow_size // 2),
        (up_button.centerx + arrow_size // 2, up_button.centery + arrow_size // 2)
    ])

    # Flecha abajo (▼)
    pygame.draw.polygon(screen, BLACK, [
        (down_button.centerx, down_button.centery + arrow_size // 2),
        (down_button.centerx - arrow_size // 2, down_button.centery - arrow_size // 2),
        (down_button.centerx + arrow_size // 2, down_button.centery - arrow_size // 2)
    ])



def handle_touch(pos):
    """ Detecta si el usuario toca un botón y mueve el jugador """
    x, y = pos  # Obtener coordenadas del toque

    print(f"Tocado en: {x}, {y}")  # Debug para ver dónde está detectando el toque

    if left_button.collidepoint(x, y):
        print("Tocaste IZQUIERDA")
        move_player(np.array([-1, 0]))
    elif right_button.collidepoint(x, y):
        print("Tocaste DERECHA")
        move_player(np.array([1, 0]))
    elif up_button.collidepoint(x, y):
        print("Tocaste ARRIBA")
        move_player(np.array([0, -1]))
    elif down_button.collidepoint(x, y):
        print("Tocaste ABAJO")
        move_player(np.array([0, 1]))

# Captura de eventos en el loop principal
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        running = False

    # Detectar teclas del teclado
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            print("Tecla IZQUIERDA presionada")  # Debug
            move_player(np.array([-1, 0]))
        elif event.key == pygame.K_RIGHT:
            print("Tecla DERECHA presionada")  # Debug
            move_player(np.array([1, 0]))
        elif event.key == pygame.K_UP:
            print("Tecla ARRIBA presionada")  # Debug
            move_player(np.array([0, -1]))
        elif event.key == pygame.K_DOWN:
            print("Tecla ABAJO presionada")  # Debug
            move_player(np.array([0, 1]))

    # Detectar clics en la pantalla táctil
    elif event.type == pygame.MOUSEBUTTONDOWN:
        handle_touch(event.pos)  # Manejar toques en la pantalla




def display_info():
    font = pygame.font.Font(None, 30)
    pos_text = font.render(f"Posición: ({int(player_pos[0])}, {int(player_pos[1])})", True, BLACK)
    level_text = font.render(f"Nivel: {level}/{max_levels}", True, BLACK)
    screen.blit(pos_text, (10, 10))
    screen.blit(level_text, (10, 40))

running = True
show_start_screen()
while running:
    render_game()
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            print(f"Tecla presionada: {event.key}")  # Debug
            if event.key == pygame.K_LEFT:
                move_player(np.array([-1, 0]))
            elif event.key == pygame.K_RIGHT:
                move_player(np.array([1, 0]))
            elif event.key == pygame.K_UP:
                move_player(np.array([0, -1]))
            elif event.key == pygame.K_DOWN:
                move_player(np.array([0, 1]))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_touch(event.pos)  # Manejar toques en la pantalla
    
    if check_win():
        show_goal = True  # Mostrar la meta solo si el jugador ha alcanzado la solución
        level_up_sound.play()  # Reproducir sonido al pasar de nivel
        level += 1
        if level > max_levels:
            break
        show_intro = True
        player_pos = np.array([0, 0])  # Asegurar que el vector tenga dos valores
        obstacles = generate_obstacles()
        show_start_screen()
    
    clock.tick(60)
