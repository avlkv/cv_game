import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 15

# Game Variables
left_paddle = pygame.Rect(30, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WIDTH - 40, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

ball_speed_x = random.choice((3, -3))
ball_speed_y = random.choice((3, -3))
paddle_speed = 10
computer_speed = 6

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Paddle movement for player (left paddle) using arrow keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and left_paddle.top > 0:  # Move left paddle up
        left_paddle.y -= paddle_speed
    if keys[pygame.K_DOWN] and left_paddle.bottom < HEIGHT:  # Move left paddle down
        left_paddle.y += paddle_speed

    # Simple AI for the computer opponent (right paddle)
    if right_paddle.centery < ball.centery and right_paddle.bottom < HEIGHT:
        right_paddle.y += computer_speed
    if right_paddle.centery > ball.centery and right_paddle.top > 0:
        right_paddle.y -= computer_speed

    # Move the ball
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Ball collision with top and bottom walls
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1

    # Ball collision with paddles
    if left_paddle.colliderect(ball) or right_paddle.colliderect(ball):
        ball_speed_x *= -1

    # Reset the ball if it goes out of bounds
    if ball.left <= 0 or ball.right >= WIDTH:
        ball.x = WIDTH // 2 - BALL_SIZE // 2
        ball.y = HEIGHT // 2 - BALL_SIZE // 2
        ball_speed_x *= random.choice((1, -1))
        ball_speed_y *= random.choice((1, -1))

    # Drawing everything
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)

    # Update the display
    pygame.display.flip()

    # Frame rate control
    pygame.time.Clock().tick(60)
