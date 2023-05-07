import pygame
from sys import exit
import os
import random
import time
import csv

# Start Window
pygame.init()
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
ROWS = 16
COLUMNS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21

level = 0

moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

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


def draw_text(text, fonts, text_color, x, y):
    img = fonts.render(text, True, text_color)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 400), (SCREEN_WIDTH, 400))


class Soldier(pygame.sprite.Sprite):
    def __init__(self, character_type, x=200, y=200, scale=0.0, speed=0, ammo=0, default_shoot_cooldown=0, grenades=0,
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
        self.x = x
        self.y = y
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
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        return self.check_alive()

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump and self.in_air != True:
            self.velocity_y = -11
            self.jump = False
            self.in_air = True

        self.velocity_y += GRAVITY
        if self.velocity_y > 10:
            self.velocity_y = 10
        dy += self.velocity_y

        if self.rect.bottom + dy > 400:
            dy = 400 - self.rect.bottom
            self.in_air = False

        self.rect.x += dx
        self.rect.y += dy

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
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  # 0 : Idle
                self.idling = True
                self.idling_counter = 75
            if self.idling == False and random.randint(1, 200) == 1:
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


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    image = image_list[tile]
                    img_rect = image.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (image, img_rect)
                    if 0 <= tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif 9 <= tile <= 10:
                        pass
                    elif 11 <= tile <= 14:
                        pass
                    elif tile == 15:
                        player = Soldier("/joe", int(x * TILE_SIZE), int(y * TILE_SIZE), .175, 3, 20, 10, 10, 100, 50)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                        shield_bar = ShieldBar(10, 10, player.shield, player.max_shield)
                    elif tile == 16:
                        enemy = Soldier("/donald", 300, 350, .2, 2, 200, 20, 0, 100, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:
                        item_box = ItemBox("Ammo", int(x * TILE_SIZE), int(y * TILE_SIZE))
                        item_box_group.add(item_box)
                    elif tile == 18:
                        item_box = ItemBox("Grenade", int(x * TILE_SIZE), int(y * TILE_SIZE))
                        item_box_group.add(item_box)
                    elif tile == 19:
                        item_box = ItemBox("Health", int(x * TILE_SIZE), int(y * TILE_SIZE))
                        item_box_group.add(item_box)
                    elif tile == 20:
                        pass
        return player, health_bar, shield_bar


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + (TILE_SIZE // 2), y + (TILE_SIZE - self.image.get_height()))

    def update(self):
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


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health

        ratio = self.health / self.max_health

        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y + 12, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y + 14, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y + 14, 150 * ratio, 20))


class ShieldBar():
    def __init__(self, x, y, shield, max_shield):
        self.x = x
        self.y = y
        self.shield = shield
        self.max_shield = max_shield

    def draw(self, shield):
        self.shield = shield

        ratio = self.shield / self.max_shield

        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 10, 154, 23))
        pygame.draw.rect(screen, WHITE, (self.x, self.y - 8, 150, 19))
        pygame.draw.rect(screen, BLUE, (self.x, self.y - 8, 150 * ratio, 19))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed)

        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
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
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    if enemy.shield > 0:
                        enemy.shield -= 25
                        if enemy.shield < 0:
                            enemy.health += enemy.shield
                            enemy.shield = 0
                    else:
                        enemy.health -= 25
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        if self.rect.bottom + dy > 400:
            dy = 400 - self.rect.bottom
            self.speed = 0

        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed

        self.rect.x += dx
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

            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    if enemy.shield > 0:
                        enemy.shield -= 100
                        if enemy.shield < 0:
                            enemy.health += enemy.shield
                            enemy.shield = 0
                    else:
                        enemy.health -= 100


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 9):
            img = pygame.image.load(f"images/explosion/{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        explosion_speed = 4
        self.counter += 1

        if self.counter >= explosion_speed:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()


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
    draw_bg()

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
    bullet_group.draw(screen)
    grenade_group.draw(screen)
    explosion_group.draw(screen)
    item_box_group.draw(screen)

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
        player.move(moving_left, moving_right)

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
