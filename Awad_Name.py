import requests
from bs4 import BeautifulSoup

# Wikipedia URL for Academy Awards
url = "https://en.wikipedia.org/wiki/Academy_Awards"

# Headers to mimic a real browser
headers = {'User-Agent': 'Mozilla/5.0'}

# Fetch the page
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all lists in the page that may contain categories
categories = []

# Possible section headers for award categories
section_headers = [
    "Current categories", "Discontinued categories", "Proposed categories"
]

for header in soup.find_all(['h2', 'h3']):
    if any(keyword in header.text for keyword in section_headers):
        ul = header.find_next_sibling('ul')
        if ul:
            for li in ul.find_all('li'):
                category = li.text.strip()
                categories.append(category)

# Print extracted categories
print("\n🎬 Academy Award Categories 🎬\n")
for category in categories:
    print(f"- {category}")

# Save to a file
with open("OscarCategories.txt", "w", encoding="utf-8") as file:
    for category in categories:
        file.write(category + "\n")

print("\n✅ Categories successfully saved to OscarCategories.txt")
