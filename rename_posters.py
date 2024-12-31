import os
from pathlib import Path

def rename_movie_posters(sorted_dir):
    """
    Rename movie posters in the sorted directory.

    Args:
        sorted_dir (str): Path to the sorted directory for movies.
    """
    movies_dir = os.path.join(sorted_dir, "movies")
    if not os.path.isdir(movies_dir):
        raise ValueError(f"Movies directory does not exist: {movies_dir}")

    # Iterate through each movie directory
    for dir_path in Path(movies_dir).iterdir():
        if dir_path.is_dir():
            for file in dir_path.iterdir():
                # Check if the file is an image
                if file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                    # Rename the file to "poster.<extension>"
                    new_file = dir_path / f"poster{file.suffix}"
                    if not new_file.exists():  # Avoid overwriting existing files
                        file.rename(new_file)
                        print(f"Renamed {file} to {new_file}")


def rename_series_season_specials_posters(sorted_dir):
    """
    Rename series posters for seasons and specials.

    Args:
        sorted_dir (str): Path to the sorted directory for series.
    """
    series_dir = os.path.join(sorted_dir, "series")
    if not os.path.isdir(series_dir):
        raise ValueError(f"Series directory does not exist: {series_dir}")

    # Loop through each series directory
    for dir_path in Path(series_dir).iterdir():
        if dir_path.is_dir():
            # Handle renaming for seasons and specials
            for file in dir_path.iterdir():
                if file.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
                    file_name = file.name
                    file_extension = file.suffix

                    # Rename files for "Season #" (1-9)
                    if "Season " in file_name:
                        if any(f"Season {i}" in file_name for i in range(1, 10)):
                            season_number = file_name.split("Season ")[1].split()[0]
                            new_file_name = f"Season0{season_number}{file_extension}"
                            new_file_path = dir_path / new_file_name
                            if not new_file_path.exists():  # Avoid overwriting existing files
                                file.rename(new_file_path)
                                print(f"Renamed {file} to {new_file_path}")

                    # Rename files for "Season ##" (10 or greater)
                    elif any(f"Season {i}" in file_name for i in range(10, 100)):
                        season_number = file_name.split("Season ")[1].split()[0]
                        new_file_name = f"Season{season_number}{file_extension}"
                        new_file_path = dir_path / new_file_name
                        if not new_file_path.exists():  # Avoid overwriting existing files
                            file.rename(new_file_path)
                            print(f"Renamed {file} to {new_file_path}")

                    # Rename files containing "Specials"
                    elif "Specials" in file_name:
                        new_file_name = f"Season00{file_extension}"
                        new_file_path = dir_path / new_file_name
                        if not new_file_path.exists():  # Avoid overwriting existing files
                            file.rename(new_file_path)
                            print(f"Renamed {file} to {new_file_path}")

            # Handle renaming of non-season and non-specials posters
            for file in dir_path.iterdir():
                if file.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif", ".bmp"] and "Season" not in file.name and "Specials" not in file.name:
                    new_file_name = f"poster{file.suffix}"
                    new_file_path = dir_path / new_file_name
                    if not new_file_path.exists():  # Avoid overwriting existing files
                        file.rename(new_file_path)
                        print(f"Renamed {file} to {new_file_path}")