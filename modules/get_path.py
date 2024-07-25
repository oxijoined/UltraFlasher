import os


def load_file(
    file_name: str,
) -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    return os.path.join(
        project_dir,
        file_name,
    )
