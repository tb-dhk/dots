from tasks import (
    display_tasks,
    day_view, week_view, month_view, year_view
)

from habits import (
    duration_maps, progress_maps,
    heatmaps,
    manage_habits, add_new_habit
)

from misc import (
    display_text_box, coming_soon
)

def content(
    window,
    outer_option, inner_option,
    selected,
    text_input, text_mode, text_box, text_index,
    removing, day,
    map_settings, new_habit,
    hide_completed
):
    """generate content window."""
    if outer_option == 0:
        if inner_option == 0:
            display_tasks(window, selected, text_mode, removing, hide_completed)
        elif inner_option == 1:
            day_view(window, selected, day, removing, hide_completed)
        elif inner_option == 2:
            week_view(window, selected, day, removing, hide_completed)
        elif inner_option == 3:
            month_view(window, selected, day, removing, hide_completed)
        elif inner_option == 4:
            year_view(window, selected, day, removing, hide_completed)
    elif outer_option == 1:
        if inner_option == 0:
            duration_maps(window, selected, map_settings)
        elif inner_option == 1:
            progress_maps(window, selected, map_settings)
        elif inner_option == 2:
            heatmaps(window, selected, map_settings)
        elif inner_option == 3:
            manage_habits(window, selected, removing)
        elif inner_option == 4:
            add_new_habit(window, selected, new_habit)
    else:
        coming_soon(window)
    display_text_box(window, text_input, text_box, text_index)
    window.refresh()
