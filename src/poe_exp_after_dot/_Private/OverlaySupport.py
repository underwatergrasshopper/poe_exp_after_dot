from .Commons               import merge_on_all_levels
from .Settings              import Settings

def solve_layout(settings : Settings, layout_name : str):
    command_line_layout = settings.get_dict("_command_line_layout")
    selected_layout     = settings.get_dict(f"layouts.{layout_name}")

    settings.set_tmp_dict("_solved_layout", merge_on_all_levels(selected_layout, command_line_layout)) 