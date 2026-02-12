import feedparser
import json
import os
import random
import re
from datetime import datetime, timedelta

# Fonti RSS Marche - Elite+
import random
import re

# --- OPPORTUNITÀ EVERGREEN (Filler per Hub Lavoro se news fresche < 12) ---
JOB_FILLERS = [
    {"title": "REDAZIONE_OPEN: CERCASI REPORTER PER MARCHE LIVE", "summary": "Sei un appassionato di giornalismo o lifestyle? Marche Live cerca collaboratori sul territorio per raccontare le eccellenze regionali. Candidati ora!", "source_name": "Marche Live Redazione", "province": "MARCHE", "source_url": "#"},
    {"title": "SOCIAL_MANAGER: POSIZIONE APERTA SETTORE EVENTI", "summary": "Importante agenzia marchigiana cerca Social Media Manager per gestione eventi estivi. Richiesta conoscenza territorio e creatività.", "source_name": "Job Marche Elite", "province": "ANCONA", "source_url": "#"},
    {"title": "TECNICO_AUDIO: TOUR ESTIVO 2026 MARCHE", "summary": "Cercasi tecnico audio/luci per service regionale. Esperienza minima richiesta. Disponibilità weekend e flessibilità oraria.", "source_name": "Music & Sound Marche", "province": "MACERATA", "source_url": "#"},
    {"title": "AGENTI_VENDITA: ESPANSIONE RETE COMMERCIALE ADRIATICA", "summary": "Azienda leader nel settore servizi alle imprese seleziona 3 agenti per la costa marchigiana. Fisso garantito + provvigioni.", "source_name": "Business Network", "province": "PESARO", "source_url": "#"},
    {"title": "STAGE_FORMATIVO: DIGITAL MARKETING & AI", "summary": "Startup innovativa offre stage curriculare o extracurriculare in Digital Marketing con focus su AI generative applicate ai media.", "source_name": "Tech Hub Marche", "province": "CIVITANOVA", "source_url": "#"},
    {"title": "HOSTESS_STEWARD: EVENTI FIERISTICI FERMO", "summary": "Agenzia seleziona personale per accoglienza durante le fiere di marzo. Bella presenza e conoscenza inglese base.", "source_name": "Eventi Marche", "province": "FERMO", "source_url": "#"},
    {"title": "SOFTWARE_DEV: JUNIOR POSITION (FULL REMOTE)", "summary": "Azienda IT di Ascoli Piceno cerca sviluppatore JavaScript junior. Possibilità di lavoro 100% remoto. Formazione inclusa.", "source_name": "Cyber Marche Tech", "province": "ASCOLI", "source_url": "#"},
    {"title": "PERSONAL_LIFE_JOB: ASSISTENZA DOMESTICA ELITE", "summary": "Famiglia cerca assistente domestica referenziata per gestione villa e servizi. Richiesta massima serietà e discrezione.", "source_name": "Elite Services", "province": "MACERATA", "source_url": "#"},
    {"title": "CUOCO_TRADIZIONE: RISTORANTE TIPICO CERCA PERSONALE", "summary": "Rinomato locale dell'entroterra cerca cuoco specializzato in cucina marchigiana. Contratto stagionale con possibilità rinnovo.", "source_name": "Tavola Marche", "province": "ANCONA", "source_url": "#"}
]

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
    {"name": "Picchio News", "url": "https://picchionews.it/feed/"},
    # Sezione Lavoro - Fonti Dedicate
    {"name": "Vivere Ancona Lavoro", "url": "https://www.vivereancona.it/rss/lavoro.xml"},
    {"name": "Vivere Macerata Lavoro", "url": "https://www.viveremacerata.it/rss/lavoro.xml"},
    {"name": "Vivere Civitanova Lavoro", "url": "https://www.viverecivitanova.it/rss/lavoro.xml"},
    {"name": "Vivere Pesaro Lavoro", "url": "https://www.viverepesaro.it/rss/lavoro.xml"},
    {"name": "Vivere Fano Lavoro", "url": "https://www.viverefano.it/rss/lavoro.xml"},
    {"name": "Vivere Senigallia Lavoro", "url": "https://www.viveresenigallia.it/rss/lavoro.xml"},
    {"name": "Vivere Jesi Lavoro", "url": "https://www.viverejesi.it/rss/lavoro.xml"},
    {"name": "Vivere Recanati Lavoro", "url": "https://www.vivererecanati.it/rss/lavoro.xml"},
    {"name": "Vivere Fermo Lavoro", "url": "https://www.viverefermo.it/rss/lavoro.xml"},
    {"name": "Vivere Ascoli Lavoro", "url": "https://www.vivereascoli.it/rss/lavoro.xml"},
    {"name": "Vivere San Benedetto Lavoro", "url": "https://www.viveresanbenedetto.it/rss/lavoro.xml"},
    {"name": "Vivere Urbino Lavoro", "url": "https://www.vivereurbino.it/rss/lavoro.xml"},
    {"name": "CercoLavoro Marche", "url": "https://www.cercolavoro.com/rss/lavoro-marche.xml"},
    {"name": "AnconaToday Lavoro", "url": "https://www.anconatoday.it/rss/lavoro/"},
    {"name": "MacerataToday Lavoro", "url": "https://www.maceratatoday.it/rss/lavoro/"},
    {"name": "Concorsi Pubblici Marche", "url": "https://www.concorsipubblici.com/rss/regione/marche.xml"},
    {"name": "Concorsando Marche", "url": "https://www.concorsando.it/blog/category/concorsi-per-regione/marche/feed/"},
    {"name": "Marche Notizie Lavoro", "url": "https://www.marchenotizie.info/category/lavoro/feed/"},
    {"name": "Cronache Fermane Lavoro", "url": "https://www.cronachefermane.it/category/lavoro/feed/"},
    {"name": "Corriere Adriatico", "url": "https://www.corriereadriatico.it/rss/marche.xml"}
]

# Database Immagini Elite (per evitare ripetizioni)
IMAGE_POOLS = {
    "sport": [
        "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=800",
        "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800",
        "https://images.unsplash.com/photo-1519861531473-920026238cbf?w=800",
        "https://images.unsplash.com/photo-1461896704190-3213c9ad81e1?w=800",
        "https://images.unsplash.com/photo-1504450758481-7338ef75240f?w=800"
    ],
    "lavoro": [
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800",
        "https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=800",
        "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=800",
        "https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=800", # Meeting
        "https://images.unsplash.com/photo-1454165833267-035fafa85ea4?w=800"     # Laptop/Work
    ],
    "moda": [
        "https://images.unsplash.com/photo-1445205170230-053b83016050?w=800",
        "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=800",
        "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=800",
        "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=800", # Shop
        "https://images.unsplash.com/photo-1551232864-3f0890e580d9?w=800"     # Detail
    ],
    "estetica": [
        "https://images.unsplash.com/photo-1560750588-73207b1ef5b8?w=800",
        "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=800",
        "https://images.unsplash.com/photo-1512496011951-a09947573993?w=800",
        "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800"  # Salon
    ],
    "cronaca": [
        "https://images.unsplash.com/photo-1501183638710-841dd1904471?w=800",
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800",
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800",
        "https://images.unsplash.com/photo-1444653302762-80512c47ee5d?w=800"
    ],
    "incidente": [
        "https://images.unsplash.com/photo-1501700493717-360341ea22a3?w=800", # Sirene
        "https://images.unsplash.com/photo-1549480132-71d53e6836ca?w=800", # Road accident
        "https://images.unsplash.com/photo-1594220302568-15468846c243?w=800"  # Lights
    ],
    "meteo": [
        "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?w=800", # Cloud
        "https://images.unsplash.com/photo-1534088568595-a066f710b81f?w=800"  # Sea storm
    ]
}

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
        "image": "./muchacha_event.jpg",
        "size": "big",
        "summary": "🎭 Giovedì 12 Febbraio – Carnevale alla Churrascaria Muchacha. Cena & Dopocena con DJ set. Menù donna: 20€. Lungomare Sergio Piermanni 13, Civitanova Marche. 📞 0733 1826409. Siete tutti invitati! Maschere, musica e vibes 🔥",
        "source_url": "https://www.instagram.com/muchacha_asaderia?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw==",
        "source_name": "Muchacha Instagram",
        "redirect": True,
        "expires": "2026-02-13 09:00"
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
    
    # Esclusioni per evitare falsi positivi nel settore Lavoro (Cronaca mascherata)
    if any(k in text for k in ["arrestat", "denunciat", "sequestr", "cocaina", "droga", "furto", "rapina"]): 
        return "cronaca"

    # Nuove categorie specifiche per matching immagine
    if any(k in text for k in ["incidente", "scontro", "tamponamento", "vittima", "morto", "deceduto", "ferito"]): return "incidente"
    if any(k in text for k in ["meteo", "pioggia", "neve", "allerta", "vento", "grandine", "temporale"]): return "meteo"

    # Parole chiave Job Board potenziate
    if any(k in text for k in ["lavoro", "concorso", "assunzioni", "impiego", "cercasi", "offresi", "posto di lavoro", "hr ", "recruiting", "lavorare", "selezione personale", "tirocinio", "stage", "nuova apertura", "assume", "cerca personale", "bando", "graduatoria", "posti di", "cercano", "seleziona"]): return "lavoro"
    if any(k in text for k in ["calcio", "basket", "volley", "derby", "gol", "partita", "sport", "serie a", "serie b", "serie c"]): return "sport"
    if any(k in text for k in ["moda", "fashion", "abbigliamento", "boutique", "sfilata"]): return "moda"
    if any(k in text for k in ["estetica", "beauty", "trucco", "trattamento", "spa", "benessere"]): return "estetica"
    return "cronaca"

def get_smart_image(cat, title_text):
    # Usa l'hash del titolo per selezionare un'immagine in modo coerente e unico
    import hashlib
    h = int(hashlib.md5(title_text.encode()).hexdigest(), 16)
    pool = IMAGE_POOLS.get(cat, IMAGE_POOLS["cronaca"])
    return pool[h % len(pool)]

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

    item_count = random.randint(0, 100) # Seed casuale iniziale
    for source in RSS_SOURCES:
        try:
            # Se è una fonte dedicata al lavoro o concorsi, prendiamo più articoli
            limit = 25 if any(k in source['name'] for k in ["Lavoro", "Concorsi", "Concorsando", "Today"]) else 10
            print(f"DEBUG: Scansione {source['name']} (Limit: {limit})...")
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:limit]:
                title = entry.title.strip()
                summary = re.sub('<[^<]+?>', '', entry.get('summary', '') or entry.get('description', '')).strip()[:300]
                cat = categorize_news(title, summary)
                
                # Prova a estrarre immagine reale
                image_url = None
                if 'media_content' in entry: image_url = entry.media_content[0]['url']
                elif 'links' in entry:
                    for link in entry.links:
                        if 'image' in link.get('type', ''): 
                            image_url = link.href
                            break
                elif 'description' in entry:
                    # Cerca tag img nell'html della descrizione
                    img_match = re.search(r'<img src="([^"]+)"', entry.description)
                    if img_match: image_url = img_match.group(1)

                # Se non trovata, usa lo Smart Fallback basato sulla categoria e hash titolo
                if not image_url or "photo-1501183638710-841dd1904471" in image_url:
                    image_url = get_smart_image(cat, title)

                all_news.append({
                    "id": random.randint(1000, 99999),
                    "title": f"{cat.upper()}_UPDATE: {title.upper().replace(' ', '_')}",
                    "original_title": title, "category": cat, "province": "MARCHE",
                    "tag": "RADAR_LIVE", "author": f"Agent_{source['name'].replace(' ', '_')}",
                    "date": datetime.now().strftime("%d %B %Y %H:%M").upper(),
                    "image": image_url,
                    "size": "normal",
                    "summary": summary + "...",
                    "source_url": entry.link,
                    "source_name": source['name']
                })
                item_count += 1
                item_count += 1
        except Exception: pass
    
    all_news.extend(EVENTS)
    
    lavoro_news = [n for n in all_news if n['category'] == 'lavoro']
    
    # --- FILLER LOGIC: Se abbiamo poche news lavoro reali, aggiungiamo filler ---
    if len(lavoro_news) < 12:
        needed = 12 - len(lavoro_news)
        fillers = random.sample(JOB_FILLERS, min(needed, len(JOB_FILLERS)))
        for f in fillers:
            item_id = random.randint(10000, 99999)
            lavoro_news.append({
                "id": item_id,
                "title": f['title'],
                "original_title": f['title'],
                "category": "lavoro",
                "province": f['province'],
                "tag": "TARGET_OFFER",
                "author": "System_Filler",
                "date": datetime.now().strftime("%d %B %Y %H:%M").upper(),
                "image": get_smart_image("lavoro", f['title']),
                "size": "normal",
                "summary": f['summary'],
                "source_url": f['source_url'],
                "source_name": f['source_name']
            })

    other_news = [n for n in all_news if n['category'] != 'lavoro']
    
    random.shuffle(other_news)
    final_list = lavoro_news + other_news
    
    return final_list[:100] # Aumentato limite a 100 per ospitare più offerte

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
        print(f"SISTEMA ELITE: {len(news)} elementi pronti con Smart Image System attivo.")

if __name__ == "__main__":
    main()
