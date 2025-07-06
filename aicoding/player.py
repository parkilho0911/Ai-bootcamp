import pygame
import math

class Projectile:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.radius = 10
        self.color = (0, 180, 255)
        self.speed = 12
        self.direction = direction  # (dx, dy) 튜플
        self.alive = True

    def update(self, screen_width, screen_height):
        self.x += self.speed * self.direction[0]
        self.y += self.speed * self.direction[1]
        if self.x < 0 or self.x > screen_width or self.y < 0 or self.y > screen_height:
            self.alive = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.color = (0, 0, 255)
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.hp = 20
        self.max_hp = 20
        self.shoot_cooldown = 0
        self.attack_cooldown = 0
        self.attack_dir = (1, 0)  # 기본 오른쪽
        self.last_dir = (1, 0)    # 마지막 방향
        self.multishot = False
        self.multishot_timer = 0

    def get_input_direction(self, keys):
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_DOWN]:
            dy += 1
        if dx != 0 or dy != 0:
            length = (dx**2 + dy**2) ** 0.5
            return (dx/length, dy/length)
        else:
            return None

    def handle_keys(self, keys):
        self.vel_x = 0
        self.vel_y = 0
        input_dir = self.get_input_direction(keys)
        if input_dir:
            self.attack_dir = input_dir
            self.last_dir = input_dir
        else:
            self.attack_dir = self.last_dir
        if keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
        if keys[pygame.K_UP]:
            self.vel_y = -self.speed
        if keys[pygame.K_DOWN]:
            self.vel_y = self.speed

    def get_attack_rect(self):
        extra = 50
        dx, dy = self.attack_dir
        if dx == 1 and dy == 0:
            return pygame.Rect(self.x + self.width, self.y + 10, extra, self.height - 20)
        elif dx == -1 and dy == 0:
            return pygame.Rect(self.x - extra, self.y + 10, extra, self.height - 20)
        elif dx == 0 and dy == -1:
            return pygame.Rect(self.x + 10, self.y - extra, self.width - 20, extra)
        elif dx == 0 and dy == 1:
            return pygame.Rect(self.x + 10, self.y + self.height, self.width - 20, extra)
        elif dx > 0 and dy < 0:
            return pygame.Rect(self.x + self.width, self.y - extra, extra, extra)
        elif dx < 0 and dy < 0:
            return pygame.Rect(self.x - extra, self.y - extra, extra, extra)
        elif dx > 0 and dy > 0:
            return pygame.Rect(self.x + self.width, self.y + self.height, extra, extra)
        elif dx < 0 and dy > 0:
            return pygame.Rect(self.x - extra, self.y + self.height, extra, extra)
        else:
            return pygame.Rect(self.x, self.y, self.width, self.height)

    def shoot(self):
        if self.shoot_cooldown == 0:
            dx, dy = self.attack_dir
            proj_x = self.x + self.width // 2
            proj_y = self.y + self.height // 2
            self.shoot_cooldown = 15
            projectiles = []
            if self.multishot:
                # 10방향, 30도 간격
                angle0 = math.atan2(dy, dx)
                for i in range(10):
                    angle = angle0 + math.radians(-135 + i*30)
                    dir_x = math.cos(angle)
                    dir_y = math.sin(angle)
                    projectiles.append(Projectile(proj_x, proj_y, (dir_x, dir_y)))
            else:
                projectiles.append(Projectile(proj_x, proj_y, (dx, dy)))
            return projectiles
        return []

    def update(self, screen_height, screen_width):
        self.x += self.vel_x
        self.y += self.vel_y
        if self.x < 0:
            self.x = 0
        if self.x + self.width > screen_width:
            self.x = screen_width - self.width
        if self.y < 0:
            self.y = 0
        if self.y + self.height > screen_height:
            self.y = screen_height - self.height
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.multishot:
            self.multishot_timer -= 1
            if self.multishot_timer <= 0:
                self.multishot = False

    def draw(self, screen):
        # 인형 외형 그리기
        cx = int(self.x + self.width // 2)
        cy = int(self.y + self.height // 4)
        # 머리
        pygame.draw.circle(screen, (255, 220, 180), (cx, cy), 18)
        # 몸통
        pygame.draw.rect(screen, (200, 180, 255), (self.x + 10, self.y + 30, 20, 30))
        # 팔
        pygame.draw.line(screen, (150, 120, 80), (self.x, self.y + 40), (self.x + self.width, self.y + 40), 6)
        # 다리
        pygame.draw.line(screen, (120, 80, 60), (self.x + 15, self.y + self.height), (self.x + 15, self.y + 50), 5)
        pygame.draw.line(screen, (120, 80, 60), (self.x + 25, self.y + self.height), (self.x + 25, self.y + 50), 5)
        # HP바
        pygame.draw.rect(screen, (0,0,0), (self.x, self.y-16, self.width, 10))
        hp_width = int(self.width * (self.hp / self.max_hp))
        pygame.draw.rect(screen, (0,0,255), (self.x, self.y-16, hp_width, 10)) 