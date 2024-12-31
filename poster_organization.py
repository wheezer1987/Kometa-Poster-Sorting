import os
import shutil
from pathlib import Path

def collection_poster_move(unsorted_dir, sorted_dir):
    """
    Organize collection posters.

    Args:
        unsorted_dir (str): Path to the unsorted collections directory.
        sorted_dir (str): Path to the sorted directory for collections.
    """
    target_dir = os.path.join(sorted_dir, "collections")
    os.makedirs(target_dir, exist_ok=True)

    # Search for image files in the unsorted directory and its subdirectories
    for file in Path(unsorted_dir).rglob("*"):
        # Process only image files containing the word "collection"
        if file.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif", ".bmp"] and "collection" in file.name.lower():
            # Create a subdirectory for each image file, removing the word "collection" from the directory name
            subdirectory_name = file.stem.replace("collection", "").strip()  # Remove "collection" and strip whitespace
            subdirectory_path = os.path.join(target_dir, subdirectory_name)
            os.makedirs(subdirectory_path, exist_ok=True)

            # Rename the image file to "poster" while keeping the extension intact
            new_file_name = f"poster{file.suffix}"
            target_path = os.path.join(subdirectory_path, new_file_name)

            # Check if the file already exists in the target location
            if os.path.exists(target_path):
                # File already exists, skip
                continue

            # Move the image file to the new subdirectory
            shutil.move(str(file), target_path)

def movies_poster_move(sorted_dir, unsorted_dir):
    """
    Organize movie posters.

    Args:
        sorted_dir (str): Path to the sorted directory for movies.
        unsorted_dir (str): Path to the unsorted movies directory.
    """
    movies_dir = os.path.join(sorted_dir, "movies")

    # Loop through each directory in the sorted movies directory
    for dir_path in Path(movies_dir).iterdir():
        if dir_path.is_dir():
            dir_name = dir_path.name
            # Extract the first portion of the directory name up to the last ')'
            match_name = dir_name.rsplit(")", 1)[0] + ")"

            # Flag to ensure only one image is moved per directory
            image_moved = False

            # Search for image files in the unsorted directory and its subdirectories
            for img_path in Path(unsorted_dir).rglob("*"):
                if img_path.is_file() and img_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
                    # Check if the image filename matches the extracted portion of the directory name
                    if match_name.lower() in img_path.name.lower():
                        target_path = dir_path / img_path.name
                        if target_path.exists():
                            # File already exists, skip
                            continue
                        # Move the image file to the corresponding directory
                        shutil.move(str(img_path), str(target_path))
                        image_moved = True
                        break  # Stop processing further images for this directory

            # If no matching image was found, continue to the next directory
            if not image_moved:
                pass

def series_poster_move(sorted_dir, unsorted_dir):
    """
    Organize series posters.

    Args:
        sorted_dir (str): Path to the sorted directory for series.
        unsorted_dir (str): Path to the unsorted series directory.
    """
    series_dir = os.path.join(sorted_dir, "series")

    # Loop through each directory in the sorted series directory
    for dir_path in Path(series_dir).iterdir():
        if dir_path.is_dir():
            dir_name = dir_path.name
            # Extract the first portion of the directory name up to the last ')'
            match_name = dir_name.rsplit(")", 1)[0] + ")"

            # Search for image files in the unsorted directory and its subdirectories
            for img_path in Path(unsorted_dir).rglob("*"):
                if img_path.is_file() and img_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
                    # Check if the image filename matches the extracted portion of the directory name
                    if match_name.lower() in img_path.name.lower():
                        target_path = dir_path / img_path.name
                        if target_path.exists():
                            # File already exists, skip
                            continue
                        # Move the image file to the corresponding directory
                        shutil.move(str(img_path), str(target_path))
                        
def delete_empty_directories(unsorted_dir):
    """
    Recursively delete all empty directories in the given directory.

    Args:
        unsorted_dir (str): Path to the directory to clean up.
    """
    for dir_path in Path(unsorted_dir).rglob("*"):
        if dir_path.is_dir() and not any(dir_path.iterdir()):  # Check if the directory is empty
            try:
                dir_path.rmdir()  # Remove the empty directory
            except Exception as e:
                print(f"Failed to delete directory {dir_path}: {e}")