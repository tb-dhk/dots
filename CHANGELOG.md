# changelog

## [0.2.0] - 2024-12-14

### new features:
- habit management:  
  - introduced a dedicated screen to manage habits with options to edit and delete.  
  - supported three main habit types:  
    - frequency: doing something x times without a set goal.  
    - duration: tracking time from start to end.  
    - progress: completing tasks x times towards a goal.  
  - dynamic habit heatmaps with weekly, monthly, and yearly intervals.  
    - enhanced date handling for accurate display.  
    - added helper functions to format data based on selected intervals.  

- task management:  
  - hiding completed tasks: toggle via the “h” keybinding for completed tasks and subtasks.  
  - improved task table formatting:  
    - added autosorting (completed tasks first, then by due date).  
    - styled completed tasks in non-list views.  

- installation flexibility:  
  - integrated gum for enhanced user prompts and selection during installation.  
  - introduced the `use_gum=false` option for non-gum installations, with updated scripts and comprehensive instructions.  

### improvements:
- navigation views:  
  - unified `week`, `month`, and `year` views into a single function for better maintainability.  
  - addressed navigation bugs and fixed truncation issues in duration maps.  

- code structure:  
  - refactored and modularized major components:  
    - moved content-related functions to `content.py`.  
    - consolidated class definitions in `modules.py`.  
    - isolated utility functions (e.g., `init_color()` and navbar rendering) in `misc.py`.  
  - renamed `journals` to `logs` for clarity.  
  - reduced line lengths for readability.  

- habit management improvements:  
  - sorted records by date in habit-based mode.  
  - resolved crashes in the edit menu.  
  - fixed table border issues for habits.  

- performance enhancements:  
  - increased frame rate from 10 fps to 50 fps.  
  - optimized sorting and rendering logic for tasks.  

### bug fixes:  
- fixed screen flickering issue.  
- fixed navigation and overflow issues in task tables and list views.  
- improved exception handling for stability (e.g., `addwstr` exceptions).  
- fixed message priorities to address format prompts first.  
- fixed "." keybinding functionality: toggling due dates to/from "today".  

### other changes:  
- enhanced table borders for better aesthetics.  
- added descriptions for all functions for improved documentation.  
- updated README.md and added new gifs.  
- reworked GitHub workflows: fixed artifact uploads and integrated new steps.  
- cleaned up repository by removing `dist/` from `.gitignore`.  

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

