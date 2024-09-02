from tkinter import Tk, BOTH, Canvas
from typing import Self
from time import sleep
import random

class Point:
    def __init__(self, x: int = 0 , y: int  = 0) -> None:
        self.x = x    
        self.y = y

class Line:
    def __init__(self,p1: Point, p2: Point) -> None:
        self.p1 = p1
        self.p2 = p2

    def draw(self, canvas: Canvas, fill_color: str = 'black'):
        canvas.create_line(self.p1.x, self.p1.y, self.p2.x, self.p2.y, fill=fill_color, width=2)




class Window:
    def __init__(self, width: int = 600, height: int= 400, title: str ='Maze Solver'):
        self.__root = Tk()
        self.__root.title(title)
        self.__root.maxsize(width, height )
        self.__root.minsize(width, height)
        self.bg = self.__root.cget('bg')
        self.__canvas =  Canvas(self.__root,height=height, width=width, bg=self.bg)
        self.__canvas.pack(fill=BOTH, expand=1)
        self.__running = False
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):

        self.__running = True
        while(self.__running):
            self.redraw()

    def close(self):
        self.__running = False

    def draw_line(self, line: Line, fill_color: str = 'black'):
        line.draw(self.__canvas, fill_color)


class Cell:
    def __init__(self, win: Window | None) -> None:
        self._x1: int
        self._y1: int
        self._x2: int 
        self._y2: int 
        self.has_left_wall   : bool = True
        self.has_right_wall  : bool = True
        self.has_top_wall    : bool = True
        self.has_bottom_wall : bool = True
        self._win = win
        self.visited: bool = False

    def draw(self, x1, y1, x2, y2):
        self._x1: int = x1  
        self._y1: int = y1 
        self._x2: int = x2  
        self._y2: int = y2  

        self._center = Point((x1+x2)/2, (y1+y2)/2)


        if self._win :
            color = 'black' if self.has_left_wall else self._win.bg 
            line = Line(Point(x1,y1), Point(x1,y2))
            self._win.draw_line(line, color)

        if self._win:
            color = 'black' if self.has_top_wall else self._win.bg
            line = Line(Point(x1,y1), Point(x2,y1))
            self._win.draw_line(line, color)

        if self._win:
            color = 'black' if self.has_right_wall else self._win.bg
            line = Line(Point(x2,y1), Point(x2,y2))
            self._win.draw_line(line, color)

        if self._win:
            color = 'black' if self.has_bottom_wall else self._win.bg
            line = Line(Point(x1,y2), Point(x2,y2))
            self._win.draw_line(line, color)

    def draw_move(self, to_cell: Self, undo: bool = False):
        if self._win:
            color = self._win.bg if undo else 'red'
            line = Line(self._center, to_cell._center)
            self._win.draw_line(line, color)


class Maze:

    def __init__( self, x1, y1, num_rows, num_cols, cell_size_x, cell_size_y, win = None,
                 seed = None) :
        self._x1: int = x1
        self._y1: int = y1
        self._num_rows: int = num_rows
        self._num_cols: int = num_cols
        self._cell_size_x: int = cell_size_x
        self._cell_size_y: int = cell_size_y
        self._win: Window | None = win 
        if seed:
            random.seed(seed)

        self._create_cells()
        self._break_entrance_and_exit()
        self._break_wall_r(0,0)
        self._reset_cell_visited()    

    def _create_cells(self):
        self._cells: list[list[Cell]] = []
        for _ in range(self._num_cols):
            self._cells.append([Cell(self._win) for _ in range(self._num_rows) ])

        for i in range(self._num_cols):
            for j in range(self._num_rows):
                self._draw_cell(i,j)

    def _draw_cell(self, i:int ,j: int) -> None:
        cell = self._cells[i][j]
        x1 = self._x1 + i * self._cell_size_x 
        y1 = self._y1 + j * self._cell_size_y 
        x2 = x1 + self._cell_size_x
        y2 = y1 + self._cell_size_y
        if isinstance(self._win, Window):
            cell.draw(x1,y1,x2,y2)
            self._animate()

    def _break_entrance_and_exit(self):
        top_left = self._cells[0][0]
        top_left.has_top_wall = False
        self._draw_cell(0,0)
        botoom_right= self._cells[-1][-1]
        botoom_right.has_bottom_wall = False
        self._draw_cell(self._num_cols-1, self._num_rows-1)
            

    def _animate(self):
        if self._win:
            self._win.redraw()
            sleep(0.025)

    def _reset_cell_visited(self):    
        for col in self._cells:
            for c in col:
                c.visited = False


    def _break_wall_r(self, i, j):
        cur: Cell = self._cells[i][j]
        cur.visited = True

        while True:
            need_visited: list[tuple[int, int]]  = []

            # left
            if i-1 >= 0 and not self._cells[i-1][j].visited:
                need_visited.append((i-1, j))
            #right
            if i+1 < self._num_cols  and not self._cells[i+1][j].visited:
                need_visited.append((i+1, j))
            # above 
            if j-1 >= 0 and not self._cells[i][j-1].visited:
                need_visited.append((i, j-1))
            #below 
            if j+1 < self._num_rows  and not self._cells[i][j+1].visited:
                need_visited.append((i,j+1))

            if len(need_visited) == 0:
                self._draw_cell(i,j)
                return
            
            rindex =random.randrange(len(need_visited))
            dx  = need_visited[rindex]

            nx = dx[0]
            ny = dx[1]

            if nx == i -1:
                self._cells[i][j].has_left_wall = False
                self._cells[i-1][j].has_right_wall =  False
            elif nx == i + 1:
                self._cells[i][j].has_right_wall = False
                self._cells[i + 1][j].has_left_wall =  False
            elif ny == j + 1:
                self._cells[i][j].has_bottom_wall = False
                self._cells[i][j+1].has_top_wall =  False
        
            elif ny == j - 1:
                self._cells[i][j].has_top_wall= False
                self._cells[i][j-1].has_botoom_wall = False

            self._break_wall_r(nx, ny)
    
    def solve(self):
        return self._solve_r(0,0)
    
    def _solve_r(self, i: int, j: int):
        self._animate()    
        self._cells[i][j].visited = True 
        if i+1 == self._num_cols and j+1 == self._num_rows:
            return True
      
        cur =  self._cells[i][j]
        right= self._cells[i+1][j] if i+1 < self._num_cols else None
        down = self._cells[i][j+1] if j+1 < self._num_rows else None 
        left = self._cells[i-1][j] if i-1 >= 0 else  None
        up   = self._cells[i][j-1] if j-1 >= 0 else None

        if not cur.has_right_wall and right and  not right.visited:
            cur.draw_move(right)
            if self._solve_r(i+1, j):
                return True
            else:
                cur.draw_move(right,True)
        
        if not cur.has_bottom_wall and down and  not down.visited:
            cur.draw_move(down)
            if self._solve_r(i, j+1):
                return True
            else:
                cur.draw_move(down, True) 

        if not cur.has_left_wall and left and  not left.visited:
            cur.draw_move(left)
            if self._solve_r(i-1, j):
                return True
            else:
                cur.draw_move(left,True)

        
        if not cur.has_top_wall and up and  not up.visited:
            cur.draw_move(up)
            if self._solve_r(i, j-1):
                return True
            else:
                cur.draw_move(up,True)

        return False
        
            




          
            
            


            
            
            
        



        




def main():
    win = Window(820,820)
    maze = Maze(10,10,40,40,20,20, win)
    maze.solve()

    win.wait_for_close()


if __name__ == "__main__":
    main()
