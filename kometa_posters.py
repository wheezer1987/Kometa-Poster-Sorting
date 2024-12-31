import os
import json
from pathlib import Path
from directory_creation import movie_poster_directories, series_poster_directories
from poster_organization import (
    collection_poster_move,
    movies_poster_move,
    series_poster_move,
    delete_empty_directories,
)
from rename_posters import rename_movie_posters, rename_series_season_specials_posters


def load_config():
    """
    Load the configuration from a JSON file located in the same directory as the script.

    Returns:
        dict: Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If the config file is not found.
        ValueError: If the config file is not a valid JSON.
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file '{config_path}' not found.")
    
    with open(config_path, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON file: {e}")


def validate_directory(path):
    """
    Validate that the given path is a valid directory.

    Args:
        path (str): Path to the directory to validate.

    Raises:
        SystemExit: If the path is not a valid directory.
    """
    if not os.path.isdir(path):
        print(f"Error: {path} is not a valid directory.")
        exit(1)


def main():
    # Load configuration
    try:
        config = load_config()
    except (FileNotFoundError, ValueError) as e:
        print(e)
        exit(1)

    # Extract API configurations
    radarr_config = config.get("radarr", {})
    sonarr_config = config.get("sonarr", {})
    tmdb_config = config.get("tmdb", {})

    # Collect user inputs
    sorted_dir = input("Enter the path to the sorted directory: ").strip()
    unsorted_dir = input("Enter the path to the unsorted directory: ").strip()

    # Validate directories
    validate_directory(sorted_dir)
    validate_directory(unsorted_dir)

    # Assign subdirectories for unsorted movies and series
    unsorted_movies = os.path.join(unsorted_dir, "movies")
    unsorted_series = os.path.join(unsorted_dir, "series")

    # Ensure that subdirectories exist
    validate_directory(unsorted_movies)
    validate_directory(unsorted_series)

    # Step 1: Organize collection posters
    print("\nOrganizing collection posters...")
    collection_poster_move(
        unsorted_dir=unsorted_dir,
        sorted_dir=sorted_dir,
    )
    print("Finished organizing collection posters.")
    
    # Step 2: Process movie posters
    print("\nProcessing movie posters...")
    movie_poster_directories(
        sorted_dir=sorted_dir,
        unsorted_movies=unsorted_movies,
        radarr_config=radarr_config,
        tmdb_config=tmdb_config,
    )
    print("Finished processing movie posters.")

    # Step 3: Process series posters
    print("\nProcessing series posters...")
    series_poster_directories(
        sorted_dir=sorted_dir,
        unsorted_series=unsorted_series,
        sonarr_config=sonarr_config,
    )
    print("Finished processing series posters.")

    # Step 4: Organize unsorted movie posters into sorted directories
    print("\nOrganizing unsorted movie posters...")
    movies_poster_move(
        unsorted_dir=unsorted_dir,
        sorted_dir=sorted_dir,
    )
    print("Finished organizing unsorted movie posters.")

    # Step 5: Organize unsorted series posters into sorted directories
    print("\nOrganizing unsorted series posters...")
    series_poster_move(
        unsorted_dir=unsorted_dir,
        sorted_dir=sorted_dir,
    )
    print("Finished organizing unsorted series posters.")

    # Step 6: Delete empty directories in the unsorted directory
    print("\nDeleting empty directories in the unsorted directory...")
    delete_empty_directories(unsorted_dir)
    print("Finished deleting empty directories.")

    # Step 7: Rename movie posters
    print("\nRenaming movie posters...")
    rename_movie_posters(sorted_dir)
    print("Finished renaming movie posters.")

    # Step 8: Rename series posters (including seasons and specials)
    print("\nRenaming series posters (including seasons and specials)...")
    rename_series_season_specials_posters(sorted_dir)
    print("Finished renaming series posters.")

    print("\nAll tasks completed successfully!")


if __name__ == "__main__":
    main()