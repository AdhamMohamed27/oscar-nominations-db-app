import requests
from bs4 import BeautifulSoup
import csv
import re
import time

# Set headers to mimic a real browser
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

def build_ceremony_url(iteration):
    """Construct the URL for a ceremony page based on iteration."""
    base_url = "https://en.wikipedia.org/wiki/"
    
    # Special cases for known URLs
    special_cases = {
        95: "95th_Academy_Awards",
        94: "94th_Academy_Awards"
    }
    if iteration in special_cases:
        return base_url + special_cases[iteration]
    
    # Compute ordinal correctly
    suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(iteration % 10, 'th') if iteration % 100 not in [11, 12, 13] else 'th'
    return base_url + f"{iteration}{suffix}_Academy_Awards"

def extract_winners_from_ceremony(url, iteration):
    """Extract winners from an individual Oscar ceremony page."""
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch {url}, status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    winners = []
    
    # Look for award categories in table cells
    # Find all table cells that contain categories
    award_cells = soup.find_all(['td', 'th'])
    
    for cell in award_cells:
        # Look for category headers (usually in bold or as headings)
        category_header = cell.find(['b', 'strong', 'h3', 'h4'])
        if category_header and ('Best' in category_header.text or 'Outstanding' in category_header.text):
            category = clean_text(category_header.text)
            print(f"Found category: {category}")
            
            # Find adjacent winners (usually bullet points or in the same cell)
            winners_list = []
            
            # Look for bullet points (list items)
            if cell.parent:
                # Find the winner entries (usually in list items after the category)
                winner_items = cell.parent.find_next_siblings('li')
                if not winner_items:
                    # Check for list items within the cell or nearby
                    winner_items = cell.find_all('li')
                
                for item in winner_items:
                    winner_name = None
                    film_title = None
                    
                    # Look for winner name (often in plain text) and film (often in italics)
                    italic = item.find('i')
                    if italic:
                        film_title = clean_text(italic.text)
                    
                    # Extract winner name (usually before the film or dash)
                    item_text = clean_text(item.text)
                    if ' – ' in item_text:
                        parts = item_text.split(' – ', 1)
                        winner_name = clean_text(parts[0])
                        if not film_title and len(parts) > 1:
                            film_title = clean_text(parts[1])
                    else:
                        winner_name = item_text
                    
                    if winner_name:
                        winners.append({
                            'iteration': iteration,
                            'category': category,
                            'winner': winner_name,
                            'film': film_title if film_title else "N/A"
                        })
                        print(f"Added winner: {winner_name} for {category}")
    
    # If no winners found using the cell method, try the table processing approach
    if not winners:
        # Find all wikitables
        wikitables = soup.find_all('table', {'class': 'wikitable'})
        for table in wikitables:
            winners.extend(process_table(table, iteration))
    
    return winners

def process_table(table, iteration):
    """Process a single table to extract winners."""
    winners = []
    
    # For early ceremonies, the tables may have different structures
    # Look for table headers or category cells
    category_cells = table.find_all(['th', 'td'], string=lambda s: s and ('Best' in s or 'Outstanding' in s))
    
    for category_cell in category_cells:
        category = clean_text(category_cell.text)
        print(f"Found category in table: {category}")
        
        # Find the associated row or section
        current_row = category_cell.parent
        if not current_row:
            continue
            
        # Look for winners in the same row or following rows
        winner_cells = current_row.find_all(['td', 'li'])
        if not winner_cells and current_row.next_sibling:
            # Try next row if no winners in current row
            winner_cells = current_row.next_sibling.find_all(['td', 'li'])
        
        for winner_cell in winner_cells:
            winner_name = None
            film_title = None
            
            # Look for bold elements (often winner names)
            bold = winner_cell.find(['b', 'strong'])
            if bold:
                winner_name = clean_text(bold.text)
            
            # Look for italic elements (often film titles)
            italic = winner_cell.find('i')
            if italic:
                film_title = clean_text(italic.text)
            
            # If we couldn't find structured elements, try to parse the text
            if not winner_name:
                cell_text = clean_text(winner_cell.text)
                if ' – ' in cell_text:
                    parts = cell_text.split(' – ', 1)
                    winner_name = clean_text(parts[0])
                    if not film_title and len(parts) > 1:
                        film_title = clean_text(parts[1])
            
            if winner_name and category and 'Best' in category:
                winners.append({
                    'iteration': iteration,
                    'category': category,
                    'winner': winner_name,
                    'film': film_title if film_title else "N/A"
                })
                print(f"Added winner from table: {winner_name} for {category}")
    
    return winners

def clean_text(text):
    """Clean up text by removing unwanted characters and excessive whitespace."""
    if not text:
        return ""
    
    # Remove reference markers, footnotes, etc.
    text = re.sub(r'\[\d+\]|\[note \d+\]|\[\w\]', '', text)
    
    # Remove symbols often used as markers
    text = re.sub(r'[\*‡†]', '', text)
    
    # Replace newlines and multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove any leading/trailing whitespace
    return text.strip()

def main():
    # List of Oscar ceremony iterations to scrape (start with just a few)
    iterations = range(1, 98)  # For testing, just try first 5 ceremonies
    all_winners = []

    for iteration in iterations:
        url = build_ceremony_url(iteration)
        print(f"\nProcessing {iteration} ({url})...")

        winners = extract_winners_from_ceremony(url, iteration)

        if winners:
            all_winners.extend(winners)
            print(f"  Found {len(winners)} award winners for {iteration}.")
        else:
            print(f"  No winners extracted for {iteration}.")

        # Delay to prevent getting blocked
        time.sleep(2)

    if not all_winners:
        print("\nNo winners were extracted.")
        return

    print(f"\nExtracted {len(all_winners)} total winners.")

    # Write results to CSV
    with open('OscarsAllWinners.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Iteration', 'Award Category', 'Winner', 'Film'])

        for winner in sorted(all_winners, key=lambda x: x['iteration']):
            writer.writerow([
                winner['iteration'],
                winner['category'],
                winner['winner'],
                winner['film']
            ])

    print("Data successfully saved to OscarsAllWinners.csv")

if __name__ == "__main__":
    main()