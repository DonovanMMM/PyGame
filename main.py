import pygame
from pygame import mixer
from sys import exit
import os
import random
import csv
import button

# Start Window
pygame.init()
mixer.init()
# Create Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = SCREEN_WIDTH * .8
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

# Change Caption and Image
pygame.display.set_caption("Shooter")
pygame_icon = pygame.image.load("images/amongus.png")
pygame.display.set_icon(pygame_icon)

# clock
clock = pygame.time.Clock()
FPS = 60

GRAVITY = .75
SCROLL_THRESHOLD = 200
ROWS = 16
COLUMNS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3

screen_scroll = 0
bg_scroll = 0
level = 0
start_game = False

moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

start_img = pygame.image.load("images/start_btn.png").convert_alpha()
restart_img = pygame.image.load("images/restart_btn.png").convert_alpha()
exit_img = pygame.image.load("images/exit_btn.png").convert_alpha()

pine1_img = pygame.image.load("images/background/pine1.png").convert_alpha()
pine2_img = pygame.image.load("images/background/pine2.png").convert_alpha()
sky1_img = pygame.image.load("images/background/sky1.png").convert_alpha()
mountain1_img = pygame.image.load("images/background/mountain1.png").convert_alpha()

image_list = []
for x in range(TILE_TYPES):
    image = pygame.image.load(f"images/assets/{x}.png").convert_alpha()
    image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
    image_list.append(image)

bullet_img = pygame.image.load("images/icons/bullet2.png").convert_alpha()
grenade_img = pygame.image.load("images/icons/grenade.png").convert_alpha()
health_box_img = pygame.image.load("images/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("images/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("images/icons/grenade_box.png").convert_alpha()
item_boxes = {
    "Health": health_box_img,
    "Ammo": ammo_box_img,
    "Grenade": grenade_box_img
}

BG = (144, 201, 120)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

font = pygame.font.SysFont("Futura", 30)


def draw_text(text, fonts, text_color, xc, yc):
    img = fonts.render(text, True, text_color)
    screen.blit(img, (xc, yc))


def draw_bg():
    screen.fill(BG)
    width = sky1_img.get_width()
    for xe in range(5):
        screen.blit(sky1_img, ((xe * width) - bg_scroll * .5, 0))
        screen.blit(mountain1_img, ((xe * width) - bg_scroll * .6, SCREEN_HEIGHT - mountain1_img.get_height() - 300))
        screen.blit(pine1_img, ((xe * width) - bg_scroll * .7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((xe * width) - bg_scroll * .8, SCREEN_HEIGHT - pine2_img.get_height()))


def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()
    data = []
    for rows in range(ROWS):
        ra = [-1] * COLUMNS
        world_data.append(ra)
    return data


class Soldier(pygame.sprite.Sprite):
    def __init__(self, character_type, xb=200, yb=200, scale=0.0, speed=0, ammo=0, default_shoot_cooldown=0, grenades=0,
                 health=0, shield=0):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.character_type = character_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.default_shoot_cooldown = default_shoot_cooldown
        self.grenades = grenades
        self.health = health
        self.max_health = self.health
        self.shield = shield
        self.max_shield = self.shield
        self.direction = 1
        self.velocity_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.x = xb
        self.y = yb
        self.scale = scale
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # AI variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        animation_types = ["idle", "walking", "jump", "death"]
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f"images{self.character_type}/{animation}"))
            for i in range(num_of_frames - 1):
                img = pygame.image.load(f"images{self.character_type}/{animation}/{i}.PNG").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (xb, yb)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        return self.check_alive()

    def move(self, left, right):
        screen_scroll1 = 0
        dx = 0
        dy = 0

        if left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump and self.in_air == False:
            self.velocity_y = -11
            self.jump = False
            self.in_air = True

        self.velocity_y += GRAVITY
        if self.velocity_y > 10:
            self.velocity_y = 10
        dy += self.velocity_y

        for til1 in world.obstacle_list:
            if til1[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.character_type == "/donald":
                    self.direction *= -1
                    self.move_counter = 0

            if til1[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.velocity_y < 0:
                    self.velocity_y = 0
                    dy = til1[1].bottom - self.rect.top
                elif self.velocity_y >= 0:
                    self.velocity_y = 0
                    dy = til1[1].top - self.rect.bottom

        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
            self.shield = 0
        complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            complete = True
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0
            self.shield = 0

        if self.character_type == "/joe":
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        self.rect.x += dx
        self.rect.y += dy

        if self.character_type == "/joe":
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESHOLD and bg_scroll < (
                    world.level_length * TILE_SIZE) - SCREEN_WIDTH) \
                    or (self.rect.left < SCROLL_THRESHOLD and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll1 = -dx
        return screen_scroll1, complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = self.default_shoot_cooldown
            if self.character_type == "/donald":
                if self.direction == -1:
                    bullet = Bullet(self.rect.centerx + (1.5 * (-1) * self.rect.size[0]),
                                    self.rect.centery, self.direction)
                    bullet_group.add(bullet)
                    self.ammo -= 1
                else:
                    bullet = Bullet(self.rect.centerx + (1.5 * self.rect.size[0]),
                                    self.rect.centery, self.direction)
                    bullet_group.add(bullet)
                    self.ammo -= 1
            elif self.character_type == "/joe":
                if self.direction == -1:
                    bullet = Bullet(self.rect.centerx + (1.5 * player.direction * self.rect.size[0]),
                                    self.rect.centery, self.direction)
                    bullet_group.add(bullet)
                    self.ammo -= 1
                else:
                    bullet = Bullet(self.rect.centerx + (1.5 * player.direction * self.rect.size[0]),
                                    self.rect.centery, self.direction)
                    bullet_group.add(bullet)
                    self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if self.idling is False and random.randint(1, 200) == 1:
                self.update_action(0)  # 0 : Idle
                self.idling = True
                self.idling_counter = 75
            if self.idling is False and random.randint(1, 200) == 1:
                self.jump = True
                self.update_action(2)

            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()
            else:
                if not self.idling:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1 : RUN
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        self.rect.x += screen_scroll

    def update_animation(self):
        animation_cooldown = 120
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)
            self.kill()
            return True
        return False

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World:
    def __init__(self):
        self.level_length = None
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        for yu, row1 in enumerate(data):
            for xu, tile1 in enumerate(row1):
                if tile1 >= 0:
                    current_image = image_list[tile1]
                    img_rect = current_image.get_rect()
                    img_rect.x = xu * TILE_SIZE
                    img_rect.y = yu * TILE_SIZE
                    tile_data = (current_image, img_rect)
                    if 0 <= tile1 <= 8:
                        self.obstacle_list.append(tile_data)
                    elif 9 <= tile1 <= 10:
                        water = Water(current_image, xu * TILE_SIZE, yu * TILE_SIZE)
                        water_group.add(water)
                    elif 11 <= tile1 <= 14:
                        decoration = Decoration(current_image, xu * TILE_SIZE, yu * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile1 == 15:
                        new_player = Soldier("/joe", int(xu * TILE_SIZE), int(yu * TILE_SIZE), .155, 6, 20, 10, 10,
                                             100, 50)
                        new_health_bar = HealthBar(10, 10, new_player.health, new_player.health)
                        new_shield_bar = ShieldBar(10, 10, new_player.shield, new_player.max_shield)
                    elif tile1 == 16:
                        new_enemy = Soldier("/donald", int(xu * TILE_SIZE), int(yu * TILE_SIZE), .2, 2, 200, 20, 0, 100,
                                            0)
                        enemy_group.add(new_enemy)
                    elif tile1 == 17:
                        current_item_box = ItemBox("Ammo", int(xu * TILE_SIZE), int(yu * TILE_SIZE))
                        item_box_group.add(current_item_box)
                    elif tile1 == 18:
                        current_item_box = ItemBox("Grenade", int(xu * TILE_SIZE), int(yu * TILE_SIZE))
                        item_box_group.add(current_item_box)
                    elif tile1 == 19:
                        current_item_box = ItemBox("Health", int(xu * TILE_SIZE), int(yu * TILE_SIZE))
                        item_box_group.add(current_item_box)
                    elif tile1 == 20:
                        current_exit = Exit(current_image, xu * TILE_SIZE, yu * TILE_SIZE)
                        exit_group.add(current_exit)
        return new_player, new_health_bar, new_shield_bar

    def draw(self):
        for til1 in self.obstacle_list:
            til1[1][0] += screen_scroll
            screen.blit(til1[0], til1[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, xi, yi):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (xi + TILE_SIZE // 2, yi + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, xr, yr):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (xr + TILE_SIZE // 2, yr + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, xa, ya):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (xa + TILE_SIZE // 2, ya + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, xt, yt):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (xt + (TILE_SIZE // 2), yt + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == "Health":
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == "Ammo":
                player.ammo += 15
            elif self.item_type == "Grenade":
                player.grenades += 3
            self.kill()


class HealthBar:
    def __init__(self, xg, yg, health, max_health):
        self.x = xg
        self.y = yg
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health

        ratio = self.health / self.max_health

        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y + 12, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y + 14, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y + 14, 150 * ratio, 20))


class ShieldBar:
    def __init__(self, xh, yh, shield, max_shield):
        self.x = xh
        self.y = yh
        self.shield = shield
        self.max_shield = max_shield

    def draw(self, shield):
        self.shield = shield

        ratio = self.shield / self.max_shield

        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 10, 154, 23))
        pygame.draw.rect(screen, WHITE, (self.x, self.y - 8, 150, 19))
        pygame.draw.rect(screen, BLUE, (self.x, self.y - 8, 150 * ratio, 19))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, xn, yn, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (xn, yn)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed) + screen_scroll

        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        for current_tile in world.obstacle_list:
            if current_tile[1].colliderect(self.rect):
                self.kill()

        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                if player.shield > 0:
                    player.shield -= 5
                    if player.shield < 0:
                        player.health += player.shield
                        player.shield = 0
                else:
                    player.health -= 5
                self.kill()
        for current_enemy in enemy_group:
            if pygame.sprite.spritecollide(current_enemy, bullet_group, False):
                if current_enemy.alive:
                    if current_enemy.shield > 0:
                        current_enemy.shield -= 25
                        if current_enemy.shield < 0:
                            current_enemy.health += current_enemy.shield
                            current_enemy.shield = 0
                    else:
                        current_enemy.health -= 25
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, xh, yh, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (xh, yh)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        for current_tile in world.obstacle_list:
            if current_tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            if current_tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if current_tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = current_tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = current_tile[1].top - self.rect.bottom

        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.9)
            explosion_group.add(explosion)
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                if player.shield > 0:
                    player.shield -= 100
                    if player.shield < 0:
                        player.health += player.shield
                        player.shield = 0
                else:
                    player.health -= 100

            for current_enemy in enemy_group:
                if abs(self.rect.centerx - current_enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - current_enemy.rect.centery) < TILE_SIZE * 2:
                    if current_enemy.shield > 0:
                        current_enemy.shield -= 100
                        if current_enemy.shield < 0:
                            current_enemy.health += current_enemy.shield
                            current_enemy.shield = 0
                    else:
                        current_enemy.health -= 100


class Explosion(pygame.sprite.Sprite):
    def __init__(self, xi, yi, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 9):
            img = pygame.image.load(f"images/explosion/{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (xi, yi)
        self.counter = 0

    def update(self):
        self.rect.x += screen_scroll
        explosion_speed = 4
        self.counter += 1

        if self.counter >= explosion_speed:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

world_data = []
for row in range(ROWS):
    r = [-1] * COLUMNS
    world_data.append(r)
with open(f'level{level}_data.csv', newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar, shield_bar = world.process_data(world_data)

while True:
    clock.tick(FPS)
    if not start_game:
        screen.fill(BG)
        if start_button.draw(screen):
            start_game = True
        if exit_button.draw(screen):
            pygame.quit()
            exit()
    else:
        draw_bg()

        world.draw()

        health_bar.draw(player.health)
        shield_bar.draw(player.shield)

        draw_text(f"Ammo: {player.ammo}", font, WHITE, 10, 60)
        draw_text(f"Grenades: {player.grenades}", font, WHITE, 10, 85)

        player.draw()
        player.update()

        for enemy in enemy_group:
            enemy.ai()
            if enemy.update():
                item_box = ItemBox("Ammo", enemy.rect.x, enemy.rect.y)
                item_box_group.add(item_box)
            enemy.draw()

        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        if player.alive:
            if shoot:
                player.shoot()
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (player.rect.size[0] * 0.5 * player.direction),
                                  player.rect.top,
                                  player.direction)
                grenade_group.add(grenade)
                grenade_thrown = True
                player.grenades -= 1
            if player.in_air:
                player.update_action(2)
            elif moving_left or moving_right:
                player.update_action(1)
            else:
                player.update_action(0)
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            if level_complete:
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    with open(f"level{level}_data.csv", newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar, shield_bar = world.process_data(world_data)
        else:
            screen_scroll = 0
            if restart_button.draw(screen):
                bg_scroll = 0
                world_data = reset_level()
                with open(f'level{level}_data.csv', newline="") as csvfile:
                    reader = csv.reader(csvfile, delimiter=",")
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, health_bar, shield_bar = world.process_data(world_data)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True

            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    pygame.display.update()
