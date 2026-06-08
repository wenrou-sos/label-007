import pygame
import math
from . import settings


def _normalize_angle(angle):
    while angle > math.pi:
        angle -= math.pi * 2
    while angle < -math.pi:
        angle += math.pi * 2
    return angle


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 22
        self.speed = 3.6
        self.base_speed = 3.6
        self.max_hp = 100
        self.hp = 100
        self.attack_range = 90
        self.base_attack_range = 90
        self.attack_damage = 28
        self.base_attack_damage = 28
        self.attack_angle = math.radians(100)
        self.attack_cooldown = 0
        self.attack_cooldown_max = 20
        self.attack_timer = 0
        self.attack_dir = 0
        self.facing = 0
        self.skill_cooldown = 0
        self.skill_cooldown_max = 600
        self.skill_radius = 320
        self.skill_damage = 90
        self.invincible = 0
        self.level = 1
        self.kills_for_level = 0
        self.kills_per_level = 50
        self.walk_anim = 0

    @property
    def is_attacking(self):
        return self.attack_timer > 0

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
            self.facing = math.atan2(dy, dx)
            self.walk_anim += 0.25
        self.x = max(self.radius, min(settings.SCREEN_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(settings.SCREEN_HEIGHT - self.radius, self.y))

    def attack(self, mouse_x, mouse_y):
        if self.attack_cooldown <= 0:
            self.attack_timer = 14
            self.attack_cooldown = self.attack_cooldown_max
            self.attack_dir = math.atan2(mouse_y - self.y, mouse_x - self.x)
            self.facing = self.attack_dir
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

    def check_attack_hit(self, target_x, target_y, target_radius):
        hitbox = self.get_attack_hitbox()
        if not hitbox:
            return False
        dx = target_x - hitbox['x']
        dy = target_y - hitbox['y']
        dist = math.sqrt(dx * dx + dy * dy)
        if dist <= hitbox['range'] + target_radius:
            angle_to_target = math.atan2(dy, dx)
            angle_diff = abs(_normalize_angle(angle_to_target - hitbox['direction']))
            return angle_diff <= hitbox['angle'] / 2
        return False

    def take_damage(self, damage):
        if self.invincible > 0:
            return False
        self.hp -= damage
        self.invincible = 35
        return True

    def level_up(self, choice):
        self.level += 1
        self.kills_for_level = 0
        if choice == 'range':
            self.attack_range += 22
            self.attack_damage += 6
        elif choice == 'speed':
            self.speed += 0.5
            self.base_attack_damage += 4

    def draw(self, surface, mouse_pos=None):
        blink = self.invincible > 0 and self.invincible % 5 < 2
        body_color = (255, 210, 210) if blink else (70, 150, 255)
        body_dark = (40, 90, 180)
        armor_color = (230, 230, 255)

        bob = math.sin(self.walk_anim) * 1.2 if not self.is_attacking else 0
        cx = int(self.x)
        cy = int(self.y + bob)

        shadow = pygame.Surface((self.radius * 3, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 80), (self.radius * 0.5, self.radius * 1.1, self.radius * 2, self.radius * 0.7))
        surface.blit(shadow, (cx - self.radius * 1.5, cy - self.radius))

        pygame.draw.circle(surface, body_dark, (cx, cy + 3), self.radius - 1)
        pygame.draw.circle(surface, body_color, (cx, cy), self.radius - 2)

        pygame.draw.circle(surface, armor_color, (cx, cy - 3), self.radius - 8, 2)

        if mouse_pos:
            aim_angle = math.atan2(mouse_pos[1] - self.y, mouse_pos[0] - self.x)
        else:
            aim_angle = self.facing

        eye_offset = 7
        eye_dx = math.cos(aim_angle) * eye_offset
        eye_dy = math.sin(aim_angle) * eye_offset
        pygame.draw.circle(surface, (255, 255, 255), (cx + int(eye_dx) - 3, cy + int(eye_dy) - 3), 3)
        pygame.draw.circle(surface, (255, 255, 255), (cx + int(eye_dx) + 3, cy + int(eye_dy) - 3), 3)
        pygame.draw.circle(surface, (20, 20, 40), (cx + int(eye_dx) - 3, cy + int(eye_dy) - 3), 2)
        pygame.draw.circle(surface, (20, 20, 40), (cx + int(eye_dx) + 3, cy + int(eye_dy) - 3), 2)

        if self.is_attacking:
            swing_progress = 1 - (self.attack_timer / 14)
            start_a = self.attack_dir - self.attack_angle / 2
            end_a = self.attack_dir + self.attack_angle / 2
            current_a = start_a + (end_a - start_a) * swing_progress
            self._draw_sword(surface, cx, cy, current_a, swing_progress)
        else:
            rest_angle = aim_angle - 0.6
            self._draw_sword(surface, cx, cy, rest_angle, 0.0, resting=True)

    def _draw_sword(self, surface, cx, cy, angle, swing_progress, resting=False):
        hilt_len = 10
        blade_len = 46 if not resting else 38
        blade_width = 7
        guard_w = 16

        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        hilt_x = cx + cos_a * (self.radius - 4)
        hilt_y = cy + sin_a * (self.radius - 4)

        tip_x = hilt_x + cos_a * (hilt_len + blade_len)
        tip_y = hilt_y + sin_a * (hilt_len + blade_len)

        perp_x = -sin_a
        perp_y = cos_a

        if not resting and swing_progress < 0.6:
            glow_r = int(30 * (1 - swing_progress / 0.6))
            glow = pygame.Surface((glow_r * 2 + 10, glow_r * 2 + 10), pygame.SRCALPHA)
            try:
                pygame.draw.circle(glow, (255, 240, 150, 100), (glow_r + 5, glow_r + 5), glow_r)
            except:
                pass
            surface.blit(glow, (int(tip_x - glow_r - 5), int(tip_y - glow_r - 5)))

        blade_pts = [
            (hilt_x + cos_a * hilt_len + perp_x * blade_width / 2,
             hilt_y + sin_a * hilt_len + perp_y * blade_width / 2),
            (tip_x + perp_x * 2, tip_y + perp_y * 2),
            (tip_x - perp_x * 2, tip_y - perp_y * 2),
            (hilt_x + cos_a * hilt_len - perp_x * blade_width / 2,
             hilt_y + sin_a * hilt_len - perp_y * blade_width / 2),
        ]
        try:
            pygame.draw.polygon(surface, (230, 240, 255), blade_pts)
            pygame.draw.polygon(surface, (170, 190, 220), blade_pts, 2)
        except:
            pass

        guard_x1 = hilt_x + cos_a * (hilt_len - 3) + perp_x * guard_w / 2
        guard_y1 = hilt_y + sin_a * (hilt_len - 3) + perp_y * guard_w / 2
        guard_x2 = hilt_x + cos_a * (hilt_len - 3) - perp_x * guard_w / 2
        guard_y2 = hilt_y + sin_a * (hilt_len - 3) - perp_y * guard_w / 2
        pygame.draw.line(surface, (120, 80, 40), (guard_x1, guard_y1), (guard_x2, guard_y2), 5)

        hilt_end_x = hilt_x
        hilt_end_y = hilt_y
        hilt_start_x = hilt_x + cos_a * hilt_len
        hilt_start_y = hilt_y + sin_a * hilt_len
        pygame.draw.line(surface, (90, 60, 30), (hilt_end_x, hilt_end_y), (hilt_start_x, hilt_start_y), 5)

        try:
            pygame.draw.circle(surface, (180, 140, 60), (int(hilt_end_x), int(hilt_end_y)), 4)
        except:
            pass


class Enemy:
    def __init__(self, x, y, enemy_type='normal'):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        if enemy_type == 'normal':
            self.radius = 15
            self.max_hp = 32
            self.speed = 1.7
            self.damage = 8
            self.body_color = (210, 50, 50)
            self.dark_color = (140, 20, 30)
            self.eye_color = (255, 230, 80)
            self.score = 10
        elif enemy_type == 'elite':
            self.radius = 18
            self.max_hp = 75
            self.speed = 1.5
            self.damage = 13
            self.body_color = (255, 150, 40)
            self.dark_color = (170, 90, 20)
            self.eye_color = (255, 255, 150)
            self.score = 30
        self.hp = self.max_hp
        self.hit_flash = 0
        self.attack_cooldown = 0
        self.walk_anim = 0
        self.angle_to_player = 0

    def update(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            self.angle_to_player = math.atan2(dy, dx)
            self.walk_anim += 0.2
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def take_damage(self, damage):
        self.hp -= damage
        self.hit_flash = 10
        return self.hp <= 0

    def check_player_collision(self, player):
        dx = self.x - player.x
        dy = self.y - player.y
        dist = math.sqrt(dx * dx + dy * dy)
        return dist < (self.radius + player.radius)

    def draw(self, surface):
        flash = self.hit_flash > 0 and self.hit_flash % 4 < 2
        body_c = (255, 255, 255) if flash else self.body_color
        dark_c = (200, 200, 200) if flash else self.dark_color

        bob = math.sin(self.walk_anim) * 1.0
        cx = int(self.x)
        cy = int(self.y + bob)

        shadow = pygame.Surface((self.radius * 3, self.radius * 2), pygame.SRCALPHA)
        try:
            pygame.draw.ellipse(shadow, (0, 0, 0, 70), (self.radius * 0.6, self.radius * 1.1, self.radius * 1.8, self.radius * 0.6))
        except:
            pass
        surface.blit(shadow, (cx - self.radius * 1.5, cy - self.radius))

        pygame.draw.circle(surface, dark_c, (cx, cy + 3), self.radius)
        pygame.draw.circle(surface, body_c, (cx, cy), self.radius - 1)

        if self.enemy_type == 'elite':
            pygame.draw.circle(surface, (255, 220, 120), (cx, cy), self.radius - 6, 2)
            try:
                pygame.draw.circle(surface, (255, 255, 200), (cx, cy - self.radius - 3), 3)
            except:
                pass

        eye_dx = math.cos(self.angle_to_player) * 5
        eye_dy = math.sin(self.angle_to_player) * 5 - 2
        er = 3 if self.enemy_type == 'elite' else 2
        try:
            pygame.draw.circle(surface, self.eye_color, (cx + int(eye_dx) - 3, cy + int(eye_dy)), er)
            pygame.draw.circle(surface, self.eye_color, (cx + int(eye_dx) + 3, cy + int(eye_dy)), er)
            pygame.draw.circle(surface, (30, 0, 0), (cx + int(eye_dx) - 3, cy + int(eye_dy)), er - 1)
            pygame.draw.circle(surface, (30, 0, 0), (cx + int(eye_dx) + 3, cy + int(eye_dy)), er - 1)
        except:
            pass

        if self.hp < self.max_hp:
            bw = self.radius * 2 + 6
            bh = 5
            bx = self.x - bw / 2
            by = self.y - self.radius - 12
            pygame.draw.rect(surface, settings.GRAY, (int(bx), int(by), int(bw), bh), border_radius=2)
            ratio = max(0, self.hp / self.max_hp)
            hp_c = settings.GREEN if ratio > 0.5 else settings.YELLOW if ratio > 0.25 else settings.RED
            pygame.draw.rect(surface, hp_c, (int(bx), int(by), int(bw * ratio), bh), border_radius=2)


class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 36
        self.max_hp = 550
        self.hp = 550
        self.speed = 1.3
        self.damage = 22
        self.body_color = (180, 70, 220)
        self.dark_color = (110, 30, 160)
        self.score = 200
        self.hit_flash = 0
        self.attack_cooldown = 0
        self.charge_cooldown = random.randint(200, 320)
        self.is_charging = False
        self.charge_dir_x = 0
        self.charge_dir_y = 0
        self.charge_timer = 0
        self.charge_duration = 32
        self.charge_speed = 7.5
        self.charge_windup = 0
        self.charge_windup_max = 45
        self.angle_to_player = 0
        self.walk_anim = 0

    def update(self, player_x, player_y):
        if self.charge_windup > 0:
            self.charge_windup -= 1
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                self.charge_dir_x = dx / dist
                self.charge_dir_y = dy / dist
                self.angle_to_player = math.atan2(dy, dx)
        elif self.is_charging:
            self.x += self.charge_dir_x * self.charge_speed
            self.y += self.charge_dir_y * self.charge_speed
            self.charge_timer -= 1
            if self.charge_timer <= 0:
                self.is_charging = False
                self.charge_cooldown = random.randint(260, 440)
        else:
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
                self.angle_to_player = math.atan2(dy, dx)
                self.walk_anim += 0.15
            self.charge_cooldown -= 1
            if self.charge_cooldown <= 0:
                self.charge_windup = self.charge_windup_max
                self.is_charging = True
                self.charge_timer = self.charge_duration

        self.x = max(self.radius, min(settings.SCREEN_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(settings.SCREEN_HEIGHT - self.radius, self.y))

        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def take_damage(self, damage):
        self.hp -= damage
        self.hit_flash = 10
        return self.hp <= 0

    def check_player_collision(self, player):
        dx = self.x - player.x
        dy = self.y - player.y
        dist = math.sqrt(dx * dx + dy * dy)
        return dist < (self.radius + player.radius)

    def draw(self, surface):
        if self.charge_windup > 0:
            flash = self.charge_windup % 8 < 4
            if flash:
                body_c = (255, 200, 80)
                dark_c = (200, 130, 20)
            else:
                body_c = self.body_color
                dark_c = self.dark_color
        elif self.is_charging:
            body_c = (255, 120, 120)
            dark_c = (180, 50, 50)
        elif self.hit_flash > 0 and self.hit_flash % 4 < 2:
            body_c = (255, 255, 255)
            dark_c = (210, 210, 210)
        else:
            body_c = self.body_color
            dark_c = self.dark_color

        bob = math.sin(self.walk_anim) * 1.5
        cx = int(self.x)
        cy = int(self.y + bob)

        shadow_s = pygame.Surface((self.radius * 3, self.radius * 2), pygame.SRCALPHA)
        try:
            pygame.draw.ellipse(shadow_s, (0, 0, 0, 90),
                                (self.radius * 0.5, self.radius * 1.1, self.radius * 2, self.radius * 0.7))
        except:
            pass
        surface.blit(shadow_s, (cx - self.radius * 1.5, cy - self.radius))

        if self.is_charging:
            trail_s = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            try:
                pygame.draw.circle(trail_s, (255, 100, 100, 90), (self.radius * 2, self.radius * 2), self.radius + 8)
            except:
                pass
            surface.blit(trail_s, (cx - self.radius * 2, cy - self.radius * 2))

        pygame.draw.circle(surface, dark_c, (cx, cy + 5), self.radius)
        pygame.draw.circle(surface, body_c, (cx, cy), self.radius - 2)
        pygame.draw.circle(surface, (255, 220, 255), (cx, cy), self.radius - 8, 3)

        armor_y = cy - self.radius // 3
        try:
            pygame.draw.circle(surface, (80, 30, 120), (cx, armor_y), self.radius - 12, 2)
        except:
            pass

        eye_dx = math.cos(self.angle_to_player) * 10
        eye_dy = math.sin(self.angle_to_player) * 10 - 4
        try:
            pygame.draw.circle(surface, (255, 240, 120), (cx + int(eye_dx) - 7, cy + int(eye_dy)), 5)
            pygame.draw.circle(surface, (255, 240, 120), (cx + int(eye_dx) + 7, cy + int(eye_dy)), 5)
            pygame.draw.circle(surface, (40, 0, 0), (cx + int(eye_dx) - 7, cy + int(eye_dy)), 3)
            pygame.draw.circle(surface, (40, 0, 0), (cx + int(eye_dx) + 7, cy + int(eye_dy)), 3)
        except:
            pass

        crown_y = cy - self.radius - 2
        crown_pts = [
            (cx - 22, crown_y + 8),
            (cx - 14, crown_y - 10),
            (cx - 7, crown_y + 4),
            (cx, crown_y - 14),
            (cx + 7, crown_y + 4),
            (cx + 14, crown_y - 10),
            (cx + 22, crown_y + 8),
        ]
        try:
            pygame.draw.lines(surface, settings.GOLD, False, crown_pts, 4)
            for px, py in [(cx - 14, crown_y - 10), (cx, crown_y - 14), (cx + 14, crown_y - 10)]:
                pygame.draw.circle(surface, (255, 100, 100), (int(px), int(py)), 2)
        except:
            pass

        if self.hp < self.max_hp:
            bw = self.radius * 2.8
            bh = 8
            bx = self.x - bw / 2
            by = self.y - self.radius - 26
            pygame.draw.rect(surface, (50, 50, 70), (int(bx), int(by), int(bw), bh), border_radius=3)
            ratio = max(0, self.hp / self.max_hp)
            pygame.draw.rect(surface, settings.RED, (int(bx), int(by), int(bw * ratio), bh), border_radius=3)
            pygame.draw.rect(surface, settings.WHITE, (int(bx), int(by), int(bw), bh), 1, border_radius=3)

            if self.charge_windup > 0:
                w_ratio = 1 - (self.charge_windup / self.charge_windup_max)
                pygame.draw.rect(surface, settings.YELLOW,
                                 (int(bx), int(by) + bh + 2, int(bw * w_ratio), 3), border_radius=1)
