let newsData = [];
let curiosityData = null;
let recipeData = null;
let currentCategory = 'all';
let currentProvince = 'all';
let activeUpdates = [];

// Funzione principale di caricamento dati
async function loadAllData() {
    console.log("🚀 AGENTE: Inizializzazione sistema dinamico...");

    // Verifica versione per pulizia cache
    const currentVersion = '2.2';
    if (localStorage.getItem('marche_live_version') !== currentVersion) {
        if ('caches' in window) {
            try {
                const keys = await caches.keys();
                await Promise.all(keys.map(key => caches.delete(key)));
            } catch (e) { console.log("Cache clear skip"); }
        }
        localStorage.setItem('marche_live_version', currentVersion);
    }

    // Caricamento Notizie
    try {
        const newsRes = await fetch('news.json');
        const data = await newsRes.json();
        newsData = data.articles || data;

        if (data.last_update) {
            document.getElementById('js-writing-status').innerText = `Sistema Sincronizzato - Ultimo Radar: ${data.last_update}`;
        }

        renderBentoGrid();
        startAgentScanner();
    } catch (e) { console.warn("Errore news:", e); }

    // Caricamento Curiosità
    try {
        const curiosityRes = await fetch('curiosity.json');
        curiosityData = await curiosityRes.json();
        renderCuriosity();
    } catch (e) { console.warn("Errore curiosità:", e); }

    // Caricamento Ricetta
    try {
        const recipeRes = await fetch('recipe.json');
        recipeData = await recipeRes.json();
        renderRecipe();
    } catch (e) { console.warn("Errore ricetta:", e); }
}

function init() {
    loadAllData();
    renderWeather();
    renderTraffic();
    setupClock();
    setupNav();
    setupProvinceFilter();
    startStatusSimulation();
    startTrafficTimer();
    setupIntersectionObserver();
}

function setupIntersectionObserver() {
    const observerOptions = { threshold: 0.1 };
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
    if (!grid) return;

    let filtered = newsData;
    if (currentCategory !== 'all') {
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
                <div class="bento-footer">
                    <span class="bento-province">${news.province}</span>
                    <span class="bento-more">APRI_RADAR ↗</span>
                </div>
            </div>
        </div>
    `).join('');
}

function renderCuriosity() {
    const container = document.getElementById('js-curiosity-content');
    if (!container || !curiosityData) return;
    container.innerHTML = `
        <div class="curiosity-card">
            <h4>${curiosityData.title}</h4>
            <p>${curiosityData.content}</p>
        </div>
    `;
}

function renderRecipe() {
    const container = document.getElementById('js-recipe-content');
    if (!container || !recipeData) return;
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
    if (!grid) return;
    const cities = [
        { name: "Civitanova", icon: "🌤️", temp: Math.floor(Math.random() * 5 + 12) + "°" },
        { name: "Ancona", icon: "🌧️", temp: Math.floor(Math.random() * 5 + 10) + "°" },
        { name: "Macerata", icon: "⛅", temp: Math.floor(Math.random() * 5 + 9) + "°" },
        { name: "Pesaro", icon: "🌬️", temp: Math.floor(Math.random() * 5 + 11) + "°" },
        { name: "Fermo", icon: "🌤️", temp: Math.floor(Math.random() * 5 + 13) + "°" }
    ];
    grid.innerHTML = cities.map(c => `
        <div class="weather-item">
            <span class="w-name">${c.name}</span>
            <span class="w-icon">${c.icon}</span>
            <span class="w-temp">${c.temp}</span>
        </div>
    `).join('');
}

function renderTraffic() {
    const list = document.getElementById('js-traffic-list');
    if (!list) return;
    const alerts = [
        { road: "A14", status: "rallentata", text: "Coda Civitanova Nord", color: "red" },
        { road: "SS16", status: "scorrimento", text: "Regolare", color: "green" },
        { road: "V.Conero", status: "intenso", text: "Traffico locale", color: "yellow" }
    ];
    list.innerHTML = alerts.map(a => `
        <div class="traffic-item">
            <span class="t-road">${a.road}</span>
            <span class="t-dot" style="background: var(--accent-${a.color === 'red' ? 'gold' : (a.color === 'green' ? 'green' : 'blue')})"></span>
            <span class="t-text">${a.text}</span>
        </div>
    `).join('');
}

function startTrafficTimer() {
    let s = 30;
    setInterval(() => {
        s = s <= 0 ? 30 : s - 1;
        const el = document.getElementById('js-traffic-timer');
        if (el) el.innerText = s + "s";
    }, 1000);
}

function openArticle(id) {
    const news = newsData.find(n => n.id === id);
    if (!news) return;
    const modal = document.getElementById('js-article-modal');
    const content = document.getElementById('js-modal-content');
    content.innerHTML = `
        <img src="${news.image}" alt="${news.title}">
        <div class="m-body">
            <span class="bento-tag">${news.tag}</span>
            <div style="font-size: 0.8rem; color: #94a3b8; margin: 10px 0;">Fonte: ${news.source_name} | Provincia: ${news.province} | ${news.date}</div>
            <h2 style="font-size: 2.2rem; margin: 20px 0; color: #fff;">${news.original_title || news.title}</h2>
            <div class="m-text" style="line-height: 1.6; font-size: 1.1rem; color: #cbd5e1; margin-bottom: 30px;">
                ${news.summary}
            </div>
            <a href="${news.source_url}" target="_blank" class="btn-report" style="display: block; text-align: center; background: var(--accent-blue); color: #000; text-decoration: none; font-weight: 800; border: none; cursor: pointer;">🌐 LEGGI NOTIZIA COMPLETA SU ${news.source_name.toUpperCase()}</a>
        </div>
    `;
    modal.classList.add('active');
}

function openRecipe() {
    if (!recipeData) return;
    const modal = document.getElementById('js-article-modal');
    const content = document.getElementById('js-modal-content');
    content.innerHTML = `
        <img src="${recipeData.img}" alt="${recipeData.title}">
        <div class="m-body">
            <span class="bento-tag">ECCELLENZA_MARCHE</span>
            <h2 style="font-size: 2.2rem; margin: 20px 0; color: #fff;">${recipeData.title}</h2>
            <div class="wine-pairing" style="background: rgba(190, 18, 60, 0.1); border: 1px solid #be123c; padding: 15px; border-radius: 8px; margin-bottom: 30px;">
                <strong style="color: #fb7185;">🍷 ABBINAMENTO VINO CONSIGLIATO:</strong>
                <p style="margin-top: 5px; font-size: 0.95rem;">${recipeData.wine}</p>
            </div>
            <div class="recipe-ingredients">
                <h3 style="color: var(--accent-blue);">Ingredienti Necessari</h3>
                <ul style="margin: 15px 0; padding-left: 20px; line-height: 1.8; color: #cbd5e1;">
                    ${recipeData.ingredients.map(i => `<li>${i}</li>`).join('')}
                </ul>
            </div>
            <div class="recipe-steps">
                <h3 style="color: var(--accent-blue);">Preparazione</h3>
                <ol style="margin: 15px 0; padding-left: 20px; line-height: 1.8; color: #cbd5e1;">
                    ${recipeData.steps.map(s => `<li>${s}</li>`).join('')}
                </ol>
            </div>
            <button class="btn-report" onclick="window.print()" style="margin-top: 30px; background: #fff; color: #000; width: 100%; border: none; font-weight: 800;">🖨️ STAMPA RICETTA (PDF)</button>
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
        const el = document.getElementById('js-clock');
        if (el) el.innerText = new Date().toLocaleTimeString('it-IT', { hour12: false });
    }, 1000);
}

function startStatusSimulation() {
    const statusText = document.getElementById('js-writing-status');
    if (!statusText) return;
    const statuses = ["Scansione Ansa...", "Aggiornamento Radar...", "Sincronizzazione...", "Live Marche Attivo"];
    let i = 0;
    setInterval(() => {
        if (!statusText.innerText.includes("Ultimo Radar")) {
            statusText.innerText = statuses[i % statuses.length];
            i++;
        }
    }, 8000);
}

function startAgentScanner() {
    if (!newsData || newsData.length === 0) return;

    // Popola il ticker con le notizie reali iniziali
    activeUpdates = newsData.slice(0, 10).map(n => ({
        source: n.source_name.toUpperCase(),
        text: n.original_title,
        time: n.date.split(' ').pop()
    }));

    renderRadarTicker();

    setInterval(() => {
        const up = newsData[Math.floor(Math.random() * newsData.length)];
        const time = new Date().toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' });
        activeUpdates.unshift({ source: up.source_name.toUpperCase(), text: up.original_title, time: time });
        if (activeUpdates.length > 10) activeUpdates.pop();
        renderRadarTicker();
    }, 5000);
}

function renderRadarTicker() {
    const track = document.getElementById('js-radar-track');
    if (!track) return;
    track.innerHTML = activeUpdates.map(up => `
        <span>[${up.time}] ${up.source}: ${up.text}</span>
    `).join('');
}

function simulateReport() {
    const topic = prompt("Cosa vuoi segnalare?");
    if (topic) alert("Copia ricevuta. L'agente verificherà la segnalazione.");
}

document.addEventListener('DOMContentLoaded', init);
