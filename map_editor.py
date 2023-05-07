import pygame

pygame.init()

FPS = 60
clock = pygame.time.Clock()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption("Level Editor")

ROWS = 16
MAX_COLUMNS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS

scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

pine1_img = pygame.image.load("images/background/pine1.png").convert_alpha()
pine2_img = pygame.image.load("images/background/pine2.png").convert_alpha()
mountain_img = pygame.image.load("images/background/mountain1.png").convert_alpha()
sky_img = pygame.image.load("images/background/sky1.png").convert_alpha()

GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)


def draw_bg():
    screen.fill(GREEN)
    width = sky_img.get_width()
    for x in range(4):
        screen.blit(sky_img, ((x * width) - scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine1_img, ((x * width) - scroll * 0.8, SCREEN_HEIGHT - pine1_img.get_height()))


def draw_grid():
    for c in range(MAX_COLUMNS + 1):
        pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
    for c in range(ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))


run = True
while run:
    clock.tick(FPS)
    draw_bg()
    draw_grid()

    if scroll_left and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right:
        scroll += 5 * scroll_speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                scroll_left = True
            if event.key == pygame.K_d:
                scroll_right = True
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 5
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                scroll_left = False
            if event.key == pygame.K_d:
                scroll_right = False
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 1

    pygame.display.update()

pygame.quit()
