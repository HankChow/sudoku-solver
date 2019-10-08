# sudoku-solver

### Introduction

A simple sudoku solver.

### Requirements

* Python 3.6+
* See _requirements.txt_

### Usage

Set a sudoku board in the main file with valid format, then run `python sudoku.py`.

### Additional tips

* The valid format of a board is `(\d{9}\,){8}\d{9}`, 0 will stand for a cell without any number.
* Three boolean arguments `show_board`, `show_remains` and `show_cost` can be specified in `Sudoku.solve()`. All of them is `True` by default.
  * `show_board`: Shows the board with a readable display. Colors are provided.
  * `show_remains`: Shows how many cells are still not completed after the calculation.
  * `show_cost`: Shows how long the calculation costs.
