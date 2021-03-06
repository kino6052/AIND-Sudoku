assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'


def cross(A, B):
    """Cross product of elements in A and elements in B."""
    return [a + b for a in A for b in B]


def zip_strings(A, B):
    """Zip to Strings Together"""
    return set(A[i] + B[i] for i in range(min(len(A), len(B))))

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
diagonal_units = [zip_strings(rows, cols), zip_strings(rows, cols[::-1])]  # List of Diagonal Units
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    for unit in unitlist:
        twin_dictionary = {}
        for box in unit:
            if len(values[box]) == 2:  # Look Only for Values of Length 2
                box_value = values[box]
                # Construct Twin Dictionary with Keys Being "value" ("12", "47", etc.) and Values being Array of Boxes (["A1", "A2"]) etc.
                if box_value in twin_dictionary.keys():
                    twin_dictionary[box_value].append(box)
                else:
                    twin_dictionary[box_value] = [box]
        # Eliminate the naked twins as possibilities for their peers
        values = remove_twins_from_unit(values, get_list_of_twins(twin_dictionary), unit)
    return values


def get_list_of_twins(twin_dictionary):
    return [key for key, value in twin_dictionary.items() if len(value) == 2]


def remove_twins_from_unit(values, twins, unit):
    for twin in twins:
        for box in unit:
            if values[box] != twin:  # Make Sure You Don't Remove Twin Values
                values[box] = values[box].replace(twin[0], "").replace(twin[1], "")
    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    """
        Display the values as a 2-D grid.
        Input: The sudoku in dictionary form
        Output: None
        """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for row in rows:
        print(''.join(values[row + col].center(width) + ('|' if col in '36' else '')
                      for col in cols))
        if row in 'CF':
            print(line)
    print


def eliminate(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]: # Peers Not Including Diagonal Boxes
            values[peer] = values[peer].replace(digit, '')
    return values


def eliminate_diagonals(values):
    for diagonal_unit in diagonal_units:  # Solve for Both Diagonals
        solved_values = [box for box in diagonal_unit if len(values[box]) == 1]  # Solved Values for Diagonals
        for box in solved_values:
            digit = values[box]
            for peer in diagonal_unit:
                if len(values[peer]) > 1:  # Shouldn't Modify the Original Value
                    values[peer] = values[peer].replace(digit, '')
    return values


def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values = assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate_diagonals(values)
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for c in values[s]:
        new_values = values.copy()
        new_values[s] = c
        attempt = search(new_values)
        if attempt:
            return attempt

def is_sudoku_correct(values):
    for unitBox in units:
        for unit in units[unitBox]:
            numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
            for box in unit:
                numbers.remove(values[box])
    for diagonal in diagonal_units:
        numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        for box in diagonal:
            numbers.remove(values[box])
    return True

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')