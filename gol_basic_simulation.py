def start_sim(height, width, steps):
    grid = [[0 for _ in range(width)] for _ in range(height)]
    grid_seed(grid, 10,10)
    print_grid(grid)
    for i in range(steps):
        print("step: ", i)
        update(grid)
        print_grid(grid)

def update(grid):
    update_grid = [[0 for _ in range(len(grid[0]))] for _ in range(len(grid))]
    neighbours = [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            counter = 0
            for neighbour in neighbours:
                if (0<=j+neighbour[1]<=len(grid)-1) and (0<=i+neighbour[0]<=len(grid[j])-1):
                    if(grid[i+neighbour[0]][j+neighbour[1]])==1:
                        counter+=1

            if grid[i][j]==1:
                if counter<2:
                    update_grid[i][j] = -1
                elif 3<counter:
                    update_grid[i][j] = -1

            elif grid[i][j]==0:
                if counter==3:
                    update_grid[i][j] = 1
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            grid[i][j]+=update_grid[i][j]

def print_grid(grid):
    output=""
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j]==1:
                output+="■"
            else:
                output+="□"
        output += "\n"
    print(output)

def grid_seed(grid,x,y):
    f = open("hammerhead.txt")
    pattern = f.read().splitlines()

    if len(grid)<len(pattern)+x or len(grid[0])<len(pattern[0])+y:
        print("Couldn't load chosen seed. Please increase grid size.")
    else:
        for i in range(len(pattern)):
            for j in range(len(pattern[i])):
                if pattern[i][j]=='1':
                    grid[x][y+j]=1
                else:
                    grid[x][y+j]=0
            x+=1

if __name__ == '__main__':
    start_sim(42, 42, 10)
    start_sim(42, 42, 10)

