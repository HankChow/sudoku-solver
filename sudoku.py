# author: Hank

import re
import time
import click


class Cell(object):

    def __init__(self, row, col, value):
        self._row = row
        self._col = col
        self._value = value
        self._block = self._row // 3 * 3 + self._col // 3
        self._original = False
        self._possibles = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def get_attr(self, attr):
        if attr == "row":
            return self._row
        if attr == "col":
            return self._col
        if attr == "block":
            return self._block
        if attr == "value":
            return self._value

    def get_row(self):
        return self._row

    def get_col(self):
        return self._col

    def get_block(self):
        return self._block

    def get_value(self):
        return self._value

    def is_original(self):
        return self._original

    def get_possibles(self):
        return self._possibles

    def set_value(self, value):
        self._value = value

    def set_original(self):
        self._original = True

    def remove_possibles(self, possibles):
        for p in possibles:
            if p in self._possibles:
                self._possibles.remove(p)

    def clear_possibles(self):
        self.remove_possibles([1, 2, 3, 4, 5, 6, 7, 8, 9])


class Board(object):

    def __init__(self, board_numbers):
        # initial
        self.cells = {(row, col): Cell(row, col, 0) for row in range(9) for col in range(9)}
        if not re.match("(\d{9}\,){8}\d{9}", board_numbers):
            print("Invalid board numbers.")
            exit()
        # put original numbers
        for index_row, row in enumerate(board_numbers.split(",")):
            for index_col, col in enumerate(row):
                if int(col):
                    self.cells[(index_row, index_col)].set_value(int(col))
                    self.cells[(index_row, index_col)].set_original()
                    self.cells[(index_row, index_col)].clear_possibles()
                    self.remove_possibles((index_row, index_col))

    def show(self):
        for row in range(9):
            if row > 0 and row % 3 == 0:
                click.secho("------+-------+------")
            for col in range(9):
                cell = self.cells[(row, col)]
                cell_value = cell.get_value()
                cell_original = cell.is_original()
                click.secho(str(cell_value) if cell_value else " ", 
                    nl=False, 
                    fg="white" if cell_original else "blue",
                    bold=not cell_original
                )
                click.secho(" | " if col % 3 == 2 and col != 8 else " ", nl=False)
            click.secho()

    def show_possibles(self):
        for row in range(9):
            for col in range(9):
                print(row, col, self.cells[(row, col)].get_possibles())        

    def get_remains(self):
        return len([self.cells[(row, col)] for row in range(9) for col in range(9) if self.cells[(row, col)].get_value() == 0])

    def dump_board(self):
        dump = ""
        for row in range(9):
            for col in range(9):
                dump += str(self.cells[(row, col)].get_value())
            if row != 8:
                dump += ","
        return dump

    def check_board(self):
        # if a row/col/block has two numbers in same, it's an incorrect board
        for unit in ["row", "col", "block"]:
            for unit_num in range(9):
                values = [cell.get_value() for key, cell in self.cells.items() if cell.get_attr(unit) == unit_num and cell.get_value() != 0]
                if len(values) > len(set(values)):
                    return False
        # if a certain cell has neither value nor possibles, it's an incorrect board
        for row in range(9):
            for col in range(9):
                if self.cells[(row, col)].get_value() == 0 and self.cells[(row, col)].get_possibles == []:
                    return False
        # if a certain number cannot be filled into any cell in a row/col/block, it's an incorrect board
        for unit in ["row", "col", "block"]:
            for unit_num in range(9):
                values = []
                possibles = []
                for key, cell in self.cells.items():
                    if cell.get_attr(unit) == unit_num:
                        if cell.get_value() != 0:
                            values.append(cell.get_value())
                        else:
                            possibles.extend(cell.get_possibles())
                for num in range(1, 10):
                    if (num not in values) and (num not in possibles):
                        return False
        return True

    def get_least_possible_cells(self):
        return sorted([cell for key, cell in self.cells.items() if cell.get_value() == 0], key=lambda cell: len(cell.get_possibles()))

    def remove_possibles(self, coordinate):
        if self.cells[coordinate].get_value() == 0:
            return None
        c = self.cells[coordinate]
        for key, cell in self.cells.items():
            if cell.get_row() == c.get_row() or cell.get_col() == c.get_col() or cell.get_block() == c.get_block():
                self.cells[(cell.get_row(), cell.get_col())].remove_possibles([c.get_value()])

    def set_cell(self, coordinate, value):
        self.cells[coordinate].set_value(value)
        self.cells[coordinate].clear_possibles()
        self.remove_possibles(coordinate)

    # set the value of a cell if there is only one possible number for the cell
    def put_only_one_possible(self, coordinate):
        cell = self.cells[coordinate]
        if cell.get_value() == 0 and len(cell.get_possibles()) == 1:
            self.set_cell(coordinate, cell.get_possibles()[0])

    def all_put_only_one_possible(self):
        remains = self.get_remains()
        while True:
            for row in range(9):
                for col in range(9):
                    self.put_only_one_possible((row, col))
            if (remains == 0) or (remains == self.get_remains()):
                return remains
            else:
                remains = self.get_remains()

    # set the value of a cell only one cell of a row/col/block has a certain number in its possibles
    def put_only_one_cell(self, unit, unit_number):
        if unit not in ["row", "col", "block"]:
            return None
        unit_cells = [cell for key, cell in self.cells.items() if cell.get_attr(unit) == unit_number]
        for num in range(1, 10):
            cell = [c for c in unit_cells if num in c.get_possibles()]
            if len(cell) == 1:
                self.set_cell((cell[0].get_row(), cell[0].get_col()), num)

    def all_put_only_one_cell(self):
        remains = self.get_remains()
        while True:
            for unit in ["row", "col", "block"]:
                for unit_number in range(9):
                    self.put_only_one_cell(unit, unit_number)
            if (remains == 0) or (remains == self.get_remains()):
                return remains
            else:
                remains = self.get_remains()

    def run(self):
        methods = [self.all_put_only_one_possible, self.all_put_only_one_cell]
        remains = self.get_remains()
        while True:
            for method in methods:
                remains = method()
                if remains == 0:
                    return None
            for method in methods[::-1]:
                remains = method()
            if (remains == 0) or (remains == self.get_remains()):
                break


class Sudoku(object):

    def __init__(self, board_numbers):
        self.main_board = Board(board_numbers)
        self.original_board = board_numbers
        self.original_remains = self.original_board.count("0")

    def attempt(self, i=0):
        main_board = self.main_board.dump_board()
        print(len(self.main_board.get_least_possible_cells()))
        attempt_cell = self.main_board.get_least_possible_cells()[i]
        print("Attempting {coordinate} in {possible}...".format(
            coordinate=(attempt_cell.get_row(), attempt_cell.get_col()),
            possible=attempt_cell.get_possibles()
        ))
        copies = [Board(main_board) for _ in attempt_cell.get_possibles()]
        for index, possible in enumerate(attempt_cell.get_possibles()):
            copies[index].set_cell((attempt_cell.get_row(), attempt_cell.get_col()), possible)
            copies[index].run()
        for index, cp in enumerate(copies):
            if cp.check_board():
                return {
                    "coordinate": (attempt_cell.get_row(), attempt_cell.get_col()),
                    "possible": attempt_cell.get_possibles()[index]
                }

    def solve(self, show_board=True, show_remains=True, show_cost=True):
        start_time = time.clock()
        self.main_board.run()
        if self.main_board.get_remains() == 0:
            if show_board:
                self.main_board.show()
        else:
            for i in range(len(self.main_board.get_least_possible_cells())):
                attempt_result = self.attempt(i)
                if attempt_result:
                    self.main_board.set_cell(attempt_result["coordinate"], attempt_result["possible"])
                    self.main_board.run()
                    if self.main_board.get_remains() == 0:
                        if show_board:
                            self.main_board.show()
                        break
            else:
                if show_board:
                    self.main_board.show()
        end_time = time.clock()
        if show_remains:
            print("Remain: {origin} -> {remain}".format(
                origin=self.original_remains,
                remain=self.main_board.get_remains(),
            ))
        if show_cost:
            print("Cost: {cost}s".format(
                cost=round(end_time-start_time, 3)
            ))
        return {
            "board": self.main_board.dump_board(),
            "original_board": self.original_board,
            "original_remains": self.original_remains,
            "remains": self.main_board.get_remains(),
            "cost": round(end_time - start_time, 3)
        }


if __name__ == "__main__":
    board = ""
    s = Sudoku(board)
    s.solve(show_board=False)
