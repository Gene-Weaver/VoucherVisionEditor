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
def dms_to_decimal(dms_string):
    """Convert DMS string to decimal format for latitude and longitude."""
    
    def parse_dms(dms):
        """Parse degrees, minutes, seconds coordinates to decimal degrees"""
        direction = dms[-1].strip()
        parts = re.split('[°\'"MinutesSecondsNSEWnsew]+', dms)
        parts = [p.strip() for p in parts if p.strip()]  # removing leading/trailing whitespaces and empty strings
        
        while len(parts) < 3:  # if no seconds or no minutes and seconds, fill with zeros
            parts.append('0')
        
        if len(parts) == 3:
            degrees, minutes, seconds = parts
            dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
            if direction in ('S', 'W'):
                dd *= -1
            return dd
        else:
            raise
    
    # Splitting into latitude and longitude parts
    # lat_str, lon_str = dms_string.split(", ")
    lat_str = dms_string[0]
    lon_str = dms_string[1]
    
    lat_decimal = parse_dms(lat_str)
    lon_decimal = parse_dms(lon_str)

    return lat_decimal, lon_decimal
# def parse_dms(dms):
#     """Parse degrees, minutes, seconds coordinates to decimal degrees"""
#     parts = re.split('[°\'"]+', dms)
#     direction = parts[-1]
#     parts = parts[:-1]
    
#     while len(parts) < 3:  # if no seconds or no minutes and seconds, fill with zeros
#         parts.append('0')
    
#     degrees, minutes, seconds = parts
#     dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
#     if direction in ('S','W'):
#         dd *= -1
#     return dd
def parse_coordinate(coordinate):
    """Try to parse a coordinate to decimal degrees format"""
    try:
        return float(coordinate)  # plain decimal degrees
    except:
        pass
    try:
        return dms_to_decimal(coordinate)  # degrees, minutes, seconds
    except:
        pass
    try:
        # degrees, decimal minutes
        parts = re.split('[°\']+', coordinate.upper())
        dd = float(parts[0]) + float(parts[1])/60
        if parts[2] in ('S', 'W'):
            dd *= -1
        return dd
    except:
        return None, None
def check_for_sep(verbatim_coordinates):
    # Split latitude and longitude from the verbatim_coordinates using regex
    chars = [',', '|', '-']
    counts = {}
    
    for char in chars:
        counts[char] = verbatim_coordinates.count(char)
    total_count = sum(counts.values())
    
    # Check if we have two separate coordinates
    if total_count >= 1:
        return False
    else:
        return True
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
    elif opt == 'jpg':
        transcription_index = parts.index('Transcription') if 'Transcription' in parts else None
    else:
        raise

    if transcription_index is not None:
        # Replace the base path up to 'Transcription' with the new_base_path
        new_path = os.path.join(new_base_path, *parts[transcription_index:])
        return new_path
    else:
        return old_path  # Return the old_path unchanged if 'Transcription' is not in the path