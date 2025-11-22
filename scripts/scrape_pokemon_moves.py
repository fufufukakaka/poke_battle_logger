"""
Scrape Pokemon moves data from pokemondb.net/move/all
"""
import csv
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


def scrape_pokemon_moves() -> List[Dict[str, str]]:
    """
    Scrape all Pokemon moves from pokemondb.net

    Returns:
        List of dictionaries containing move data
    """
    url = "https://pokemondb.net/move/all"

    # Send request with user agent to avoid blocking
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the main moves table
    table = soup.find('table', class_='data-table')

    if not table:
        raise ValueError("Could not find moves table on page")

    moves = []

    # Get table headers
    headers_row = table.find('thead').find('tr')
    headers = [th.get_text(strip=True) for th in headers_row.find_all('th')]

    # Process table rows
    tbody = table.find('tbody')
    for row in tbody.find_all('tr'):
        cells = row.find_all('td')

        if len(cells) < 6:
            continue

        move_data = {}

        # Name (first column)
        name_cell = cells[0].find('a', class_='ent-name')
        move_data['name'] = name_cell.get_text(strip=True) if name_cell else ""

        # Type (second column)
        type_cell = cells[1].find('a')
        move_data['type'] = type_cell.get_text(strip=True) if type_cell else ""

        # Category (third column - Physical/Special/Status)
        category_img = cells[2].find('img')
        if category_img and 'alt' in category_img.attrs:
            move_data['category'] = category_img['alt']
        else:
            move_data['category'] = cells[2].get_text(strip=True)

        # Power (fourth column)
        move_data['power'] = cells[3].get_text(strip=True)

        # Accuracy (fifth column)
        move_data['accuracy'] = cells[4].get_text(strip=True)

        # PP (sixth column)
        move_data['pp'] = cells[5].get_text(strip=True)

        # Effect (seventh column if exists)
        if len(cells) > 6:
            move_data['effect'] = cells[6].get_text(strip=True)
        else:
            move_data['effect'] = ""

        # Probability (eighth column if exists)
        if len(cells) > 7:
            move_data['probability'] = cells[7].get_text(strip=True)
        else:
            move_data['probability'] = ""

        moves.append(move_data)

    return moves


def save_to_csv(moves: List[Dict[str, str]], output_file: str = "pokemon_moves.csv"):
    """
    Save moves data to CSV file

    Args:
        moves: List of move dictionaries
        output_file: Output CSV file path
    """
    if not moves:
        print("No moves data to save")
        return

    fieldnames = ['name', 'type', 'category', 'power', 'accuracy', 'pp', 'effect', 'probability']

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(moves)

    print(f"Saved {len(moves)} moves to {output_file}")


def main():
    """Main execution function"""
    print("Scraping Pokemon moves from pokemondb.net...")

    try:
        moves = scrape_pokemon_moves()
        print(f"Successfully scraped {len(moves)} moves")

        # Display first 5 moves as sample
        print("\nFirst 5 moves:")
        for i, move in enumerate(moves[:5], 1):
            print(f"{i}. {move['name']} - Type: {move['type']}, "
                  f"Category: {move['category']}, Power: {move['power']}")

        # Save to CSV
        output_file = "data/pokemon_moves.csv"
        save_to_csv(moves, output_file)

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
