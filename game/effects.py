import pygame
import math
import random
from . import settings


class Particle:
    def __init__(self, x, y, color, size, speed_x, speed_y, life, gravity=0.0):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.life = life
        self.max_life = life
        self.gravity = gravity

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        self.speed_x *= 0.93
        self.speed_y *= 0.93
        self.life -= 1

    def draw(self, surface):
        ratio = self.life / self.max_life
        alpha = int(255 * ratio)
        current_size = max(1, int(self.size * (0.5 + 0.5 * ratio)))
        s = pygame.Surface((current_size * 2 + 2, current_size * 2 + 2), pygame.SRCALPHA)
        try:
            pygame.draw.circle(s, (*self.color, alpha), (current_size + 1, current_size + 1), current_size)
        except:
            pygame.draw.circle(s, self.color + (alpha,), (current_size + 1, current_size + 1), current_size)
        surface.blit(s, (int(self.x - current_size - 1), int(self.y - current_size - 1)))


class DamageNumber:
    def __init__(self, x, y, value, color=settings.YELLOW, is_crit=False):
        self.x = x
        self.y = y
        self.value = value
        self.color = color
        self.is_crit = is_crit
        self.life = 45
        self.max_life = 45
        self.vy = -1.8

    def update(self):
        self.y += self.vy
        self.vy *= 0.95
        self.life -= 1

    def draw(self, surface, fonts):
        ratio = self.life / self.max_life
        alpha = int(255 * ratio)
        font = fonts["medium"] if self.is_crit else fonts["small"]
        text = font.render(str(self.value), True, self.color)
        if self.is_crit:
            outline = font.render(str(self.value), True, settings.BLACK)
            text_surf = pygame.Surface(text.get_size(), pygame.SRCALPHA)
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                s = outline.copy()
                s.set_alpha(alpha)
                text_surf.blit(s, (dx, dy))
            t = text.copy()
            t.set_alpha(alpha)
            text_surf.blit(t, (0, 0))
            surface.blit(text_surf, (int(self.x - text.get_width() / 2), int(self.y)))
        else:
            text_surf = pygame.Surface(text.get_size(), pygame.SRCALPHA)
            text_surf.blit(text, (0, 0))
            text_surf.set_alpha(alpha)
            surface.blit(text_surf, (int(self.x - text.get_width() / 2), int(self.y)))


class SkillEffect:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.max_radius = radius
        self.life = 40
        self.max_life = 40

    def update(self):
        self.life -= 1

    def draw(self, surface):
        progress = 1 - (self.life / self.max_life)
        current_radius = int(self.max_radius * (0.2 + 0.8 * progress))
        alpha = int(220 * (1 - progress))
        if alpha < 0:
            alpha = 0
        s = pygame.Surface((current_radius * 2 + 10, current_radius * 2 + 10), pygame.SRCALPHA)
        cx = current_radius + 5
        cy = current_radius + 5
        try:
            pygame.draw.circle(s, (100, 180, 255, int(alpha * 0.25)), (cx, cy), current_radius)
            pygame.draw.circle(s, (150, 210, 255, alpha), (cx, cy), current_radius, max(2, current_radius // 12))
            inner_r = max(1, current_radius - 20)
            pygame.draw.circle(s, (200, 230, 255, int(alpha * 0.6)), (cx, cy), inner_r, max(1, inner_r // 18))
        except:
            pass
        surface.blit(s, (int(self.x - current_radius - 5), int(self.y - current_radius - 5)))


class SlashEffect:
    def __init__(self, x, y, direction, attack_range, arc_angle=math.radians(90)):
        self.x = x
        self.y = y
        self.direction = direction
        self.attack_range = attack_range
        self.arc_angle = arc_angle
        self.life = 14
        self.max_life = 14

    def update(self):
        self.life -= 1

    def draw(self, surface):
        progress = 1 - (self.life / self.max_life)
        start_angle = self.direction - self.arc_angle / 2
        end_angle = self.direction + self.arc_angle / 2
        sweep = (end_angle - start_angle) * progress
        current_end = start_angle + sweep
        r = self.attack_range
        alpha = int(240 * (1 - progress))
        edge_alpha = int(255 * max(0, 1 - progress * 1.5))

        s = pygame.Surface((r * 2 + 20, r * 2 + 20), pygame.SRCALPHA)
        cx = r + 10
        cy = r + 10

        fill_pts = [(cx, cy)]
        steps = 28
        for i in range(steps + 1):
            t = i / steps
            a = start_angle + sweep * t
            px = cx + math.cos(a) * r
            py = cy + math.sin(a) * r
            fill_pts.append((px, py))

        if len(fill_pts) >= 3:
            try:
                pygame.draw.polygon(s, (255, 255, 200, int(alpha * 0.35)), fill_pts)
            except:
                pass

        for ring_idx, (ring_r, ring_a) in enumerate([(r, 255), (r - 12, 150)]):
            pts = []
            for i in range(steps + 1):
                t = i / steps
                a = start_angle + sweep * t
                px = cx + math.cos(a) * ring_r
                py = cy + math.sin(a) * ring_r
                pts.append((px, py))
            if len(pts) >= 2:
                w = 6 - ring_idx * 2
                try:
                    pygame.draw.lines(s, (255, 245, 150, int(edge_alpha * (ring_a / 255))), False, pts, w)
                except:
                    pass

        surface.blit(s, (int(self.x - r - 10), int(self.y - r - 10)))


def spawn_burst_particles(particles_list, x, y, color, count=10, speed_range=(1, 6), size_range=(2, 7)):
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(*speed_range)
        size = random.randint(*size_range)
        life = random.randint(18, 40)
        particles_list.append(Particle(
            x, y, color, size,
            math.cos(angle) * speed,
            math.sin(angle) * speed,
            life
        ))


def spawn_hit_sparks(particles_list, x, y, direction):
    for _ in range(6):
        offset = random.uniform(-0.6, 0.6)
        a = direction + offset
        speed = random.uniform(2, 7)
        size = random.randint(2, 5)
        particles_list.append(Particle(
            x, y, (255, 240, 160), size,
            math.cos(a) * speed,
            math.sin(a) * speed,
            random.randint(10, 22)
        ))
