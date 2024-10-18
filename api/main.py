from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import re
import unicodedata

app = Flask(__name__)

# Fonction pour normaliser le slug
def slugify(value):
    if value:
        value = str(value)
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        value = re.sub('[-\s]+', '-', value)
        return value
    return None

# Fonction pour construire l'URL de tononkalo
def find_song_url(auteur, titre):
    base_url = 'https://vetso.serasera.org'
    auteur_slug = slugify(auteur)
    titre_slug = slugify(titre)
    return f'{base_url}/tononkalo/{auteur_slug}/{titre_slug}'

# Fonction pour extraire les paroles à partir du HTML
def scrape_lyrics_from_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')

    # Trouver la section contenant le titre et l'auteur
    title_author = soup.find('h2', class_='border-bottom')
    if not title_author:
        return None

    # Récupérer le titre et l'auteur
    title = title_author.contents[0].strip()  # Titre
    author = title_author.find('a').text.strip()  # Auteur

    # Extraire les paroles (texte qui suit le h2)
    lyrics_content = []
    for elem in title_author.find_all_next():
        if elem.name == 'div' and 'no-print' in elem.get('class', []):
            break  # Arrêter si on atteint un div qui marque la fin des paroles
        if elem.string:
            lyrics_content.append(elem.string.strip())
        elif elem.name == 'br':
            lyrics_content.append('\n')

    lyrics = ''.join(lyrics_content).strip()
    return title, author, lyrics

# Route pour obtenir les paroles d'une chanson
@app.route('/tononkalo', methods=['GET'])
def get_tononkalo():
    auteur = request.args.get('auteur')
    titre = request.args.get('titre')

    if not auteur or not titre:
        return jsonify({'error': 'Veuillez fournir les paramètres "auteur" et "titre"'}), 400

    try:
        # Construire l'URL de la chanson
        song_url = find_song_url(auteur, titre)

        # Récupérer la page HTML de la chanson
        response = requests.get(song_url)
        if response.status_code != 200:
            return jsonify({'error': 'Chanson non trouvée'}), 404

        # Extraire les paroles
        title, author, lyrics = scrape_lyrics_from_html(response.text)
        if not lyrics:
            return jsonify({'error': 'Paroles non trouvées'}), 404

        # Retourner les résultats
        return jsonify({'title': title, 'author': author, 'content': lyrics})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Lancement du serveur Flask sur host 0.0.0.0 et port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
