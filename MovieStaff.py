import requests
from bs4 import BeautifulSoup
import csv
import re
import time

# Set headers to mimic a real browser
headers = {'User-Agent': 'Mozilla/5.0'}

def extract_staff_details(info_box):
    """Extracts movie staff details from the Wikipedia infobox."""
    staff_roles = ["Directed by", "Produced by", "Written by", "Starring", "Music by", "Cinematography", "Edited by"]
    staff_details = []
    
    if info_box:
        rows = info_box.find_all('tr')
        for row in rows:
            cols = row.find_all(['th', 'td'])
            if len(cols) > 1:
                label = cols[0].text.strip()
                if label in staff_roles:
                    people_links = cols[1].find_all('a')
                    for person_link in people_links:
                        person_name = person_link.text.strip()
                        person_url = "https://en.wikipedia.org" + person_link['href']
                        
                        # Fetch and extract personal details
                        try:
                            person_response = requests.get(person_url, headers=headers)
                            person_soup = BeautifulSoup(person_response.content, 'html.parser')
                            
                            birth_date, birth_country, death_date = extract_personal_details(person_soup)
                            first_name, last_name = split_name(person_name)
                            
                            staff_details.append({
                                'firstName': first_name,
                                'lastName': last_name,
                                'dateOfBirth': birth_date,
                                'countryOfBirth': birth_country,
                                'dateOfDeath': death_date,
                                'role': label
                            })
                            time.sleep(1)  # Avoid rate-limiting
                        except Exception as e:
                            print(f"Error processing {person_name}: {e}")
    return staff_details

def extract_personal_details(person_soup):
    """Extracts birth date, country of birth, and death date if applicable."""
    birth_date, birth_country, death_date = None, None, None
    info_box = person_soup.find('table', class_=lambda x: x and 'infobox' in x)
    
    if info_box:
        rows = info_box.find_all('tr')
        for row in rows:
            label = row.find('th')
            if label:
                label_text = label.text.strip().lower()
                value = row.find('td')
                if value:
                    if 'born' in label_text:
                        birth_info = value.text.strip()
                        birth_date = re.search(r'\d{1,2}\s\w+\s\d{4}', birth_info)
                        birth_country = value.find('a')
                        birth_date = birth_date.group(0) if birth_date else None
                        birth_country = birth_country.text.strip() if birth_country else None
                    elif 'died' in label_text:
                        death_info = value.text.strip()
                        death_date = re.search(r'\d{1,2}\s\w+\s\d{4}', death_info)
                        death_date = death_date.group(0) if death_date else None
    return birth_date, birth_country, death_date

def extract_release_year(info_box):
    """Extracts the release year of the movie from the Wikipedia infobox."""
    release_year = None
    if info_box:
        rows = info_box.find_all('tr')
        for row in rows:
            label = row.find('th')
            if label and ('release date' in label.text.lower() or 'released' in label.text.lower()):
                value = row.find('td')
                if value:
                    year_match = re.search(r'\b(19|20)\d{2}\b', value.text)  # Match years 1900–2099
                    if year_match:
                        release_year = year_match.group(0)
                        break
    return release_year

def split_name(full_name):
    """Splits a full name into first and last name."""
    parts = full_name.split()
    first_name = parts[0] if parts else None
    last_name = parts[-1] if len(parts) > 1 else None
    return first_name, last_name

# Fetch Academy Award-nominated films
url = "https://en.wikipedia.org/wiki/List_of_Academy_Award%E2%80%93nominated_films"
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

movie_data = []
tables = soup.find_all('table', class_=lambda x: x and 'wikitable' in x)

for table in tables:
    rows = table.find_all('tr')[1:]  # Skip header row
    
    for row in rows:
        cols = row.find_all(['td', 'th'])
        if len(cols) < 3:
            continue

        movie_title_link = cols[0].find('a')
        if movie_title_link:
            movie_title = movie_title_link.text.strip()
            movie_url = "https://en.wikipedia.org" + movie_title_link['href']
        else:
            continue

        print(f"Processing: {movie_title}")
        
        try:
            movie_response = requests.get(movie_url, headers=headers)
            movie_soup = BeautifulSoup(movie_response.content, 'html.parser')
            info_box = movie_soup.find('table', class_=lambda x: x and 'infobox' in x)
            
            staff_details = extract_staff_details(info_box)
            release_year = extract_release_year(info_box)
            
            movie_data.append({
                'movieTitle': movie_title,
                'releaseYear': release_year,
                'staff': staff_details
            })
            
            print(f"Movie: {movie_title} ({release_year})")
            print("Staff Details:", staff_details, "\n")
            
            time.sleep(2)  # To avoid getting blocked
        except Exception as e:
            print(f"Error processing {movie_title}: {e}")

# Save data to CSV
with open('MovieStaff.csv', 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Movie Title', 'Release Year', 'First Name', 'Last Name', 'Date of Birth', 'Country of Birth', 'Date of Death', 'Role'])
    
    for entry in movie_data:
        for staff in entry['staff']:
            writer.writerow([
                entry['movieTitle'],
                entry['releaseYear'],
                staff['firstName'],
                staff['lastName'],
                staff['dateOfBirth'],
                staff['countryOfBirth'],
                staff['dateOfDeath'],
                staff['role']
            ])

print(" Data successfully saved to MovieStaff.csv")
