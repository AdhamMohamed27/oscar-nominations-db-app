import requests
from bs4 import BeautifulSoup
import csv
import re
import time

def extract_company_details(company_url):
    """Extract company headquarters and founding year from Wikipedia."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(company_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        info_box = soup.find('table', class_=lambda x: x and 'infobox' in x)

        company_name, hq, founded_year = None, None, None

        if info_box:
            rows = info_box.find_all('tr')
            for row in rows:
                header_cell = row.find('th')
                data_cell = row.find('td')
                if header_cell and data_cell:
                    header_text = header_cell.text.strip().lower()
                    data_text = data_cell.text.strip()
                    if re.search(r'headquarters', header_text, re.IGNORECASE):
                        hq = data_text.split('\n')[0]
                    elif re.search(r'founded|established', header_text, re.IGNORECASE):
                        founded_year_match = re.search(r'\b(\d{4})\b', data_text)
                        if founded_year_match:
                            founded_year = founded_year_match.group(1)
            company_name_tag = soup.find('h1', id='firstHeading')
            company_name = company_name_tag.text.strip() if company_name_tag else None

        return company_name, hq, founded_year

    except Exception as e:
        print(f"Error fetching company details: {e}")
        return None, None, None


def extract_release_year(info_box):
    """Extracts only the release year from Wikipedia infobox."""
    if info_box:
        rows = info_box.find_all('tr')
        for row in rows:
            cols = row.find_all(['th', 'td'])
            if len(cols) > 1:
                label = cols[0].text.strip().lower()
                value = cols[1].text.strip()
                if re.search(r'release date|released', label, re.IGNORECASE):
                    year_match = re.search(r'\b(\d{4})\b', value)  # Extracts only the year
                    if year_match:
                        return year_match.group(0)
    return None

url = "https://en.wikipedia.org/wiki/List_of_Academy_Award%E2%80%93nominated_films"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

movie_data = []

tables = soup.find_all('table', class_=lambda x: x and 'wikitable' in x)

for table in tables:
    rows = table.find_all('tr')[1:]

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

            release_year = extract_release_year(info_box)
            production_companies = []

            if info_box:
                rows = info_box.find_all('tr')
                for row in rows:
                    cols = row.find_all(['th', 'td'])
                    if len(cols) > 1:
                        label = cols[0].text.strip().lower()
                        value = cols[1]
                        if 'productioncompany' in label or 'productioncompanies' in label:
                            if value:
                                links = value.find_all('a')
                                if links:
                                    for link in links:
                                        company_name = link.text.strip()
                                        company_url = "https://en.wikipedia.org" + link['href'] if link.has_attr('href') else None
                                        production_companies.append((company_name, company_url))
                                else:
                                    company_names = [text.strip() for text in value.stripped_strings]
                                    for company_name in company_names:
                                        production_companies.append((company_name, None))
                            break

            companies_details = []
            for company_name, company_url in production_companies:
                cname, chq, cfyear = (company_name, None, None)
                if company_url:
                    cname, chq, cfyear = extract_company_details(company_url)
                companies_details.append({
                    'companyName': cname,
                    'companyHQ': chq,
                    'companyFoundedYear': cfyear,
                    'originalName': company_name
                })

            movie_data.append({
                'movieTitle': movie_title,
                'releaseYear': release_year,
                'productionCompanies': companies_details
            })

            print("Movie Title ", movie_title)
            print("Release Year ", release_year)
            print("Production Companies ", companies_details, "\n")

            time.sleep(0.5)

        except Exception as e:
            print(f"Error processing {movie_title}: {e}")

with open('ProductionCompanies_of_Nmovies.csv', 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Movie Title', 'Release Year', 'Production Company Name',
                     'Company Name (Wikipedia)', 'Company HQ', 'Company Founded Year'])

    for entry in movie_data:
        for company in entry['productionCompanies']:
            writer.writerow([
                entry['movieTitle'],
                entry['releaseYear'],
                company['originalName'],
                company['companyName'],
                company['companyHQ'],
                company['companyFoundedYear']
            ])

print("✅ Data successfully saved to ProductionCompanies_of_Nmovies.csv")
