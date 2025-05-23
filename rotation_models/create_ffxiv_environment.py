from .ninja.ninja_combat_data import create_ninja_environment


def create_ffxiv_environment(class_name: str, target_time_millisecond: int, start_time_millisecond: int):
    """Factory method for creating a new environment for different classes"""

    if class_name == "ninja":
        return create_ninja_environment(target_time_millisecond, start_time_millisecond)
    else:
        raise ValueError(f"Invalid class name: {class_name}")
