import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import os



def clean_runtime(runtime_str):
    # Remove any non-digit characters except for spaces, commas, hyphens, and question marks
    cleaned_str = re.sub(r'[^\d\s,\-\?]', '', runtime_str)

    # Remove any question marks
    cleaned_str = cleaned_str.replace('?', '')

    # Split by comma or space to handle multiple runtimes
    runtimes = re.split(r'[,\s]+', cleaned_str)

    # Extract the first runtime
    first_runtime = runtimes[0]

    # Handle runtime ranges (e.g., 130-154)
    if '-' in first_runtime:
        first_runtime = first_runtime.split('-')[0]

    # Handle format like "8:11"
    if ':' in first_runtime:
        parts = first_runtime.split(':')
        minutes = int(parts[0]) + int(parts[1]) / 60
        return round(minutes * 60)

    # Convert to minutes if it's in hours and minutes format
    if 'h' in first_runtime:
        match = re.search(r'(\d+)h\s*(\d+)m', first_runtime)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            return hours * 60 + minutes
        else:
            # Handle cases where only hours are specified
            match = re.search(r'(\d+)h', first_runtime)
            if match:
                hours = int(match.group(1))
                return hours * 60
    elif 'm' in first_runtime:
        # Remove 'm' and convert to integer
        return int(re.sub(r'[^\d]', '', first_runtime))
    else:
        # If no 'h' or 'm', assume it's already in minutes
        return int(first_runtime)

def convert_to_number(value_str):
    # Remove dollar signs and commas
    cleaned_str = re.sub(r'[\$,]', '', value_str)

    # Extract numeric part and unit (million/billion)
    match = re.search(r'(\d+(?:\.\d+)?)\s*(million|billion)?', cleaned_str, re.IGNORECASE)

    if match:
        value = float(match.group(1))
        unit = match.group(2)

        if unit == 'million':
            return value * 1e6
        elif unit == 'billion':
            return value * 1e9
        else:
            return value
    else:
        return None

def clean_language(language_str):
    cleaned_str = re.sub(r'[^\w\s]', '', language_str)
    words = cleaned_str.split()

    if words:
        return words[0]
    else:
        return 'Unknown'

# Fetch the Wikipedia page
url = "https://en.wikipedia.org/wiki/List_of_Academy_Award%E2%80%93nominated_films"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Prepare data storage
movie_data = []
sound_films_started = False

# Find all wikitable tables on the page
tables = soup.find_all('table', class_=lambda x: x and 'wikitable' in x)

for table in tables:
    rows = table.find_all('tr')[1:]  # Skip header row

    for row in rows:
        cols = row.find_all(['td', 'th'])

        # Skip invalid rows
        if len(cols) < 3:
            continue

        # Extract movie title and release year
        movie_title_link = cols[0].find('a')
        if movie_title_link:
            movie_title = movie_title_link.text.strip()
            movie_url = "https://en.wikipedia.org" + movie_title_link['href']
        else:
            movie_title = cols[0].text.strip()
            continue  # Skip if no link

        release_year = cols[1].text.strip()  # Use release year from the table

        # Check if sound films have started
        if movie_title == "White Shadows in the South Seas":
            sound_films_started = True

        # Fetch the movie's Wikipedia page
        try:
            headers = {'User-Agent': 'Your Script Name'}
            movie_response = requests.get(movie_url, headers=headers)
            movie_soup = BeautifulSoup(movie_response.content, 'html.parser')

            # Extract additional details
            details = {
                'movieTitle': movie_title,
                'releaseYear': release_year,
                'language': None,
                'runtime': None,
                'budget': None,
                'boxOffice': None
            }

            # Extract release year (not needed since we use the table's release year)
            info_box = movie_soup.find('table', class_=lambda x: x and 'infobox' in x)
            if info_box:
                rows = info_box.find_all('tr')
                for row in rows:
                    cols = row.find_all(['th', 'td'])
                    if len(cols) > 1:
                        if cols[0].text.strip() == 'Language':
                            if sound_films_started:
                                details['language'] = clean_language(cols[1].text.strip())
                            else:
                                details['language'] = 'Silent'
                        elif cols[0].text.strip() == 'Running time':
                            details['runtime'] = clean_runtime(cols[1].text.strip())
                        elif cols[0].text.strip() == 'Budget':
                            details['budget'] = convert_to_number(cols[1].text.strip())
                        elif cols[0].text.strip() == 'Box office':
                            details['boxOffice'] = convert_to_number(cols[1].text.strip())

            # Print the fetched data
            print(f"Movie: {details['movieTitle']}")
            print(f"Release Year: {details['releaseYear']}")
            print(f"Language: {details['language']}")
            print(f"Runtime: {details['runtime']}")
            print(f"Budget: {details['budget']}")
            print(f"Box Office: {details['boxOffice']}\n")

            movie_data.append(details)

            # Add a delay to avoid overwhelming the server
            time.sleep(1)

        except Exception as e:
            print(f"Failed to fetch {movie_title}: {e}")
            # Continue to the next movie if an error occurs
            continue

# Save movie data to a CSV file
with open('oscar_nominated_movies.csv', mode='w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Movie Title', 'Release Year', 'Language', 'Runtime', 'Budget', 'Box Office'])

    for entry in movie_data:
        writer.writerow([
            entry['movieTitle'],
            entry['releaseYear'],
            entry['language'],
            entry['runtime'],
            entry['budget'],
            entry['boxOffice']
        ])

print("Movie data saved to 'oscar_nominated_movies.csv'")
print("Current file path:", os.path.abspath(__file__))
