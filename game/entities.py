from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import pygame

from .utils import ASSETS_DIR


@dataclass
class Platform:
    rect: pygame.Rect
    kind: str = 'normal'


@dataclass
class Coin:
    rect: pygame.Rect
    collected: bool = False


@dataclass
class Gem:
    rect: pygame.Rect
    collected: bool = False


@dataclass
class Checkpoint:
    rect: pygame.Rect
    active: bool = False


@dataclass
class Spring:
    rect: pygame.Rect
    bounced: bool = False


@dataclass
class Spike:
    rect: pygame.Rect


@dataclass
class Lava:
    rect: pygame.Rect


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    color: Tuple[int, int, int]


@dataclass
class PowerUp:
    rect: pygame.Rect
    kind: str
    collected: bool = False


@dataclass
class Player:
    x: float
    y: float
    width: int = 32
    height: int = 54
    vx: float = 0.0
    vy: float = 0.0
    on_ground: bool = False
    facing: int = 1
    double_jump_used: bool = False
    wall_jump_cooldown: float = 0.0
    slide_time: float = 0.0
    invincible_time: float = 0.0
    lives: int = 3
    coins: int = 0
    gems: int = 0
    shield: bool = False
    shield_time: float = 0.0
    speed_boost: bool = False
    speed_boost_time: float = 0.0
    jumped: bool = False
    last_checkpoint: Optional[Tuple[float, float]] = None

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)


@dataclass
class LevelData:
    name: str
    width: int
    height: int
    platforms: List[Platform] = field(default_factory=list)
    moving_platforms: List[Platform] = field(default_factory=list)
    falling_platforms: List[Platform] = field(default_factory=list)
    spikes: List[Spike] = field(default_factory=list)
    lava: List[Lava] = field(default_factory=list)
    springs: List[Spring] = field(default_factory=list)
    coins: List[Coin] = field(default_factory=list)
    gems: List[Gem] = field(default_factory=list)
    checkpoints: List[Checkpoint] = field(default_factory=list)
    finish_rect: pygame.Rect = field(default_factory=pygame.Rect)


class LevelBuilder:
    def __init__(self, level_id: int) -> None:
        self.level_id = level_id

    def build(self) -> LevelData:
        if self.level_id == 1:
            return self._build_level_1()
        if self.level_id == 2:
            return self._build_level_2()
        return self._build_level_3()

    def _build_level_1(self) -> LevelData:
        level = LevelData(name='Neon Meadow', width=2600, height=1200)
        level.platforms = [
            Platform(pygame.Rect(0, 980, 2600, 40)),
            Platform(pygame.Rect(220, 850, 180, 24)),
            Platform(pygame.Rect(530, 750, 160, 24)),
            Platform(pygame.Rect(760, 620, 180, 24)),
            Platform(pygame.Rect(1080, 500, 180, 24)),
            Platform(pygame.Rect(1420, 620, 180, 24)),
            Platform(pygame.Rect(1720, 760, 180, 24)),
            Platform(pygame.Rect(2040, 900, 180, 24)),
            Platform(pygame.Rect(2320, 980, 220, 24)),
        ]
        level.moving_platforms = [Platform(pygame.Rect(1180, 650, 120, 24), kind='moving')]
        level.falling_platforms = [Platform(pygame.Rect(1500, 840, 120, 24), kind='falling')]
        level.spikes = [Spike(pygame.Rect(1660, 956, 40, 24))]
        level.lava = [Lava(pygame.Rect(2440, 1004, 220, 24))]
        level.springs = [Spring(pygame.Rect(720, 596, 32, 24))]
        level.coins = [Coin(pygame.Rect(260, 820, 16, 16)), Coin(pygame.Rect(580, 710, 16, 16)), Coin(pygame.Rect(800, 580, 16, 16)), Coin(pygame.Rect(1100, 460, 16, 16)), Coin(pygame.Rect(1440, 580, 16, 16)), Coin(pygame.Rect(1740, 720, 16, 16)), Coin(pygame.Rect(2060, 860, 16, 16))]
        level.gems = [Gem(pygame.Rect(1180, 620, 16, 16))]
        level.checkpoints = [Checkpoint(pygame.Rect(1000, 460, 32, 64), active=True)]
        level.finish_rect = pygame.Rect(2400, 900, 32, 84)
        return level

    def _build_level_2(self) -> LevelData:
        level = LevelData(name='Skyline Rush', width=3200, height=1400)
        level.platforms = [
            Platform(pygame.Rect(0, 1120, 3200, 40)),
            Platform(pygame.Rect(160, 950, 160, 24)),
            Platform(pygame.Rect(400, 830, 140, 24)),
            Platform(pygame.Rect(680, 740, 140, 24)),
            Platform(pygame.Rect(940, 620, 170, 24)),
            Platform(pygame.Rect(1280, 520, 150, 24)),
            Platform(pygame.Rect(1600, 700, 180, 24)),
            Platform(pygame.Rect(2000, 860, 150, 24)),
            Platform(pygame.Rect(2320, 760, 160, 24)),
            Platform(pygame.Rect(2680, 980, 180, 24)),
        ]
        level.moving_platforms = [Platform(pygame.Rect(900, 780, 120, 24), kind='moving'), Platform(pygame.Rect(2180, 940, 120, 24), kind='moving')]
        level.falling_platforms = [Platform(pygame.Rect(1460, 900, 100, 24), kind='falling'), Platform(pygame.Rect(2500, 860, 100, 24), kind='falling')]
        level.spikes = [Spike(pygame.Rect(1180, 1096, 40, 24)), Spike(pygame.Rect(2860, 956, 40, 24))]
        level.lava = [Lava(pygame.Rect(3000, 1144, 200, 24))]
        level.springs = [Spring(pygame.Rect(1080, 596, 32, 24)), Spring(pygame.Rect(2500, 836, 32, 24))]
        level.coins = [Coin(pygame.Rect(220, 910, 16, 16)), Coin(pygame.Rect(450, 790, 16, 16)), Coin(pygame.Rect(720, 700, 16, 16)), Coin(pygame.Rect(990, 580, 16, 16)), Coin(pygame.Rect(1320, 480, 16, 16)), Coin(pygame.Rect(1620, 660, 16, 16)), Coin(pygame.Rect(2020, 820, 16, 16)), Coin(pygame.Rect(2360, 720, 16, 16)), Coin(pygame.Rect(2710, 940, 16, 16))]
        level.gems = [Gem(pygame.Rect(1100, 740, 16, 16)), Gem(pygame.Rect(2580, 820, 16, 16))]
        level.checkpoints = [Checkpoint(pygame.Rect(1200, 460, 32, 64), active=True)]
        level.finish_rect = pygame.Rect(3000, 900, 32, 84)
        return level

    def _build_level_3(self) -> LevelData:
        level = LevelData(name='Chrome Canyon', width=3800, height=1500)
        level.platforms = [
            Platform(pygame.Rect(0, 1200, 3800, 40)),
            Platform(pygame.Rect(140, 1020, 180, 24)),
            Platform(pygame.Rect(430, 900, 160, 24)),
            Platform(pygame.Rect(760, 800, 160, 24)),
            Platform(pygame.Rect(1120, 680, 180, 24)),
            Platform(pygame.Rect(1500, 560, 180, 24)),
            Platform(pygame.Rect(1940, 700, 180, 24)),
            Platform(pygame.Rect(2280, 820, 180, 24)),
            Platform(pygame.Rect(2700, 940, 160, 24)),
            Platform(pygame.Rect(3080, 760, 180, 24)),
            Platform(pygame.Rect(3440, 620, 180, 24)),
        ]
        level.moving_platforms = [Platform(pygame.Rect(1040, 860, 120, 24), kind='moving'), Platform(pygame.Rect(2420, 940, 120, 24), kind='moving'), Platform(pygame.Rect(3220, 900, 120, 24), kind='moving')]
        level.falling_platforms = [Platform(pygame.Rect(1740, 860, 120, 24), kind='falling'), Platform(pygame.Rect(2900, 840, 120, 24), kind='falling')]
        level.spikes = [Spike(pygame.Rect(920, 1176, 40, 24)), Spike(pygame.Rect(1860, 1176, 40, 24)), Spike(pygame.Rect(3480, 1176, 40, 24))]
        level.lava = [Lava(pygame.Rect(3600, 1224, 200, 24))]
        level.springs = [Spring(pygame.Rect(940, 776, 32, 24)), Spring(pygame.Rect(2180, 676, 32, 24)), Spring(pygame.Rect(3340, 596, 32, 24))]
        level.coins = [Coin(pygame.Rect(180, 980, 16, 16)), Coin(pygame.Rect(480, 860, 16, 16)), Coin(pygame.Rect(800, 760, 16, 16)), Coin(pygame.Rect(1160, 640, 16, 16)), Coin(pygame.Rect(1540, 520, 16, 16)), Coin(pygame.Rect(1980, 660, 16, 16)), Coin(pygame.Rect(2320, 780, 16, 16)), Coin(pygame.Rect(2740, 900, 16, 16)), Coin(pygame.Rect(3120, 720, 16, 16)), Coin(pygame.Rect(3480, 580, 16, 16))]
        level.gems = [Gem(pygame.Rect(1060, 820, 16, 16)), Gem(pygame.Rect(2820, 900, 16, 16)), Gem(pygame.Rect(3520, 580, 16, 16))]
        level.checkpoints = [Checkpoint(pygame.Rect(1300, 520, 32, 64), active=True)]
        level.finish_rect = pygame.Rect(3600, 520, 32, 84)
        return level
