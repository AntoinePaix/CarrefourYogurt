#!/usr/bin/python3
# Coding: utf-8

# Author : Antoine Paix
# Date : 2020/02/16

# Ce programme scrape les informations des yaourts et desserts commercialisés
# par l'enseigne Carrefour. Le but est de trouver le yaourt avec le taux de protéine
# le plus élevé et de faire quelques statistiques sur les informations nutritionnelles
# des différents produits.

import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import datetime

category = 'yaourts'
websites = ['http://www.jeuxvideo.com', 'https://www.amazon.fr', 'https://www.youtube.com', 'https://www.lemonde.fr', ]
headers = {"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/536.30.1 (KHTML, like Gecko) Version/6.0.5 Safari/536.30.1", "referer": random.choice(websites)}
session = requests.Session()

def getTotalPages():
    """Retourne le nombre de pages à générer en fonction du nombre de résultats"""
    url = "https://www.carrefour.fr/r/cremerie/yaourts-desserts-et-specialites-vegetales"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    total = int(soup.find('div', class_='product-listing-page__top-wrapper').find('h5').text.strip().split()[0])
    if total % 60 == 0:
        return total // 60 + 1
    else:
        return total // 60 + 2

def generateProductsUrls():
    for i in range(1, getTotalPages()):
        time.sleep(random.random())
        url = 'https://www.carrefour.fr/r/cremerie/yaourts-desserts-et-specialites-vegetales?noRedirect=1&page=' + str(i)

        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        grid = soup.find('ul', class_='product-grid')

        for produit in grid.find_all('li', class_='product-grid-item')[:-1]:
            try:
                url = produit.find('a', class_='product-card-title product-card-title--food')
                url = "https://www.carrefour.fr" + url.get('href')
            except AttributeError:
                pass
            yield url


def parsingProduct(url):
    time.sleep(random.random())
    produit = session.get(url, headers=headers)
    soup = BeautifulSoup(produit.text, "html.parser")
    titre = soup.title.text.split(':')[0]
    quantite = soup.title.text.split(':')[1].replace('à Prix Carrefour', '').strip()
    prix = soup.find('div', class_='product-card-price__price').text.strip().replace(',', '.').replace('€', '').strip()
    prix_kilos = soup.find('div', class_='ds-body-text ds-body-text--size-s').text.strip().split('/')[0].replace('€', '').strip()

    dicrow = {'URL':url, 'TITRE':titre, 'QUANTITE':quantite, 'PRIX':prix, 'PRIX_KILOS':prix_kilos}

    infos = soup.find('div', class_='secondary-details-blocks')
    for info in infos.find_all('div', class_='nutritional-fact__name'):
        matiere = info.find('h3', class_='subtitle').text.strip()
        valeur = info.find('div', class_='nutritional-fact-value nutritional-fact__center').text.strip()
        if '100 g' in valeur:
            matiere = matiere.upper()
            valeur = valeur.split()[0]

            dicrow[matiere] = valeur

    return dicrow

def Filename():
    """Génère un nom de fichier au format csv"""
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%-m-%d')
    return timestamp + '_' + category + '.csv'


########## CORPS DU PROGRAMME ##########

if __name__ == "__main__":

    # on génère toutes les urls et on les place dans une liste
    liste_urls_produits = list(generateProductsUrls())

    # on retire le poulet qui est dans la catégorie "Yaourts, desserts et spécialités végétales". Allez comprendre...
    for url in liste_urls_produits:
        if 'poulet-roti-certifie' in url:
            liste_urls_produits.remove(url)
    
    datas = []
    compteur = 0

    # on parse toutes les pages et on ajoute les dictionnaires une liste
    for url in liste_urls_produits:
        row = parsingProduct(url)
        compteur += 1
        print(compteur, '\t', row)
        datas.append(row)

    # on extrait les clés de toutes les dictionnaires pour construire la variable "fieldnames"
    fieldnames = []
    for data in datas:
        for key in data.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    # on boucle sur data et on écrit dans le fichier csv
    with open(Filename(), 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for ligne in datas:
            writer.writerow(ligne)