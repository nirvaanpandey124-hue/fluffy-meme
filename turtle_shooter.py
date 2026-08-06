import os
import sys
import turtle
import random

# The turtle module requires a graphical display. In Codespaces there is no DISPLAY,
# so the game cannot run here. This script is preserved for local desktop use only.
if not os.environ.get("DISPLAY"):
    sys.stderr.write(
        "Error: no DISPLAY environment variable found.\n"
        "Turtle graphics require a local desktop environment.\n"
        "Run this script locally on Windows/macOS with VS Code or a terminal.\n"
    )
    sys.exit(1)

# Screen
screen = turtle.Screen()
screen.title("Mini Shooter")
screen.bgcolor("black")
screen.setup(width=600, height=600)
screen.tracer(0)

# Player
player = turtle.Turtle()
player.shape("triangle")
player.color("cyan")
player.penup()
player.setheading(90)
player.goto(0, -250)

# Bullet
bullet = turtle.Turtle()
bullet.shape("square")
bullet.color("yellow")
bullet.shapesize(0.3, 1)
bullet.penup()
bullet.hideturtle()
bullet_speed = 20
bullet_state = "ready"

# Enemy
enemy = turtle.Turtle()
enemy.shape("circle")
enemy.color("red")
enemy.penup()
enemy.goto(random.randint(-250, 250), 250)
enemy_speed = 3

# Score
score = 0
pen = turtle.Turtle()
pen.hideturtle()
pen.color("white")
pen.penup()
pen.goto(-280, 260)
pen.write("Score: 0", font=("Arial", 14, "normal"))


def move_left():
    x = player.xcor() - 20
    if x > -280:
        player.setx(x)

def move_right():
    x = player.xcor() + 20
    if x < 280:
        player.setx(x)

def fire_bullet():
    global bullet_state
    if bullet_state == "ready":
        bullet_state = "fire"
        bullet.goto(player.xcor(), player.ycor() + 10)
        bullet.showturtle()

screen.listen()
screen.onkeypress(move_left, "Left")
screen.onkeypress(move_right, "Right")
screen.onkeypress(fire_bullet, "space")

while True:
    screen.update()

    # Enemy movement
    enemy.sety(enemy.ycor() - enemy_speed)

    if enemy.ycor() < -300:
        enemy.goto(random.randint(-250, 250), 250)

    # Bullet movement
    if bullet_state == "fire":
        bullet.sety(bullet.ycor() + bullet_speed)

    if bullet.ycor() > 300:
        bullet.hideturtle()
        bullet_state = "ready"

    # Collision
    if bullet.distance(enemy) < 20:
        bullet.hideturtle()
        bullet_state = "ready"
        bullet.goto(0, -400)

        enemy.goto(random.randint(-250, 250), 250)

        score += 1
        pen.clear()
        pen.write(f"Score: {score}", font=("Arial", 14, "normal"))

    # Game Over
    if enemy.distance(player) < 25:
        pen.goto(-80, 0)
        pen.write("GAME OVER", font=("Arial", 24, "bold"))
        break

screen.mainloop()