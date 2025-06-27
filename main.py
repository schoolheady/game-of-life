#!/usr/bin/env python3
"""
Conway's Game of Life - Interactive Implementation

A modular, maintainable implementation of Conway's Game of Life using:
- OpenGL for efficient rendering with unified grid/cell shaders
- Pygame for window management and input handling
- Perfect mouse-to-grid alignment with interactive cell placement
- Eye-friendly dark color scheme with adaptive grid padding
- State machine supporting interactive editing in all states

This is the legacy entry point that delegates to the new modular app.
For the main application class, see app.py.
"""

from app import main

if __name__ == "__main__":
    main()
