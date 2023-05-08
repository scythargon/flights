import pygame

# Константы цветов
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Константы размеров окна
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

# Координаты стран на карте
countries = {
    "Russia": (100, 200),
    "USA": (100, 300),
    "China": (200, 350),
    "India": (300, 300),
    "Brazil": (400, 250),
    "Australia": (400, 350),
    "Argentina": (500, 250),
    "Canada": (100, 350),
    "Kazakhstan": (100, 150),
    "Algeria": (400, 100),
    "Greenland": (100, 50),
    "Mexico": (200, 300),
    "Saudi Arabia": (300, 150),
    "Indonesia": (400, 350),
    "Iran": (300, 200),
    "Mongolia": (200, 150),
    "Peru": (500, 200),
    "Chile": (500, 100),
    "Niger": (300, 50),
    "Mali": (200, 50),
}

# Инициализация Pygame
pygame.init()

# Создание окна
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Установка заголовка окна
pygame.display.set_caption("World Map")

# Главный цикл приложения
running = True
while running:
    # Обработка событий Pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Отрисовка карты
    screen.fill(WHITE)
    for country, pos in countries.items():
        pygame.draw.circle(screen, BLUE, pos, 10)
        text_surface = pygame.font.SysFont(None, 20).render(country, True, BLUE)
        text_rect = text_surface.get_rect()
        text_rect.center = pos
        screen.blit(text_surface, text_rect)

    # Обновление экрана
    pygame.display.flip()

# Выход из Pygame
pygame.quit()
