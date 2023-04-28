import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption("Level Editor")

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
    screen.blit(sky_img, (-scroll, 0))
    screen.blit(mountain_img, (-scroll, SCREEN_HEIGHT - mountain_img.get_height() - 300))
    screen.blit(pine1_img, (-scroll, SCREEN_HEIGHT - pine1_img.get_height() - 150))
    screen.blit(pine1_img, (-scroll, SCREEN_HEIGHT - pine1_img.get_height()))



run = True
while run:
    draw_bg()

    if scroll_left == True:
        scroll -= 5
    if scroll_right == True:
        scroll += 5

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                scroll_left = True
            if event.key == pygame.K_d:
                scroll_right = True
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                scroll_left = False
            if event.key == pygame.K_d:
                scroll_right = False


    pygame.display.update()

pygame.quit()