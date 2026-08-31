import os
import sys
from game.app import GameApp

if __name__ == '__main__':
    os.makedirs('assets', exist_ok=True)
    app = GameApp()
    app.run()
    sys.exit(0)
