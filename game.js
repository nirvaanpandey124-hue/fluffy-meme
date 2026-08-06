const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const menuScreen = document.getElementById('menu-screen');
const playButton = document.getElementById('play-button');
const gameUi = document.getElementById('game-ui');
const pauseButton = document.getElementById('pause-button');
const resetButton = document.getElementById('reset-button');
const exitButton = document.getElementById('exit-button');
const leftButton = document.getElementById('control-left');
const rightButton = document.getElementById('control-right');
const fireButton = document.getElementById('control-fire');
const scoreValue = document.getElementById('score-value');
const levelValue = document.getElementById('level-value');

const DESIGN_SIZE = 600;
const LEVEL_COUNT = 15;
const POINTS_PER_LEVEL = 4;
const BASE_ENEMY_SPEED = 2;
const ENEMY_SPEED_STEP = 0.3;
const BASE_ENEMY_RADIUS = 16;
const ENEMY_RADIUS_STEP = -0.35;
const MIN_ENEMY_RADIUS = 8;
const MAX_ENEMIES = 64;
const BASE_BULLET_SPEED = 10;
const BULLET_SPEED_STEP = 0.1;
const BASE_PLAYER_SPEED = 6;
const PLAYER_SPEED_STEP = 0.08;

let displaySize = DESIGN_SIZE;
let gameStarted = false;
let gameOver = false;
let paused = false;
let leftPressed = false;
let rightPressed = false;
let level = 1;

let audioContext = null;
let musicGain = null;
let musicTimer = null;
let musicStarted = false;
let fireHeld = false;
let autoFireTimer = null;

const player = { x: DESIGN_SIZE / 2, y: DESIGN_SIZE - 50, width: 30, height: 30, color: 'cyan', speed: BASE_PLAYER_SPEED };
const bullet = { x: 0, y: 0, width: 7, height: 14, color: 'yellow', speed: BASE_BULLET_SPEED + 2, active: false };
let enemies = [];
let score = 0;

function setButtonActive(button, active) {
    button.classList.toggle('active', active);
}

function configureButton(button, onStart, onEnd) {
    const handleStart = (event) => {
        event.preventDefault();
        event.stopPropagation();
        ensureMusicStarted();
        setButtonActive(button, true);
        onStart();
    };

    const handleEnd = (event) => {
        event.preventDefault();
        event.stopPropagation();
        setButtonActive(button, false);
        if (onEnd) onEnd();
    };

    if (window.PointerEvent) {
        button.addEventListener('pointerdown', handleStart);
        button.addEventListener('pointerup', handleEnd);
        button.addEventListener('pointercancel', handleEnd);
        button.addEventListener('pointerleave', handleEnd);
    } else {
        button.addEventListener('touchstart', handleStart, { passive: false });
        button.addEventListener('touchend', handleEnd);
        button.addEventListener('touchcancel', handleEnd);
        button.addEventListener('mousedown', handleStart);
        button.addEventListener('mouseup', handleEnd);
        button.addEventListener('mouseleave', handleEnd);
    }
}

function setPauseState(value) {
    paused = value;
    pauseButton.textContent = paused ? 'Resume' : 'Pause';
    setButtonActive(pauseButton, paused);
}

function togglePause() {
    if (!gameStarted || gameOver) return;
    setPauseState(!paused);
}

function showMenu() {
    gameStarted = false;
    leftPressed = false;
    rightPressed = false;
    gameOver = false;
    paused = false;
    stopAutoFire();
    menuScreen.classList.remove('hidden');
    gameUi.classList.add('hidden');
    resetGame();
}

function startGame() {
    gameStarted = true;
    menuScreen.classList.add('hidden');
    gameUi.classList.remove('hidden');
    ensureMusicStarted();
    resetGame();
}

function exitToMenu() {
    showMenu();
}

function resetGame() {
    gameOver = false;
    paused = false;
    leftPressed = false;
    rightPressed = false;
    score = 0;
    level = 1;
    setPauseState(false);
    player.x = DESIGN_SIZE / 2;
    player.y = DESIGN_SIZE - 50;
    player.width = 30;
    player.height = 30;
    player.speed = BASE_PLAYER_SPEED;
    bullet.active = false;
    bullet.x = 0;
    bullet.y = 0;
    bullet.width = 7;
    bullet.height = 14;
    bullet.speed = BASE_BULLET_SPEED + 2;
    spawnEnemies(level);
    updateHUD();
}

function fireBullet() {
    if (!gameStarted || paused || gameOver) return;
    if (bullet.active) return;
    bullet.active = true;
    bullet.x = player.x;
    bullet.y = player.y - player.height / 2 - bullet.height / 2 - 4;
}

function startAutoFire() {
    fireHeld = true;
    if (autoFireTimer) return;
    const tick = () => {
        if (!fireHeld || !gameStarted || paused || gameOver) {
            autoFireTimer = null;
            return;
        }
        fireBullet();
        autoFireTimer = setTimeout(tick, 70);
    };
    tick();
}

function stopAutoFire() {
    fireHeld = false;
    if (autoFireTimer) {
        clearTimeout(autoFireTimer);
        autoFireTimer = null;
    }
}

function drawRect(obj) {
    ctx.fillStyle = obj.color;
    ctx.fillRect(obj.x - obj.width / 2, obj.y - obj.height / 2, obj.width, obj.height);
}

function drawPlayerShip(obj) {
    const scale = Math.max(1, obj.width / 30);
    const px = obj.x;
    const py = obj.y;

    ctx.fillStyle = '#4fdcff';
    ctx.fillRect(px - 5 * scale, py - 10 * scale, 10 * scale, 20 * scale);
    ctx.fillRect(px - 12 * scale, py + 2 * scale, 24 * scale, 6 * scale);
    ctx.fillRect(px - 9 * scale, py - 6 * scale, 18 * scale, 4 * scale);

    ctx.fillStyle = '#2c7cff';
    ctx.fillRect(px - 7 * scale, py - 6 * scale, 14 * scale, 12 * scale);
    ctx.fillRect(px - 12 * scale, py + 8 * scale, 6 * scale, 4 * scale);
    ctx.fillRect(px + 6 * scale, py + 8 * scale, 6 * scale, 4 * scale);

    ctx.fillStyle = '#fff';
    ctx.fillRect(px - 2 * scale, py - 8 * scale, 4 * scale, 8 * scale);
    ctx.fillRect(px - 5 * scale, py + 4 * scale, 10 * scale, 3 * scale);
}

function drawEnemyShip(enemy) {
    const scale = Math.max(1, enemy.radius / 8);
    const px = enemy.x;
    const py = enemy.y;

    ctx.fillStyle = '#ff7cc2';
    ctx.fillRect(px - 6 * scale, py - 12 * scale, 12 * scale, 24 * scale);
    ctx.fillRect(px - 10 * scale, py + 2 * scale, 20 * scale, 6 * scale);
    ctx.fillRect(px - 8 * scale, py - 6 * scale, 16 * scale, 4 * scale);

    ctx.fillStyle = '#ff3fa7';
    ctx.fillRect(px - 4 * scale, py - 10 * scale, 8 * scale, 12 * scale);
    ctx.fillRect(px - 10 * scale, py + 8 * scale, 4 * scale, 4 * scale);
    ctx.fillRect(px + 6 * scale, py + 8 * scale, 4 * scale, 4 * scale);

    ctx.fillStyle = '#ffc0e8';
    ctx.fillRect(px - 2 * scale, py - 8 * scale, 4 * scale, 8 * scale);
    ctx.fillRect(px - 4 * scale, py + 4 * scale, 8 * scale, 3 * scale);
}

function drawCircle(obj) {
    ctx.fillStyle = obj.color;
    ctx.beginPath();
    ctx.arc(obj.x, obj.y, obj.radius, 0, Math.PI * 2);
    ctx.fill();
}

function drawText() {
    ctx.fillStyle = 'white';
    ctx.font = `${Math.max(16, Math.round(displaySize * 0.03))}px Arial`;
    ctx.fillText(`Score: ${score}`, 12, Math.max(24, displaySize * 0.04));

    if (paused) {
        ctx.font = `${Math.max(24, Math.round(displaySize * 0.06))}px Arial`;
        ctx.fillText('PAUSED', DESIGN_SIZE / 2 - DESIGN_SIZE * 0.12, DESIGN_SIZE / 2);
    }

    if (gameOver) {
        ctx.font = `${Math.max(28, Math.round(displaySize * 0.07))}px Arial`;
        ctx.fillText('GAME OVER', DESIGN_SIZE / 2 - DESIGN_SIZE * 0.18, DESIGN_SIZE / 2);
    }
}

function computeLevel(scoreValue) {
    return Math.min(LEVEL_COUNT, Math.floor(scoreValue / POINTS_PER_LEVEL) + 1);
}

function updateDifficulty() {
    const nextLevel = computeLevel(score);
    if (nextLevel !== level) {
        level = nextLevel;
        playLevelUpSound();
        spawnEnemies(level);
    }

    enemies.forEach((enemy) => {
        enemy.speed = BASE_ENEMY_SPEED + (level - 1) * ENEMY_SPEED_STEP;
        enemy.radius = Math.max(MIN_ENEMY_RADIUS, BASE_ENEMY_RADIUS + (level - 1) * ENEMY_RADIUS_STEP);
    });

    bullet.speed = BASE_BULLET_SPEED + (level - 1) * BULLET_SPEED_STEP;
    player.speed = BASE_PLAYER_SPEED + (level - 1) * PLAYER_SPEED_STEP;
    updateHUD();
}

function updateHUD() {
    scoreValue.textContent = score.toString();
    levelValue.textContent = `${level} / ${LEVEL_COUNT}`;
    const progress = (score % POINTS_PER_LEVEL) / POINTS_PER_LEVEL * 100;
    const progressFill = document.getElementById('level-progress');
    const nextLevelValue = document.getElementById('next-level-value');
    if (progressFill) {
        progressFill.style.width = `${progress}%`;
    }
    if (nextLevelValue) {
        const pointsUntil = Math.max(0, POINTS_PER_LEVEL - (score % POINTS_PER_LEVEL));
        nextLevelValue.textContent = pointsUntil
            ? `Next level in ${pointsUntil} point${pointsUntil === 1 ? '' : 's'}`
            : 'Level up next hit!';
    }
}

function createEnemy(levelNumber) {
    const radius = Math.max(MIN_ENEMY_RADIUS, BASE_ENEMY_RADIUS + (levelNumber - 1) * ENEMY_RADIUS_STEP);
    return {
        x: Math.random() * (DESIGN_SIZE - radius * 2) + radius,
        y: -radius - Math.random() * 120,
        radius,
        color: 'pink',
        speed: BASE_ENEMY_SPEED + (levelNumber - 1) * ENEMY_SPEED_STEP,
    };
}

function spawnEnemies(levelNumber) {
    const count = 5;
    enemies = [];
    for (let i = 0; i < count; i += 1) {
        enemies.push(createEnemy(levelNumber));
    }
}

function playSound(frequency, duration, type = 'sine', volume = 0.16) {
    if (!audioContext) return;
    const osc = audioContext.createOscillator();
    const gain = audioContext.createGain();
    osc.type = type;
    osc.frequency.value = frequency;
    gain.gain.setValueAtTime(volume, audioContext.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + duration);
    osc.connect(gain).connect(audioContext.destination);
    osc.start();
    osc.stop(audioContext.currentTime + duration);
}

function playLevelUpSound() {
    playSound(520, 0.12, 'triangle', 0.16);
    setTimeout(() => playSound(660, 0.1, 'triangle', 0.14), 110);
}

function playDeathSound() {
    playSound(120, 0.35, 'sawtooth', 0.22);
    setTimeout(() => playSound(90, 0.2, 'square', 0.12), 120);
}

function initMusic() {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;

    audioContext = new AudioContext();
    musicGain = audioContext.createGain();
    musicGain.gain.value = 0.24;
    musicGain.connect(audioContext.destination);

    const melody = [330, 392, 440, 392, 330, 294, 262, 294];
    const rhythm = [0.28, 0.28, 0.28, 0.28, 0.28, 0.28, 0.28, 0.4];
    let melodyIndex = 0;

    const playStep = () => {
        const now = audioContext.currentTime;
        const noteOsc = audioContext.createOscillator();
        noteOsc.type = 'triangle';
        noteOsc.frequency.setValueAtTime(melody[melodyIndex], now);

        const noteGain = audioContext.createGain();
        noteGain.gain.setValueAtTime(0.14, now);
        noteGain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);

        noteOsc.connect(noteGain).connect(musicGain);
        noteOsc.start(now);
        noteOsc.stop(now + 0.24);

        melodyIndex = (melodyIndex + 1) % melody.length;
        musicTimer = setTimeout(playStep, rhythm[melodyIndex] * 1000);
    };

    playStep();
}

function ensureMusicStarted() {
    if (musicStarted) return;
    musicStarted = true;
    initMusic();
}

function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}

function update() {
    if (!gameStarted || paused || gameOver) return;

    if (leftPressed) {
        player.x -= player.speed;
    }
    if (rightPressed) {
        player.x += player.speed;
    }

    player.x = clamp(player.x, player.width / 2, DESIGN_SIZE - player.width / 2);

    if (bullet.active) {
        bullet.y -= bullet.speed;
        if (bullet.y + bullet.height / 2 < 0) {
            bullet.active = false;
        }
    }

    enemies.forEach((enemy) => {
        enemy.y += enemy.speed;
        if (enemy.y - enemy.radius > DESIGN_SIZE) {
            enemy.y = -enemy.radius;
            enemy.x = Math.random() * (DESIGN_SIZE - enemy.radius * 2) + enemy.radius;
        }
    });

    const hitEnemyIndex = enemies.findIndex((enemy) => bullet.active && Math.hypot(bullet.x - enemy.x, bullet.y - enemy.y) < enemy.radius + bullet.width / 2);
    if (hitEnemyIndex !== -1) {
        score += 1;
        bullet.active = false;
        enemies.splice(hitEnemyIndex, 1);
        updateDifficulty();
    }

    if (enemies.some((enemy) => Math.hypot(player.x - enemy.x, player.y - enemy.y) < enemy.radius + player.width / 2)) {
        if (!gameOver) {
            playDeathSound();
        }
        gameOver = true;
    }
}

function render() {
    ctx.clearRect(0, 0, DESIGN_SIZE, DESIGN_SIZE);
    drawPlayerShip(player);

    if (bullet.active) {
        drawRect(bullet);
    }

    enemies.forEach((enemy) => drawEnemyShip(enemy));
    drawText();
}

function resizeCanvas() {
    const reservedHeight = Math.max(120, window.innerHeight * 0.18);
    const maxSize = Math.min(window.innerWidth, window.innerHeight - reservedHeight, DESIGN_SIZE);
    displaySize = Math.max(320, Math.floor(maxSize));

    const dpr = window.devicePixelRatio || 1;
    canvas.width = DESIGN_SIZE * dpr;
    canvas.height = DESIGN_SIZE * dpr;
    canvas.style.width = `${displaySize}px`;
    canvas.style.height = `${displaySize}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}

function preventScroll(event) {
    event.preventDefault();
}

configureButton(leftButton, () => { leftPressed = true; }, () => { leftPressed = false; });
configureButton(rightButton, () => { rightPressed = true; }, () => { rightPressed = false; });
configureButton(fireButton, startAutoFire, stopAutoFire);
configureButton(pauseButton, togglePause, () => {});
configureButton(resetButton, resetGame, () => {});
configureButton(exitButton, exitToMenu, () => {});
playButton.addEventListener('click', startGame);

window.addEventListener('resize', resizeCanvas);
window.addEventListener('touchmove', preventScroll, { passive: false });
window.addEventListener('gesturestart', preventScroll);
window.addEventListener('orientationchange', resizeCanvas);

resizeCanvas();
showMenu();

function loop() {
    update();
    render();
    requestAnimationFrame(loop);
}

loop();
