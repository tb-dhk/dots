# changelog

## [0.2.1] - 2024-11-14
### bugs fixed
- updated changelog
- further linted code

## [0.2.0] - 2024-11-12

### new features
- **habit management screen**: added a dedicated screen to manage habits with options to edit and delete habits.
- **three main habit types**:
  - **frequency**: tracking occurrences without a specific goal.
  - **duration**: tracking habits from start to end time.
  - **progress**: tracking occurrences with a set goal.
- **dynamic habit heatmaps**:
  - added weekly, monthly, and yearly heatmap intervals.
  - enhanced date handling for accurate display across intervals.
  - implemented helper functions to format data based on selected start and end dates.

### bugs fixed
- rewrote file imports for improved structure.
- rearranged `try/except` logic in `duration_maps()` for error handling.
- fixed minimum width logic in `draw_task_table()` for better layout.

### others
- **general code updates**:
  - renamed `draw_table` to `draw_task_table` for clarity.
  - moved shared methods to `misc.py` for better consistency across modules.
- **linting**:
  - fixed trailing whitespace.
  - removed unused arguments and resolved `redefined-outer-name` and `redefined-builtin` issues.
  - corrected `undefined-variable` and `unused-variable` errors.
  - simplified nested min-max expressions.
  - optimized code by using `dict.items()` and eliminated redundant `else` statements after `continue`.
- **renamed "journals" to "logs"**.
- moved `coming_soon()` function from `src/tasks.py` to `src/misc.py`.

---

## [0.1.1] - 2024-10-15

### bugs fixed
- added space character to allowed characters in the text box.

### others
- linted code for consistency and readability.
- updated `readme.md` to include a warning against modifying the config file.
- removed `dots.spec` file.

## [0.1.0] - 2024-10-13

### new features
- **list view (core view)**:
  - add new tasks with a title.
  - edit tasks:
    - update title.
    - adjust due date.
    - change priority.
    - toggle completed status.
    - move tasks.
    - modify tags/categories.
  - delete tasks.
  - support for nested tasks/subtasks.
- **day/week/month/year view**:
  - display tasks or goals for the current time period.
  - change the range of the current time period.
  - add, edit, and delete tasks within the selected time period.

