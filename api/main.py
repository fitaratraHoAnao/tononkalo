from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Route pour rechercher un poème
@app.route('/antsa', methods=['GET'])
def antsy():
    # Récupérer les paramètres fournis dans l'URL
    mpanoratra = request.args.get('mpanoratra', '').lower()
    tononkalo = request.args.get('tononkalo', '').lower()
    
    # Vérifier que les paramètres sont fournis
    if not mpanoratra or not tononkalo:
        return jsonify({"error": "Paramètres manquants"}), 400

    # URL de base du site à scraper
    base_url = "https://vetso.serasera.org"

    # Construire l'URL de la page de l'auteur
    author_url = f"{base_url}/tononkalo/{mpanoratra}"
    
    try:
        # Faire la requête vers la page de l'auteur
        response = requests.get(author_url)
        if response.status_code != 200:
            return jsonify({"error": "Auteur introuvable"}), 404
        
        # Parse le HTML de la page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Chercher tous les liens des poèmes sur la page
        poems_links = soup.find_all('a', href=True, string=True)

        # Rechercher le poème correspondant au titre fourni
        matched_poem_url = None
        for link in poems_links:
            if tononkalo in link.string.lower():
                matched_poem_url = base_url + link['href']
                break

        # Si aucun poème n'est trouvé
        if not matched_poem_url:
            return jsonify({"error": "Poème introuvable"}), 404

        # Faire la requête pour récupérer la page du poème
        poem_page = requests.get(matched_poem_url)
        soup_poem = BeautifulSoup(poem_page.content, 'html.parser')

        # Récupérer le titre et le contenu du poème
        title = soup_poem.find('h1').text.strip()  # Titre du poème
        poem_content = soup_poem.find('div', class_='entry').text.strip()  # Contenu du poème

        # Retourner le poème en format JSON
        return jsonify({
            "title": title,
            "author": mpanoratra.upper(),
            "content": poem_content
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Erreur de connexion au site"}), 500

# Lancer l'application Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
