from pathlib import Path


def get_report_path():
    """Returns the path of the reports folder. Makes it accessible accross the project"""
    return Path(__file__).parent