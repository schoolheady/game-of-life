"""
Game of Life cell management and Conway's rule implementation.
"""
from __future__ import annotations
from typing import Set, Tuple, Iterator
import glm


class CellPopulation:
    
    def __init__(self):
        self.living_cells: Set[Tuple[int, int]] = set()
        
    def add_cell(self, x: int, y: int) -> None:
        self.living_cells.add((x, y))
        
    def remove_cell(self, x: int, y: int) -> None:
        self.living_cells.discard((x, y))
        
    def toggle_cell(self, x: int, y: int) -> bool:
        # Returns True if cell is now alive
        pos = (x, y)
        if pos in self.living_cells:
            self.living_cells.remove(pos)
            return False
        else:
            self.living_cells.add(pos)
            return True
            
    def toggle_cell_at(self, grid_pos: glm.ivec2) -> bool:
        return self.toggle_cell(grid_pos.x, grid_pos.y)
        
    def is_alive(self, x: int, y: int) -> bool:
        return (x, y) in self.living_cells
        
    def is_alive_at(self, grid_pos: glm.ivec2) -> bool:
        return self.is_alive(grid_pos.x, grid_pos.y)
        
    def count(self) -> int:
        return len(self.living_cells)
        
    def clear(self) -> None:
        self.living_cells.clear()
        
    def get_positions(self) -> Set[Tuple[int, int]]:
        return self.living_cells.copy()
        
    def get_neighbors(self, center_x: int, center_y: int) -> Iterator[Tuple[int, int]]:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:  # Exclude center cell
                    yield (center_x + dx, center_y + dy)
                    
    def count_neighbors(self, x: int, y: int) -> int:
        count = 0
        for nx, ny in self.get_neighbors(x, y):
            if (nx, ny) in self.living_cells:
                count += 1
        return count
        
    def get_evaluation_candidates(self) -> Set[Tuple[int, int]]:
        # All living cells + their neighbors need evaluation
        candidates = set()
        
        for pos in self.living_cells:
            candidates.add(pos)
            
        for x, y in self.living_cells:
            for neighbor in self.get_neighbors(x, y):
                candidates.add(neighbor)
                
        return candidates
        
    def evolve(self) -> None:
        # Get all cells that need evaluation
        candidates = self.get_evaluation_candidates()
        
        # Calculate neighbor counts
        neighbor_counts = {}
        for x, y in candidates:
            neighbor_counts[(x, y)] = self.count_neighbors(x, y)
            
        # Apply Conway's rules
        new_living = set()
        
        for (x, y), neighbors in neighbor_counts.items():
            is_alive = (x, y) in self.living_cells
            
            if is_alive:
                # Survival: 2-3 neighbors
                if neighbors == 2 or neighbors == 3:
                    new_living.add((x, y))
            else:
                # Birth: exactly 3 neighbors
                if neighbors == 3:
                    new_living.add((x, y))
                    
        self.living_cells = new_living
        
    def get_bounds(self) -> Tuple[int, int, int, int]:
        # Returns (min_x, min_y, max_x, max_y)
        if not self.living_cells:
            return (0, 0, 0, 0)
            
        xs = [x for x, y in self.living_cells]
        ys = [y for x, y in self.living_cells]
        
        return (min(xs), min(ys), max(xs), max(ys))
        
    def __len__(self) -> int:
        return len(self.living_cells)
        
    def __iter__(self) -> Iterator[Tuple[int, int]]:
        return iter(self.living_cells)
        
    def __repr__(self) -> str:
        return f"CellPopulation(count={len(self.living_cells)})"