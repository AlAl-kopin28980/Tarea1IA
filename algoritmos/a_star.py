ROW = 9
COL = 10
## código a continuación fue sacado de geeksforgeeks: https://www.geeksforgeeks.org/python/a-search-algorithm-in-python/
import heapq

class Cell:
    def __init__(self):
        self.parent_i = -1
        self.parent_j = -1
        self.f = float('inf')
        self.g = float('inf')
        self.h = 0

def is_valid(row, col):
    return 0 <= row < ROW and 0 <= col < COL

def is_unblocked(grid, row, col):
    return grid[row][col] == 1

def is_destination(row, col, dest):
    return row == dest[0] and col == dest[1]

def calculate_h_value(row, col, dest):
    return ((row - dest[0]) ** 2 + (col - dest[1]) ** 2) ** 0.5

def trace_path(cell_details,src, dest):
    path = []
    curr_row, curr_col = dest

    # Backtrack until reaching the source cell
    while not (curr_row == src[0] and curr_col == src[1]):
        path.append((curr_row, curr_col))
        temp_row = cell_details[curr_row][curr_col].parent_i
        temp_col = cell_details[curr_row][curr_col].parent_j
        curr_row, curr_col = temp_row, temp_col

    path.append(src)
    path.reverse()

    print("The Path is:")
    for cell in path:
        print("->", cell, end=" ")
    print()

def a_star_search(grid, src, dest):

    if not is_valid(src[0], src[1]) or not is_valid(dest[0], dest[1]):
        print("Source or destination is invalid")
        return

    if not is_unblocked(grid, src[0], src[1]) or not is_unblocked(grid, dest[0], dest[1]):
        print("Source or destination is blocked")
        return

    if is_destination(src[0], src[1], dest):
        print("We are already at the destination")
        return

    closed_list = [[False for _ in range(COL)] for _ in range(ROW)]
    cell_details = [[Cell() for _ in range(COL)] for _ in range(ROW)]

    i, j = src

    cell_details[i][j].f = 0
    cell_details[i][j].g = 0
    cell_details[i][j].h = 0
    cell_details[i][j].parent_i = i
    cell_details[i][j].parent_j = j

    open_list = []
    heapq.heappush(open_list, (0.0, i, j))

    directions = [
        (0, 1), (0, -1), (1, 0), (-1, 0),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]

    while open_list:
        _, i, j = heapq.heappop(open_list)

        if closed_list[i][j]:
            continue

        closed_list[i][j] = True

        for di, dj in directions:
            new_i = i + di
            new_j = j + dj

            if not is_valid(new_i, new_j):
                continue

            if not is_unblocked(grid, new_i, new_j):
                continue

            if closed_list[new_i][new_j]:
                continue
            if is_destination(new_i, new_j, dest):
                cell_details[new_i][new_j].parent_i = i
                cell_details[new_i][new_j].parent_j = j

                print("The destination cell is found")
                trace_path(cell_details,src, dest)
                return

            g_new = cell_details[i][j].g + 1.0
            h_new = calculate_h_value(new_i, new_j, dest)
            f_new = g_new + h_new

            if cell_details[new_i][new_j].f > f_new:
                cell_details[new_i][new_j].f = f_new
                cell_details[new_i][new_j].g = g_new
                cell_details[new_i][new_j].h = h_new

                cell_details[new_i][new_j].parent_i = i
                cell_details[new_i][new_j].parent_j = j

                heapq.heappush(
                    open_list,
                    (f_new, new_i, new_j)
                )

    print("Failed to find the destination cell")