import pygame
import sys
import random
import math
from player import Player, Projectile
from monster import Monster, DragonBoss, MonsterProjectile

# 게임 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 난이도 설정
DIFFICULTY_LEVELS = ['Easy', 'Normal', 'Hard']

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

ATTACK_DAMAGE = 3
ATTACK_COOLDOWN = 20
PORTAL_RADIUS = 32
PORTAL_X = 740  # 오른쪽 끝 근처
PORTAL_Y = 500

ITEM_DURATION = 300  # 멀티샷 효과 지속 프레임(5초)
ITEM_RADIUS = 18

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('2D 스테이지 게임')
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)

# 난이도 선택 함수
def select_difficulty():
    selected = 0
    while True:
        screen.fill(WHITE)
        title = font.render('난이도 선택', True, BLACK)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        for i, level in enumerate(DIFFICULTY_LEVELS):
            color = BLACK if i == selected else GRAY
            text = font.render(level, True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 200 + i*60))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(DIFFICULTY_LEVELS)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(DIFFICULTY_LEVELS)
                elif event.key == pygame.K_RETURN:
                    return DIFFICULTY_LEVELS[selected]
        clock.tick(15)

# 일시정지 메뉴 함수
def pause_menu():
    selected = 0
    options = ['계속하기', '게임 종료']
    while True:
        screen.fill(GRAY)
        title = font.render('일시정지', True, BLACK)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        for i, opt in enumerate(options):
            color = BLACK if i == selected else WHITE
            text = font.render(opt, True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 250 + i*60))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return selected  # 0: 계속, 1: 종료
        clock.tick(15)

# 스테이지별 몬스터 수 설정
def get_monster_count(stage, difficulty):
    # 난이도별 몬스터 최대 수 제한
    max_monsters = {'Easy': 6, 'Normal': 9, 'Hard': 12}
    base = [3, 5, 4, 4, 0]
    diff = {'Easy': 0, 'Normal': 2, 'Hard': 4}
    count = base[stage-1] + diff[difficulty]
    return min(count, max_monsters[difficulty])

class Item:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 300  # 5초간 유지
        self.radius = ITEM_RADIUS
    def update(self):
        self.timer -= 1
    def draw(self, screen):
        pygame.draw.circle(screen, (255, 200, 0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.radius-6)

# 메인 게임 루프
def main():
    difficulty = select_difficulty()
    stage = 1  # 난이도 선택 후 1스테이지부터 시작
    player = Player(100, SCREEN_HEIGHT-100)
    monsters = []
    boss = None
    running = True
    paused = False
    portal_active = False
    portal_rect = pygame.Rect(PORTAL_X-PORTAL_RADIUS, PORTAL_Y-PORTAL_RADIUS, PORTAL_RADIUS*2, PORTAL_RADIUS*2)
    projectiles = []
    monster_projectiles = []
    items = []
    def spawn(stage):
        nonlocal monsters, boss, portal_active, projectiles, monster_projectiles, items
        monsters = []
        boss = None
        portal_active = False
        projectiles = []
        monster_projectiles = []
        items = []
        if stage < 5:
            for i in range(get_monster_count(stage, difficulty)):
                rand_x = random.randint(0, SCREEN_WIDTH-40)
                rand_y = random.randint(0, SCREEN_HEIGHT-60)
                monsters.append(Monster(rand_x, rand_y))
        else:
            boss = DragonBoss(SCREEN_WIDTH//2-60, SCREEN_HEIGHT-180)
    spawn(stage)
    while running:
        if not paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = True
                    # F5 키로 5스테이지 바로가기
                    if event.key == pygame.K_F5:
                        stage = 5
                        player.x, player.y = 100, SCREEN_HEIGHT-100
                        spawn(stage)
            keys = pygame.key.get_pressed()
            player.handle_keys(keys)
            # 방향키+CTRL 또는 CTRL만 눌러도 공격(마지막 방향 유지)
            ctrl_pressed = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
            direction_pressed = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]
            if ctrl_pressed and player.attack_cooldown == 0:
                # 근접 공격
                attack_rect = player.get_attack_rect()
                for m in monsters:
                    if m.alive and attack_rect.colliderect(pygame.Rect(m.x, m.y, m.width, m.height)):
                        dropped = m.take_damage(ATTACK_DAMAGE)
                        if dropped:
                            items.append(Item(m.x + m.width//2, m.y + m.height//2))
                if boss:
                    if boss.hp > 0 and attack_rect.colliderect(pygame.Rect(boss.x, boss.y, boss.width, boss.height)):
                        boss.take_damage(ATTACK_DAMAGE)
                player.attack_cooldown = 15
                # 원거리 공격
                new_projectiles = player.shoot()
                for proj in new_projectiles:
                    projectiles.append(proj)
            player.update(SCREEN_HEIGHT, SCREEN_WIDTH)
            if player.attack_cooldown > 0:
                player.attack_cooldown -= 1
            # 아이템 업데이트 및 획득 처리
            for item in items:
                item.update()
            items = [item for item in items if item.timer > 0]
            player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
            for item in items[:]:
                if player_rect.collidepoint(item.x, item.y):
                    player.multishot = True
                    player.multishot_timer = ITEM_DURATION
                    items.remove(item)
            # 총알 업데이트 및 충돌
            for proj in projectiles:
                proj.update(SCREEN_WIDTH, SCREEN_HEIGHT)
                for m in monsters:
                    if m.alive and pygame.Rect(m.x, m.y, m.width, m.height).collidepoint(proj.x, proj.y):
                        dropped = m.take_damage(ATTACK_DAMAGE)
                        if dropped:
                            items.append(Item(m.x + m.width//2, m.y + m.height//2))
                        proj.alive = False
                if boss:
                    if boss.hp > 0 and pygame.Rect(boss.x, boss.y, boss.width, boss.height).collidepoint(proj.x, proj.y):
                        boss.take_damage(ATTACK_DAMAGE)
                        proj.alive = False
            projectiles = [p for p in projectiles if p.alive]
            # 몬스터 총알 업데이트 및 충돌
            for m in monsters:
                m.update(SCREEN_WIDTH, SCREEN_HEIGHT)
                m.hit_player(player)
                m_proj = m.shoot(player)
                if m_proj:
                    monster_projectiles.append(m_proj)
            for m_proj in monster_projectiles:
                m_proj.update(SCREEN_WIDTH, SCREEN_HEIGHT)
                if pygame.Rect(player.x, player.y, player.width, player.height).collidepoint(m_proj.x, m_proj.y):
                    player.hp -= 1
                    if player.hp < 0:
                        player.hp = 0
                    m_proj.alive = False
            monster_projectiles = [mp for mp in monster_projectiles if mp.alive]
            monsters = [m for m in monsters if m.alive]
            if boss:
                boss.update(SCREEN_WIDTH, SCREEN_HEIGHT, player.x, player.y)
                boss.hit_player(player)
                boss.hit_player_pattern(player)
            # 플레이어 체력이 0이 되면 게임 종료 및 the end 표시
            if player.hp <= 0:
                end = True
                while end:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                end = False
                                running = False
                    screen.fill((0,0,0))
                    msg = font.render('the end', True, (255,0,0))
                    msg2 = font.render('엔터를 눌러 종료', True, (255,255,255))
                    screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 220))
                    screen.blit(msg2, (SCREEN_WIDTH//2 - msg2.get_width()//2, 320))
                    pygame.display.flip()
                    clock.tick(30)
            # 포탈 활성화 조건: 몬스터가 모두 죽고, 보스가 없거나 보스가 죽었을 때
            if not monsters and (not boss or boss.hp <= 0):
                portal_active = True
            # 포탈 진입 처리
            if portal_active:
                player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
                if player_rect.colliderect(portal_rect) and keys[pygame.K_UP]:
                    if stage < 5:
                        stage += 1
                        player.x, player.y = 100, SCREEN_HEIGHT-100
                        spawn(stage)
                    else:
                        ending = True
                        while ending:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                elif event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_RETURN:
                                        ending = False
                                        running = False
                            screen.fill((0,0,0))
                            msg = font.render('축하합니다! 모든 스테이지 클리어!', True, (255,255,0))
                            msg2 = font.render('엔터를 눌러 종료', True, (255,255,255))
                            screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 220))
                            screen.blit(msg2, (SCREEN_WIDTH//2 - msg2.get_width()//2, 320))
                            pygame.display.flip()
                            clock.tick(30)
            # 화면 그리기
            screen.fill(WHITE)
            info = small_font.render(f'난이도: {difficulty} / 스테이지: {stage}', True, BLACK)
            screen.blit(info, (20, 20))
            hp_text = small_font.render(f'플레이어 HP: {player.hp} / {player.max_hp}', True, (0,0,255))
            screen.blit(hp_text, (20, 50))
            player.draw(screen)
            for item in items:
                item.draw(screen)
            for proj in projectiles:
                proj.draw(screen)
            for m_proj in monster_projectiles:
                m_proj.draw(screen)
            for m in monsters:
                m.draw(screen)
            if boss:
                boss.draw(screen)
            if portal_active:
                pygame.draw.circle(screen, (0,128,255), (PORTAL_X, PORTAL_Y), PORTAL_RADIUS)
                portal_msg = small_font.render('↑ 포탈 진입', True, (0,0,128))
                screen.blit(portal_msg, (PORTAL_X-40, PORTAL_Y-50))
            pygame.display.flip()
            clock.tick(FPS)
        else:
            sel = pause_menu()
            if sel == 0:
                paused = False
            else:
                running = False
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main() 