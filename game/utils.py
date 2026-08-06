from __future__ import annotations

import math
import os
import wave
from pathlib import Path
from typing import Tuple

import pygame

ASSETS_DIR = Path(__file__).resolve().parent.parent / 'assets'


def ensure_assets() -> None:
    ASSETS_DIR.mkdir(exist_ok=True)
    if not (ASSETS_DIR / 'player.png').exists():
        _write_player_image()
    if not (ASSETS_DIR / 'platform.png').exists():
        _write_platform_image()
    if not (ASSETS_DIR / 'coin.png').exists():
        _write_coin_image()
    if not (ASSETS_DIR / 'gem.png').exists():
        _write_gem_image()
    if not (ASSETS_DIR / 'flag.png').exists():
        _write_flag_image()
    if not (ASSETS_DIR / 'checkpoint.png').exists():
        _write_checkpoint_image()
    if not (ASSETS_DIR / 'spring.png').exists():
        _write_spring_image()
    if not (ASSETS_DIR / 'spikes.png').exists():
        _write_spikes_image()
    if not (ASSETS_DIR / 'lava.png').exists():
        _write_lava_image()
    if not (ASSETS_DIR / 'music.wav').exists():
        _write_music_wave()
    if not (ASSETS_DIR / 'jump.wav').exists():
        _write_jump_wave()
    if not (ASSETS_DIR / 'coin.wav').exists():
        _write_coin_wave()
    if not (ASSETS_DIR / 'checkpoint.wav').exists():
        _write_checkpoint_wave()
    if not (ASSETS_DIR / 'death.wav').exists():
        _write_death_wave()


def _write_player_image() -> None:
    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.rect(surf, (60, 180, 255), (14, 12, 36, 40), border_radius=10)
    pygame.draw.rect(surf, (255, 255, 255), (22, 20, 20, 14), border_radius=5)
    pygame.draw.rect(surf, (255, 255, 255), (20, 42, 24, 8), border_radius=4)
    pygame.image.save(surf, ASSETS_DIR / 'player.png')


def _write_platform_image() -> None:
    surf = pygame.Surface((64, 32), pygame.SRCALPHA)
    pygame.draw.rect(surf, (90, 200, 120), (0, 0, 64, 32), border_radius=6)
    pygame.draw.rect(surf, (255, 255, 255), (4, 4, 56, 8), border_radius=4)
    pygame.image.save(surf, ASSETS_DIR / 'platform.png')


def _write_coin_image() -> None:
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 220, 80), (16, 16), 12)
    pygame.draw.circle(surf, (255, 240, 160), (16, 16), 7)
    pygame.image.save(surf, ASSETS_DIR / 'coin.png')


def _write_gem_image() -> None:
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (255, 90, 200), [(16, 4), (28, 14), (22, 28), (10, 28), (4, 14)])
    pygame.image.save(surf, ASSETS_DIR / 'gem.png')


def _write_flag_image() -> None:
    surf = pygame.Surface((32, 64), pygame.SRCALPHA)
    pygame.draw.rect(surf, (255, 90, 90), (8, 4, 8, 56))
    pygame.draw.polygon(surf, (255, 220, 80), [(16, 4), (28, 16), (16, 28)])
    pygame.image.save(surf, ASSETS_DIR / 'flag.png')


def _write_checkpoint_image() -> None:
    surf = pygame.Surface((32, 64), pygame.SRCALPHA)
    pygame.draw.rect(surf, (80, 220, 120), (10, 8, 12, 48))
    pygame.draw.rect(surf, (255, 220, 80), (4, 4, 24, 8), border_radius=4)
    pygame.image.save(surf, ASSETS_DIR / 'checkpoint.png')


def _write_spring_image() -> None:
    surf = pygame.Surface((32, 24), pygame.SRCALPHA)
    pygame.draw.rect(surf, (255, 120, 120), (2, 8, 28, 10), border_radius=4)
    pygame.draw.rect(surf, (255, 220, 80), (4, 4, 24, 6), border_radius=3)
    pygame.image.save(surf, ASSETS_DIR / 'spring.png')


def _write_spikes_image() -> None:
    surf = pygame.Surface((32, 24), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (220, 220, 230), [(0, 24), (16, 0), (32, 24)])
    pygame.image.save(surf, ASSETS_DIR / 'spikes.png')


def _write_lava_image() -> None:
    surf = pygame.Surface((64, 24), pygame.SRCALPHA)
    pygame.draw.rect(surf, (255, 100, 40), (0, 0, 64, 24), border_radius=4)
    pygame.draw.rect(surf, (255, 180, 80), (0, 8, 64, 8), border_radius=4)
    pygame.image.save(surf, ASSETS_DIR / 'lava.png')


def _write_music_wave() -> None:
    _write_wav(ASSETS_DIR / 'music.wav', 0.8, 440, 660, 880)


def _write_jump_wave() -> None:
    _write_wav(ASSETS_DIR / 'jump.wav', 0.18, 620, 760)


def _write_coin_wave() -> None:
    _write_wav(ASSETS_DIR / 'coin.wav', 0.16, 980, 1160)


def _write_checkpoint_wave() -> None:
    _write_wav(ASSETS_DIR / 'checkpoint.wav', 0.22, 700, 900)


def _write_death_wave() -> None:
    _write_wav(ASSETS_DIR / 'death.wav', 0.28, 180, 90)


def _write_wav(path: Path, duration: float, *freqs: int) -> None:
    sample_rate = 22050
    frames = int(sample_rate * duration)
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        buf = bytearray()
        for i in range(frames):
            t = i / sample_rate
            value = 0.0
            for freq in freqs:
                value += math.sin(2 * math.pi * freq * t) * 0.25
            sample = int(max(-32768, min(32767, value * 12000)))
            buf.extend(sample.to_bytes(2, 'little', signed=True))
        wav.writeframes(buf)


def load_sound(path: str) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(str(ASSETS_DIR / path))
