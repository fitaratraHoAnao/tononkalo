from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route('/antsa', methods=['GET'])
def antsy():
    mpanoratra = request.args.get('mpanoratra')
    tononkalo = request.args.get('tononkalo')

    if not mpanoratra or not tononkalo:
        return jsonify({"error": "Veuillez fournir à la fois un auteur (mpanoratra) et un titre (tononkalo)"}), 400

    # Base URL pour l'auteur
    author_url = f"https://vetso.serasera.org/mpanoratra/{mpanoratra.lower()}"

    # Récupérer la page de l'auteur
    page = requests.get(author_url)
    if page.status_code != 200:
        return jsonify({"error": "Auteur non trouvé"}), 404

    soup = BeautifulSoup(page.content, 'html.parser')

    # Chercher tous les liens vers les poèmes de cet auteur
    poems_links = soup.find_all('a', href=True, text=True)
    
    # Normaliser la recherche du titre (enlever espaces, accents, etc.)
    normalized_tononkalo = re.sub(r'\W+', '', tononkalo.lower())

    matched_poem_url = None
    for link in poems_links:
        poem_title = link.get_text(strip=True)
        normalized_title = re.sub(r'\W+', '', poem_title.lower())
        
        # Si une correspondance partielle est trouvée
        if normalized_tononkalo in normalized_title:
            matched_poem_url = f"https://vetso.serasera.org{link['href']}"
            break

    if not matched_poem_url:
        return jsonify({"error": "Poème non trouvé"}), 404

    # Requête vers la page du poème correspondant
    poem_page = requests.get(matched_poem_url)
    soup_poem = BeautifulSoup(poem_page.content, 'html.parser')

    try:
        # Extraire le titre et le contenu du poème
        title = soup_poem.find('h2').get_text(strip=True)
        poem_lines = soup_poem.find('div', class_='col-md-8').get_text(strip=True).splitlines()
        poem = "\n".join(line for line in poem_lines if line)

        # Organiser le contenu en format JSON
        result = {
            "titre": title,
            "auteur": mpanoratra.upper(),
            "poeme": poem
        }

        return jsonify(result)

    except AttributeError:
        return jsonify({"error": "Erreur lors de l'extraction du poème"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  
