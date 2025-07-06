import pygame
import random
import math

DRAGON_IMAGE = None

class MonsterProjectile:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.radius = 10
        self.color = (255, 100, 0)
        self.speed = 4  # 더 느리게
        self.direction = direction  # (dx, dy)
        self.alive = True

    def update(self, screen_width, screen_height):
        self.x += self.speed * self.direction[0]
        self.y += self.speed * self.direction[1]
        if self.x < 0 or self.x > screen_width or self.y < 0 or self.y > screen_height:
            self.alive = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

def load_dragon_image():
    global DRAGON_IMAGE
    if DRAGON_IMAGE is None:
        DRAGON_IMAGE = pygame.image.load('dragon.png')
        DRAGON_IMAGE = pygame.transform.scale(DRAGON_IMAGE, (120, 80))

class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.color = (0, 200, 0)
        self.speed = 1.6
        self.hp = 6
        self.max_hp = 6
        self.alive = True
        self.attack_cooldown = 0
        self.shoot_cooldown = 0
        self.dir_x = random.choice([-1, 0, 1])
        self.dir_y = random.choice([-1, 0, 1])
        if self.dir_x == 0 and self.dir_y == 0:
            self.dir_x = 1
        self.type = random.choice(['skull', 'slime'])
        self.pattern_warning = False
        self.pattern_warning_timer = 0
        self.pattern_dir = None
        self.pattern_pos = None

    def update(self, screen_width, screen_height):
        # 상하좌우 자유 이동
        if random.randint(0, 30) == 0:
            self.dir_x = random.choice([-1, 0, 1])
            self.dir_y = random.choice([-1, 0, 1])
            if self.dir_x == 0 and self.dir_y == 0:
                self.dir_x = 1
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed
        if self.x < 0:
            self.x = 0
            self.dir_x *= -1
        if self.x + self.width > screen_width:
            self.x = screen_width - self.width
            self.dir_x *= -1
        if self.y < 0:
            self.y = 0
            self.dir_y *= -1
        if self.y + self.height > screen_height:
            self.y = screen_height - self.height
            self.dir_y *= -1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False
            return self.drop_item()
        return False

    def drop_item(self):
        # 30% 확률로 아이템 드랍
        return random.random() < 0.3

    def hit_player(self, player):
        if self.attack_cooldown == 0:
            if pygame.Rect(self.x, self.y, self.width, self.height).colliderect(
                pygame.Rect(player.x, player.y, player.width, player.height)):
                player.hp -= 1
                if player.hp < 0:
                    player.hp = 0
                self.attack_cooldown = 30

    def shoot(self, player):
        # 플레이어가 일정 거리 이내면 해당 방향으로 총알 발사
        dx = player.x + player.width//2 - (self.x + self.width//2)
        dy = player.y + player.height//2 - (self.y + self.height//2)
        distance = (dx**2 + dy**2) ** 0.5
        if distance < 200 and self.shoot_cooldown == 0:
            if distance == 0:
                direction = (1, 0)
            else:
                direction = (dx/distance, dy/distance)
            proj_x = self.x + self.width//2
            proj_y = self.y + self.height//2
            self.shoot_cooldown = 40
            return MonsterProjectile(proj_x, proj_y, direction)
        return None

    def draw(self, screen):
        if self.type == 'skull':
            # 해골: 머리(흰 원), 눈(검은 점), 입(선)
            cx = int(self.x + self.width // 2)
            cy = int(self.y + self.height // 2)
            pygame.draw.circle(screen, (230,230,230), (cx, cy), 20)  # 머리
            pygame.draw.circle(screen, (0,0,0), (cx-8, cy-5), 4)    # 왼눈
            pygame.draw.circle(screen, (0,0,0), (cx+8, cy-5), 4)    # 오른눈
            pygame.draw.line(screen, (0,0,0), (cx-8, cy+8), (cx+8, cy+8), 2)  # 입
        else:
            # 슬라임: 초록 반원, 눈, 입
            cx = int(self.x + self.width // 2)
            cy = int(self.y + self.height // 2)
            pygame.draw.ellipse(screen, (0,220,100), (self.x, self.y+10, self.width, self.height-10))  # 몸통
            pygame.draw.circle(screen, (0,0,0), (cx-8, cy+8), 4)    # 왼눈
            pygame.draw.circle(screen, (0,0,0), (cx+8, cy+8), 4)    # 오른눈
            pygame.draw.arc(screen, (0,0,0), (cx-10, cy+10, 20, 10), 3.14, 0, 2)  # 입
        # HP바
        pygame.draw.rect(screen, (0,0,0), (self.x, self.y-10, self.width, 6))
        hp_width = int(self.width * (self.hp / self.max_hp))
        pygame.draw.rect(screen, (0,200,0), (self.x, self.y-10, hp_width, 6))

class DragonBoss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 120
        self.height = 80
        self.color = (200, 0, 0)
        self.speed = 2
        self.pattern_timer = 0
        self.pattern = 0
        self.vel_x = 0
        self.vel_y = 0
        self.jump_power = 18
        self.is_jumping = False
        self.fireballs = []
        self.shockwaves = []
        self.hp = 100
        self.max_hp = 100
        self.pattern_cooldown = 0
        self.combo = 0
        self.target_x = x
        self.target_y = y
        self.warning = False
        self.warning_timer = 0
        self.attack_cooldown = 0
        self.dir_x = random.choice([-1, 0, 1])
        self.dir_y = random.choice([-1, 0, 1])
        if self.dir_x == 0 and self.dir_y == 0:
            self.dir_x = 1
        self.alive = True
        self.pattern_warning = False
        self.pattern_warning_timer = 0
        self.pattern_dir = None
        self.pattern_pos = None  # 패턴 6: 리스트로 사용
        self.player_ref = None
        load_dragon_image()

    def update(self, screen_width, screen_height, player_x=None, player_y=None):
        # 몬스터처럼 자유 이동
        if not self.is_jumping and not self.warning:
            if random.randint(0, 30) == 0:
                self.dir_x = random.choice([-1, 0, 1])
                self.dir_y = random.choice([-1, 0, 1])
                if self.dir_x == 0 and self.dir_y == 0:
                    self.dir_x = 1
            self.x += self.dir_x * self.speed
            self.y += self.dir_y * self.speed
            if self.x < 0:
                self.x = 0
                self.dir_x *= -1
            if self.x + self.width > screen_width:
                self.x = screen_width - self.width
                self.dir_x *= -1
            if self.y < 0:
                self.y = 0
                self.dir_y *= -1
            if self.y + self.height > screen_height:
                self.y = screen_height - self.height
                self.dir_y *= -1
        # 기본 공격: 항상 플레이어 방향으로 불덩이 발사 (빈도 더 줄임)
        if player_x is not None and player_y is not None and random.randint(0, 24) == 0:
            cx = self.x + self.width//2
            cy = self.y + self.height//2
            dx = player_x + 20 - cx
            dy = player_y + 30 - cy
            angle = math.atan2(dy, dx)
            speed = random.randint(5, 9)
            self.fireballs.append([cx, cy, speed * math.cos(angle), speed * math.sin(angle)])
        # 기존 패턴 공격 로직
        fireball_count = 1 + (self.max_hp - self.hp) // 30
        pattern_speed = 1 + (self.max_hp - self.hp) // 40
        self.pattern_timer += pattern_speed
        if self.pattern_cooldown > 0:
            self.pattern_cooldown -= 1
            return
        if self.pattern_warning:
            self.pattern_warning_timer -= 1
            if self.pattern_warning_timer <= 0:
                self.pattern_warning = False
                # 패턴 실행 준비 완료
                if self.pattern == 4:
                    # 한쪽 벽까지 돌진
                    if isinstance(self.pattern_dir, tuple) and len(self.pattern_dir) == 2:
                        self.vel_x, self.vel_y = self.pattern_dir
                        # 돌진 방향으로 쭉 이동(속도 고정)
                elif self.pattern == 5:
                    # 대각선 돌진
                    if isinstance(self.pattern_dir, tuple) and len(self.pattern_dir) == 2:
                        self.vel_x, self.vel_y = self.pattern_dir
                        # 대각선 방향으로 쭉 이동(속도 고정)
                elif self.pattern == 6:
                    # 충격파 4개 생성
                    if isinstance(self.pattern_pos, list) and len(self.pattern_pos) == 4:
                        for pos in self.pattern_pos:
                            self.shockwaves.append([pos[0], pos[1], 0])
                        self.pattern_cooldown = 40
        elif self.pattern_timer > 80:
            self.pattern = random.choice([0, 1, 2, 3, 4, 5, 6])
            self.pattern_timer = 0
            self.combo = random.choice([1, 2])
            if self.pattern == 1:
                if player_x is not None:
                    self.target_x = player_x
                if player_y is not None:
                    self.target_y = player_y
                self.warning = True
                self.warning_timer = 30
            elif self.pattern == 2 and not self.is_jumping:
                self.is_jumping = True
                self.vel_y = -self.jump_power
            elif self.pattern == 4:
                # (1) 예고 후 한쪽 벽까지 돌진
                self.pattern_warning = True
                self.pattern_warning_timer = 60
                # 방향: 상하좌우 중 랜덤
                dirs = [(-1,0),(1,0),(0,-1),(0,1)]
                self.pattern_dir = random.choice(dirs)
            elif self.pattern == 5:
                # (2) 예고 후 대각선 돌진
                self.pattern_warning = True
                self.pattern_warning_timer = 60
                # 대각선 방향 랜덤
                dirs = [(-1,-1),(1,-1),(-1,1),(1,1)]
                self.pattern_dir = random.choice(dirs)
            elif self.pattern == 6:
                # (3) 예고 후 랜덤 위치 충격파 4개
                self.pattern_warning = True
                self.pattern_warning_timer = 60
                self.pattern_pos = []
                for _ in range(4):
                    px = random.randint(60, screen_width-60)
                    py = random.randint(60, screen_height-60)
                    self.pattern_pos.append((px, py))
        # 패턴 실행
        if self.pattern == 0:
            # 불뿜기: 플레이어 방향으로 발사 (빈도 더 줄임)
            if player_x is not None and player_y is not None and random.randint(0, 17) == 0:
                cx = self.x + self.width//2
                cy = self.y + self.height//2
                dx = player_x + 20 - cx
                dy = player_y + 30 - cy
                base_angle = math.atan2(dy, dx)
                for i in range(fireball_count):
                    angle = base_angle + random.uniform(-0.3, 0.3)
                    speed = random.randint(5, 9)
                    self.fireballs.append([cx, cy, speed * math.cos(angle), speed * math.sin(angle)])
        elif self.pattern == 1:
            if self.warning:
                self.warning_timer -= 1
                if self.warning_timer <= 0:
                    self.warning = False
                    if player_x is not None:
                        self.vel_x = (player_x - self.x) // abs(player_x - self.x) * self.speed * 3 if player_x != self.x else 0
            else:
                self.x += self.vel_x
                if self.x < 0 or self.x + self.width > screen_width or (player_x is not None and abs(self.x - player_x) < 10):
                    self.vel_x = 0
                    self.pattern_cooldown = 30
        elif self.pattern == 2:
            if self.is_jumping:
                self.y += self.vel_y
                self.vel_y += 1
                if self.y + self.height >= screen_height:
                    self.y = screen_height - self.height
                    self.is_jumping = False
                    self.vel_y = 0
                    self.shockwaves.append([self.x + self.width//2, self.y + self.height, 1])
                    self.shockwaves.append([self.x + self.width//2, self.y + self.height, -1])
        elif self.pattern == 3:
            # 불뿜기+돌진 연속: 불뿜기는 플레이어 방향 (빈도 더 줄임)
            if self.combo > 0:
                if player_x is not None and player_y is not None and random.randint(0, 11) == 0:
                    cx = self.x + self.width//2
                    cy = self.y + self.height//2
                    dx = player_x + 20 - cx
                    dy = player_y + 30 - cy
                    base_angle = math.atan2(dy, dx)
                    for i in range(fireball_count):
                        angle = base_angle + random.uniform(-0.2, 0.2)
                        speed = random.randint(6, 10)
                        self.fireballs.append([cx, cy, speed * math.cos(angle), speed * math.sin(angle)])
                self.combo -= 1
            else:
                if player_x is not None:
                    self.vel_x = (player_x - self.x) // abs(player_x - self.x) * self.speed * 3 if player_x != self.x else 0
                self.x += self.vel_x
                if self.x < 0 or self.x + self.width > screen_width or (player_x is not None and abs(self.x - player_x) < 10):
                    self.vel_x = 0
                    self.pattern_cooldown = 30
        elif self.pattern == 4:
            # (1) 한쪽 벽까지 돌진
            if not self.pattern_warning and self.pattern_dir is not None and (self.vel_x != 0 or self.vel_y != 0):
                self.x += self.vel_x * 14
                self.y += self.vel_y * 14
                # 벽에 닿으면 멈춤
                if self.x < 0:
                    self.x = 0
                    self.vel_x = 0
                if self.x + self.width > screen_width:
                    self.x = screen_width - self.width
                    self.vel_x = 0
                if self.y < 0:
                    self.y = 0
                    self.vel_y = 0
                if self.y + self.height > screen_height:
                    self.y = screen_height - self.height
                    self.vel_y = 0
                # 돌진 중 플레이어와 충돌 시 데미지 5
                if hasattr(self, 'player_ref') and self.player_ref is not None:
                    player = self.player_ref
                    if pygame.Rect(self.x, self.y, self.width, self.height).colliderect(
                        pygame.Rect(player.x, player.y, player.width, player.height)):
                        player.hp -= 5
                        if player.hp < 0:
                            player.hp = 0
                if self.vel_x == 0 and self.vel_y == 0:
                    self.pattern_cooldown = 25
                    self.pattern_dir = None
            else:
                self.vel_x = 0
                self.vel_y = 0
        elif self.pattern == 5:
            # (2) 대각선 돌진
            if not self.pattern_warning and self.pattern_dir is not None and (self.vel_x != 0 or self.vel_y != 0):
                self.x += self.vel_x * 12
                self.y += self.vel_y * 12
                # 돌진 중 플레이어와 충돌 시 데미지 5
                if hasattr(self, 'player_ref') and self.player_ref is not None:
                    player = self.player_ref
                    if pygame.Rect(self.x, self.y, self.width, self.height).colliderect(
                        pygame.Rect(player.x, player.y, player.width, player.height)):
                        player.hp -= 5
                        if player.hp < 0:
                            player.hp = 0
                if self.x < 0:
                    self.x = 0
                    self.vel_x = 0
                if self.x + self.width > screen_width:
                    self.x = screen_width - self.width
                    self.vel_x = 0
                if self.y < 0:
                    self.y = 0
                    self.vel_y = 0
                if self.y + self.height > screen_height:
                    self.y = screen_height - self.height
                    self.vel_y = 0
                if self.vel_x == 0 and self.vel_y == 0:
                    self.pattern_cooldown = 25
                    self.pattern_dir = None
            else:
                self.vel_x = 0
                self.vel_y = 0
        elif self.pattern == 6:
            # (3) 충격파 생성(실제 생성은 warning 끝나고 위에서)
            if not self.pattern_warning and self.pattern_pos is not None:
                self.pattern_pos = None
                self.pattern_cooldown = 25
        for fireball in self.fireballs:
            fireball[0] += fireball[2]
            fireball[1] += fireball[3]
        self.fireballs = [f for f in self.fireballs if 0 < f[0] < screen_width and 0 < f[1] < screen_height]
        for shock in self.shockwaves:
            shock[0] += shock[2] * 12
        self.shockwaves = [s for s in self.shockwaves if 0 < s[0] < screen_width]
        if self.hp <= 0:
            self.alive = False

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0

    def hit_player(self, player):
        if self.attack_cooldown == 0:
            if pygame.Rect(self.x, self.y, self.width, self.height).colliderect(
                pygame.Rect(player.x, player.y, player.width, player.height)):
                player.hp -= 1
                if player.hp < 0:
                    player.hp = 0
                self.attack_cooldown = 30

    def hit_player_pattern(self, player):
        # 불덩이(파란 원) 충돌
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        for fireball in self.fireballs:
            if player_rect.collidepoint(fireball[0], fireball[1]):
                player.hp -= 2
                if player.hp < 0:
                    player.hp = 0
                self.fireballs.remove(fireball)
        # 충격파(노란 원) 충돌
        for shock in self.shockwaves:
            if player_rect.collidepoint(shock[0], shock[1]):
                player.hp -= 2
                if player.hp < 0:
                    player.hp = 0
                self.shockwaves.remove(shock)

    def draw(self, screen):
        if not self.alive:
            return
        if DRAGON_IMAGE:
            screen.blit(DRAGON_IMAGE, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        for fireball in self.fireballs:
            pygame.draw.circle(screen, (0,0,255), (int(fireball[0]), int(fireball[1])), 10)
        for shock in self.shockwaves:
            pygame.draw.circle(screen, (255, 215, 0), (int(shock[0]), int(shock[1])), 18, 3)
        if self.warning:
            pygame.draw.rect(screen, (255,0,0), (self.x-5, self.y-5, self.width+10, self.height+10), 4)
        pygame.draw.rect(screen, (0,0,0), (self.x, self.y-16, self.width, 10))
        hp_width = int(self.width * (self.hp / self.max_hp))
        pygame.draw.rect(screen, (255,0,0), (self.x, self.y-16, hp_width, 10))
        # 패턴 예고 시 시각적 경고 표시
        if self.pattern_warning:
            if (self.pattern == 4 or self.pattern == 5):
                if isinstance(self.pattern_dir, tuple) and len(self.pattern_dir) == 2:
                    cx = self.x + self.width//2
                    cy = self.y + self.height//2
                    dx = self.pattern_dir[0]*999
                    dy = self.pattern_dir[1]*999
                    pygame.draw.line(screen, (255,0,0), (cx, cy), (cx+dx, cy+dy), 6)
            elif self.pattern == 6:
                if isinstance(self.pattern_pos, list):
                    for pos in self.pattern_pos:
                        if isinstance(pos, tuple) and len(pos) == 2:
                            pygame.draw.circle(screen, (255,0,0), pos, 40, 6)

    # 플레이어 참조를 보스에 연결하는 함수(메인에서 1회 호출 필요)
    def set_player_ref(self, player):
        self.player_ref = player 