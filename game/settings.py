import pygame
from enum import Enum

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
DARK_RED = (140, 20, 30)
GREEN = (60, 220, 90)
DARK_GREEN = (25, 110, 40)
BLUE = (60, 140, 255)
LIGHT_BLUE = (120, 190, 255)
DARK_BLUE = (25, 70, 170)
YELLOW = (255, 225, 60)
GOLD = (255, 190, 30)
ORANGE = (255, 140, 30)
PURPLE = (180, 80, 220)
DARK_PURPLE = (120, 40, 170)
GRAY = (90, 90, 100)
LIGHT_GRAY = (190, 190, 200)
BG_COLOR = (25, 25, 38)
GRID_COLOR = (38, 38, 52)
PANEL_BG = (20, 20, 32, 210)
PANEL_BORDER = (80, 80, 120)


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    UPGRADE = 4
    GAME_OVER = 5


FONT_NAMES = ["microsoftyahei", "simhei", "arial"]


def load_fonts():
    result = {}
    result["title"] = pygame.font.SysFont(FONT_NAMES, 72, bold=True)
    result["big"] = pygame.font.SysFont(FONT_NAMES, 44, bold=True)
    result["subtitle"] = pygame.font.SysFont(FONT_NAMES, 32, bold=True)
    result["medium"] = pygame.font.SysFont(FONT_NAMES, 26, bold=True)
    result["normal"] = pygame.font.SysFont(FONT_NAMES, 22)
    result["small"] = pygame.font.SysFont(FONT_NAMES, 18)
    result["tiny"] = pygame.font.SysFont(FONT_NAMES, 14)
    return result
