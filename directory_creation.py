import os
import re
import requests
from pathlib import Path
from collections import defaultdict


def movie_poster_directories(sorted_dir, unsorted_movies, radarr_config, tmdb_config):
    """
    Search for movie posters in the unsorted_movies directory, query TMDB, and organize into sorted directories.

    Args:
        sorted_dir (str): Path to the sorted directory containing movie folders.
        unsorted_movies (str): Path to the unsorted movies directory.
        radarr_config (dict): Configuration for accessing the Radarr API.
        tmdb_config (dict): Configuration for accessing the TMDB API.

    Returns:
        None
    """
    # Validate Radarr and TMDB configurations
    radarr_api_key = radarr_config.get("api_key")
    radarr_base_url = radarr_config.get("base_url")
    tmdb_api_key = tmdb_config.get("api_key")
    tmdb_base_url = tmdb_config.get("base_url")

    if not radarr_api_key or not radarr_base_url:
        raise ValueError("Radarr API key or base URL is missing in configuration.")
    if not tmdb_api_key or not tmdb_base_url:
        raise ValueError("TMDB API key or base URL is missing in configuration.")

    # Search for image files in the unsorted_movies directory
    for root, _, files in os.walk(unsorted_movies):
        for file_name in files:
            if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
                # Extract the file path
                file_path = os.path.join(root, file_name)
                print(f"\nFound image file: {file_name}")

                # Extract the portion of the file name before the first '('
                search_query = file_name.split('(')[0].strip()

                # Extract the year from the file name using a regex pattern
                year_match = re.search(r"\((\d{4})\)", file_name)
                file_year = year_match.group(1) if year_match else None

                if not search_query:
                    print(f"Skipping file '{file_name}' as no valid search query could be extracted.")
                    continue

                print(f"Using search query: '{search_query}'")
                if file_year:
                    print(f"Extracted year from file name: {file_year}")

                # Prepare TMDB search URL
                tmdb_search_url = f"{tmdb_base_url}/search/movie"
                page = 1  # Start with the first page of results
                selected_movie = None

                while True:
                    # Send the TMDB search request
                    response = requests.get(tmdb_search_url, params={
                        "api_key": tmdb_api_key,
                        "query": search_query,
                        "language": "en-US",  # Specify the language
                        "page": page  # Handle pagination
                    })

                    if response.status_code != 200:
                        print(f"Error searching TMDB: {response.status_code} - {response.json().get('status_message', 'Unknown error')}")
                        break

                    # Parse the search results
                    results = response.json().get("results", [])
                    if not results:
                        print("No movies found on TMDB for this search query.")
                        break

                    # Attempt to automatically match a result based on the year
                    for result in results:
                        release_date = result.get('release_date', None)
                        release_year = release_date.split("-")[0] if release_date else None
                        if file_year and release_year == file_year:
                            selected_movie = result
                            print(f"Automatically matched movie: {result['title']} ({release_year})")
                            break

                    if selected_movie:
                        break

                    # If no automatic match, display the top 5 results for manual selection
                    print("\nSearch Results:")
                    for i, result in enumerate(results[:5], start=1):
                        title = result['title']
                        release_date = result.get('release_date', 'Unknown release date')
                        overview = result.get('overview', 'No overview available')
                        print(f"{i}. {title} ({release_date}) - {overview}")

                    # Check if there are more results to display (for pagination)
                    show_more_option = len(results) > 5
                    if show_more_option:
                        print("6. Show next page of results")

                    # Get user selection
                    try:
                        selection = int(input("Select a movie (1-6): "))
                        if 1 <= selection <= len(results[:5]):
                            selected_movie = results[selection - 1]
                            break
                        elif selection == 6 and show_more_option:
                            page += 1  # Load the next page
                        else:
                            print("Invalid selection. Please try again.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")

                if not selected_movie:
                    print("No movie selected. Skipping this file.")
                    continue

                # Get the TMDB ID of the selected movie
                tmdb_id = selected_movie["id"]
                print(f"Selected movie: {selected_movie['title']} (TMDB ID: {tmdb_id})")

                # Use the TMDB ID to search for the movie in Radarr
                radarr_movie_url = f"{radarr_base_url}/movie"
                response = requests.get(
                    radarr_movie_url,
                    headers={"X-Api-Key": radarr_api_key}
                )

                if response.status_code != 200:
                    print(f"Error fetching movies from Radarr: {response.status_code}")
                    continue

                radarr_movies = response.json()
                movie_found = None
                for movie in radarr_movies:
                    if movie.get("tmdbId") == tmdb_id:
                        movie_found = movie
                        break

                if not movie_found:
                    print("Movie not found in Radarr.")
                    continue

                # Create a directory using the Radarr "path" field
                movie_path = movie_found.get("path")
                root_directory = movie_found.get("rootFolderPath")
                if not movie_path or not root_directory:
                    print("Invalid path or root directory found in Radarr.")
                    continue

                # Remove the root directory from the movie path
                relative_path = os.path.relpath(movie_path, root_directory)

                # Create the directory in the sorted directory
                target_dir = os.path.join(sorted_dir, "movies", relative_path)
                os.makedirs(target_dir, exist_ok=True)
                print(f"Created directory: {target_dir}")

                # Do not move the image file; leave it in its original location
                print(f"Image file remains in: {file_path}")            

def series_poster_directories(sorted_dir, unsorted_series, sonarr_config):
    """
    Search for series posters in the unsorted_series directory using Sonarr's API and organize into sorted directories.
    Automatically match the series if the year in the file name matches the release year in the Sonarr lookup.

    Args:
        sorted_dir (str): Path to the sorted directory containing series folders.
        unsorted_series (str): Path to the unsorted series directory.
        sonarr_config (dict): Configuration for accessing the Sonarr API.

    Returns:
        None
    """
    # Validate Sonarr configuration
    sonarr_api_key = sonarr_config.get("api_key")
    sonarr_base_url = sonarr_config.get("base_url")
    if not sonarr_api_key or not sonarr_base_url:
        raise ValueError("Sonarr API key or base URL is missing in configuration.")

    # Regular expression to extract "SERIES (YEAR)" from file names
    series_pattern = re.compile(r"^(.*? \((\d{4})\))")  # Match "SERIES (YEAR)" pattern

    # Group all image files by "SERIES (YEAR)"
    series_groups = defaultdict(list)

    for root, _, files in os.walk(unsorted_series):
        for file_name in files:
            if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
                # Extract the file path
                file_path = os.path.join(root, file_name)

                # Match the series name and year using the regex pattern
                match = series_pattern.match(file_name)
                if match:
                    series_key = match.group(1)  # Extract the "SERIES (YEAR)" part
                    series_year = match.group(2)  # Extract the year
                    series_groups[series_key].append((file_path, series_year))
                else:
                    print(f"Skipping file '{file_name}' as it does not match the expected pattern.")

    # Process each series group
    for series_key, files_with_years in series_groups.items():
        print(f"\nProcessing series group: {series_key}")
        print("Files in group:")
        for file_path, _ in files_with_years:
            # Only display the file name, not the full path
            print(f"  - {os.path.basename(file_path)}")

        # Extract the search query and year for Sonarr lookup
        search_query = series_key.split(" (")[0].strip()  # Extract the series name without the year
        series_year = files_with_years[0][1]  # Use the year from the first file in the group
        print(f"Using search query: '{search_query}' with year: {series_year}")

        # Query Sonarr API for the series
        sonarr_search_url = f"{sonarr_base_url}/series/lookup"
        response = requests.get(sonarr_search_url, headers={"X-Api-Key": sonarr_api_key}, params={"term": search_query})

        if response.status_code != 200:
            print(f"Error searching Sonarr: {response.status_code} - {response.text}")
            continue

        results = response.json()
        if not results:
            print("No series found in Sonarr for this search query.")
            continue

        # Attempt to automatically match the series based on the release year
        matched_series = None
        for result in results:
            premiere_date = result.get("year", None)  # Extract the year from the result
            if premiere_date and str(premiere_date) == series_year:
                matched_series = result
                print(f"Automatically matched series: {result['title']} ({premiere_date})")
                break

        # If no automatic match, display results for manual selection
        if not matched_series:
            print("\nSearch Results:")
            for i, result in enumerate(results[:5], start=1):
                title = result.get("title", "Unknown title")
                premiere_date = result.get("year", "Unknown year")
                overview = result.get("overview", "No overview available")
                print(f"{i}. {title} ({premiere_date}) - {overview}")
            if len(results) > 5:
                print("6. Show more results")

            # Ask the user to make a selection
            while True:
                try:
                    selection = int(input("Select a series (1-5): "))
                    if 1 <= selection <= len(results[:5]):
                        matched_series = results[selection - 1]
                        break
                    elif selection == 6 and len(results) > 5:
                        # Display additional results if the user selects to show more
                        for i, result in enumerate(results[5:], start=6):
                            title = result.get("title", "Unknown title")
                            premiere_date = result.get("year", "Unknown year")
                            overview = result.get("overview", "No overview available")
                            print(f"{i}. {title} ({premiere_date}) - {overview}")
                    else:
                        print("Invalid selection. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

        if not matched_series:
            print("No series selected. Skipping this group.")
            continue

        # Get the series path from Sonarr
        series_path = matched_series.get("path")
        if not series_path:
            print(f"Series '{matched_series['title']}' does not have a valid path in Sonarr.")
            continue

        # Create the directory in the sorted directory
        target_dir = os.path.join(sorted_dir, "series", os.path.basename(series_path))
        os.makedirs(target_dir, exist_ok=True)
        print(f"Created directory: {target_dir}")

        # Skip the remaining files in the group
        print(f"Skipping the rest of the files for series '{series_key}' as the series has been processed.")