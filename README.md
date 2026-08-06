# Turtle Shooter Fix for GitHub Codespaces

## Why this broke in Codespaces

GitHub Codespaces runs in a container without a graphical desktop environment. Python's `turtle` module depends on Tkinter, which requires an X11/Wayland display server and the `$DISPLAY` environment variable. In Codespaces, that display is not available, so `turtle.Screen()` raises:

```
_tkinter.TclError: no display name and no $DISPLAY environment variable
```

That is the root cause, not a bug in the game logic.

## What changed

1. Renamed `import turtle.py` to `turtle_shooter.py`.
   - This avoids shadowing Python's built-in `turtle` module.
2. Kept the original Turtle game for local desktop use.
3. Added a browser-safe HTML5 Canvas version with `index.html` and `game.js`.
   - This version runs in Codespaces without `DISPLAY` or Tkinter.
4. Added a `.vscode/launch.json` file with optional local launch configurations.
5. Improved the Python script with a `__main__` guard and a clear display-error message.

## How to run in Codespaces

Open `index.html` in a browser. If your Codespaces environment has a Live Server or HTML preview extension, use that to load the page.

## How to run locally on Windows/Mac

1. Install Python 3.
2. Open a terminal in the repository folder.
3. Run:

```bash
python turtle_shooter.py
```

This local run works because Windows and macOS provide a graphical display for Tkinter.

## Files

- `turtle_shooter.py` — local Python Turtle version
- `index.html` — browser-based HTML5 Canvas version
- `game.js` — browser game logic
- `.vscode/launch.json` — optional launch configurations
