import feedparser
import json
import os
import random
import re
from datetime import datetime

# Fonti RSS Marche - Espandiamo per coprire Sport, Lavoro e Istituzioni
RSS_SOURCES = [
    {"name": "Ansa Marche", "url": "https://www.ansa.it/marche/notizie/marche_rss.xml"},
    {"name": "Cronache Maceratesi", "url": "https://www.cronachemaceratesi.it/feed/"},
    {"name": "Cronache Ancona", "url": "https://www.cronacheancona.it/feed/"},
    {"name": "Cronache Picene", "url": "https://www.cronachepicene.it/feed/"},
    {"name": "Cronache Fermane", "url": "https://www.cronachefermane.it/feed/"},
    {"name": "Vivere Ancona", "url": "https://www.vivereancona.it/rss/index.xml"},
    {"name": "Vivere Pesaro", "url": "https://www.viverepesaro.it/rss/index.xml"},
    {"name": "Regione Marche News", "url": "https://www.regione.marche.it/News-ed-Eventi?rss=1"},
    {"name": "Marche Sport", "url": "https://www.marchesport.info/feed/"},
    {"name": "Centro Impiego Marche", "url": "https://www.regione.marche.it/Entra-in-Regione/Centri-Impiego?rss=1"}
]

NEWS_FILE = "news.json"
RECIPE_FILE = "recipe.json"
CURIOSITY_FILE = "curiosity.json"

# Database locale per rotazione (Reali ed eccellenze marchigiane)
CURIOSITIES = [
    {
        "title": "Ancona: Il Solo Sorgere e Tramontare", 
        "content": "Ancona è l'unica città adriatica dove si può vedere il sole sorgere e tramontare sul mare, grazie alla forma a gomito del promontorio del Conero.", 
        "img": "https://images.unsplash.com/photo-1544085311-11a028465b03?w=800"
    },
    {
        "title": "La Grotta della Sibilla", 
        "content": "Sui Monti Sibillini, a 2173 metri, si trova la grotta dove leggenda vuole vivesse la Sibilla Appenninica, profetessa amata da cavalieri di tutta Europa.", 
        "img": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800"
    },
    {
        "title": "Il Tempio del Valadier", 
        "content": "A Genga, incastonato in una grotta, sorge un maestoso tempio ottagonale in travertino, voluto da Papa Leone XII e progettato dal celebre architetto Valadier.", 
        "img": "https://images.unsplash.com/photo-1528114039593-4366cc08227d?w=800"
    },
    {
        "title": "L'Infinito di Leopardi", 
        "content": "Giacomo Leopardi scrisse 'L'Infinito' a soli 21 anni sul monte Tabor a Recanati, guardando verso i Monti Sibillini.", 
        "img": "https://images.unsplash.com/photo-1505673542670-a11e2f92419c?w=800"
    }
]

RECIPES = [
    {
        "title": "Vincisgrassi alla Maceratese",
        "summary": "Il 'lasagna' delle Marche. Un piatto ricco, sontuoso, con un ragù di carni tagliate al coltello e durelli di pollo.",
        "wine": "Rosso Conero Riserva DOCG",
        "img": "https://images.unsplash.com/photo-1619895092538-1283417871fa?w=800",
        "ingredients": ["Pasta all'uovo (12 tuorli)", "Manzo e maiale", "Fegatini e durelli di pollo", "Besciamella densa", "Parmigiano Reggiano stagionato"],
        "steps": ["Preparare il ragù con cotturura lenta (4 ore)", "Sbollentare i fogli di pasta", "Stratificare con abbondante condimento", "Cuocere in forno finché non si forma una crosticina croccante"]
    },
    {
        "title": "Olive all'Ascolana del Piceno",
        "summary": "Olive tenere ascolane DOP farcite con un impasto di tre carni diverse, panate e fritte. Un'opera d'arte artigianale.",
        "wine": "Offida Passerina DOCG",
        "img": "https://images.unsplash.com/photo-1541529086526-db283c563270?w=800",
        "ingredients": ["Olive tenere Ascolane DOP", "Manzo, Maiale e Pollo", "Parmigiano", "Uova e pangrattato", "Scorza di limone e noce moscata"],
        "steps": ["Denocciolare l'oliva a spirale", "Preparare il ripieno cotto e macinato", "Farcire l'oliva ridandole la forma", "Doppia panatura e frittura in olio bollente"]
    },
    {
        "title": "Stoccafisso all'Anconetana",
        "summary": "Piatto simbolo della città dorica. Lo stoccafisso varietà Ragno cotto lentamente con pomodoro, patate e abbondante olio EVO.",
        "wine": "Verdicchio dei Castelli di Jesi Classico Superiore",
        "img": "https://images.unsplash.com/photo-1534939561126-3657662e2239?w=800",
        "ingredients": ["Stoccafisso varietà Ragno", "Patate gialle", "Pomodori pelati", "Acciughe e capperi", "Olio Extravergine d'Oliva delle Marche"],
        "steps": ["Pulire e tagliare lo stoccafisso", "Disporre su un letto di odori e patate", "Coprire con olio e pomodoro", "Cuocere a fuoco lentissimo senza mai mescolare"]
    }
]

# Generatore Offerte Lavoro
JOB_ROLES = ["Web Developer", "Cuoco di linea", "Addetto Vendite", "Social Media Manager", "Manutentore Meccanico", "Impiegato Amministrativo", "Graphic Designer", "Barman"]
COMPANIES = ["TechMarche Srl", "Hotel Conero Luxury", "Boutique Civitanova", "Agenzia Digital Ancona", "Meccanica Picena", "Studio Associato Fermo"]
LOCATIONS = ["Civitanova Marche", "Ancona", "Macerata", "Pesaro", "Ascoli Piceno", "Fermo", "Senigallia", "Fano"]

def categorize_news(title, summary):
    text = (title + " " + summary).lower()
    if any(k in text for k in ["calcio", "basket", "volley", "derby", "vince", "sconfitta", "classifica", "sport", "serie a", "serie b", "serie c"]):
        return "sport"
    if any(k in text for k in ["lavoro", "concorso", "assunzioni", "cercasi", "opportunità", "impiego", "professione"]):
        return "lavoro"
    if any(k in text for k in ["tecnologia", "digitale", "hi-tech", "internet", "startup", "innovazione", "software"]):
        return "tecnologia"
    if any(k in text for k in ["moda", "fashion", "abbigliamento", "stile", "sfilata"]):
        return "moda"
    if any(k in text for k in ["estetica", "bellezza", "beauty", "benessere", "wellness"]):
        return "estetica"
    return "cronaca"

def generate_job_offers():
    jobs = []
    for _ in range(5):
        role = random.choice(JOB_ROLES)
        company = random.choice(COMPANIES)
        loc = random.choice(LOCATIONS)
        jobs.append({
            "id": random.randint(10000, 99999),
            "title": f"OFFERTA_LAVORO: {role.upper()} @ {company.upper()}",
            "original_title": f"Cercasi {role} a {loc}",
            "category": "lavoro",
            "province": "MC" if "Civitanova" in loc or "Macerata" in loc else "AN" if "Ancona" in loc or "Senigallia" in loc else "PU" if "Pesaro" in loc or "Fano" in loc else "AP" if "Ascoli" in loc else "FM",
            "tag": "LAVORO_LIVE",
            "author": "Marche_Job_Agent",
            "date": datetime.now().strftime("%d %B %Y %H:%M").upper(),
            "image": "https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=800",
            "size": "normal",
            "summary": f"Importante realtà di {loc} ({company}) seleziona urgentemente {role}. Contratto a tempo indeterminato, ambiente dinamico e possibilità di crescita professionale.",
            "source_url": "https://www.regione.marche.it/Entra-in-Regione/Centri-Impiego",
            "source_name": "Centri Impiego Marche"
        })
    return jobs

def fetch_rss_news():
    all_news = []
    print(f"AGENTE: Scansione fonti RSS professionali in corso...")
    
    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:10]:
                clean_title = entry.title.strip()
                summary_text = entry.get('summary', '') or entry.get('description', '')
                summary_text = re.sub('<[^<]+?>', '', summary_text).strip().replace("&nbsp;", " ").replace("\n", " ")
                
                cat = categorize_news(clean_title, summary_text)
                
                # Tech title formatting
                tech_title = clean_title.upper().replace(" ", "_")
                if ":" not in tech_title:
                    tech_title = f"{cat.upper()}_UPDATE: {tech_title}"
                
                # Image extraction
                image_url = "https://images.unsplash.com/photo-1444653300602-7609d665975b?w=800"
                if 'media_content' in entry:
                    image_url = entry.media_content[0]['url']
                elif 'links' in entry:
                    for link in entry.links:
                        if 'image' in link.get('type', ''):
                            image_url = link.href
                
                news_item = {
                    "id": random.randint(1000, 9999),
                    "title": tech_title,
                    "original_title": clean_title,
                    "category": cat,
                    "province": "AN" if "Ancona" in clean_title or "Ancona" in summary_text else "MC" if "Macerata" in clean_title or "Civitanova" in clean_title else "FM" if "Fermo" in clean_title else "PU" if "Pesaro" in clean_title or "Urbino" in clean_title else "AP" if "Ascoli" in clean_title else "MARCHE",
                    "tag": "RADAR_LIVE" if cat != "lavoro" else "LAVORO_LIVE",
                    "author": f"Agent_{source['name'].replace(' ', '_')}",
                    "date": datetime.now().strftime("%d %B %Y %H:%M").upper(),
                    "image": image_url,
                    "size": "big" if random.random() > 0.8 else "normal", # Alcune grandi a caso
                    "summary": summary_text[:350] + "...",
                    "source_url": entry.link,
                    "source_name": source['name']
                }
                all_news.append(news_item)
        except Exception as e:
            print(f"Errore su {source['name']}: {e}")
    
    # Mix news with jobs
    jobs = generate_job_offers()
    all_news.extend(jobs)
    
    random.shuffle(all_news)
    return all_news[:25] # Più contenuti in totale

def update_dynamic_content():
    # Ruota Curiosità
    cur = random.choice(CURIOSITIES)
    with open(CURIOSITY_FILE, 'w', encoding='utf-8') as f:
        json.dump(cur, f, indent=4)
        
    # Ruota Ricetta
    rec = random.choice(RECIPES)
    with open(RECIPE_FILE, 'w', encoding='utf-8') as f:
        json.dump(rec, f, indent=4)

def main():
    news = fetch_rss_news()
    if news:
        # Aggiungiamo metadati globali
        final_data = {
            "last_update": datetime.now().strftime("%H:%M:%S"),
            "articles": news
        }
        with open(NEWS_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4)
        print(f"Notizie e Lavoro aggiornati: {len(news)} elementi caricati.")
    
    update_dynamic_content()
    print(f"Curiosità e Ricette reali aggiornate.")

if __name__ == "__main__":
    main()
