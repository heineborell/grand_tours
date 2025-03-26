import numpy as np

def convert_time_to_seconds(time_str):
    """
    Convert a time string in HH:MM:SS or MM:SS format into total seconds.
    Input:
        time_str (str): A string representing time in either "HH:MM:SS" or "MM:SS" format.
    Returns:
        int or float: The total time in seconds. If input is invalid, returns NaN.
    """
    try:
        parts = list(map(int, time_str.split(':')))
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        return np.nan
    except:
        return np.nan
    

def seconds_to_hms(seconds):
    """
    Convert a total number of seconds into a formatted HH:MM:SS string.
    Input:
        seconds (int or float): The total number in seconds.
    Returns:
        str: A string representing the time in "HH:MM:SS" format.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"