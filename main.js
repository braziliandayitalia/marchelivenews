let newsData = [];

async function loadNewsData() {
    try {
        const response = await fetch('news.json');
        newsData = await response.json();
        renderBentoGrid();
    } catch (error) {
        console.error('Errore nel caricamento notizie:', error);
    }
}

const curiosityData = {
    title: "Le Grotte di Frasassi: Un ecosistema unico al mondo",
    content: "Scoperte nel 1971, le Grotte di Frasassi ospitano l'Abisso Ancona, una cavità talmente vasta che potrebbe contenere il Duomo di Milano. Ma la vera curiosità è biologica: all'interno vivono specie animali uniche che non hanno mai visto la luce del sole, evolvendosi in isolamento totale per milioni di anni.",
    img: "img/marche_village.png"
};

const recipeData = {
    title: "Vincisgrassi: La Ricetta Originale del 1781",
    summary: "Il piatto più prestigioso della tradizione marchigiana, con ingredienti nobili e una preparazione cerimoniale.",
    img: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=400&q=80",
    wine: "Rosso Conero Riserva DOCG (Corposo, tannico, con note di marasca)",
    ingredients: [
        "1kg di farina di grano tenero e 10 uova fresche",
        "500g di carne macinata (manzo e maiale)",
        "200g di fegatini e animelle di pollo",
        "1 litro di latte intero per la besciamella",
        "100g di burro artigianale",
        "Parmigiano Reggiano stagionato 24 mesi",
        "Vino cotto marchigiano per sfumare"
    ],
    steps: [
        "Iniziare stendendo la sfoglia sottilissima e tagliandola in rettangoli.",
        "Preparare il ragù complesso: sfumare le carni con il vino cotto per una nota aromatica unica.",
        "Cuocere la pasta per pochi secondi e immergerla in acqua fredda.",
        "Assemblare non meno di 10 strati con ragù e besciamella vellutata.",
        "Ricoprire l'ultimo strato con abbondante parmigiano.",
        "Infornare a 180°C per circa 50 minuti fino alla crosticina perfetta."
    ]
};

const agentUpdates = [
    { source: "REDAZIONE_AI", text: "Report province aggiornato: Focus su Fermo ed Ascoli." },
    { source: "METEO_MARCHE", text: "Allerta vento su Pesaro-Urbino nelle prossime 2 ore." },
    { source: "FOOD_SCANNER", text: "Ricetta Vincisgrassi: Aggiunto abbinamento vini DOCG." }
];

let currentCategory = 'all';
let currentProvince = 'all';

function init() {
    loadNewsData();
    renderCuriosity();
    renderRecipe();
    renderWeather();
    renderTraffic();
    setupClock();
    setupNav();
    setupProvinceFilter();
    startAgentScanner();
    startStatusSimulation();
    startTrafficTimer();
    setupIntersectionObserver();
}

function setupIntersectionObserver() {
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.bento-item, .widget-card, .side-panel').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
        observer.observe(el);
    });
}

function renderBentoGrid() {
    const grid = document.getElementById('js-bento-grid');
    let filtered = newsData;

    if (currentCategory !== 'all' && currentCategory !== 'ricettes' && currentCategory !== 'curiosita') {
        filtered = filtered.filter(n => n.category === currentCategory);
    }

    if (currentProvince !== 'all') {
        filtered = filtered.filter(n => n.province === currentProvince);
    }

    if (filtered.length === 0) {
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 50px; color: var(--text-dim);">Nessun aggiornamento radar per questi filtri.</div>`;
        return;
    }

    grid.innerHTML = filtered.map(news => `
        <div class="bento-item ${news.size === 'big' || news.size === 'wide' ? 'big-card' : ''}" onclick="openArticle(${news.id})">
            <img src="${news.image}" class="bento-img" alt="${news.title}">
            <div class="bento-content">
                <span class="bento-tag">${news.tag}</span>
                <h3 class="bento-title">${news.title}</h3>
                <div style="font-size: 0.65rem; color: #fff; opacity: 0.6; margin-top: 5px;">PROVINCIA: ${news.province}</div>
            </div>
        </div>
    `).join('');
}

function renderCuriosity() {
    const container = document.getElementById('js-curiosity-content');
    container.innerHTML = `<div class="curiosity-card"><h4>${curiosityData.title}</h4><p>${curiosityData.content}</p></div>`;
}

function renderRecipe() {
    const container = document.getElementById('js-recipe-content');
    container.innerHTML = `
        <div class="recipe-card" onclick="openRecipe()">
            <img src="${recipeData.img}" alt="${recipeData.title}">
            <h4>${recipeData.title}</h4>
            <p style="font-size: 0.8rem; color: #94a3b8;">${recipeData.summary}</p>
        </div>
    `;
}

function renderWeather() {
    const grid = document.getElementById('js-weather-grid');
    const cities = [
        { name: "Civitanova", icon: "🌤️", temp: "16°" },
        { name: "Ancona", icon: "🌧️", temp: "14°" },
        { name: "Macerata", icon: "⛅", temp: "13°" },
        { name: "Pesaro", icon: "🌬️", temp: "12°" },
        { name: "Fermo", icon: "🌤️", temp: "15°" }
    ];
    grid.innerHTML = cities.map(c => `<div class="weather-item"><span class="w-name">${c.name}</span><span class="w-icon">${c.icon}</span><span class="w-temp">${c.temp}</span></div>`).join('');
}

function renderTraffic() {
    const list = document.getElementById('js-traffic-list');
    const alerts = [
        { road: "A14", status: "rallentata", text: "Coda Civitanova Nord", color: "red" },
        { road: "SS16", status: "scorrimento", text: "Regolare", color: "green" },
        { road: "V.Conero", status: "intenso", text: "Traffico locale", color: "yellow" }
    ];
    list.innerHTML = alerts.map(a => `<div class="traffic-item"><span class="t-road">${a.road}</span><span class="t-dot" style="background: var(--accent-${a.color === 'red' ? 'gold' : (a.color === 'green' ? 'green' : 'blue')})"></span><span class="t-text">${a.text}</span></div>`).join('');
}

function startTrafficTimer() {
    let s = 30;
    setInterval(() => { s = s <= 0 ? 30 : s - 1; document.getElementById('js-traffic-timer').innerText = s + "s"; }, 1000);
}

function simulateReport() {
    const topic = prompt("Cosa vuoi segnalare?");
    if (topic) {
        alert("Ricevuto!");
        const feed = document.getElementById('js-agent-feed');
        const line = document.createElement('div');
        line.style.color = '#fbbf24';
        line.innerHTML = `[REPORT]: Segnalata voce "${topic}". Inviata a redazione.`;
        feed.prepend(line);
    }
}

function openArticle(id) {
    const news = newsData.find(n => n.id === id);
    const modal = document.getElementById('js-article-modal');
    const content = document.getElementById('js-modal-content');
    content.innerHTML = `
        <img src="${news.image}" alt="${news.title}">
        <div class="m-body">
            <span class="bento-tag">${news.tag}</span>
            <div style="font-size: 0.8rem; color: #94a3b8; margin: 10px 0;">Autore: ${news.author} | Provincia: ${news.province}</div>
            <h2 style="font-size: 2.2rem; margin: 20px 0; color: #fff;">${news.title}</h2>
            <div class="m-text">${news.content}</div>
        </div>
    `;
    modal.classList.add('active');
}

function openRecipe() {
    const modal = document.getElementById('js-article-modal');
    const content = document.getElementById('js-modal-content');
    content.innerHTML = `
        <img src="${recipeData.img}" alt="${recipeData.title}">
        <div class="m-body">
            <span class="bento-tag">CUCINA_MARCHIGIANA</span>
            <h2 style="font-size: 2.2rem; margin: 20px 0; color: #fff;">${recipeData.title}</h2>
            <div class="wine-pairing" style="background: rgba(190, 18, 60, 0.1); border: 1px solid #be123c; padding: 15px; border-radius: 8px; margin-bottom: 30px;">
                <strong style="color: #fb7185;">🍷 ABBINAMENTO VINO CONSIGLIATO:</strong>
                <p style="margin-top: 5px; font-size: 0.95rem;">${recipeData.wine}</p>
            </div>
            <div class="recipe-ingredients">
                <h3>Ingredienti Necessari</h3>
                <ul class="ingredient-list">${recipeData.ingredients.map(i => `<li>${i}</li>`).join('')}</ul>
            </div>
            <div class="recipe-steps">
                <h3>Preparazione Dettagliata</h3>
                <ol class="step-list">${recipeData.steps.map(s => `<li>${s}</li>`).join('')}</ol>
            </div>
            <button class="btn-report" onclick="window.print()" style="margin-top: 30px; background: #fff; color: #000;">🖨️ STAMPA RICETTA (PDF)</button>
        </div>
    `;
    modal.classList.add('active');
}

function closeArticle() { document.getElementById('js-article-modal').classList.remove('active'); }

function setupNav() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCategory = btn.dataset.category;
            renderBentoGrid();
        });
    });
}

function setupProvinceFilter() {
    document.querySelectorAll('.p-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            document.querySelectorAll('.p-chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            currentProvince = chip.dataset.province;
            renderBentoGrid();
        });
    });
}

function setupClock() {
    setInterval(() => {
        const now = new Date();
        document.getElementById('js-clock').innerText = now.toLocaleTimeString('it-IT', { hour12: false });
    }, 1000);
}

function startStatusSimulation() {
    const statusText = document.getElementById('js-writing-status');
    const statuses = ["In scansione Ancona...", "Rilevato trend Fermano...", "Sincronizzazione Pesaro...", "Marche Live Radar Attivo"];
    let i = 0;
    setInterval(() => { statusText.innerText = statuses[i % statuses.length]; i++; }, 6000);
}

let activeUpdates = [];

function startAgentScanner() {
    const track = document.getElementById('js-radar-track');

    // Initial content
    activeUpdates = [...agentUpdates];
    renderRadarTicker();

    setInterval(() => {
        const up = agentUpdates[Math.floor(Math.random() * agentUpdates.length)];
        const time = new Date().toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

        // Add new update and keep only 5
        activeUpdates.unshift({ source: up.source, text: up.text, time: time });
        if (activeUpdates.length > 5) activeUpdates.pop();

        renderRadarTicker();
    }, 4500);
}

function renderRadarTicker() {
    const track = document.getElementById('js-radar-track');
    if (!track) return;

    track.innerHTML = activeUpdates.map(up => `
        <span>[${up.time || '--:--:--'}] ${up.source}: ${up.text}</span>
    `).join('');
}

document.addEventListener('DOMContentLoaded', init);

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js')
            .then(reg => console.log('SW Registered'))
            .catch(err => console.log('SW Error:', err));
    });
}
