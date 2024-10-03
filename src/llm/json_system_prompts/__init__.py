import os


def load_text_file(file_path: str) -> dict or None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # check if file exists
    path = os.path.join(base_dir, file_path)
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    else:
        print(f"File {file_path} not found")
        return None
