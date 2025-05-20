import requests
from bs4 import BeautifulSoup

# Wikipedia URL for Academy Awards
url = "https://en.wikipedia.org/wiki/Academy_Awards"

# Headers to mimic a real browser
headers = {'User-Agent': 'Mozilla/5.0'}

# Fetch the page
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the table with award categories
categories = []
table = soup.find('table', {'class': 'wikitable'})

if table:
    for row in table.find_all('tr')[1:]:  # Skip header row
        columns = row.find_all('td')
        if len(columns) >= 2:
            category = columns[1].text.strip()
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
