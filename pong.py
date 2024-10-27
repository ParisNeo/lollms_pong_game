import pygame
import numpy as np
import json
import os
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
BALL_SIZE = 15
PADDLE_SPEED = 5
BALL_SPEED = 7
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class GameState(Enum):
    MENU = 1
    GAME = 2
    LEADERBOARD = 3

class Player:
    def __init__(self, name, is_ai=False, difficulty=1):
        self.name = name
        self.score = 0
        self.is_ai = is_ai
        self.difficulty = difficulty
        self.paddle = pygame.Rect(0, WINDOW_HEIGHT//2 - PADDLE_HEIGHT//2, 
                                PADDLE_WIDTH, PADDLE_HEIGHT)

class AI:
    def __init__(self, difficulty):
        self.difficulty = difficulty
    
    def move(self, paddle, ball):
        prediction_error = (4 - self.difficulty) * 30
        target_y = ball.y + np.random.randint(-prediction_error, prediction_error)
        
        if paddle.centery < target_y:
            paddle.y += PADDLE_SPEED * (self.difficulty/2)
        elif paddle.centery > target_y:
            paddle.y -= PADDLE_SPEED * (self.difficulty/2)
        
        paddle.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

class Ball:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.rect = pygame.Rect(WINDOW_WIDTH//2 - BALL_SIZE//2,
                              WINDOW_HEIGHT//2 - BALL_SIZE//2,
                              BALL_SIZE, BALL_SIZE)
        self.dx = BALL_SPEED if np.random.random() > 0.5 else -BALL_SPEED
        self.dy = np.random.uniform(-BALL_SPEED, BALL_SPEED)

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        # Wall collisions
        if self.rect.top <= 0 or self.rect.bottom >= WINDOW_HEIGHT:
            self.dy *= -1

class PongGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("LOLLMS Pong Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.state = GameState.MENU
        self.load_leaderboard()
        
    def load_leaderboard(self):
        self.leaderboard = []
        if os.path.exists('leaderboard.json'):
            with open('leaderboard.json', 'r') as f:
                self.leaderboard = json.load(f)
    
    def save_leaderboard(self):
        with open('leaderboard.json', 'w') as f:
            json.dump(self.leaderboard, f)
    
    def update_leaderboard(self, player):
        self.leaderboard.append({"name": player.name, "score": player.score})
        self.leaderboard.sort(key=lambda x: x["score"], reverse=True)
        self.leaderboard = self.leaderboard[:10]  # Keep top 10
        self.save_leaderboard()

    def handle_menu(self):
        self.screen.fill(BLACK)
        title = self.font.render("LOLLMS PONG", True, WHITE)
        vs_ai = self.font.render("1. Play vs AI", True, WHITE)
        vs_player = self.font.render("2. Play vs Player", True, WHITE)
        show_leaderboard = self.font.render("3. Leaderboard", True, WHITE)
        quit_game = self.font.render("4. Quit", True, WHITE)
        
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
        self.screen.blit(vs_ai, (WINDOW_WIDTH//2 - vs_ai.get_width()//2, 250))
        self.screen.blit(vs_player, (WINDOW_WIDTH//2 - vs_player.get_width()//2, 300))
        self.screen.blit(show_leaderboard, (WINDOW_WIDTH//2 - show_leaderboard.get_width()//2, 350))
        self.screen.blit(quit_game, (WINDOW_WIDTH//2 - quit_game.get_width()//2, 400))
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if self.state == GameState.MENU:
                        if event.key == pygame.K_1:
                            self.start_ai_game()
                        elif event.key == pygame.K_2:
                            self.start_vs_game()
                        elif event.key == pygame.K_3:
                            self.state = GameState.LEADERBOARD
                        elif event.key == pygame.K_4:
                            running = False
                    
                    elif self.state == GameState.LEADERBOARD:
                        if event.key == pygame.K_ESCAPE:
                            self.state = GameState.MENU
            
            if self.state == GameState.MENU:
                self.handle_menu()
            elif self.state == GameState.GAME:
                self.handle_game()
            elif self.state == GameState.LEADERBOARD:
                self.show_leaderboard()
            
            self.clock.tick(60)
        
        pygame.quit()

    def start_ai_game(self):
        self.player1 = Player("Player 1")
        self.player2 = Player("AI", is_ai=True, difficulty=2)
        self.ball = Ball()
        self.ai = AI(self.player2.difficulty)
        self.state = GameState.GAME
        
        # Position paddles
        self.player1.paddle.x = 50
        self.player2.paddle.x = WINDOW_WIDTH - 50 - PADDLE_WIDTH

    def start_vs_game(self):
        self.player1 = Player("Player 1")
        self.player2 = Player("Player 2")
        self.ball = Ball()
        self.state = GameState.GAME
        
        # Position paddles
        self.player1.paddle.x = 50
        self.player2.paddle.x = WINDOW_WIDTH - 50 - PADDLE_WIDTH

    def handle_game(self):
        keys = pygame.key.get_pressed()
        
        # Player 1 controls
        if keys[pygame.K_w] and self.player1.paddle.top > 0:
            self.player1.paddle.y -= PADDLE_SPEED
        if keys[pygame.K_s] and self.player1.paddle.bottom < WINDOW_HEIGHT:
            self.player1.paddle.y += PADDLE_SPEED
        
        # Player 2 controls
        if self.player2.is_ai:
            self.ai.move(self.player2.paddle, self.ball.rect)
        else:
            if keys[pygame.K_UP] and self.player2.paddle.top > 0:
                self.player2.paddle.y -= PADDLE_SPEED
            if keys[pygame.K_DOWN] and self.player2.paddle.bottom < WINDOW_HEIGHT:
                self.player2.paddle.y += PADDLE_SPEED
        
        # Ball movement and collision
        self.ball.move()
        
        # Paddle collisions
        if self.ball.rect.colliderect(self.player1.paddle) or \
           self.ball.rect.colliderect(self.player2.paddle):
            self.ball.dx *= -1
        
        # Score points
        if self.ball.rect.left <= 0:
            self.player2.score += 1
            self.ball.reset()
        elif self.ball.rect.right >= WINDOW_WIDTH:
            self.player1.score += 1
            self.ball.reset()
        
        # Draw everything
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, self.player1.paddle)
        pygame.draw.rect(self.screen, WHITE, self.player2.paddle)
        pygame.draw.rect(self.screen, WHITE, self.ball.rect)
        
        # Draw scores
        score1 = self.font.render(str(self.player1.score), True, WHITE)
        score2 = self.font.render(str(self.player2.score), True, WHITE)
        self.screen.blit(score1, (WINDOW_WIDTH//4, 20))
        self.screen.blit(score2, (3*WINDOW_WIDTH//4, 20))
        
        pygame.display.flip()

    def show_leaderboard(self):
        self.screen.fill(BLACK)
        title = self.font.render("LEADERBOARD", True, WHITE)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 50))
        
        for i, entry in enumerate(self.leaderboard):
            text = self.font.render(f"{i+1}. {entry['name']}: {entry['score']}", True, WHITE)
            self.screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, 150 + i*40))
        
        back = self.font.render("Press ESC to return to menu", True, WHITE)
        self.screen.blit(back, (WINDOW_WIDTH//2 - back.get_width()//2, 500))
        
        pygame.display.flip()

def main():
    game = PongGame()
    game.run()

if __name__ == "__main__":
    main()