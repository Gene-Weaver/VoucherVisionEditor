import streamlit as st
import pandas as pd
from PIL import Image
import json, os, argparse, shutil, re
import requests
from urllib.parse import urlencode

def remove_number_lines(text, threshold=6):
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        numbers = re.findall(r'\b\d+(\.\d+)?\b', line)
        if len(numbers) < threshold:
            cleaned_lines.append(line)
    cleaned_lines2 = '\n'.join(cleaned_lines)
    return cleaned_lines2

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
# def replace_base_path(old_path, new_base_path, opt):
#     # Normalize the old_path to match the OS's current path separator
#     old_path = os.path.normpath(old_path)
#     # print(f"old = {old_path}")
#     # print(f"new = {new_base_path}")
#     # Replace the base path of the old_path with the new_base_path.
#     # Split the path into parts
#     parts = old_path.split(os.path.sep)
#     # Find the index of the 'Transcription' part
#     if opt == 'crop':
#         transcription_index = parts.index('Cropped_Images') if 'Cropped_Images' in parts else None
#     elif opt == 'original':
#         transcription_index = parts.index('Original_Images') if 'Original_Images' in parts else None
#     elif opt == 'json':
#         transcription_index = parts.index('Transcription') if 'Transcription' in parts else None
#     elif opt == 'jpg':
#         transcription_index = parts.index('Transcription') if 'Transcription' in parts else None
#     else:
#         raise

#     if transcription_index is not None:
#         # Replace the base path up to 'Transcription' with the new_base_path
#         new_path = os.path.join(new_base_path, *parts[transcription_index:])
#         return new_path
#     else:
#         return old_path  # Return the old_path unchanged if 'Transcription' is not in the path
def replace_base_path(old_path, new_base_path, opt):
    # Normalize the old_path to match the OS's current path separator
    normalized_old_path = os.path.normpath(old_path)
    
    # Define the target directory based on 'opt'
    target_dir_map = {
        'crop': ['Cropped_Images', 'Original_Images',],
        'original': ['Original_Images',],
        'json': ['Transcription'],
        'jpg': ['Transcription']  # Assuming this is correct based on your function
    }
    target_dir = target_dir_map.get(opt)
    
    if target_dir is None:
        raise ValueError(f"Invalid option: {opt}")

    normalized_old_path = normalized_old_path.replace('\\', os.path.sep)

    # Split the normalized path into parts
    parts = normalized_old_path.split(os.path.sep)
    
    try:
        # Find the index of the target directory part
        for target in target_dir:
            try:
                target_index = parts.index(target)
                # Construct the new path by joining the new_base_path with the parts after the target directory
                new_path_parts = [new_base_path] + parts[target_index:]
                new_path = os.path.join(*new_path_parts)
                return new_path
            except:
                pass
    except ValueError:
        # Target directory not found in the path
        return old_path
    

def get_wfo_url(input_string, check_homonyms=True, check_rank=True, accept_single_candidate=True):
    good_basic = False
    good_search = False
    base_url = "https://list.worldfloraonline.org/matching_rest.php?"
    base_url_search = "https://www.worldfloraonline.org/search?query="

    params = {
        "input_string": input_string,
        "check_homonyms": check_homonyms,
        "check_rank": check_rank,
        "method": "full",
        "accept_single_candidate": accept_single_candidate,
    }

    full_url = base_url + urlencode(params)

    response_basic = requests.get(full_url)
    if response_basic.status_code == 200:
        # return full_url
        # response_basic = response_basic.json()
        good_basic = True

    # new_input_string = '+'.join(input_string.split(" "))
    # search_url = base_url_search + new_input_string + '&start=0&sort='
    
    # try:
    #     response_search = requests.get(search_url,timeout=2.0)
    #     if response_search.status_code == 200:
    #         # return full_url
    #         response_search = response_search.json()
    #         good_search = True
    # except:
    #     pass

    if good_basic and good_search:
        return full_url, None #search_url
    elif good_basic and not good_search:
        return full_url, None
    elif not good_basic and good_search:
        return None, None #search_url
    else:
        return None, None

    
    
    # simplified_response = {}
    # ranked_candidates = None

    # exact_match = response.get("match")
    # simplified_response["WFO_exact_match"] = bool(exact_match)

    # candidates = response.get("candidates", [])
    # candidate_names = [candidate["full_name_plain"] for candidate in candidates] if candidates else []

    # if not exact_match and candidate_names:
    #     cleaned_candidates, ranked_candidates = self._rank_candidates_by_similarity(query, candidate_names)
    #     simplified_response["WFO_candidate_names"] = cleaned_candidates
    #     simplified_response["WFO_best_match"] = cleaned_candidates[0] if cleaned_candidates else ''
    # elif exact_match:
    #     simplified_response["WFO_candidate_names"] = exact_match.get("full_name_plain")
    #     simplified_response["WFO_best_match"] = exact_match.get("full_name_plain")
    # else:
    #     simplified_response["WFO_candidate_names"] = ''
    #     simplified_response["WFO_best_match"] = ''

    # # Call WFO again to update placement using WFO_best_match
    # try:
    #     response_placement = self.query_wfo_name_matching(simplified_response["WFO_best_match"])
    #     placement_exact_match = response_placement.get("match")
    #     simplified_response["WFO_placement"] = placement_exact_match.get("placement", '')
    # except:
    #     simplified_response["WFO_placement"] = ''

    # return simplified_response, ranked_candidates