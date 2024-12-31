import importlib
import json
import os


def get_obj_by_name(name: str):
    module_path, attr_name = name.rsplit(".", 1)

    # Dynamically import the module and attribute
    module = importlib.import_module(module_path)
    attr = getattr(module, attr_name)
    return attr


def load_text(file_path):
    """
    Reads the contents of a text file and returns it as a string.

    Args:
    file_path (str): The path to the text file to be read.

    Returns:
    str: The contents of the file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def load_json(file_path):
    """
    Loads a JSON file from a specified file path and returns its content as a dictionary.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The content of the JSON file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # Load and return the JSON data
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def load_model(file_path, cls):
    data = load_json(file_path)
    return cls(**data)


def save_json(file, file_path):
    """
    Saves a dictionary to a JSON file at the specified file path.

    Args:
        file (dict): The dictionary to save as JSON.
        file_path (str): Path where the JSON file will be saved.
    """
    with open(file_path, "w") as json_file:
        json.dump(file, json_file)
