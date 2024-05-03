import pygame
import shapefile

# Константы цветов
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Инициализация Pygame
pygame.init()

# Создание окна
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)

# Установка заголовка окна
pygame.display.set_caption("World Map")

# Загрузка геоданных стран
sf = shapefile.Reader("ne_110m_admin_0_countries.shp")

# Получение списка контуров для каждой страны
contours = []
names = []
for record, shape in zip(sf.records(), sf.shapes()):
    name = record[4] if len(record[4]) > 0 else record[5]
    if name != "RUS":
        continue
    names.append(name)
    points = []
    for x, y in shape.points:
        points.append((x, -y))  # Инвертирование координаты Y
    parts = shape.parts + [len(points)]
    for i in range(len(parts) - 1):
        contours.append(points[parts[i]:parts[i+1]])

# Функция для масштабирования координат точек контура в соответствии с размерами экрана
def scale_points(points, width, height):
    min_x = min([x for x, y in points])
    max_x = max([x for x, y in points])
    min_y = min([y for x, y in points])
    max_y = max([y for x, y in points])
    scale_x = width / (max_x - min_x)
    scale_y = height / (max_y - min_y)
    scaled_points = []
    for x, y in points:
        scaled_points.append(((x - min_x) * scale_x, (y - min_y) * scale_y))
    return scaled_points

# Масштабирование координат контуров
scaled_contours = [scale_points(contour, screen.get_width(), screen.get_height()) for contour in contours]

# Главный цикл приложения
running = True
while running:
    # Обработка событий Pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            scaled_contours = [scale_points(contour, screen.get_width(), screen.get_height()) for contour in contours]

    screen.fill(WHITE)
    for name, contour in zip(names, scaled_contours):
        pygame.draw.lines(screen, BLACK, False, contour, 1)
        # Отображение названия страны
        font = pygame.font.SysFont(None, 20)
        text = font.render(name, True, BLACK)
        text_rect = text.get_rect(
            center=(sum([x for x, y in contour]) / len(contour), sum([y for x, y in contour]) / len(contour)))
        screen.blit(text, text_rect)

    # Обновление экрана
    pygame.display.flip()

pygame.quit()