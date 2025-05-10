from .ninja.ninja_environment import NinjaEnvironment

def create_ffxiv_environment(class_name: str, target_time_millisecond: int):
    """Factory method for creating a new environment for different classes
    """

    if class_name == "Ninja":
        return NinjaEnvironment(target_time_millisecond)
    else:
        raise ValueError(f"Invalid class name: {class_name}")
