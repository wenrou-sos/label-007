import pygame
import math
from . import settings


def draw_rounded_rect(surface, rect, color, radius=10, width=0):
    try:
        pygame.draw.rect(surface, color, rect, border_radius=radius, width=width)
    except TypeError:
        x, y, w, h = rect
        pygame.draw.rect(surface, color, (x + radius, y, w - radius * 2, h), width)
        pygame.draw.rect(surface, color, (x, y + radius, w, h - radius * 2), width)
        for cx, cy in [(x + radius, y + radius), (x + w - radius, y + radius),
                       (x + radius, y + h - radius), (x + w - radius, y + h - radius)]:
            pygame.draw.circle(surface, color, (int(cx), int(cy)), radius, width)


def draw_text_with_shadow(surface, font, text, x, y, color=settings.WHITE, shadow_color=settings.BLACK, shadow_offset=2):
    sw = font.render(text, True, shadow_color)
    surface.blit(sw, (x + shadow_offset, y + shadow_offset))
    t = font.render(text, True, color)
    surface.blit(t, (x, y))
    return t


def draw_grid(surface):
    grid_size = 60
    for x in range(0, settings.SCREEN_WIDTH, grid_size):
        pygame.draw.line(surface, settings.GRID_COLOR, (x, 0), (x, settings.SCREEN_HEIGHT))
    for y in range(0, settings.SCREEN_HEIGHT, grid_size):
        pygame.draw.line(surface, settings.GRID_COLOR, (0, y), (settings.SCREEN_WIDTH, y))


def draw_hud(surface, fonts, player, score, total_kills, combo, combo_timer, combo_timeout):
    pad = 18

    hp_w = 320
    hp_h = 32
    hp_x = pad
    hp_y = pad
    panel_h = hp_h + 95
    panel_rect = pygame.Rect(pad - 8, pad - 8, hp_w + 220, panel_h)
    draw_rounded_rect(surface, panel_rect, settings.PANEL_BG, 12)
    pygame.draw.rect(surface, settings.PANEL_BORDER, panel_rect, 2, border_radius=12)

    draw_text_with_shadow(surface, fonts["small"], "生 命", hp_x, hp_y - 2, settings.LIGHT_GRAY)
    hp_bg = pygame.Rect(hp_x, hp_y + 18, hp_w, hp_h)
    draw_rounded_rect(surface, hp_bg, (60, 15, 25), 8)
    ratio = max(0, player.hp / player.max_hp)
    hp_c = settings.GREEN if ratio > 0.5 else settings.YELLOW if ratio > 0.25 else settings.RED
    hp_fill = pygame.Rect(hp_x, hp_y + 18, int(hp_w * ratio), hp_h)
    if hp_fill.width > 0:
        draw_rounded_rect(surface, hp_fill, hp_c, 8)
        if ratio > 0.05:
            shine = pygame.Rect(hp_x + 4, hp_y + 20, max(0, int(hp_w * ratio) - 8), 4)
            if shine.width > 0:
                draw_rounded_rect(surface, shine, (255, 255, 255, 120), 3)
    pygame.draw.rect(surface, (255, 255, 255, 120), hp_bg, 2, border_radius=8)
    hp_text = fonts["medium"].render(f"{max(0, int(player.hp))} / {player.max_hp}", True, settings.WHITE)
    surface.blit(hp_text, (hp_x + hp_w // 2 - hp_text.get_width() // 2,
                           hp_y + 18 + hp_h // 2 - hp_text.get_height() // 2))

    sy = hp_y + hp_h + 30
    score_t = draw_text_with_shadow(surface, fonts["medium"], f"得 分: {score}", hp_x, sy, settings.YELLOW)
    lvl_t = draw_text_with_shadow(surface, fonts["small"],
                                  f"等级 {player.level}   击杀 {total_kills}",
                                  hp_x, sy + 34, settings.WHITE)

    xp_w = 230
    xp_h = 10
    xp_x = hp_x
    xp_y = sy + 64
    draw_text_with_shadow(surface, fonts["tiny"],
                          f"升级进度  {player.kills_for_level} / {player.kills_per_level}",
                          xp_x, xp_y - 16, settings.LIGHT_GRAY)
    xp_bg = pygame.Rect(xp_x, xp_y, xp_w, xp_h)
    draw_rounded_rect(surface, xp_bg, (30, 30, 60), 4)
    xp_ratio = min(1.0, player.kills_for_level / player.kills_per_level)
    xp_fill = pygame.Rect(xp_x, xp_y, int(xp_w * xp_ratio), xp_h)
    if xp_fill.width > 0:
        draw_rounded_rect(surface, xp_fill, settings.LIGHT_BLUE, 4)
    pygame.draw.rect(surface, (255, 255, 255, 100), xp_bg, 1, border_radius=4)

    if combo > 0:
        combo_c = settings.YELLOW
        if combo >= 10:
            combo_c = settings.ORANGE
        if combo >= 25:
            combo_c = settings.RED
        if combo >= 50:
            combo_c = (255, 80, 255)

        pulse = 1.0
        if combo >= 25:
            pulse = 1.0 + math.sin(pygame.time.get_ticks() / 80) * 0.08

        combo_x = settings.SCREEN_WIDTH - pad
        combo_y = pad

        bg_w = 280
        bg_h = 90
        bg_rect = pygame.Rect(combo_x - bg_w, combo_y - 8, bg_w, bg_h)
        draw_rounded_rect(surface, bg_rect, settings.PANEL_BG, 12)
        pygame.draw.rect(surface, combo_c, bg_rect, 2, border_radius=12)

        if combo >= 10:
            glow_s = pygame.Surface((bg_w + 20, bg_h + 20), pygame.SRCALPHA)
            try:
                pygame.draw.rect(glow_s, (*combo_c, 40), (0, 0, bg_w + 20, bg_h + 20), border_radius=14)
            except:
                pass
            surface.blit(glow_s, (bg_rect.x - 10, bg_rect.y - 10))

        combo_font = fonts["big"]
        combo_text = f"{combo} COMBO"
        if combo >= 50:
            combo_text = f"{combo} COMBO!!!"
        elif combo >= 25:
            combo_text = f"{combo} COMBO!!"
        elif combo >= 10:
            combo_text = f"{combo} COMBO!"

        scaled_w = int(combo_font.size(combo_text)[0] * pulse)
        scaled_h = int(combo_font.size(combo_text)[1] * pulse)
        surf_small = pygame.font.SysFont(settings.FONT_NAMES, int(44 * pulse), bold=True).render(
            combo_text, True, combo_c)
        outline = pygame.font.SysFont(settings.FONT_NAMES, int(44 * pulse), bold=True).render(
            combo_text, True, settings.BLACK)
        tx = combo_x - surf_small.get_width() - 15
        ty = combo_y + 2
        surface.blit(outline, (tx + 3, ty + 3))
        surface.blit(surf_small, (tx, ty))

        bonus = int(min(combo * 2, 100))
        bonus_t = fonts["small"].render(f"攻击力 +{bonus}%", True, combo_c)
        surface.blit(bonus_t, (combo_x - bonus_t.get_width() - 15, combo_y + 55))

        cd_ratio = max(0, combo_timer / combo_timeout)
        cd_w = bg_w - 30
        cd_rect = pygame.Rect(combo_x - cd_w - 15, combo_y + bg_h - 14, cd_w, 5)
        draw_rounded_rect(surface, cd_rect, (60, 60, 80), 3)
        cd_fill = pygame.Rect(combo_x - cd_w - 15, combo_y + bg_h - 14, int(cd_w * cd_ratio), 5)
        if cd_fill.width > 0:
            draw_rounded_rect(surface, cd_fill, combo_c, 3)

    sk_x = settings.SCREEN_WIDTH - 65
    sk_y = settings.SCREEN_HEIGHT - 70
    sk_r = 38
    sk_bg = pygame.Rect(sk_x - sk_r - 8, sk_y - sk_r - 8, (sk_r + 8) * 2, (sk_r + 8) * 2)
    draw_rounded_rect(surface, sk_bg, settings.PANEL_BG, 14)
    pygame.draw.rect(surface, settings.PANEL_BORDER, sk_bg, 2, border_radius=14)

    pygame.draw.circle(surface, (35, 35, 55), (sk_x, sk_y), sk_r)
    if player.skill_cooldown > 0:
        cd_ratio = player.skill_cooldown / player.skill_cooldown_max
        cd_angle = cd_ratio * math.pi * 2
        cd_s = pygame.Surface((sk_r * 2 + 4, sk_r * 2 + 4), pygame.SRCALPHA)
        cx2 = sk_r + 2
        cy2 = sk_r + 2
        pts = [(cx2, cy2)]
        steps = 60
        for i in range(steps + 1):
            t = i / steps
            a = -math.pi / 2 + cd_angle * t
            px = cx2 + math.cos(a) * (sk_r + 10)
            py = cy2 + math.sin(a) * (sk_r + 10)
            pts.append((px, py))
        if len(pts) >= 3:
            try:
                pygame.draw.polygon(cd_s, (0, 0, 0, 200), pts)
            except:
                pass
        surface.blit(cd_s, (sk_x - sk_r - 2, sk_y - sk_r - 2))
    else:
        pulse_g = 1.0 + math.sin(pygame.time.get_ticks() / 200) * 0.12
        glow_r = int((sk_r + 4) * pulse_g)
        glow_s = pygame.Surface((glow_r * 2 + 10, glow_r * 2 + 10), pygame.SRCALPHA)
        try:
            pygame.draw.circle(glow_s, (80, 160, 255, 80), (glow_r + 5, glow_r + 5), glow_r)
        except:
            pass
        surface.blit(glow_s, (sk_x - glow_r - 5, sk_y - glow_r - 5))
        pygame.draw.circle(surface, (80, 170, 255), (sk_x, sk_y), sk_r, 3)

    pygame.draw.circle(surface, settings.WHITE, (sk_x, sk_y), sk_r, 2)
    key_t = fonts["small"].render("SPACE", True, settings.WHITE)
    surface.blit(key_t, (sk_x - key_t.get_width() // 2, sk_y - 14))
    if player.skill_cooldown > 0:
        cd_t = fonts["medium"].render(f"{player.skill_cooldown // settings.FPS + 1}", True, settings.LIGHT_GRAY)
        surface.blit(cd_t, (sk_x - cd_t.get_width() // 2, sk_y + 4))
    else:
        ok_t = fonts["tiny"].render("就绪", True, (120, 220, 255))
        surface.blit(ok_t, (sk_x - ok_t.get_width() // 2, sk_y + 6))

    ctrl = [
        ("WASD", "移动"),
        ("鼠标左键", "挥砍"),
        ("空格", "全屏技能"),
        ("ESC", "暂停"),
    ]
    cw = 160
    ch = 20 * len(ctrl) + 16
    cx = settings.SCREEN_WIDTH - pad - cw
    cy = pad + 110
    c_rect = pygame.Rect(cx - 8, cy - 8, cw + 16, ch)
    draw_rounded_rect(surface, c_rect, settings.PANEL_BG, 10)
    pygame.draw.rect(surface, settings.PANEL_BORDER, c_rect, 1, border_radius=10)
    for i, (k, v) in enumerate(ctrl):
        k_t = fonts["tiny"].render(k, True, settings.YELLOW)
        v_t = fonts["tiny"].render(v, True, settings.LIGHT_GRAY)
        surface.blit(k_t, (cx, cy + i * 20))
        surface.blit(v_t, (cx + 75, cy + i * 20))


def draw_menu(surface, fonts):
    overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((15, 15, 30, 180))
    surface.blit(overlay, (0, 0))

    cx = settings.SCREEN_WIDTH // 2
    cy = settings.SCREEN_HEIGHT // 2

    for i in range(5, 0, -1):
        size = int(72 + i * 6)
        glow = pygame.font.SysFont(settings.FONT_NAMES, size, bold=True).render(
            "割 草 无 双", True, (*settings.YELLOW, 30))
        surface.blit(glow, (cx - glow.get_width() // 2, cy - 230 + i * 2))

    title_t = draw_text_with_shadow(surface, fonts["title"], "割 草 无 双",
                                    cx - fonts["title"].size("割 草 无 双")[0] // 2,
                                    cy - 230, settings.YELLOW, settings.BLACK, 3)

    sub = fonts["subtitle"].render("一骑当千，横扫千军！", True, settings.WHITE)
    surface.blit(sub, (cx - sub.get_width() // 2, cy - 145))

    sections = [
        ("【操作说明】", [
            "WASD / 方向键   移动角色",
            "鼠标左键          朝鼠标方向挥砍",
            "空格键             释放全屏技能",
            "ESC 键              暂停 / 继续",
        ]),
        ("【玩法说明】", [
            "击杀小兵 +10 分，精英 +30 分，武将 +200 分",
            "每击杀 50 个敌人升级，选择一项强化",
            "连杀越高攻击力加成越多，被击中则重置",
            "血量归零游戏结束",
        ]),
    ]

    sy = cy - 70
    for title, lines in sections:
        t_t = fonts["medium"].render(title, True, settings.GOLD)
        surface.blit(t_t, (cx - 280, sy))
        sy += 34
        for line in lines:
            l_t = fonts["normal"].render(line, True, (210, 210, 225))
            surface.blit(l_t, (cx - 250, sy))
            sy += 26
        sy += 18

    pulse = 1.0 + math.sin(pygame.time.get_ticks() / 350) * 0.1
    start_font = pygame.font.SysFont(settings.FONT_NAMES, int(30 * pulse), bold=True)
    start_t = start_font.render("按 回车键 开始游戏", True, settings.GREEN)
    outline = start_font.render("按 回车键 开始游戏", True, settings.BLACK)
    surface.blit(outline, (cx - start_t.get_width() // 2 + 2, settings.SCREEN_HEIGHT - 130 + 2))
    surface.blit(start_t, (cx - start_t.get_width() // 2, settings.SCREEN_HEIGHT - 130))


def draw_upgrade_screen(surface, fonts, player, options):
    overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    cx = settings.SCREEN_WIDTH // 2

    title = fonts["big"].render(f"升 级！  Lv.{player.level}  →  Lv.{player.level + 1}", True, settings.YELLOW)
    outline = fonts["big"].render(f"升 级！  Lv.{player.level}  →  Lv.{player.level + 1}", True, settings.BLACK)
    surface.blit(outline, (cx - title.get_width() // 2 + 3, 90 + 3))
    surface.blit(title, (cx - title.get_width() // 2, 90))

    tip = fonts["subtitle"].render("选择一项强化（按 1 或 2）", True, settings.WHITE)
    surface.blit(tip, (cx - tip.get_width() // 2, 170))

    card_w = 360
    card_h = 300
    spacing = 80
    total_w = card_w * 2 + spacing
    sx = (settings.SCREEN_WIDTH - total_w) // 2
    card_y = 240

    icons = ["⚔", "👟"]
    for i, (opt, icon) in enumerate(zip(options, icons)):
        cx_c = sx + i * (card_w + spacing)
        c_rect = pygame.Rect(cx_c, card_y, card_w, card_h)
        border_c = settings.YELLOW if i == 0 else (100, 200, 255)
        bg_c = (35, 35, 55)

        glow_s = pygame.Surface((card_w + 20, card_h + 20), pygame.SRCALPHA)
        try:
            draw_rounded_rect(glow_s, (*border_c, 50), pygame.Rect(0, 0, card_w + 20, card_h + 20), 18)
        except:
            pass
        surface.blit(glow_s, (cx_c - 10, card_y - 10))

        draw_rounded_rect(surface, c_rect, bg_c, 16)
        pygame.draw.rect(surface, border_c, c_rect, 4, border_radius=16)

        num_surf = fonts["title"].render(str(i + 1), True, border_c)
        surface.blit(num_surf, (cx_c + 22, card_y + 18))

        icon_surf = pygame.font.SysFont("segoeuisymbol, arial", 72).render(icon, True, border_c)
        surface.blit(icon_surf, (cx_c + card_w // 2 - icon_surf.get_width() // 2, card_y + 55))

        name = fonts["medium"].render(opt['name'], True, settings.WHITE)
        surface.blit(name, (cx_c + card_w // 2 - name.get_width() // 2, card_y + 165))

        desc = fonts["normal"].render(opt['desc'], True, settings.LIGHT_GRAY)
        surface.blit(desc, (cx_c + card_w // 2 - desc.get_width() // 2, card_y + 215))


def draw_game_over(surface, fonts, score, total_kills, max_combo, level, game_time):
    overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))

    cx = settings.SCREEN_WIDTH // 2

    for i in range(5, 0, -1):
        size = int(72 + i * 5)
        g = pygame.font.SysFont(settings.FONT_NAMES, size, bold=True).render(
            "战 败", True, (*settings.RED, 25))
        surface.blit(g, (cx - g.get_width() // 2, 80 + i * 2))

    title = draw_text_with_shadow(surface, fonts["title"], "战 败",
                                  cx - fonts["title"].size("战 败")[0] // 2, 80,
                                  settings.RED, settings.BLACK, 3)

    panel_w = 520
    panel_h = 360
    panel_rect = pygame.Rect(cx - panel_w // 2, 220, panel_w, panel_h)
    draw_rounded_rect(surface, panel_rect, settings.PANEL_BG, 16)
    pygame.draw.rect(surface, settings.RED, panel_rect, 3, border_radius=16)

    stats = [
        ("最终得分", f"{score}", settings.YELLOW),
        ("击杀数", f"{total_kills}", settings.WHITE),
        ("最高连杀", f"{max_combo}", settings.ORANGE),
        ("最终等级", f"{level}", (120, 200, 255)),
        ("存活时间", f"{game_time // settings.FPS} 秒", settings.LIGHT_GRAY),
    ]
    sy = 260
    for label, value, color in stats:
        lt = fonts["subtitle"].render(label, True, settings.LIGHT_GRAY)
        vt = fonts["big"].render(value, True, color)
        surface.blit(lt, (cx - panel_w // 2 + 40, sy))
        surface.blit(vt, (cx + panel_w // 2 - vt.get_width() - 40, sy - 8))
        sy += 62

    pulse = 1.0 + math.sin(pygame.time.get_ticks() / 350) * 0.1
    rest_font = pygame.font.SysFont(settings.FONT_NAMES, int(28 * pulse), bold=True)
    rest_t = rest_font.render("按 回车键 重新开始", True, settings.GREEN)
    outline = rest_font.render("按 回车键 重新开始", True, settings.BLACK)
    surface.blit(outline, (cx - rest_t.get_width() // 2 + 2, settings.SCREEN_HEIGHT - 100 + 2))
    surface.blit(rest_t, (cx - rest_t.get_width() // 2, settings.SCREEN_HEIGHT - 100))


def draw_pause_screen(surface, fonts):
    overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))

    cx = settings.SCREEN_WIDTH // 2
    cy = settings.SCREEN_HEIGHT // 2

    for i in range(6, 0, -1):
        size = int(80 + i * 6)
        glow = pygame.font.SysFont(settings.FONT_NAMES, size, bold=True).render(
            "已 暂 停", True, (*settings.WHITE, 18))
        surface.blit(glow, (cx - glow.get_width() // 2, cy - 90 + i * 2))

    title = draw_text_with_shadow(surface, fonts["title"], "已 暂 停",
                                  cx - fonts["title"].size("已 暂 停")[0] // 2,
                                  cy - 90, settings.WHITE, settings.BLACK, 3)

    panel_w = 460
    panel_h = 140
    panel_rect = pygame.Rect(cx - panel_w // 2, cy + 40, panel_w, panel_h)
    draw_rounded_rect(surface, panel_rect, settings.PANEL_BG, 14)
    pygame.draw.rect(surface, settings.PANEL_BORDER, panel_rect, 2, border_radius=14)

    pulse = 1.0 + math.sin(pygame.time.get_ticks() / 350) * 0.08
    f_sz = int(26 * pulse)
    info_font = pygame.font.SysFont(settings.FONT_NAMES, f_sz, bold=True)
    info_t = info_font.render("按 ESC 或 回车键 继续游戏", True, settings.LIGHT_BLUE)
    surface.blit(info_t, (cx - info_t.get_width() // 2, cy + 95))
