import cells as c
class GameOfLife:
    def __init__(self):
        self.living_cells = set()  # Set to store living cells as tuples (x, y)


    def add_cell(self, x, y):
        """Add a cell at position (x, y) to the living cells."""
        cell_id = 0
        cell = c.Cell(x,y,cell_id)
        
        cell_id = cell_id + 1
        
        self.living_cells.add(cell)
    
    def kill_cell(self, cell_id):
        #     # Find a cell with the given ID
        # for cell in self.living_cells:
        #     if cell.get_id() == cell_id:
            
        #         self.living_cells.remove(cell)
        #         break
            
