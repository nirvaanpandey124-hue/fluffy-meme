from __future__ import annotations

import json
import math
import os
import random
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame

from .entities import Checkpoint, Coin, Gem, Lava, LevelBuilder, Particle, Platform, Player, PowerUp, Spike, Spring
from .utils import ASSETS_DIR, ensure_assets, load_sound


class GameApp:
    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        ensure_assets()
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.SCALED)
        pygame.display.set_caption('Neon Parkour')
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene = 'menu'
        self.level_id = 1
        self.max_level = 1
        self.save_path = Path('save_data.json')
        self.load_progress()
        self.font = pygame.font.SysFont('arial', 24)
        self.title_font = pygame.font.SysFont('arial', 48, bold=True)
        self.small_font = pygame.font.SysFont('arial', 18)
        self.current_level = None
        self.player = None
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_target_x = 0.0
        self.camera_target_y = 0.0
        self.shake_time = 0.0
        self.shake_intensity = 0.0
        self.particles: List[Particle] = []
        self.background_offset = 0
        self.time_start = 0.0
        self.level_time = 0.0
        self.deaths = 0
        self.achievements = []
        self.volume = 0.6
        self.music_playing = False
        self.music = None
        self.jump_sound = None
        self.coin_sound = None
        self.checkpoint_sound = None
        self.death_sound = None
        self.touch_buttons = {}
        self.touch_active = False
        self.input_left = False
        self.input_right = False
        self.input_jump = False
        self.input_slide = False
        self.input_pause = False
        self.input_fire = False
        self.input_escape = False
        self.level_complete = False
        self.level_message = ''
        self.settings = {'music': True, 'sfx': True, 'fullscreen': False}
        self.load_assets()
        self.init_touch_buttons()
        self.create_menu_surface()

    def load_assets(self) -> None:
        self.player_img = pygame.image.load(ASSETS_DIR / 'player.png').convert_alpha()
        self.platform_img = pygame.image.load(ASSETS_DIR / 'platform.png').convert_alpha()
        self.coin_img = pygame.image.load(ASSETS_DIR / 'coin.png').convert_alpha()
        self.gem_img = pygame.image.load(ASSETS_DIR / 'gem.png').convert_alpha()
        self.flag_img = pygame.image.load(ASSETS_DIR / 'flag.png').convert_alpha()
        self.checkpoint_img = pygame.image.load(ASSETS_DIR / 'checkpoint.png').convert_alpha()
        self.spring_img = pygame.image.load(ASSETS_DIR / 'spring.png').convert_alpha()
        self.spikes_img = pygame.image.load(ASSETS_DIR / 'spikes.png').convert_alpha()
        self.lava_img = pygame.image.load(ASSETS_DIR / 'lava.png').convert_alpha()
        try:
            self.music = pygame.mixer.Sound(str(ASSETS_DIR / 'music.wav'))
            self.jump_sound = pygame.mixer.Sound(str(ASSETS_DIR / 'jump.wav'))
            self.coin_sound = pygame.mixer.Sound(str(ASSETS_DIR / 'coin.wav'))
            self.checkpoint_sound = pygame.mixer.Sound(str(ASSETS_DIR / 'checkpoint.wav'))
            self.death_sound = pygame.mixer.Sound(str(ASSETS_DIR / 'death.wav'))
        except Exception:
            self.music = None
            self.jump_sound = None
            self.coin_sound = None
            self.checkpoint_sound = None
            self.death_sound = None

    def create_menu_surface(self) -> None:
        self.menu_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

    def init_touch_buttons(self) -> None:
        self.touch_buttons = {
            'left': pygame.Rect(40, self.screen_height - 160, 120, 120),
            'right': pygame.Rect(180, self.screen_height - 160, 120, 120),
            'jump': pygame.Rect(self.screen_width - 180, self.screen_height - 190, 120, 120),
            'slide': pygame.Rect(self.screen_width - 320, self.screen_height - 160, 120, 120),
        }

    def load_progress(self) -> None:
        if self.save_path.exists():
            try:
                with self.save_path.open('r', encoding='utf-8') as fh:
                    data = json.load(fh)
                self.max_level = data.get('max_level', 1)
                self.settings = data.get('settings', self.settings)
                self.volume = data.get('volume', self.volume)
                self.achievements = data.get('achievements', [])
            except Exception:
                self.max_level = 1

    def save_progress(self) -> None:
        data = {
            'max_level': self.max_level,
            'settings': self.settings,
            'volume': self.volume,
            'achievements': self.achievements,
        }
        with self.save_path.open('w', encoding='utf-8') as fh:
            json.dump(data, fh)

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()
        pygame.quit()

    def handle_events(self) -> None:
        self.input_left = False
        self.input_right = False
        self.input_jump = False
        self.input_slide = False
        self.input_pause = False
        self.input_escape = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE,):
                    self.input_escape = True
                    if self.scene == 'game':
                        self.scene = 'pause'
                if event.key in (pygame.K_a, pygame.K_LEFT):
                    self.input_left = True
                if event.key in (pygame.K_d, pygame.K_RIGHT):
                    self.input_right = True
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    self.input_jump = True
                if event.key in (pygame.K_s, pygame.K_DOWN):
                    self.input_slide = True
                if event.key == pygame.K_p:
                    if self.scene == 'game':
                        self.scene = 'pause'
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_ESCAPE,):
                    self.input_escape = False
                if event.key in (pygame.K_a, pygame.K_LEFT):
                    self.input_left = False
                if event.key in (pygame.K_d, pygame.K_RIGHT):
                    self.input_right = False
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    self.input_jump = False
                if event.key in (pygame.K_s, pygame.K_DOWN):
                    self.input_slide = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse(event.pos, True)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse(event.pos, False)
            elif event.type == pygame.FINGERDOWN:
                x = event.x * self.screen_width
                y = event.y * self.screen_height
                self.handle_touch((x, y), True)
            elif event.type == pygame.FINGERUP:
                x = event.x * self.screen_width
                y = event.y * self.screen_height
                self.handle_touch((x, y), False)

    def handle_mouse(self, pos: Tuple[int, int], down: bool) -> None:
        if self.scene == 'menu':
            if self.button_rect('play', pos):
                self.start_level(1)
            if self.button_rect('level', pos):
                self.scene = 'level_select'
            if self.button_rect('settings', pos):
                self.scene = 'settings'
        elif self.scene == 'level_select':
            for idx in range(1, min(3, self.max_level) + 1):
                if self.button_rect(f'level_{idx}', pos):
                    self.start_level(idx)
        elif self.scene == 'settings':
            if self.button_rect('music', pos):
                self.settings['music'] = not self.settings['music']
                self.save_progress()
            if self.button_rect('sfx', pos):
                self.settings['sfx'] = not self.settings['sfx']
                self.save_progress()
            if self.button_rect('back', pos):
                self.scene = 'menu'
        elif self.scene == 'pause':
            if self.button_rect('resume', pos):
                self.scene = 'game'
            if self.button_rect('menu', pos):
                self.scene = 'menu'
        elif self.scene == 'game':
            if self.button_rect('exit', pos):
                self.scene = 'menu'

    def handle_touch(self, pos: Tuple[int, int], down: bool) -> None:
        self.touch_active = True
        for name, rect in self.touch_buttons.items():
            if rect.collidepoint(pos):
                if name == 'left':
                    self.input_left = down
                elif name == 'right':
                    self.input_right = down
                elif name == 'jump':
                    self.input_jump = down
                elif name == 'slide':
                    self.input_slide = down

    def update(self, dt: float) -> None:
        if self.scene == 'game':
            self.update_game(dt)
        elif self.scene == 'menu':
            self.background_offset = (self.background_offset + 1) % 800
        elif self.scene == 'level_select':
            self.background_offset = (self.background_offset + 1) % 800

    def start_level(self, level_id: int) -> None:
        self.level_id = level_id
        self.level_complete = False
        self.level_message = ''
        self.current_level = LevelBuilder(level_id).build()
        self.player = Player(x=120, y=800)
        self.player.last_checkpoint = (120.0, 800.0)
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_target_x = 0.0
        self.camera_target_y = 0.0
        self.shake_time = 0.0
        self.particles = []
        self.time_start = pygame.time.get_ticks() / 1000.0
        self.level_time = 0.0
        self.deaths = 0
        self.scene = 'game'
        if self.settings['music']:
            self.play_music_loop()

    def restart_level(self) -> None:
        self.player = Player(x=self.player.last_checkpoint[0], y=self.player.last_checkpoint[1]) if self.player and self.player.last_checkpoint else Player(x=120, y=800)
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_target_x = 0.0
        self.camera_target_y = 0.0
        self.particles = []
        self.level_time = 0.0
        self.time_start = pygame.time.get_ticks() / 1000.0
        self.deaths += 1
        self.scene = 'game'

    def play_music_loop(self) -> None:
        if self.music is None or not self.settings['music']:
            return
        if self.music_playing:
            return
        self.music.play(-1)
        self.music_playing = True

    def stop_music(self) -> None:
        if self.music is not None:
            self.music.stop()
        self.music_playing = False

    def play_sfx(self, sound) -> None:
        if sound is None or not self.settings['sfx']:
            return
        sound.play()

    def update_game(self, dt: float) -> None:
        if self.player is None:
            return
        self.level_time = (pygame.time.get_ticks() / 1000.0) - self.time_start
        self.update_player(dt)
        self.update_camera(dt)
        self.update_particles(dt)
        self.update_moving_platforms(dt)
        self.update_shake(dt)
        self.check_collisions()
        self.check_finish()

    def update_player(self, dt: float) -> None:
        player = self.player
        move_dir = 0
        if self.input_left:
            move_dir -= 1
        if self.input_right:
            move_dir += 1
        if move_dir != 0:
            player.vx += move_dir * 1200 * dt
            player.vx = max(-250, min(250, player.vx))
            player.facing = move_dir
        else:
            player.vx *= 0.8
        if player.on_ground:
            player.double_jump_used = False
        if self.input_jump and not player.jumped:
            if player.on_ground:
                player.vy = -560
                player.on_ground = False
                player.double_jump_used = False
                self.spawn_particles(player.x, player.y + player.height, (255, 255, 255), 8)
                self.play_sfx(self.jump_sound)
            elif not player.double_jump_used:
                player.vy = -480
                player.double_jump_used = True
                self.spawn_particles(player.x, player.y + player.height, (255, 255, 255), 8)
                self.play_sfx(self.jump_sound)
            player.jumped = True
        elif not self.input_jump:
            player.jumped = False
        if self.input_slide and player.on_ground:
            player.slide_time = 0.2
            player.height = 42
            player.y += 12
        else:
            player.slide_time = max(0, player.slide_time - dt)
            if player.slide_time <= 0:
                player.height = 54
        if self.input_jump and player.wall_jump_cooldown > 0:
            player.wall_jump_cooldown = max(0, player.wall_jump_cooldown - dt)
        player.vy += 1300 * dt
        player.x += player.vx * dt
        player.y += player.vy * dt
        player.vx *= 0.98
        player.on_ground = False
        player.wall_jump_cooldown = max(0, player.wall_jump_cooldown - dt)
        player.invincible_time = max(0, player.invincible_time - dt)
        player.shield_time = max(0, player.shield_time - dt)
        player.speed_boost_time = max(0, player.speed_boost_time - dt)
        if player.speed_boost_time > 0:
            player.vx = max(-420, min(420, player.vx))

    def update_camera(self, dt: float) -> None:
        player = self.player
        if player is None:
            return
        self.camera_target_x = max(0, min(self.current_level.width - self.screen_width, player.x - self.screen_width / 2))
        self.camera_target_y = max(0, min(self.current_level.height - self.screen_height, player.y - self.screen_height / 2 + 100))
        self.camera_x += (self.camera_target_x - self.camera_x) * 0.08
        self.camera_y += (self.camera_target_y - self.camera_y) * 0.08
        if self.shake_time > 0:
            self.shake_time -= dt
            self.camera_x += random.uniform(-self.shake_intensity, self.shake_intensity)
            self.camera_y += random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_intensity = max(0, self.shake_intensity - 30 * dt)

    def update_particles(self, dt: float) -> None:
        new_particles = []
        for p in self.particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += 350 * dt
            p.life -= dt
            if p.life > 0:
                new_particles.append(p)
        self.particles = new_particles

    def update_moving_platforms(self, dt: float) -> None:
        if self.current_level is None:
            return
        for platform in self.current_level.moving_platforms:
            platform.rect.x += 80 * dt * (1 if platform.rect.x < 1500 else -1)
            if platform.rect.x < 100:
                platform.rect.x = 100
            elif platform.rect.x > 1700:
                platform.rect.x = 1700

    def update_shake(self, dt: float) -> None:
        if self.shake_time > 0:
            self.shake_time -= dt

    def check_collisions(self) -> None:
        if self.player is None or self.current_level is None:
            return
        player = self.player
        for platform in self.current_level.platforms + self.current_level.moving_platforms + self.current_level.falling_platforms:
            if player.vy >= 0 and player.y + player.height >= platform.rect.y and player.y + player.height <= platform.rect.y + 30 and player.x + player.width > platform.rect.x and player.x < platform.rect.x + platform.rect.width:
                player.y = platform.rect.y - player.height
                player.vy = 0
                player.on_ground = True
                if platform.kind == 'falling':
                    platform.rect.y += 20
                    self.shake(6, 0.15)
                if platform.kind != 'falling':
                    self.spawn_particles(player.x, player.y + player.height, (255, 255, 255), 5)
        for spike in self.current_level.spikes:
            if player.rect().colliderect(spike.rect):
                self.damage_player()
        for lava in self.current_level.lava:
            if player.rect().colliderect(lava.rect):
                self.damage_player()
        for spring in self.current_level.springs:
            if player.rect().colliderect(spring.rect):
                if not spring.bounced:
                    player.vy = -720
                    spring.bounced = True
                    self.play_sfx(self.jump_sound)
        for coin in self.current_level.coins:
            if not coin.collected and player.rect().colliderect(coin.rect):
                coin.collected = True
                player.coins += 1
                self.play_sfx(self.coin_sound)
        for gem in self.current_level.gems:
            if not gem.collected and player.rect().colliderect(gem.rect):
                gem.collected = True
                player.gems += 1
                self.achievements.append('GEM') if 'GEM' not in self.achievements else None
        for cp in self.current_level.checkpoints:
            if not cp.active and player.rect().colliderect(cp.rect):
                cp.active = True
                player.last_checkpoint = (cp.rect.x, cp.rect.y - 80)
                self.play_sfx(self.checkpoint_sound)
        if self.player.rect().colliderect(self.current_level.finish_rect):
            self.complete_level()

    def damage_player(self) -> None:
        if self.player.invincible_time > 0:
            return
        if self.player.shield:
            self.player.shield = False
            self.player.invincible_time = 0.6
            self.play_sfx(self.death_sound)
            return
        self.player.invincible_time = 1.0
        self.player.vy = -300
        self.play_sfx(self.death_sound)
        self.add_achievement('Survivor')
        self.restart_level()

    def check_finish(self) -> None:
        if self.player is None or self.current_level is None:
            return
        if self.player.rect().colliderect(self.current_level.finish_rect):
            self.complete_level()

    def complete_level(self) -> None:
        if self.level_complete:
            return
        self.level_complete = True
        self.max_level = max(self.max_level, self.level_id + 1)
        self.save_progress()
        self.scene = 'menu'
        self.level_message = f'Level {self.level_id} complete!'
        self.add_achievement('Finisher')

    def add_achievement(self, name: str) -> None:
        if name not in self.achievements:
            self.achievements.append(name)

    def shake(self, intensity: float, time: float) -> None:
        self.shake_intensity = intensity
        self.shake_time = time

    def spawn_particles(self, x: float, y: float, color: Tuple[int, int, int], count: int = 8) -> None:
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(20, 140)
            self.particles.append(Particle(x, y, math.cos(angle) * speed, math.sin(angle) * speed, random.uniform(0.2, 0.55), color))

    def render(self) -> None:
        self.screen.fill((20, 24, 45))
        self.render_background()
        if self.current_level is not None and self.scene == 'game':
            self.render_level()
        elif self.scene == 'menu':
            self.render_menu()
        elif self.scene == 'level_select':
            self.render_level_select()
        elif self.scene == 'settings':
            self.render_settings()
        elif self.scene == 'pause':
            self.render_pause()
        pygame.display.flip()

    def render_background(self) -> None:
        self.background_offset = (self.background_offset + 1) % 800
        for i in range(5):
            y = i * 140
            pygame.draw.rect(self.screen, (20 + i * 8, 24 + i * 8, 45 + i * 8), (0, y, self.screen_width, 140))
        for i in range(8):
            x = (self.background_offset * (i + 1) / 8) % self.screen_width
            pygame.draw.circle(self.screen, (255, 255, 255, 60), (int(x), 100 + i * 60), 3)

    def render_level(self) -> None:
        if self.current_level is None or self.player is None:
            return
        self.screen.fill((14, 18, 32))
        for platform in self.current_level.platforms:
            self.draw_platform(platform.rect)
        for platform in self.current_level.moving_platforms:
            self.draw_platform(platform.rect)
        for platform in self.current_level.falling_platforms:
            self.draw_platform(platform.rect)
        for spike in self.current_level.spikes:
            self.screen.blit(self.spikes_img, (spike.rect.x - self.camera_x, spike.rect.y - self.camera_y))
        for lava in self.current_level.lava:
            self.screen.blit(self.lava_img, (lava.rect.x - self.camera_x, lava.rect.y - self.camera_y))
        for spring in self.current_level.springs:
            self.screen.blit(self.spring_img, (spring.rect.x - self.camera_x, spring.rect.y - self.camera_y))
        for coin in self.current_level.coins:
            if not coin.collected:
                self.screen.blit(self.coin_img, (coin.rect.x - self.camera_x, coin.rect.y - self.camera_y))
        for gem in self.current_level.gems:
            if not gem.collected:
                self.screen.blit(self.gem_img, (gem.rect.x - self.camera_x, gem.rect.y - self.camera_y))
        for cp in self.current_level.checkpoints:
            self.screen.blit(self.checkpoint_img, (cp.rect.x - self.camera_x, cp.rect.y - self.camera_y))
        self.screen.blit(self.flag_img, (self.current_level.finish_rect.x - self.camera_x, self.current_level.finish_rect.y - self.camera_y))
        self.render_particles()
        self.render_player()
        self.render_ui()
        self.render_touch_controls()

    def draw_platform(self, rect: pygame.Rect) -> None:
        self.screen.blit(self.platform_img, (rect.x - self.camera_x, rect.y - self.camera_y))

    def render_player(self) -> None:
        player = self.player
        if player is None:
            return
        frame = self.player_img
        x = player.x - self.camera_x
        y = player.y - self.camera_y
        if player.invincible_time > 0 and int(player.invincible_time * 10) % 2 == 0:
            return
        if player.facing < 0:
            frame = pygame.transform.flip(frame, True, False)
        self.screen.blit(frame, (x, y))

    def render_particles(self) -> None:
        for p in self.particles:
            pygame.draw.circle(self.screen, p.color, (int(p.x - self.camera_x), int(p.y - self.camera_y)), 3)

    def render_ui(self) -> None:
        self.draw_text(f'Coins: {self.player.coins}', 20, 20)
        self.draw_text(f'Level: {self.level_id}', 20, 50)
        self.draw_text(f'Time: {self.level_time:.1f}s', 20, 80)
        self.draw_text(f'Deaths: {self.deaths}', 20, 110)
        self.draw_text(f'Best: {self.best_time()}s', 20, 140)
        if self.level_message:
            self.draw_text(self.level_message, self.screen_width // 2 - 120, 20)

    def best_time(self) -> float:
        return 0.0

    def draw_text(self, text: str, x: int, y: int, color=(255, 255, 255)) -> None:
        surf = self.font.render(text, True, color)
        self.screen.blit(surf, (x, y))

    def render_menu(self) -> None:
        self.screen.blit(self.menu_surface, (0, 0))
        self.draw_centered_text('Neon Parkour', 60, 120)
        self.draw_centered_text('Jump, wall-jump, slide and dash through neon levels', 28, 220)
        self.button('Play', 300, 360, 220, 60, 'play')
        self.button('Level Select', 300, 440, 220, 60, 'level')
        self.button('Settings', 300, 520, 220, 60, 'settings')

    def render_level_select(self) -> None:
        self.draw_centered_text('Level Select', 40, 120)
        for idx in range(1, 4):
            locked = idx > self.max_level
            label = 'Locked' if locked else f'Level {idx}'
            self.button(label, 300, 220 + idx * 90, 220, 60, f'level_{idx}', locked=locked)

    def render_settings(self) -> None:
        self.draw_centered_text('Settings', 40, 120)
        self.button('Music: ON' if self.settings['music'] else 'Music: OFF', 300, 240, 300, 60, 'music')
        self.button('SFX: ON' if self.settings['sfx'] else 'SFX: OFF', 300, 320, 300, 60, 'sfx')
        self.button('Back', 300, 400, 300, 60, 'back')

    def render_pause(self) -> None:
        self.draw_centered_text('Paused', 40, 160)
        self.button('Resume', 300, 280, 260, 60, 'resume')
        self.button('Main Menu', 300, 360, 260, 60, 'menu')

    def draw_centered_text(self, text: str, size: int, y: int) -> None:
        surf = self.title_font.render(text, True, (255, 255, 255))
        rect = surf.get_rect(center=(self.screen_width // 2, y))
        self.screen.blit(surf, rect)

    def button(self, label: str, x: int, y: int, width: int, height: int, name: str, locked: bool = False) -> None:
        rect = pygame.Rect(x, y, width, height)
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        color = (80, 120, 255) if not locked else (100, 100, 100)
        if hovered:
            color = (120, 180, 255)
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        text = self.font.render(label, True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)

    def button_rect(self, name: str, pos: Tuple[int, int]) -> bool:
        if name == 'play':
            return pygame.Rect(300, 360, 220, 60).collidepoint(pos)
        if name == 'level':
            return pygame.Rect(300, 440, 220, 60).collidepoint(pos)
        if name == 'settings':
            return pygame.Rect(300, 520, 220, 60).collidepoint(pos)
        if name == 'music':
            return pygame.Rect(300, 240, 300, 60).collidepoint(pos)
        if name == 'sfx':
            return pygame.Rect(300, 320, 300, 60).collidepoint(pos)
        if name == 'back':
            return pygame.Rect(300, 400, 300, 60).collidepoint(pos)
        if name == 'resume':
            return pygame.Rect(300, 280, 260, 60).collidepoint(pos)
        if name == 'menu':
            return pygame.Rect(300, 360, 260, 60).collidepoint(pos)
        if name == 'exit':
            return pygame.Rect(self.screen_width - 140, 20, 120, 48).collidepoint(pos)
        if name.startswith('level_'):
            idx = int(name.split('_')[1])
            return pygame.Rect(300, 220 + idx * 90, 220, 60).collidepoint(pos)
        return False

    def render_touch_controls(self) -> None:
        for name, rect in self.touch_buttons.items():
            color = (60, 80, 140) if name in ('left', 'right') else (120, 70, 180)
            pygame.draw.rect(self.screen, color, rect, border_radius=18)
            label = '◀' if name == 'left' else '▶' if name == 'right' else '↑' if name == 'jump' else '↓'
            text = self.font.render(label, True, (255, 255, 255))
            self.screen.blit(text, (rect.x + 40, rect.y + 40))
