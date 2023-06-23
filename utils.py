import streamlit as st
import pandas as pd
from PIL import Image
import json, os, argparse, shutil, re


def remove_number_lines(text, threshold=6):
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        numbers = re.findall(r'\b\d+(\.\d+)?\b', line)
        if len(numbers) < threshold:
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)
def parse_dms(dms):
    """Parse degrees, minutes, seconds coordinates to decimal degrees"""
    parts = re.split('[°\'"]+', dms)
    direction = parts[-1]
    parts = parts[:-1]
    
    while len(parts) < 3:  # if no seconds or no minutes and seconds, fill with zeros
        parts.append('0')
    
    degrees, minutes, seconds = parts
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
    if direction in ('S','W'):
        dd *= -1
    return dd
def parse_coordinate(coordinate):
    """Try to parse a coordinate to decimal degrees format"""
    try:
        return float(coordinate)  # plain decimal degrees
    except ValueError:
        pass
    try:
        return parse_dms(coordinate)  # degrees, minutes, seconds
    except ValueError:
        pass
    try:
        # degrees, decimal minutes
        parts = re.split('[°\']+', coordinate.upper())
        dd = float(parts[0]) + float(parts[1])/60
        if parts[2] in ('S', 'W'):
            dd *= -1
        return dd
    except (ValueError, IndexError):
        raise ValueError("Could not parse coordinate")
def check_for_sep(verbatim_coordinates):
    # Split latitude and longitude from the verbatim_coordinates using regex
    verbatim_coordinates = verbatim_coordinates.strip()
    coords = re.split(',|-', verbatim_coordinates)
    
    # Check if we have two separate coordinates
    if len(coords) != 2:
        return True
    else:
        return False
def replace_base_path(old_path, new_base_path, opt):
    # print(f"old = {old_path}")
    # print(f"new = {new_base_path}")
    # Replace the base path of the old_path with the new_base_path.
    # Split the path into parts
    parts = old_path.split(os.path.sep)
    # Find the index of the 'Transcription' part
    if opt == 'crop':
        transcription_index = parts.index('Cropped_Images') if 'Cropped_Images' in parts else None
    elif opt == 'original':
        transcription_index = parts.index('Original_Images') if 'Original_Images' in parts else None
    elif opt == 'json':
        transcription_index = parts.index('Transcription') if 'Transcription' in parts else None

    if transcription_index is not None:
        # Replace the base path up to 'Transcription' with the new_base_path
        new_path = os.path.join(new_base_path, *parts[transcription_index:])
        return new_path
    else:
        return old_path  # Return the old_path unchanged if 'Transcription' is not in the path