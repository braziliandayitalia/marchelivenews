import feedparser
import json
import os
import random
import re
from datetime import datetime

# Fonti RSS Marche
RSS_SOURCES = [
    {"name": "Cronache Maceratesi", "url": "https://www.cronachemaceratesi.it/feed/"},
    {"name": "Cronache Ancona", "url": "https://www.cronacheancona.it/feed/"},
    {"name": "Vivere Ancona", "url": "https://www.vivereancona.it/rss/index.xml"},
    {"name": "Ansa Marche", "url": "https://www.ansa.it/marche/notizie/marche_rss.xml"}
]

NEWS_FILE = "news.json"
RECIPE_FILE = "recipe.json"
CURIOSITY_FILE = "curiosity.json"

# Database locale per rotazione (simulazione AI)
CURIOSITIES = [
    {"title": "Il Mistero della Sibilla", "content": "I Monti Sibillini prendono il nome da una profetessa che viveva in una grotta a 2000 metri.", "img": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b"},
    {"title": "Ancona: Alba e Tramonto sul Mare", "content": "Ancona è l'unica città adriatica dove si può vedere il sole sorgere e tramontare sul mare grazie al gomito del Monte Conero.", "img": "https://images.unsplash.com/photo-1544085311-11a028465b03"},
    {"title": "L'Infinito di Leopardi", "content": "Il Colle dell'Infinito a Recanati ha ispirato una delle poesie più famose della letteratura mondiale.", "img": "img/marche_village.png"}
]

RECIPES = [
    {"title": "Olive all'Ascolana", "summary": "Le regine del fritto marchigiano, ripiene di tre carni diverse.", "wine": "Passerina Offida DOCG"},
    {"title": "Maccheroncini di Campofilone", "summary": "Pasta all'uovo sottilissima, eccellenza del fermano.", "wine": "Falerio dei Colli Ascolani"},
    {"title": "Brodetto all'Anconetana", "summary": "Zuppa di pesce tradizionale con almeno 13 varietà di pescato.", "wine": "Verdicchio dei Castelli di Jesi"}
]

def fetch_rss_news():
    all_news = []
    print(f"AGENTE: Scansione fonti RSS in corso...")
    
    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:8]: # Prendi più elementi per mixare meglio
                # Titolo pulito ma tech
                clean_title = entry.title.strip()
                tech_title = clean_title.upper().replace(" ", "_")
                if ":" not in tech_title:
                    tech_title = f"LOCAL_UPDATE: {tech_title}"
                
                # Immagine
                image_url = "https://images.unsplash.com/photo-1444653300602-7609d665975b?auto=format&fit=crop&w=1200&q=80"
                if 'media_content' in entry:
                    image_url = entry.media_content[0]['url']
                elif 'links' in entry:
                    for link in entry.links:
                        if 'image' in link.get('type', ''):
                            image_url = link.href
                
                # Sommario più ricco
                summary_text = entry.get('summary', '') or entry.get('description', '')
                # Rimuovi tag HTML e pulizia stringa
                summary_text = re.sub('<[^<]+?>', '', summary_text).strip()
                summary_text = summary_text.replace("&nbsp;", " ").replace("\n", " ")
                
                news_item = {
                    "id": random.randint(1000, 9999),
                    "title": tech_title,
                    "original_title": clean_title,
                    "category": "cronaca",
                    "province": "AN" if "Ancona" in clean_title or "Ancona" in summary_text else "MC" if "Macerata" in clean_title else "FM" if "Fermo" in clean_title else "PU" if "Pesaro" in clean_title else "AP" if "Ascoli" in clean_title else "MARCHE",
                    "tag": "RADAR_LIVE",
                    "author": f"Agent_{source['name'].replace(' ', '_')}",
                    "date": datetime.now().strftime("%d %b %Y %H:%M").upper(),
                    "image": image_url,
                    "size": "normal",
                    "summary": summary_text[:300] + "...", # Più lungo
                    "source_url": entry.link,
                    "source_name": source['name']
                }
                all_news.append(news_item)
        except Exception as e:
            print(f"Errore su {source['name']}: {e}")
    
    random.shuffle(all_news)
    return all_news[:15] # Mostra più notizie

def update_dynamic_content():
    # Ruota Curiosità
    cur = random.choice(CURIOSITIES)
    with open(CURIOSITY_FILE, 'w', encoding='utf-8') as f:
        json.dump(cur, f, indent=4)
        
    # Ruota Ricetta
    rec = random.choice(RECIPES)
    # Mantieni la struttura complessa per la ricetta (simulata)
    rec_full = {
        **rec,
        "img": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c",
        "ingredients": ["Ingredienti freschi locali", "Olio EVO Marche", "Passione artigianale"],
        "steps": ["Preparazione materie prime", "Cottura lenta", "Impiattamento tech"]
    }
    with open(RECIPE_FILE, 'w', encoding='utf-8') as f:
        json.dump(rec_full, f, indent=4)

def main():
    news = fetch_rss_news()
    if news:
        with open(NEWS_FILE, 'w', encoding='utf-8') as f:
            json.dump(news, f, indent=4)
        print(f"Notizie aggiornate: {len(news)} elementi caricati.")
    
    update_dynamic_content()
    print(f"Contenuti quotidiani ruotati.")

if __name__ == "__main__":
    main()
