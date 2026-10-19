def start_sim(height, width, steps):
    grid = [[0 for _ in range(width)] for _ in range(height)]
    grid_seed(grid, 3,3)
    print_grid(grid)
    for i in range(steps):
        print("step: ",i)
        update(grid)
        print_grid(grid)

def update(grid):
    updateGrid = [[0 for _ in range(len(grid[0]))] for _ in range(len(grid))]
    neighbours = [(-1, 0), (1, 0), (0, -1), (0, 1), (1,1), (-1,1), (1,-1),(-1,-1)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            counter = 0
            for neighbour in neighbours:
                if (0<=j+neighbour[1]<=len(grid)-1) and (0<=i+neighbour[0]<=len(grid[j])-1):
                    if(grid[i+neighbour[0]][j+neighbour[1]])==1:
                        counter+=1

            if grid[i][j]==1:
                if counter<2:
                    updateGrid[i][j] = -1
                elif 3<counter:
                    updateGrid[i][j] = -1

            elif grid[i][j]==0:
                if counter==3:
                    updateGrid[i][j] = 1
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            grid[i][j]+=updateGrid[i][j]

def print_grid(grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j]==1:
                print("■",end="")
            else:
                print("□",end="")
        print("")

def grid_seed(grid,x,y):
    cloverleaf = [  "000101000",
                    "011101110",
                    "100010001",
                    "101000101",
                    "011010110",
                    "000000000",
                    "011010110",
                    "101000101",
                    "100010001",
                    "011101110",
                    "000101000"]

    for i in range(len(cloverleaf)):
        for j in range(len(cloverleaf[i])):
            if cloverleaf[i][j]=='1':
                grid[x][y+j]=1
            else:
                grid[x][y+j]=0
        x+=1





if __name__ == '__main__':
    start_sim(32, 32, 10)
