#!/usr/bin/env python3
"""Icon extraction utility for mKast Game Launcher."""

import os

def extract_icon_from_exe(exe_path):
    """Extract icon from an executable file and save it to assets/game_images.
    
    Note: Icon extraction is currently disabled due to dependency issues.
    Returns empty string to indicate no icon was extracted.
    """
    try:
        print(f"Icon extraction requested for {exe_path}, but feature is currently disabled")
        return ""
        
    except Exception as e:
        print(f"Error in extract_icon_from_exe: {e}")
        return ""
