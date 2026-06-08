import pygame
import random
from . import settings
from .settings import GameState
from .entities import Player, Enemy, Boss
from .effects import (Particle, DamageNumber, SkillEffect, SlashEffect,
                      spawn_burst_particles, spawn_hit_sparks)
from . import ui as ui_module


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption("割草无双")
        self.clock = pygame.time.Clock()
        self.fonts = settings.load_fonts()

        self.state = GameState.MENU
        self.player = None
        self.enemies = []
        self.bosses = []
        self.particles = []
        self.skill_effects = []
        self.slash_effects = []
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
        self.boss_interval = 30 * settings.FPS
        self.game_time = 0

        self.upgrade_options = []
        self.running = True

    def reset(self):
        self.player = Player(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2)
        self.enemies = []
        self.bosses = []
        self.particles = []
        self.skill_effects = []
        self.slash_effects = []
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
        margin = 40
        if side == 0:
            x = random.randint(margin, settings.SCREEN_WIDTH - margin)
            y = -margin
        elif side == 1:
            x = settings.SCREEN_WIDTH + margin
            y = random.randint(margin, settings.SCREEN_HEIGHT - margin)
        elif side == 2:
            x = random.randint(margin, settings.SCREEN_WIDTH - margin)
            y = settings.SCREEN_HEIGHT + margin
        else:
            x = -margin
            y = random.randint(margin, settings.SCREEN_HEIGHT - margin)

        enemy_type = 'elite' if random.random() < 0.13 else 'normal'
        self.enemies.append(Enemy(x, y, enemy_type))

    def spawn_boss(self):
        side = random.randint(0, 3)
        margin = 60
        if side == 0:
            x = random.randint(margin, settings.SCREEN_WIDTH - margin)
            y = -margin
        elif side == 1:
            x = settings.SCREEN_WIDTH + margin
            y = random.randint(margin, settings.SCREEN_HEIGHT - margin)
        elif side == 2:
            x = random.randint(margin, settings.SCREEN_WIDTH - margin)
            y = settings.SCREEN_HEIGHT + margin
        else:
            x = -margin
            y = random.randint(margin, settings.SCREEN_HEIGHT - margin)
        self.bosses.append(Boss(x, y))

    def check_attack_hits(self):
        if not self.player.is_attacking:
            return
        all_targets = self.enemies + self.bosses
        for target in all_targets[:]:
            if self.player.check_attack_hit(target.x, target.y, target.radius):
                combo_bonus = 1 + min(self.combo * 0.02, 1.0)
                damage = int(self.player.attack_damage * combo_bonus)
                is_crit = self.combo >= 20 and random.random() < 0.3
                if is_crit:
                    damage = int(damage * 1.8)
                if isinstance(target, Boss):
                    if target.take_damage(damage):
                        self._on_boss_killed(target)
                else:
                    if target.take_damage(damage):
                        self._on_enemy_killed(target)
                self.damage_numbers.append(DamageNumber(
                    target.x, target.y - target.radius, damage,
                    settings.RED if is_crit else settings.YELLOW, is_crit))
                spawn_hit_sparks(self.particles, target.x, target.y, self.player.attack_dir)

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
        spawn_burst_particles(self.particles, enemy.x, enemy.y, enemy.body_color, 18, (1.5, 7), (2, 8))

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
        spawn_burst_particles(self.particles, boss.x, boss.y, settings.PURPLE, 50, (2, 9), (3, 10))
        spawn_burst_particles(self.particles, boss.x, boss.y, settings.GOLD, 20, (1, 6), (2, 6))

    def _trigger_upgrade(self):
        self.state = GameState.UPGRADE
        self.upgrade_options = [
            {'key': 'range', 'name': '扩大攻击范围', 'desc': '攻击范围 +22，伤害 +6'},
            {'key': 'speed', 'name': '提升移动速度', 'desc': '移动速度 +0.5，伤害 +4'}
        ]

    def use_player_skill(self):
        if not self.player.use_skill():
            return

        self.skill_effects.append(SkillEffect(self.player.x, self.player.y, self.player.skill_radius))
        spawn_burst_particles(self.particles, self.player.x, self.player.y,
                              (150, 210, 255), 60, (3, 10), (4, 10))

        all_targets = self.enemies + self.bosses
        for target in all_targets[:]:
            dx = target.x - self.player.x
            dy = target.y - self.player.y
            dist_sq = dx * dx + dy * dy
            r_sum = self.player.skill_radius + target.radius
            if dist_sq <= r_sum * r_sum:
                damage = self.player.skill_damage
                if isinstance(target, Boss):
                    if target.take_damage(damage):
                        self._on_boss_killed(target)
                else:
                    if target.take_damage(damage):
                        self._on_enemy_killed(target)
                self.damage_numbers.append(DamageNumber(
                    target.x, target.y - target.radius, damage, (150, 220, 255), True
                ))
                spawn_burst_particles(self.particles, target.x, target.y, (150, 200, 255), 12)

    def check_enemy_attacks(self):
        all_enemies = self.enemies + self.bosses
        for enemy in all_enemies:
            if enemy.check_player_collision(self.player) and enemy.attack_cooldown <= 0:
                if self.player.take_damage(enemy.damage):
                    self.combo = 0
                    spawn_burst_particles(self.particles, self.player.x, self.player.y,
                                          settings.RED, 14, (2, 6), (2, 6))
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

        if self.player.is_attacking and self.player.attack_timer == 13:
            self.slash_effects.append(SlashEffect(
                self.player.x, self.player.y,
                self.player.attack_dir, self.player.attack_range, self.player.attack_angle
            ))

        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo = 0

        self.spawn_timer += 1
        current_interval = max(6, self.spawn_interval - self.game_time // 550)
        if self.spawn_timer >= current_interval:
            self.spawn_timer = 0
            batch = min(1 + self.game_time // 1100, 6)
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
        for s in self.slash_effects[:]:
            s.update()
            if s.life <= 0:
                self.slash_effects.remove(s)
        for d in self.damage_numbers[:]:
            d.update()
            if d.life <= 0:
                self.damage_numbers.remove(d)

    def draw(self):
        self.screen.fill(settings.BG_COLOR)
        ui_module.draw_grid(self.screen)

        if self.state == GameState.MENU:
            ui_module.draw_menu(self.screen, self.fonts)
            pygame.display.flip()
            return

        for p in self.particles:
            p.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)
        for boss in self.bosses:
            boss.draw(self.screen)

        mouse_pos = pygame.mouse.get_pos()
        self.player.draw(self.screen, mouse_pos)

        for s in self.slash_effects:
            s.draw(self.screen)
        for e in self.skill_effects:
            e.draw(self.screen)
        for d in self.damage_numbers:
            d.draw(self.screen, self.fonts)

        ui_module.draw_hud(self.screen, self.fonts, self.player, self.score,
                           self.total_kills, self.combo, self.combo_timer, self.combo_timeout)

        if self.state == GameState.UPGRADE:
            ui_module.draw_upgrade_screen(self.screen, self.fonts, self.player, self.upgrade_options)
        elif self.state == GameState.PAUSED:
            ui_module.draw_pause_screen(self.screen, self.fonts)
        elif self.state == GameState.GAME_OVER:
            ui_module.draw_game_over(self.screen, self.fonts, self.score,
                                      self.total_kills, self.max_combo,
                                      self.player.level, self.game_time)

        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == GameState.PLAYING:
                    self.state = GameState.PAUSED
                elif self.state == GameState.PAUSED:
                    self.state = GameState.PLAYING
            elif self.state == GameState.MENU:
                if event.key == pygame.K_RETURN:
                    self.reset()
                    self.state = GameState.PLAYING
            elif self.state == GameState.PAUSED:
                if event.key == pygame.K_RETURN:
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
            self.clock.tick(settings.FPS)
        pygame.quit()
