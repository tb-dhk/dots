# dots
**dots** is a bullet-journal based productivity TUI app. it is partly based on my previous project [habitmap](https://github.com/tb-dhk/habitmap), a habit tracker CLI.

dots incorporates the four main types of bullet journal spreads:
- tasks (inspired by rapid logging)
- lists (inspired by collections)
- habits (based on [habitmap](https://github.com/tb-dhk/habitmap))
- journals (such as daily reflections, mood logs, etc.)

only tasks are implemented at the moment, but i plan to add the other components in the near future.

## installation
```
git clone https://github.com/tb-dhk/dots
cd dots
make build && make install
```

## usage
to run the app, simply run the following command:

```
dots
```
options:
- `-n` or `--no-home-screen`: start dots without the home screen

## keybindings

### arrows 
the arrow keys can be used to move up, down, left or right. these apply to navbars as well as the main screen.

the up and down keys are used to
- navigate between rows (tasks) on the main screen, 
- navigate the main screen and the navbar, as well as other options, and
- move the cursor to the extreme left and extreme right respectively (in the text input field).

the left and right keys are used to 
- navigate between options on the navbar,
- navigate between columns (in non-list task views) on the main screen,
- change the date (in non-list task views), and
- move the cursor to the left and the right respectively (in the text input field).

### list task view keybindings
do note that these keybindings require your cursor to be on a task (with the exception of `:`, which still requires you to be on the main screen).
- `:`: add a new task (navigate to the input field)

#### quick task keybindings
these are available in all task views.
- `x`: toggle completion status
- `.`: schedule a task for today
- `1`, `2`, `3`: set priority to low, normal, or high (respectively)
- `r`: remove/delete the task (press again to confirm)
- `Esc`: cancel the removal of a task or exit input field

#### task editing keybindings
all of these keybindings require text input and are only available in list view.
- `<`, `>`: migrate or schedule (do note that both of these refer to changing or setting the due date and the difference in recommendation is purely symbolic)
- `t`: edit tags
- `m`: move the task to another parent (or orphan the task)
- `Enter`: save changes and exit input field

#### non-list task view keybindings
- `v`: view the task in list view
- `e`: edit the task (navigates to the input field, edits the attribute that the cursor is on. cannot be used to move tasks)
- `d`: navigates to another date if cursor is on the date (if not on day view, navigates to relevant week, month or year)

## configuration
configuration is not yet available, but there is a `config.toml` file in the `~/.dots` directory that you can edit manually. the file is created when you run the app for the first time.
