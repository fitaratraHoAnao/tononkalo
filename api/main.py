from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/tononkira')
def get_tononkira():
    # Récupérer les paramètres de l'URL
    auteur = request.args.get('auteur')
    titre = request.args.get('titre')

    if not auteur or not titre:
        return jsonify({'error': 'Please provide both auteur and titre parameters'}), 400

    # URL de la page tononkira en utilisant les paramètres
    url = f'https://vetso.serasera.org/tononkalo/{auteur}/{titre}'
    
    # Faire une requête GET pour récupérer la page
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

    # Parser le contenu HTML avec BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    try:
        # Trouver la section contenant le titre et l'auteur
        title_author = soup.find('h2', class_='border-bottom')
        title = title_author.contents[0].strip()  # Titre
        author = title_author.find('a').text.strip()  # Auteur

        # Récupérer le contenu des paroles après le titre
        poem_content = ''
        for elem in title_author.find_all_next():
            if elem.name == 'div':
                break  # Arrêter à la première div qui suit le h2
            poem_content += elem.get_text(separator=' ', strip=True) + '\n'

        # Enlever les nouvelles lignes superflues
        poem_content = poem_content.strip()
        
    except AttributeError as e:
        return jsonify({'error': 'Could not find the necessary HTML elements'}), 404

    # Organiser les données sous forme de dictionnaire
    result = {
        'title': title,
        'author': author,
        'content': poem_content
    }

    # Retourner les données en format JSON
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
