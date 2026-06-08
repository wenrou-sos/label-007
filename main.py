import pygame
import sys
import math
import random
from enum import Enum

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
DARK_RED = (150, 30, 30)
GREEN = (50, 200, 80)
DARK_GREEN = (30, 120, 50)
BLUE = (60, 120, 255)
YELLOW = (255, 220, 50)
ORANGE = (255, 150, 30)
PURPLE = (180, 80, 220)
GRAY = (120, 120, 120)
LIGHT_GRAY = (200, 200, 200)


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    UPGRADE = 3
    GAME_OVER = 4


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.speed = 3.5
        self.base_speed = 3.5
        self.max_hp = 100
        self.hp = 100
        self.attack_range = 80
        self.base_attack_range = 80
        self.attack_damage = 25
        self.base_attack_damage = 25
        self.attack_angle = math.radians(90)
        self.attack_cooldown = 0
        self.attack_cooldown_max = 20
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_dir = 0
        self.skill_cooldown = 0
        self.skill_cooldown_max = 600
        self.skill_radius = 300
        self.skill_damage = 80
        self.invincible = 0
        self.level = 1
        self.kills_for_level = 0
        self.kills_per_level = 50

    def move(self, keys):
        dx = 0
        dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
        if dx != 0 or dy != 0:
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length
            self.x += dx * self.speed
            self.y += dy * self.speed
        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))

    def attack(self, mouse_x, mouse_y):
        if self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_timer = 15
            self.attack_cooldown = self.attack_cooldown_max
            self.attack_dir = math.atan2(mouse_y - self.y, mouse_x - self.x)
            return True
        return False

    def use_skill(self):
        if self.skill_cooldown <= 0:
            self.skill_cooldown = self.skill_cooldown_max
            return True
        return False

    def update(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
        else:
            self.is_attacking = False
        if self.skill_cooldown > 0:
            self.skill_cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1

    def get_attack_hitbox(self):
        if not self.is_attacking:
            return None
        return {
            'x': self.x,
            'y': self.y,
            'range': self.attack_range,
            'direction': self.attack_dir,
            'angle': self.attack_angle,
            'damage': self.attack_damage
        }

    def take_damage(self, damage):
        if self.invincible > 0:
            return False
        self.hp -= damage
        self.invincible = 30
        return True

    def level_up(self, choice):
        self.level += 1
        self.kills_for_level = 0
        if choice == 'range':
            self.attack_range += 20
            self.attack_damage += 5
        elif choice == 'speed':
            self.speed += 0.5
            self.base_attack_damage += 3

    def draw(self, surface):
        if self.invincible > 0 and self.invincible % 6 < 3:
            color = (255, 200, 200)
        else:
            color = BLUE
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (40, 80, 180), (int(self.x), int(self.y)), self.radius - 4, 2)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        dir_x = mouse_x - self.x
        dir_y = mouse_y - self.y
        length = math.sqrt(dir_x * dir_x + dir_y * dir_y)
        if length > 0:
            dir_x /= length
            dir_y /= length
            sword_x = self.x + dir_x * (self.radius + 5)
            sword_y = self.y + dir_y * (self.radius + 5)
            pygame.draw.line(surface, LIGHT_GRAY, (int(self.x), int(self.y)),
                             (int(sword_x), int(sword_y)), 4)

        if self.is_attacking:
            self._draw_attack_arc(surface)

    def _draw_attack_arc(self, surface):
        progress = 1 - (self.attack_timer / 15)
        start_angle = self.attack_dir - self.attack_angle / 2
        end_angle = self.attack_dir + self.attack_angle / 2
        current_end = start_angle + (end_angle - start_angle) * progress

        arc_surf = pygame.Surface((self.attack_range * 2, self.attack_range * 2), pygame.SRCALPHA)
        alpha = int(180 * (1 - progress))
        color = (255, 255, 200, alpha)

        points = [(self.attack_range, self.attack_range)]
        steps = 20
        for i in range(steps + 1):
            t = i / steps
            angle = start_angle + (current_end - start_angle) * t
            px = self.attack_range + math.cos(angle) * self.attack_range
            py = self.attack_range + math.sin(angle) * self.attack_range
            points.append((px, py))

        if len(points) >= 3:
            pygame.draw.polygon(arc_surf, color, points)
            pygame.draw.arc(arc_surf, (255, 255, 100, 255),
                            pygame.Rect(0, 0, self.attack_range * 2, self.attack_range * 2),
                            start_angle, current_end, 4)

        surface.blit(arc_surf, (int(self.x - self.attack_range), int(self.y - self.attack_range)))


class Enemy:
    def __init__(self, x, y, enemy_type='normal'):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        if enemy_type == 'normal':
            self.radius = 14
            self.max_hp = 30
            self.speed = 1.6
            self.damage = 8
            self.color = RED
            self.score = 10
        elif enemy_type == 'elite':
            self.radius = 17
            self.max_hp = 70
            self.speed = 1.4
            self.damage = 12
            self.color = ORANGE
            self.score = 30
        self.hp = self.max_hp
        self.hit_flash = 0
        self.attack_cooldown = 0

    def update(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def take_damage(self, damage):
        self.hp -= damage
        self.hit_flash = 8
        return self.hp <= 0

    def check_player_collision(self, player):
        dx = self.x - player.x
        dy = self.y - player.y
        dist = math.sqrt(dx * dx + dy * dy)
        return dist < (self.radius + player.radius)

    def draw(self, surface):
        color = WHITE if self.hit_flash > 0 and self.hit_flash % 4 < 2 else self.color
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        darker = tuple(max(0, c - 60) for c in self.color)
        pygame.draw.circle(surface, darker, (int(self.x), int(self.y)), self.radius - 3, 2)

        if self.hp < self.max_hp:
            bar_width = self.radius * 2
            bar_height = 4
            bar_x = self.x - bar_width / 2
            bar_y = self.y - self.radius - 10
            pygame.draw.rect(surface, GRAY, (int(bar_x), int(bar_y), bar_width, bar_height))
            hp_ratio = self.hp / self.max_hp
            pygame.draw.rect(surface, GREEN, (int(bar_x), int(bar_y), int(bar_width * hp_ratio), bar_height))


class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 32
        self.max_hp = 500
        self.hp = 500
        self.speed = 1.2
        self.damage = 20
        self.color = PURPLE
        self.score = 200
        self.hit_flash = 0
        self.attack_cooldown = 0
        self.charge_cooldown = random.randint(180, 300)
        self.is_charging = False
        self.charge_dir_x = 0
        self.charge_dir_y = 0
        self.charge_timer = 0
        self.charge_duration = 30
        self.charge_speed = 7
        self.charge_windup = 0
        self.charge_windup_max = 40

    def update(self, player_x, player_y):
        if self.charge_windup > 0:
            self.charge_windup -= 1
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                self.charge_dir_x = dx / dist
                self.charge_dir_y = dy / dist
        elif self.is_charging:
            self.x += self.charge_dir_x * self.charge_speed
            self.y += self.charge_dir_y * self.charge_speed
            self.charge_timer -= 1
            if self.charge_timer <= 0:
                self.is_charging = False
                self.charge_cooldown = random.randint(240, 420)
        else:
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
            self.charge_cooldown -= 1
            if self.charge_cooldown <= 0:
                self.charge_windup = self.charge_windup_max
                self.is_charging = True
                self.charge_timer = self.charge_duration

        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))

        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def take_damage(self, damage):
        self.hp -= damage
        self.hit_flash = 8
        return self.hp <= 0

    def check_player_collision(self, player):
        dx = self.x - player.x
        dy = self.y - player.y
        dist = math.sqrt(dx * dx + dy * dy)
        return dist < (self.radius + player.radius)

    def draw(self, surface):
        if self.charge_windup > 0:
            flash = self.charge_windup % 10 < 5
            color = YELLOW if flash else self.color
        elif self.is_charging:
            color = (255, 100, 100)
        elif self.hit_flash > 0 and self.hit_flash % 4 < 2:
            color = WHITE
        else:
            color = self.color

        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        darker = tuple(max(0, c - 60) for c in (PURPLE if self.charge_windup <= 0 and not self.is_charging else color))
        pygame.draw.circle(surface, darker, (int(self.x), int(self.y)), self.radius - 5, 3)

        crown_pts = [
            (self.x - 18, self.y - self.radius + 5),
            (self.x - 10, self.y - self.radius - 12),
            (self.x, self.y - self.radius + 2),
            (self.x + 10, self.y - self.radius - 12),
            (self.x + 18, self.y - self.radius + 5)
        ]
        pygame.draw.lines(surface, YELLOW, False, crown_pts, 3)

        bar_width = self.radius * 2.5
        bar_height = 6
        bar_x = self.x - bar_width / 2
        bar_y = self.y - self.radius - 18
        pygame.draw.rect(surface, GRAY, (int(bar_x), int(bar_y), int(bar_width), bar_height))
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, RED, (int(bar_x), int(bar_y), int(bar_width * hp_ratio), bar_height))


class Particle:
    def __init__(self, x, y, color, size, speed_x, speed_y, life):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_x *= 0.92
        self.speed_y *= 0.92
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class SkillEffect:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.max_radius = radius
        self.life = 30
        self.max_life = 30

    def update(self):
        self.life -= 1

    def draw(self, surface):
        progress = 1 - (self.life / self.max_life)
        current_radius = int(self.max_radius * (0.3 + 0.7 * progress))
        alpha = int(200 * (1 - progress))
        s = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (150, 200, 255, alpha), (current_radius, current_radius), current_radius, 6)
        pygame.draw.circle(s, (200, 230, 255, int(alpha * 0.4)), (current_radius, current_radius), current_radius - 10)
        surface.blit(s, (int(self.x - current_radius), int(self.y - current_radius)))


class DamageNumber:
    def __init__(self, x, y, value, color=YELLOW):
        self.x = x
        self.y = y
        self.value = value
        self.color = color
        self.life = 40
        self.max_life = 40

    def update(self):
        self.y -= 1.2
        self.life -= 1

    def draw(self, surface, font):
        alpha = int(255 * (self.life / self.max_life))
        text = font.render(str(self.value), True, self.color)
        text_surf = pygame.Surface(text.get_size(), pygame.SRCALPHA)
        text_surf.blit(text, (0, 0))
        text_surf.set_alpha(alpha)
        surface.blit(text_surf, (int(self.x - text.get_width() / 2), int(self.y)))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("割草无双")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont("microsoftyahei, simhei, arial", 48, bold=True)
        self.font = pygame.font.SysFont("microsoftyahei, simhei, arial", 28, bold=True)
        self.font_small = pygame.font.SysFont("microsoftyahei, simhei, arial", 20)

        self.state = GameState.MENU
        self.player = None
        self.enemies = []
        self.bosses = []
        self.particles = []
        self.skill_effects = []
        self.damage_numbers = []

        self.score = 0
        self.total_kills = 0
        self.combo = 0
        self.max_combo = 0
        self.combo_timer = 0
        self.combo_timeout = 180

        self.spawn_timer = 0
        self.spawn_interval = 45
        self.boss_timer = 0
        self.boss_interval = 30 * FPS
        self.game_time = 0

        self.upgrade_options = []
        self.running = True

    def reset(self):
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.enemies = []
        self.bosses = []
        self.particles = []
        self.skill_effects = []
        self.damage_numbers = []
        self.score = 0
        self.total_kills = 0
        self.combo = 0
        self.max_combo = 0
        self.combo_timer = 0
        self.spawn_timer = 0
        self.boss_timer = 0
        self.game_time = 0

    def spawn_enemy(self):
        side = random.randint(0, 3)
        margin = 30
        if side == 0:
            x = random.randint(margin, SCREEN_WIDTH - margin)
            y = -margin
        elif side == 1:
            x = SCREEN_WIDTH + margin
            y = random.randint(margin, SCREEN_HEIGHT - margin)
        elif side == 2:
            x = random.randint(margin, SCREEN_WIDTH - margin)
            y = SCREEN_HEIGHT + margin
        else:
            x = -margin
            y = random.randint(margin, SCREEN_HEIGHT - margin)

        enemy_type = 'elite' if random.random() < 0.12 else 'normal'
        self.enemies.append(Enemy(x, y, enemy_type))

    def spawn_boss(self):
        side = random.randint(0, 3)
        margin = 50
        if side == 0:
            x = random.randint(margin, SCREEN_WIDTH - margin)
            y = -margin
        elif side == 1:
            x = SCREEN_WIDTH + margin
            y = random.randint(margin, SCREEN_HEIGHT - margin)
        elif side == 2:
            x = random.randint(margin, SCREEN_WIDTH - margin)
            y = SCREEN_HEIGHT + margin
        else:
            x = -margin
            y = random.randint(margin, SCREEN_HEIGHT - margin)
        self.bosses.append(Boss(x, y))

    def spawn_particles(self, x, y, color, count=8):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 5)
            size = random.randint(2, 6)
            life = random.randint(15, 35)
            self.particles.append(Particle(
                x, y, color, size,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                life
            ))

    def check_attack_hits(self):
        hitbox = self.player.get_attack_hitbox()
        if not hitbox:
            return

        all_targets = self.enemies + self.bosses
        for target in all_targets[:]:
            dx = target.x - hitbox['x']
            dy = target.y - hitbox['y']
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= hitbox['range'] + target.radius:
                angle_to_target = math.atan2(dy, dx)
                angle_diff = abs(self._normalize_angle(angle_to_target - hitbox['direction']))
                if angle_diff <= hitbox['angle'] / 2:
                    combo_bonus = 1 + min(self.combo * 0.02, 1.0)
                    damage = int(hitbox['damage'] * combo_bonus)
                    if isinstance(target, Boss):
                        if target.take_damage(damage):
                            self._on_boss_killed(target)
                    else:
                        if target.take_damage(damage):
                            self._on_enemy_killed(target)
                    self.damage_numbers.append(DamageNumber(target.x, target.y - target.radius, damage))
                    self.spawn_particles(target.x, target.y, target.color, 4)

    def _normalize_angle(self, angle):
        while angle > math.pi:
            angle -= math.pi * 2
        while angle < -math.pi:
            angle += math.pi * 2
        return abs(angle)

    def _on_enemy_killed(self, enemy):
        if enemy in self.enemies:
            self.enemies.remove(enemy)
        self.score += enemy.score
        self.total_kills += 1
        self.player.kills_for_level += 1
        self.combo += 1
        self.combo_timer = self.combo_timeout
        if self.combo > self.max_combo:
            self.max_combo = self.combo
        self.spawn_particles(enemy.x, enemy.y, enemy.color, 15)

        if self.player.kills_for_level >= self.player.kills_per_level:
            self._trigger_upgrade()

    def _on_boss_killed(self, boss):
        if boss in self.bosses:
            self.bosses.remove(boss)
        self.score += boss.score
        self.total_kills += 1
        self.combo += 5
        self.combo_timer = self.combo_timeout
        if self.combo > self.max_combo:
            self.max_combo = self.combo
        self.spawn_particles(boss.x, boss.y, PURPLE, 40)

    def _trigger_upgrade(self):
        self.state = GameState.UPGRADE
        self.upgrade_options = [
            {'key': 'range', 'name': '扩大攻击范围', 'desc': '攻击范围+20, 攻击伤害+5'},
            {'key': 'speed', 'name': '提升移动速度', 'desc': '移动速度+0.5, 攻击伤害+3'}
        ]

    def use_player_skill(self):
        if not self.player.use_skill():
            return

        self.skill_effects.append(SkillEffect(self.player.x, self.player.y, self.player.skill_radius))

        all_targets = self.enemies + self.bosses
        for target in all_targets[:]:
            dx = target.x - self.player.x
            dy = target.y - self.player.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= self.player.skill_radius + target.radius:
                if isinstance(target, Boss):
                    if target.take_damage(self.player.skill_damage):
                        self._on_boss_killed(target)
                else:
                    if target.take_damage(self.player.skill_damage):
                        self._on_enemy_killed(target)
                self.damage_numbers.append(DamageNumber(
                    target.x, target.y - target.radius, self.player.skill_damage, (150, 220, 255)
                ))
                self.spawn_particles(target.x, target.y, (150, 200, 255), 10)

    def check_enemy_attacks(self):
        all_enemies = self.enemies + self.bosses
        for enemy in all_enemies:
            if enemy.check_player_collision(self.player) and enemy.attack_cooldown <= 0:
                if self.player.take_damage(enemy.damage):
                    self.combo = 0
                    self.spawn_particles(self.player.x, self.player.y, RED, 10)
                enemy.attack_cooldown = 40
                if self.player.hp <= 0:
                    self.state = GameState.GAME_OVER

    def update(self):
        if self.state != GameState.PLAYING:
            return

        self.game_time += 1
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        self.player.update()

        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo = 0

        self.spawn_timer += 1
        current_interval = max(8, self.spawn_interval - self.game_time // 600)
        if self.spawn_timer >= current_interval:
            self.spawn_timer = 0
            batch = min(1 + self.game_time // 1200, 5)
            for _ in range(batch):
                self.spawn_enemy()

        self.boss_timer += 1
        if self.boss_timer >= self.boss_interval:
            self.boss_timer = 0
            self.spawn_boss()

        for enemy in self.enemies:
            enemy.update(self.player.x, self.player.y)
        for boss in self.bosses:
            boss.update(self.player.x, self.player.y)

        self.check_attack_hits()
        self.check_enemy_attacks()

        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)
        for e in self.skill_effects[:]:
            e.update()
            if e.life <= 0:
                self.skill_effects.remove(e)
        for d in self.damage_numbers[:]:
            d.update()
            if d.life <= 0:
                self.damage_numbers.remove(d)

    def draw(self):
        self.screen.fill((30, 30, 40))
        self._draw_grid()

        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.PLAYING or self.state == GameState.UPGRADE:
            for p in self.particles:
                p.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for boss in self.bosses:
                boss.draw(self.screen)
            self.player.draw(self.screen)
            for e in self.skill_effects:
                e.draw(self.screen)
            for d in self.damage_numbers:
                d.draw(self.screen, self.font_small)
            self._draw_ui()
            if self.state == GameState.UPGRADE:
                self._draw_upgrade_screen()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_grid(self):
        grid_size = 60
        for x in range(0, SCREEN_WIDTH, grid_size):
            pygame.draw.line(self.screen, (45, 45, 55), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(self.screen, (45, 45, 55), (0, y), (SCREEN_WIDTH, y))

    def _draw_ui(self):
        hp_bar_width = 280
        hp_bar_height = 24
        hp_bar_x = 20
        hp_bar_y = 20
        pygame.draw.rect(self.screen, DARK_RED, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        hp_ratio = max(0, self.player.hp / self.player.max_hp)
        pygame.draw.rect(self.screen, RED, (hp_bar_x, hp_bar_y, int(hp_bar_width * hp_ratio), hp_bar_height))
        pygame.draw.rect(self.screen, WHITE, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)
        hp_text = self.font_small.render(f"HP: {max(0, self.player.hp)} / {self.player.max_hp}", True, WHITE)
        self.screen.blit(hp_text, (hp_bar_x + 8, hp_bar_y + 3))

        score_text = self.font.render(f"得分: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (20, hp_bar_y + hp_bar_height + 12))

        level_text = self.font_small.render(f"等级: {self.player.level}  击杀: {self.total_kills}", True, WHITE)
        self.screen.blit(level_text, (20, hp_bar_y + hp_bar_height + 48))

        xp_bar_width = 200
        xp_bar_height = 8
        xp_x = 20
        xp_y = hp_bar_y + hp_bar_height + 80
        pygame.draw.rect(self.screen, (60, 60, 80), (xp_x, xp_y, xp_bar_width, xp_bar_height))
        xp_ratio = self.player.kills_for_level / self.player.kills_per_level
        pygame.draw.rect(self.screen, BLUE, (xp_x, xp_y, int(xp_bar_width * xp_ratio), xp_bar_height))
        pygame.draw.rect(self.screen, WHITE, (xp_x, xp_y, xp_bar_width, xp_bar_height), 1)
        xp_text = self.font_small.render(f"升级进度: {self.player.kills_for_level}/{self.player.kills_per_level}", True, LIGHT_GRAY)
        self.screen.blit(xp_text, (xp_x + xp_bar_width + 10, xp_y - 4))

        if self.combo > 0:
            combo_color = YELLOW if self.combo < 10 else ORANGE if self.combo < 25 else RED
            combo_text = self.font_big.render(f"{self.combo} COMBO!", True, combo_color)
            tx = SCREEN_WIDTH - combo_text.get_width() - 25
            ty = 20
            outline = self.font_big.render(f"{self.combo} COMBO!", True, BLACK)
            self.screen.blit(outline, (tx + 2, ty + 2))
            self.screen.blit(combo_text, (tx, ty))
            bonus = int(min(self.combo * 2, 100))
            bonus_text = self.font_small.render(f"攻击力 +{bonus}%", True, combo_color)
            self.screen.blit(bonus_text, (SCREEN_WIDTH - bonus_text.get_width() - 25, ty + 55))

        skill_x = SCREEN_WIDTH - 100
        skill_y = SCREEN_HEIGHT - 100
        skill_radius = 38
        pygame.draw.circle(self.screen, (50, 50, 70), (skill_x, skill_y), skill_radius)
        if self.player.skill_cooldown > 0:
            cd_ratio = self.player.skill_cooldown / self.player.skill_cooldown_max
            cd_angle = cd_ratio * math.pi * 2
            cd_surf = pygame.Surface((skill_radius * 2, skill_radius * 2), pygame.SRCALPHA)
            pygame.draw.rect(cd_surf, (0, 0, 0, 180),
                             (0, 0, skill_radius * 2, skill_radius * 2))
            pygame.draw.polygon(cd_surf, (0, 0, 0, 0), [
                (skill_radius, skill_radius),
                (skill_radius + math.cos(-math.pi / 2 - cd_angle) * skill_radius * 2,
                 skill_radius + math.sin(-math.pi / 2 - cd_angle) * skill_radius * 2),
                (skill_radius, skill_radius - skill_radius * 2)
            ])
            self.screen.blit(cd_surf, (skill_x - skill_radius, skill_y - skill_radius))
        else:
            pygame.draw.circle(self.screen, (80, 150, 255), (skill_x, skill_y), skill_radius, 3)
        pygame.draw.circle(self.screen, WHITE, (skill_x, skill_y), skill_radius, 2)
        key_text = self.font_small.render("SPACE", True, WHITE)
        self.screen.blit(key_text, (skill_x - key_text.get_width() / 2, skill_y - 8))
        if self.player.skill_cooldown > 0:
            cd_text = self.font_small.render(f"{self.player.skill_cooldown // FPS + 1}s", True, LIGHT_GRAY)
            self.screen.blit(cd_text, (skill_x - cd_text.get_width() / 2, skill_y + 10))

        controls = [
            "WASD - 移动",
            "鼠标左键 - 挥砍",
            "空格 - 全屏技能"
        ]
        for i, c in enumerate(controls):
            t = self.font_small.render(c, True, (150, 150, 170))
            self.screen.blit(t, (SCREEN_WIDTH - 170, 110 + i * 24))

    def _draw_menu(self):
        title = self.font_big.render("割 草 无 双", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, SCREEN_HEIGHT / 2 - 150))

        subtitle = self.font.render("一骑当千，横扫千军！", True, WHITE)
        self.screen.blit(subtitle, (SCREEN_WIDTH / 2 - subtitle.get_width() / 2, SCREEN_HEIGHT / 2 - 80))

        controls = [
            "操作说明:",
            "  WASD 方向键 - 移动角色",
            "  鼠标左键 - 朝鼠标方向挥砍攻击",
            "  空格 - 释放全屏技能（有冷却）",
            "",
            "玩法说明:",
            "  击杀小兵获得 10 分，精英 30 分，武将 200 分",
            "  每击杀 50 个敌人升级，选择强化",
            "  连杀越高攻击力加成越多，被击中则重置",
            "  血量归零游戏结束"
        ]
        for i, line in enumerate(controls):
            t = self.font_small.render(line, True, LIGHT_GRAY)
            self.screen.blit(t, (SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2 - 10 + i * 26))

        start = self.font.render("按 回车键 开始游戏", True, GREEN)
        self.screen.blit(start, (SCREEN_WIDTH / 2 - start.get_width() / 2, SCREEN_HEIGHT / 2 + 240))

    def _draw_upgrade_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        title = self.font_big.render(f"升级！等级 {self.player.level} → {self.player.level + 1}", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 120))

        tip = self.font.render("选择一项强化（按 1 或 2）", True, WHITE)
        self.screen.blit(tip, (SCREEN_WIDTH / 2 - tip.get_width() / 2, 200))

        card_w = 340
        card_h = 260
        spacing = 80
        total_w = card_w * 2 + spacing
        start_x = (SCREEN_WIDTH - total_w) / 2
        card_y = 280

        for i, opt in enumerate(self.upgrade_options):
            cx = start_x + i * (card_w + spacing)
            pygame.draw.rect(self.screen, (50, 50, 70), (cx, card_y, card_w, card_h), border_radius=12)
            pygame.draw.rect(self.screen, YELLOW if i == 0 else (100, 200, 255),
                             (cx, card_y, card_w, card_h), 4, border_radius=12)

            num = self.font_big.render(str(i + 1), True, YELLOW if i == 0 else (100, 200, 255))
            self.screen.blit(num, (cx + 20, card_y + 15))

            name = self.font.render(opt['name'], True, WHITE)
            self.screen.blit(name, (cx + card_w / 2 - name.get_width() / 2, card_y + 80))

            desc = self.font_small.render(opt['desc'], True, LIGHT_GRAY)
            self.screen.blit(desc, (cx + card_w / 2 - desc.get_width() / 2, card_y + 140))

    def _draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        title = self.font_big.render("战 败", True, RED)
        self.screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 120))

        stats = [
            f"最终得分: {self.score}",
            f"击杀数: {self.total_kills}",
            f"最高连杀: {self.max_combo}",
            f"最终等级: {self.player.level}",
            f"存活时间: {self.game_time // FPS} 秒"
        ]
        for i, s in enumerate(stats):
            t = self.font.render(s, True, WHITE)
            self.screen.blit(t, (SCREEN_WIDTH / 2 - t.get_width() / 2, 240 + i * 50))

        restart = self.font.render("按 回车键 重新开始", True, GREEN)
        self.screen.blit(restart, (SCREEN_WIDTH / 2 - restart.get_width() / 2, SCREEN_HEIGHT - 120))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if self.state == GameState.MENU:
                if event.key == pygame.K_RETURN:
                    self.reset()
                    self.state = GameState.PLAYING
            elif self.state == GameState.PLAYING:
                if event.key == pygame.K_SPACE:
                    self.use_player_skill()
            elif self.state == GameState.UPGRADE:
                if event.key == pygame.K_1:
                    self.player.level_up('range')
                    self.state = GameState.PLAYING
                elif event.key == pygame.K_2:
                    self.player.level_up('speed')
                    self.state = GameState.PLAYING
            elif self.state == GameState.GAME_OVER:
                if event.key == pygame.K_RETURN:
                    self.reset()
                    self.state = GameState.PLAYING
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == GameState.PLAYING and event.button == 1:
                self.player.attack(event.pos[0], event.pos[1])

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
