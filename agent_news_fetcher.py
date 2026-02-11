import feedparser
import json
import os
import random
import re
from datetime import datetime

# Fonti RSS Marche - Espansione massiva per Elite Phase
RSS_SOURCES = [
    {"name": "Ansa Marche", "url": "https://www.ansa.it/marche/notizie/marche_rss.xml"},
    {"name": "Cronache Maceratesi", "url": "https://www.cronachemaceratesi.it/feed/"},
    {"name": "Cronache Ancona", "url": "https://www.cronacheancona.it/feed/"},
    {"name": "Cronache Picene", "url": "https://www.cronachepicene.it/feed/"},
    {"name": "Cronache Fermane", "url": "https://www.cronachefermane.it/feed/"},
    {"name": "Vivere Ancona", "url": "https://www.vivereancona.it/rss/index.xml"},
    {"name": "Vivere Pesaro", "url": "https://www.viverepesaro.it/rss/index.xml"},
    {"name": "Vivere Civitanova", "url": "https://www.viverecivitanova.it/rss/index.xml"},
    {"name": "Regione Marche News", "url": "https://www.regione.marche.it/News-ed-Eventi?rss=1"},
    {"name": "Marche Sport", "url": "https://www.marchesport.info/feed/"},
    {"name": "YouTVRS", "url": "https://youtvrs.it/feed/"},
    {"name": "Picchio News", "url": "https://picchionews.it/feed/"}
]

NEWS_FILE = "news.json"
RECIPE_FILE = "recipe.json"
CURIOSITY_FILE = "curiosity.json"

# Database Reale ed Eccellenze Marchigiane (Elite Quality)
CURIOSITIES = [
    {
        "id": 9001,
        "title": "Ancona: Il Sole tra due Mari", 
        "category": "curiosita",
        "tag": "CURIOSITÀ",
        "province": "AN",
        "content": "Ancona è l'unica città adriatica dove si può vedere il sole sorgere e tramontare sul mare, grazie alla forma a gomito del promontorio del Conero.", 
        "image": "https://images.unsplash.com/photo-1544085311-11a028465b03?w=800",
        "date": datetime.now().strftime("%d %b %Y").upper()
    },
    {
        "id": 9002,
        "title": "Le Grotte di Frasassi", 
        "category": "curiosita",
        "tag": "CURIOSITÀ",
        "province": "AN",
        "content": "L'Abisso Ancona è così vasto che potrebbe contenere comodamente il Duomo di Milano. Sono tra le grotte più spettacolari d'Europa.", 
        "image": "https://images.unsplash.com/photo-1502759683299-cdcd6974244f?w=800",
        "date": datetime.now().strftime("%d %b %Y").upper()
    },
    {
        "id": 9003,
        "title": "Il Tempio del Valadier", 
        "category": "curiosita",
        "tag": "CURIOSITÀ",
        "province": "AN",
        "content": "Costruito nel 1828 dentro una grotta, questo tempio ottagonale è un capolavoro del neoclassicismo incastonato nella roccia.", 
        "image": "https://images.unsplash.com/photo-1528114039593-4366cc08227d?w=800",
        "date": datetime.now().strftime("%d %b %Y").upper()
    }
]

RECIPES = [
    {
        "id": 8001,
        "title": "Vincisgrassi Maceratesi",
        "category": "ricette",
        "tag": "ECCELLENZA",
        "province": "MC",
        "summary": "Il 'lasagna' delle Marche. Un piatto ricco con un ragù di carni tagliate al coltello e durelli di pollo.",
        "wine": "Rosso Conero Riserva DOCG",
        "image": "https://images.unsplash.com/photo-1619895092538-1283417871fa?w=800",
        "ingredients": ["Pasta all'uovo (12 tuorli)", "Manzo e maiale", "Fegatini e durelli di pollo", "Besciamella", "Parmigiano"],
        "steps": ["Preparare il ragù (4 ore)", "Sbollentare la pasta", "Stratificare", "Infornare"],
        "date": datetime.now().strftime("%d %b %Y").upper()
    },
    {
        "id": 8002,
        "title": "Olive all'Ascolana DOP",
        "category": "ricette",
        "tag": "ECCELLENZA",
        "province": "AP",
        "summary": "Olive tenere ascolane farcite con carni miste, panate e fritte. Un simbolo mondiale del Piceno.",
        "wine": "Offida Passerina DOCG",
        "image": "https://images.unsplash.com/photo-1541529086526-db283c563270?w=800",
        "ingredients": ["Olive Ascolane DOP", "Manzo, Maiale e Pollo", "Parmigiano", "Uova", "Pangrattato"],
        "steps": ["Denocciolare a spirale", "Farcire", "Panare", "Friggere"],
        "date": datetime.now().strftime("%d %b %Y").upper()
    },
    {
        "id": 8003,
        "title": "Brodetto all'Anconetana",
        "category": "ricette",
        "tag": "ECCELLENZA",
        "province": "AN",
        "summary": "Zuppa di pesce tradizionale con 13 varietà di pescato, pomodoro e pane abbrustolito.",
        "wine": "Verdicchio dei Castelli di Jesi Classico",
        "image": "https://images.unsplash.com/photo-1534080564617-38290f6d0f8d?w=800",
        "ingredients": ["13 tipi di pesce", "Pomodoro", "Pane casereccio", "Olio EVO", "Vino bianco"],
        "steps": ["Pulire il pesce", "Soffriggere gli odori", "Aggiungere i pesci in ordine", "Servire su pane"],
        "date": datetime.now().strftime("%d %b %Y").upper()
    }
]

# Simulated Agents Content for missing niches (Elite engagement)
AGENT_NICHE_CONTENT = [
    {"category": "estetica", "title": "BEAUTY_RADAR: Tendenze Skincare 2026 nelle Marche", "summary": "I centri benessere di Civitanova e Senigallia lanciano i nuovi trattamenti bio-tecnologici.", "img": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=800", "prov": "MC"},
    {"category": "moda", "title": "FASHION_WEEK_MARCHE: Il distretto calzaturiero si rinnova", "summary": "Da Fermo a Civitanova, le eccellenze della scarpa puntano sull'eco-sostenibilità digitale.", "img": "https://images.unsplash.com/photo-1539109132304-39155024040c?w=800", "prov": "FM"},
    {"category": "tecnologia", "title": "TECH_REPORT: Startup anconetane conquistano il Web3", "summary": "Nuovo round di investimenti per la cybersecurity nelle università marchigiane.", "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800", "prov": "AN"}
]

def categorize_news(title, summary):
    text = (title + " " + summary).lower()
    if any(k in text for k in ["calcio", "basket", "volley", "derby", "vince", "sconfitta", "partita", "gol", "sport"]): return "sport"
    if any(k in text for k in ["lavoro", "concorso", "assunzioni", "cercasi", "impiego"]): return "lavoro"
    if any(k in text for k in ["tecnologia", "hi-tech", "internet", "startup", "innovazione"]): return "tecnologia"
    if any(k in text for k in ["moda", "fashion", "abbigliamento", "scarpe"]): return "moda"
    if any(k in text for k in ["estetica", "bellezza", "beauty", "benessere"]): return "estetica"
    return "cronaca"

def fetch_rss_news():
    all_news = []
    print(f"ELITE AGENTE: Scansione fonti massive in corso...")
    
    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:12]:
                title = entry.title.strip()
                summary = re.sub('<[^<]+?>', '', entry.get('summary', '') or entry.get('description', '')).strip()
                cat = categorize_news(title, summary)
                
                image_url = "https://images.unsplash.com/photo-1501183638710-841dd1904471?w=800"
                if 'media_content' in entry: image_url = entry.media_content[0]['url']
                elif 'links' in entry:
                    for link in entry.links:
                        if 'image' in link.get('type', ''): image_url = link.href

                all_news.append({
                    "id": random.randint(1000, 9999),
                    "title": f"{cat.upper()}_UPDATE: {title.upper().replace(' ', '_')}",
                    "original_title": title,
                    "category": cat,
                    "province": "AN" if "Ancona" in title+summary else "MC" if "Macerata" in title+summary or "Civitanova" in title+summary else "FM" if "Fermo" in title+summary else "PU" if "Pesaro" in title+summary else "AP" if "Ascoli" in title+summary else "MARCHE",
                    "tag": "RADAR_LIVE",
                    "author": f"Agent_{source['name'].replace(' ', '_')}",
                    "date": datetime.now().strftime("%d %B %Y %H:%M").upper(),
                    "image": image_url,
                    "size": "big" if random.random() > 0.85 else "normal",
                    "summary": summary[:320] + "...",
                    "source_url": entry.link,
                    "source_name": source['name']
                })
        except Exception: pass
    
    # Inserisci contenuti Niche simulati dagli agenti
    for niche in AGENT_NICHE_CONTENT:
        all_news.append({
            "id": random.randint(50000, 60000),
            "title": niche["title"],
            "original_title": niche["title"].split(": ")[1],
            "category": niche["category"],
            "province": niche["prov"],
            "tag": "AGENT_SCAN",
            "author": "Elite_Agent",
            "date": datetime.now().strftime("%d %B %Y %H:%M").upper(),
            "image": niche["img"],
            "size": "normal",
            "summary": niche["summary"],
            "source_url": "#",
            "source_name": "Marche Live Radar"
        })

    random.shuffle(all_news)
    return all_news[:60] # Elite pool

def main():
    news = fetch_rss_news()
    if news:
        final_data = {
            "last_update": datetime.now().strftime("%H:%M:%S"),
            "articles": news,
            "all_recipes": RECIPES,
            "all_curiosities": CURIOSITIES
        }
        with open(NEWS_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4)
        
        # Save daily spotlight (backward compatibility)
        with open(RECIPE_FILE, 'w', encoding='utf-8') as f: json.dump(RECIPES[0], f, indent=4)
        with open(CURIOSITY_FILE, 'w', encoding='utf-8') as f: json.dump(CURIOSITIES[0], f, indent=4)
        
        print(f"SISTEMA ELITE: {len(news)} elementi caricati, Ricette e Curiosità sincronizzate.")

if __name__ == "__main__":
    main()
