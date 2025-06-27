#!/usr/bin/env python3
"""
Game of Life cell management and Conway's rule implementation.

The universe of the Game of Life is an infinite two-dimensional orthogonal grid of square cells, 
each of which is in one of two possible states, alive or dead. Every cell interacts with its 
eight neighbours. At each step in time, the following transitions occur:

1. Any live cell with fewer than two live neighbours dies (underpopulation)
2. Any live cell with two or three live neighbours lives on to the next generation
3. Any live cell with more than three live neighbours dies (overpopulation)  
4. Any dead cell with exactly three live neighbours becomes a live cell (reproduction)
"""
from __future__ import annotations
from typing import Set, Tuple, Iterator
import glm


class Cells:
    """Collection of cells implementing Conway's Game of Life rules."""
    
    def __init__(self):
        self.alive_cells: Set[Tuple[int, int]] = set()
        
    def add_cell(self, x: int, y: int) -> None:
        """Add a living cell at the given coordinates."""
        self.alive_cells.add((x, y))
        
    def remove_cell(self, x: int, y: int) -> None:
        """Remove a cell (make it dead) at the given coordinates."""
        self.alive_cells.discard((x, y))
        
    def toggle_cell(self, x: int, y: int) -> bool:
        """Toggle cell state at coordinates. Returns new state (True=alive)."""
        pos = (x, y)
        if pos in self.alive_cells:
            self.alive_cells.remove(pos)
            return False
        else:
            self.alive_cells.add(pos)
            return True
            
    def toggle_cell_pos(self, grid_pos: glm.ivec2) -> bool:
        """Toggle cell state using glm vector. Returns new state (True=alive)."""
        return self.toggle_cell(grid_pos.x, grid_pos.y)
        
    def is_alive(self, x: int, y: int) -> bool:
        """Check if cell at coordinates is alive."""
        return (x, y) in self.alive_cells
        
    def is_alive_pos(self, grid_pos: glm.ivec2) -> bool:
        """Check if cell at glm vector position is alive."""
        return self.is_alive(grid_pos.x, grid_pos.y)
        
    def get_alive_count(self) -> int:
        """Get total number of alive cells."""
        return len(self.alive_cells)
        
    def clear(self) -> None:
        """Remove all living cells."""
        self.alive_cells.clear()
        
    def get_alive_cells(self) -> Set[Tuple[int, int]]:
        """Get set of all alive cell coordinates."""
        return self.alive_cells.copy()
        
    def get_neighbors(self, x: int, y: int) -> Iterator[Tuple[int, int]]:
        """Get all 8 neighbor coordinates for a cell."""
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:  # Don't include the cell itself
                    yield (x + dx, y + dy)
                    
    def count_live_neighbors(self, x: int, y: int) -> int:
        """Count how many living neighbors a cell has."""
        count = 0
        for neighbor_x, neighbor_y in self.get_neighbors(x, y):
            if (neighbor_x, neighbor_y) in self.alive_cells:
                count += 1
        return count
        
    def get_candidates_for_evaluation(self) -> Set[Tuple[int, int]]:
        """Get all cells that need to be evaluated (alive cells + their neighbors)."""
        candidates = set()
        
        # Add all alive cells
        for pos in self.alive_cells:
            candidates.add(pos)
            
        # Add all neighbors of alive cells
        for x, y in self.alive_cells:
            for neighbor_pos in self.get_neighbors(x, y):
                candidates.add(neighbor_pos)
                
        return candidates
        
    def apply_conway_rules(self) -> None:
        """Apply Conway's Game of Life rules to advance one generation."""
        # Get all cells that need evaluation
        candidates = self.get_candidates_for_evaluation()
        
        # Calculate neighbor counts for all candidates
        neighbor_counts = {}
        for x, y in candidates:
            neighbor_counts[(x, y)] = self.count_live_neighbors(x, y)
            
        # Apply Conway's rules to determine next generation
        new_alive_cells = set()
        
        for (x, y), neighbor_count in neighbor_counts.items():
            is_currently_alive = (x, y) in self.alive_cells
            
            if is_currently_alive:
                # Rules for living cells
                if neighbor_count == 2 or neighbor_count == 3:
                    # Survival: 2-3 neighbors
                    new_alive_cells.add((x, y))
                # Death: < 2 (underpopulation) or > 3 (overpopulation)
            else:
                # Rules for dead cells
                if neighbor_count == 3:
                    # Birth: exactly 3 neighbors
                    new_alive_cells.add((x, y))
                    
        # Update to new generation
        self.alive_cells = new_alive_cells
        
    def get_bounding_box(self) -> Tuple[int, int, int, int]:
        """Get bounding box of all alive cells (min_x, min_y, max_x, max_y)."""
        if not self.alive_cells:
            return (0, 0, 0, 0)
            
        xs = [x for x, y in self.alive_cells]
        ys = [y for x, y in self.alive_cells]
        
        return (min(xs), min(ys), max(xs), max(ys))
        
    def __len__(self) -> int:
        """Return number of alive cells."""
        return len(self.alive_cells)
        
    def __iter__(self) -> Iterator[Tuple[int, int]]:
        """Iterate over alive cell positions."""
        return iter(self.alive_cells)
        
    def __repr__(self) -> str:
        return f"Cells(alive_count={len(self.alive_cells)})"