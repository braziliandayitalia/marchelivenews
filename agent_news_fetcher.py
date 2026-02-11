import feedparser
import json
import os
import random
import re
from datetime import datetime, timedelta

# Fonti RSS Marche - Elite+
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

# Database Reale ed Eccellenze Marchigiane
CURIOSITIES = [
    {
        "id": 9001,
        "title": "Ancona: Il Sole tra due Mari", 
        "category": "curiosita", "tag": "CURIOSITÀ", "province": "AN",
        "content": "Ancona è l'unica città adriatica dove si può vedere il sole sorgere e tramontare sul mare, grazie alla forma a gomito del promontorio del Conero.", 
        "image": "https://images.unsplash.com/photo-1544085311-11a028465b03?w=800",
        "date": datetime.now().strftime("%d %b %Y").upper()
    },
    {
        "id": 9002, "title": "Le Grotte di Frasassi", 
        "category": "curiosita", "tag": "CURIOSITÀ", "province": "AN",
        "content": "L'Abisso Ancona è così vasto che potrebbe contenere comodamente il Duomo di Milano. Sono tra le grotte più spettacolari d'Europa.", 
        "image": "https://images.unsplash.com/photo-1502759683299-cdcd6974244f?w=800",
        "date": datetime.now().strftime("%d %b %Y").upper()
    }
]

RECIPES = [
    {
        "id": 8001, "title": "Vincisgrassi Maceratesi",
        "category": "ricette", "tag": "ECCELLENZA", "province": "MC",
        "summary": "Il 'lasagna' delle Marche. Un piatto ricco con un ragù di carni tagliate al coltello.",
        "wine": "Rosso Conero Riserva DOCG",
        "image": "https://images.unsplash.com/photo-1621510456681-23a033c79b94?w=800",
        "ingredients": ["Pasta all'uovo", "Manzo e maiale", "Fegatini", "Besciamella"],
        "steps": ["Preparare il ragù", "Sbollentare la pasta", "Stratificare", "Infornare"],
        "date": datetime.now().strftime("%d %b %Y").upper()
    }
]

# EVENTI SPECIALI CON SCADENZA (User Request)
SPECIAL_PROMOS = [
    {
        "id": 100000,
        "title": "RIO_PARTY: CARNEVALE ALLA MUCHACHA",
        "original_title": "Giovedì 12 Febbraio – Carnevale alla Churrascaria Muchacha",
        "category": "personal-life",
        "province": "MC",
        "tag": "EVENTO_TOP_MARCHE",
        "author": "Rubinho_Elite",
        "date": "12 FEB 20:30",
        "image": "./muchacha_event.jpg", # Nota: l'utente deve salvare l'immagine con questo nome nella root
        "size": "big",
        "summary": "🎭 Giovedì 12 Febbraio – Carnevale alla Churrascaria Muchacha. Cena & Dopocena con DJ set. Menù donna: 20€. Lungomare Sergio Piermanni 13, Civitanova Marche. 📞 0733 1826409. Siete tutti invitati! Maschere, musica e vibes 🔥",
        "source_url": "https://www.instagram.com/muchacha_asaderia?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw==",
        "source_name": "Muchacha Instagram",
        "redirect": True,
        "expires": "2026-02-13 09:00" # Formato: YYYY-MM-DD HH:MM
    }
]

# Database Eventi Reali generici
EVENTS = [
    {
        "id": 7002, "title": "SABATO_ELITE: MC MENOR JP @ DONOMA",
        "original_title": "Mc Menor Jp Live @ Donoma Club",
        "category": "personal-life", "province": "MC", "tag": "NOTTE_MARCHE",
        "author": "mc_events.2", "date": "14 FEB 2026 22:00",
        "image": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800",
        "size": "normal", "summary": "Mc Menor Jp al Donoma Club di Civitanova per il Sabato di Carnevale.",
        "source_url": "https://www.ticketsms.it", "source_name": "TicketSMS"
    },
    {
        "id": 7003, "title": "VIDALOCA: CARNIVAL PARTY @ BRAHMA",
        "original_title": "Vidaloca Carnival Party @ Brahma Clubship",
        "category": "personal-life", "province": "MC", "tag": "CARNEVALE_2026",
        "author": "mc_events.2", "date": "14 FEB 2026 21:00",
        "image": "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=800",
        "size": "normal", "summary": "Vidaloca Carnival Party al Brahma di Civitanova. Reggaeton e DanceHall.",
        "source_url": "https://www.ticketsms.it", "source_name": "TicketSMS"
    },
    {
        "id": 7004, "title": "CRISTINA_DAVENA: CARNEVALANDO @ CIVITANOVA",
        "original_title": "Cristina D'Avena Live in Piazza XX Settembre",
        "category": "personal-life", "province": "MC", "tag": "GRANDE_EVENTO",
        "author": "Civitanova_Live", "date": "15 FEB 2026 17:30",
        "image": "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800",
        "size": "wide", "summary": "Domenica 15 febbraio show gratuito in Piazza XX Settembre.",
        "source_url": "https://www.civitanovalive.it", "source_name": "Civitanova Live"
    }
]

def categorize_news(title, summary):
    text = (title + " " + summary).lower()
    if any(k in text for k in ["calcio", "basket", "volley", "derby", "gol"]): return "sport"
    if any(k in text for k in ["lavoro", "concorso", "assunzioni"]): return "lavoro"
    if any(k in text for k in ["moda", "fashion"]): return "moda"
    if any(k in text for k in ["estetica", "beauty"]): return "estetica"
    return "cronaca"

def fetch_rss_news():
    all_news = []
    print(f"SISTEMA ELITE: Ciclo scansione attivo...")
    
    # Inserisci Promozioni Speciali se non scadute
    now = datetime.now()
    for promo in SPECIAL_PROMOS:
        if "expires" in promo:
            expire_time = datetime.strptime(promo["expires"], "%Y-%m-%d %H:%M")
            if now < expire_time:
                all_news.append(promo)
                print(f"PINNED: {promo['title']} aggiunto (Scade: {promo['expires']})")

    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:10]:
                title = entry.title.strip()
                summary = re.sub('<[^<]+?>', '', entry.get('summary', '') or entry.get('description', '')).strip()[:300]
                cat = categorize_news(title, summary)
                image_url = "https://images.unsplash.com/photo-1501183638710-841dd1904471?w=800"
                if 'media_content' in entry: image_url = entry.media_content[0]['url']

                all_news.append({
                    "id": random.randint(1000, 9999),
                    "title": f"{cat.upper()}_UPDATE: {title.upper().replace(' ', '_')}",
                    "original_title": title, "category": cat, "province": "MARCHE",
                    "tag": "RADAR_LIVE", "author": f"Agent_{source['name'].replace(' ', '_')}",
                    "date": datetime.now().strftime("%d %B %Y %H:%M").upper(),
                    "image": image_url, "size": "normal", "summary": summary + "...",
                    "source_url": entry.link, "source_name": source['name']
                })
        except Exception: pass
    
    all_news.extend(EVENTS)
    random.shuffle(all_news)
    return all_news[:70]

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
        print(f"SISTEMA ELITE: {len(news)} elementi pronti.")

if __name__ == "__main__":
    main()
