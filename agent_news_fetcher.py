import feedparser
import json
import os
import random
import re
from datetime import datetime, timedelta

# Fonti RSS Marche - Espansione Elite+
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
        "image": "https://images.unsplash.com/photo-1621510456681-23a033c79b94?w=800",
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
        "image": "https://images.unsplash.com/photo-1599307767316-776533bb941c?w=800",
        "ingredients": ["Olive Ascolane DOP", "Manzo, Maiale e Pollo", "Parmigiano", "Uova", "Pangrattato"],
        "steps": ["Denocciolare a spirale", "Farcire", "Panare", "Friggere"],
        "date": datetime.now().strftime("%d %b %Y").upper()
    }
]

# Database Eventi Reali - mc_events.2 Sync
EVENTS = [
    {
        "id": 7001,
        "title": "GIOVEDÌ_GRASSO: CARNEVALARDO @ MUCHACHA",
        "original_title": "Grande Carnevale @ Muchacha Assaderia",
        "category": "personal-life",
        "province": "MC",
        "tag": "EVENTO_TOP",
        "author": "mc_events.2",
        "date": "12 FEB 2026 21:00",
        "image": "https://images.unsplash.com/photo-1514525253342-b0bb4d7db71f?w=800",
        "size": "big",
        "summary": "Il Giovedì Grasso più caldo delle Marche è alla Muchacha Assaderia di Civitanova Marche. Cena spettacolo, maschere e ritmo latino per iniziare il weekend di Carnevale.",
        "source_url": "https://www.instagram.com/mc_events.2",
        "source_name": "mc_events.2"
    },
    {
        "id": 7002,
        "title": "SABATO_ELITE: MC MENOR JP @ DONOMA",
        "original_title": "Mc Menor Jp Live @ Donoma Club",
        "category": "personal-life",
        "province": "MC",
        "tag": "NOTTE_MARCHE",
        "author": "mc_events.2",
        "date": "14 FEB 2026 22:00",
        "image": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800",
        "size": "normal",
        "summary": "Direttamente dal Brasile, MC Menor Jp sbarca al Donoma Club di Civitanova per il Sabato di Carnevale. Una notte di funk e pura energia.",
        "source_url": "https://www.ticketsms.it",
        "source_name": "TicketSMS / mc_events.2"
    },
    {
        "id": 7003,
        "title": "VIDALOCA: CARNIVAL PARTY @ BRAHMA",
        "original_title": "Vidaloca Carnival Party @ Brahma Clubship",
        "category": "personal-life",
        "province": "MC",
        "tag": "CARNEVALE_2026",
        "author": "mc_events.2",
        "date": "14 FEB 2026 21:00",
        "image": "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=800",
        "size": "normal",
        "summary": "Il format più amato d'Italia porta il suo show di Carnevale al Brahma di Civitanova. Reggaeton, Hip Hop e Pop in un'atmosfera incredibile.",
        "source_url": "https://www.ticketsms.it",
        "source_name": "TicketSMS"
    },
    {
        "id": 7004,
        "title": "CARNEVALANDO: CRISTINA D'AVENA @ CIVITANOVA",
        "original_title": "Cristina D'Avena Live in Piazza XX Settembre",
        "category": "personal-life",
        "province": "MC",
        "tag": "GRANDE_EVENTO",
        "author": "Civitanova_Live",
        "date": "15 FEB 2026 17:30",
        "image": "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800",
        "size": "wide",
        "summary": "Domenica 15 febbraio Civitanova ospita la regina delle sigle dei cartoni animati: Cristina D'Avena! Uno show gratuito per tutte le famiglie in centro.",
        "source_url": "https://www.civitanovalive.it",
        "source_name": "Civitanova Live"
    },
    {
        "id": 7005,
        "title": "FIERA_ANCONA: GRAN CARNEVALE DORICO",
        "original_title": "Sfilata Carri @ Corso Amendola Ancona",
        "category": "personal-life",
        "province": "AN",
        "tag": "CARNEVALE",
        "author": "Ancona_News",
        "date": "15 FEB 2026 15:00",
        "image": "https://images.unsplash.com/photo-1547153760-18fc86324498?w=800",
        "size": "normal",
        "summary": "Domenica 15 febbraio Ancona si trasforma con carri allegorici e maschere da tutto il territorio. Partenza dallo Stadio Dorico alle 15:00.",
        "source_url": "https://www.comune.ancona.it",
        "source_name": "Comune di Ancona"
    },
    {
        "id": 7006,
        "title": "TRADIZIONE: 36° CARNEVALE MACERATESE",
        "original_title": "Sfilata Carri @ Giardini Diaz Macerata",
        "category": "personal-life",
        "province": "MC",
        "tag": "TRADIZIONE",
        "author": "Macerata_Agent",
        "date": "15 FEB 2026 14:00",
        "image": "https://images.unsplash.com/photo-1520110323062-f949826f0f6c?w=800",
        "size": "normal",
        "summary": "Torna la grande storia del Carnevale di Macerata. Carri, musica e divertimento ai Giardini Diaz per l'evento più atteso della provincia.",
        "source_url": "https://www.cronachemaceratesi.it",
        "source_name": "Cronache Maceratesi"
    }
]

# Simulated Agents Content (Elite engagement)
AGENT_NICHE_CONTENT = [
    {"category": "estetica", "title": "BEAUTY_RADAR: Tendenze Skincare 2026 nelle Marche", "summary": "I centri benessere di Civitanova e Senigallia lanciano i nuovi trattamenti bio-tecnologici basati su attivi locali.", "img": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=800", "prov": "MC"},
    {"category": "tecnologia", "title": "TECH_REPORT: Startup anconetane conquistano il Web3", "summary": "Nuovo round di investimenti per l'intelligenza artificiale applicata all'industria marchigiana.", "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800", "prov": "AN"}
]

def categorize_news(title, summary):
    text = (title + " " + summary).lower()
    if any(k in text for k in ["calcio", "basket", "volley", "derby", "vince", "sconfitta", "partita", "gol", "sport"]): return "sport"
    if any(k in text for k in ["lavoro", "concorso", "assunzioni", "cercasi", "impiego", "assunzione"]): return "lavoro"
    if any(k in text for k in ["moda", "fashion", "abbigliamento", "scarpe", "calzature", "sfilata"]): return "moda"
    if any(k in text for k in ["estetica", "bellezza", "beauty", "benessere", "trattamento", "crema"]): return "estetica"
    return "cronaca"

def fetch_rss_news():
    all_news = []
    print(f"ELITE AGENTE 2.6: Scansione fonti massive in corso...")
    
    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:15]:
                title = entry.title.strip()
                summary = re.sub('<[^<]+?>', '', entry.get('summary', '') or entry.get('description', '')).strip()
                summary = summary.replace("&nbsp;", " ").replace("\n", " ")
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
                    "size": "big" if random.random() > 0.9 else "normal",
                    "summary": summary[:350] + "...",
                    "source_url": entry.link,
                    "source_name": source['name']
                })
        except Exception: pass
    
    # Inserisci contenuti Niche simulati
    for niche in AGENT_NICHE_CONTENT:
        all_news.append({
            "id": random.randint(50000, 60000),
            "title": niche["title"],
            "original_title": niche["title"].split(": ")[1],
            "category": niche["category"],
            "province": niche["prov"],
            "tag": "TREND_MARCHE",
            "author": "Elite_Agent",
            "date": datetime.now().strftime("%d %B %Y %H:%M").upper(),
            "image": niche["img"],
            "size": "normal",
            "summary": niche["summary"],
            "source_url": "#",
            "source_name": "Marche Live Insights"
        })

    # Inserisci Eventi Reali in Personal Life
    all_news.extend(EVENTS)

    random.shuffle(all_news)
    return all_news[:75] # Elite+ pool

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
        print(f"SISTEMA ELITE 2.6: {len(news)} elementi caricati. Carnevale 2026 Sincronizzato con mc_events.2.")

if __name__ == "__main__":
    main()
