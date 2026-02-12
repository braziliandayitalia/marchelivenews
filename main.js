let newsData = [];
let allRecipes = [];
let allCuriosities = [];
let currentCategory = 'all';
let currentProvince = 'all';
let activeUpdates = [];

async function loadAllData() {
    console.log("🚀 AGENTE_ELITE: Inizializzazione sistema...");

    const currentVersion = '2.6';
    if (localStorage.getItem('marche_live_version') !== currentVersion) {
        if ('caches' in window) {
            try {
                const keys = await caches.keys();
                await Promise.all(keys.map(key => caches.delete(key)));
            } catch (e) { console.log("Cache clear skip"); }
        }
        localStorage.setItem('marche_live_version', currentVersion);
    }

    try {
        const res = await fetch('news.json');
        const data = await res.json();
        newsData = data.articles || [];
        allRecipes = data.all_recipes || [];
        allCuriosities = data.all_curiosities || [];

        if (data.last_update) {
            document.getElementById('js-writing-status').innerHTML = `<span class="status-dot"></span> Radar Elite Attivo - Update: ${data.last_update}`;
        }

        renderBentoGrid();
        startAgentScanner();

        // Spotlight iniziale
        if (allCuriosities.length > 0) renderCuriosity(allCuriosities[0]);
        if (allRecipes.length > 0) renderRecipe(allRecipes[0]);

    } catch (e) { console.warn("Errore sistema:", e); }
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
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

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

    // Mostra un effetto "scansione" veloce
    grid.style.opacity = '0.5';
    setTimeout(() => grid.style.opacity = '1', 200);

    let displayItems = [];

    // Logica di selezione contenuti per categoria
    if (currentCategory === 'ricette') {
        displayItems = allRecipes;
    } else if (currentCategory === 'curiosita') {
        displayItems = allCuriosities;
    } else {
        displayItems = newsData;
        if (currentCategory !== 'all') {
            displayItems = displayItems.filter(n => n.category === currentCategory);
        }
    }

    // Filtro per Provincia (con fallback MARCHE regionale)
    if (currentProvince !== 'all') {
        displayItems = displayItems.filter(n => n.province === currentProvince || n.province === 'MARCHE');
    }

    if (displayItems.length === 0) {
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 100px 20px; color: var(--text-dim);">
            <div style="font-size: 3rem; margin-bottom: 20px; opacity: 0.3;">📡</div>
            <h3>Nessun contenuto trovato per questa selezione.</h3>
            <p>L'agente sta scansionando nuove fonti per aggiornare questa sezione.</p>
        </div>`;
        return;
    }

    grid.innerHTML = displayItems.map(item => {
        const isElite = item.tag === 'ECCELLENZA' || item.tag === 'CURIOSITÀ';
        const cardClass = item.size === 'big' ? 'big-card' : '';
        const tagColor = item.category === 'lavoro' ? 'var(--accent-blue)' : (item.category === 'sport' ? 'var(--accent-gold)' : 'rgba(255,255,255,0.2)');

        return `
            <div class="bento-item ${cardClass}" onclick="openDetail(${item.id}, '${item.category}')">
                <img src="${item.image}" class="bento-img" alt="${item.title}">
                <div class="bento-content">
                    <span class="bento-tag" style="background: ${tagColor}; color: #fff;">${item.tag || item.category.toUpperCase()}</span>
                    <h3 class="bento-title">${item.title}</h3>
                    <div class="bento-footer">
                        <span class="bento-province">${item.province}</span>
                        <span class="bento-more">SCOPRI_DI_PIÙ ↗</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function openDetail(id, cat) {
    if (cat === 'ricette') {
        const item = allRecipes.find(r => r.id === id);
        if (item) renderFullRecipeModal(item);
    } else if (cat === 'curiosita') {
        const item = allCuriosities.find(c => c.id === id);
        if (item) renderFullCuriosityModal(item);
    } else {
        const item = newsData.find(n => n.id === id);
        if (item) {
            if (item.redirect) {
                window.open(item.source_url, '_blank');
            } else {
                openArticleModal(item);
            }
        }
    }
}

function renderCuriosity(data) {
    const container = document.getElementById('js-curiosity-content');
    if (!container) return;
    container.innerHTML = `
        <div class="curiosity-card" onclick="openDetail(${data.id}, 'curiosita')" style="cursor:pointer">
            <img src="${data.image}" alt="${data.title}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 8px; margin-bottom: 12px;">
            <h4 style="color: var(--accent-blue);">${data.title}</h4>
            <p style="font-size: 0.85rem; color: #cbd5e1; margin-top: 5px;">${data.content.substring(0, 80)}...</p>
        </div>
    `;
}

function renderRecipe(data) {
    const container = document.getElementById('js-recipe-content');
    if (!container) return;
    container.innerHTML = `
        <div class="recipe-card" onclick="openDetail(${data.id}, 'ricette')" style="cursor:pointer">
            <img src="${data.image}" alt="${data.title}" style="width: 100%; height: 140px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;">
            <h4 style="color: #fff;">${data.title}</h4>
            <p style="font-size: 0.8rem; color: #94a3b8; margin: 5px 0;">${data.summary}</p>
        </div>
    `;
}

function openArticleModal(news) {
    const modal = document.getElementById('js-article-modal');
    const content = document.getElementById('js-modal-content');
    const isJob = news.category === 'lavoro';

    content.innerHTML = `
        <img src="${news.image}" alt="${news.title}" style="max-height: 400px; width: 100%; object-fit: cover;">
        <div class="m-body">
            <span class="bento-tag" style="background: ${isJob ? 'var(--accent-blue)' : 'rgba(255,255,255,0.1)'}">${news.tag}</span>
            <div style="font-size: 0.8rem; color: #94a3b8; margin: 10px 0;">Fonte: ${news.source_name} | Provincia: ${news.province} | ${news.date}</div>
            <h2 style="font-size: 2rem; margin: 20px 0; color: #fff;">${news.original_title || news.title}</h2>
            <div class="m-text" style="line-height: 1.8; font-size: 1.1rem; color: #cbd5e1; margin-bottom: 30px;">${news.summary}</div>
            <a href="${news.source_url}" target="_blank" class="btn-report" style="display: block; text-align: center; background: var(--accent-blue); color: #fff; font-weight: 800; border-radius: 6px; padding: 15px; text-decoration: none;">
                ${isJob ? '📄 CANDIDATI / DETTAGLI' : '🌐 LEGGI ARTICOLO COMPLETO'}
            </a>
        </div>
    `;
    modal.classList.add('active');
}

function renderFullRecipeModal(recipe) {
    const modal = document.getElementById('js-article-modal');
    const content = document.getElementById('js-modal-content');
    content.innerHTML = `
        <img src="${recipe.image}" alt="${recipe.title}" style="max-height: 400px; width: 100%; object-fit: cover;">
        <div class="m-body">
            <span class="bento-tag">CUCINA_TRADIZIONALE</span>
            <h2 style="font-size: 2.5rem; margin: 20px 0; color: #fff;">${recipe.title}</h2>
            <div style="background: rgba(190, 18, 60, 0.1); border: 1px solid #be123c; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
                <strong style="color: #fb7185;">🍷 ABBINAMENTO VINO:</strong> <p style="color: #fff; margin-top: 5px;">${recipe.wine}</p>
            </div>
            <h3 style="color: var(--accent-blue);">Ingredienti</h3>
            <ul style="color: #cbd5e1; line-height: 2; margin: 15px 0;">${recipe.ingredients.map(i => `<li>${i}</li>`).join('')}</ul>
            <h3 style="color: var(--accent-blue);">Preparazione</h3>
            <ol style="color: #cbd5e1; line-height: 2; margin: 15px 0;">${recipe.steps.map(s => `<li>${s}</li>`).join('')}</ol>
            <button class="btn-report" onclick="window.print()" style="margin-top: 20px; background: #fff; color: #000; width: 100%; border: none; font-weight: 800;">🖨️ STAMPA RICETTA</button>
        </div>
    `;
    modal.classList.add('active');
}

function renderFullCuriosityModal(cur) {
    const modal = document.getElementById('js-article-modal');
    const content = document.getElementById('js-modal-content');
    content.innerHTML = `
        <img src="${cur.image}" alt="${cur.title}" style="max-height: 400px; width: 100%; object-fit: cover;">
        <div class="m-body">
            <span class="bento-tag">STORIA_E_CURIOSITÀ</span>
            <h2 style="font-size: 2.22rem; margin: 20px 0; color: #fff;">${cur.title}</h2>
            <div class="m-text" style="line-height: 2; font-size: 1.2rem; color: #cbd5e1;">${cur.content}</div>
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
            window.scrollTo({ top: document.querySelector('.main-layout-wrapper').offsetTop - 80, behavior: 'smooth' });
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

function renderWeather() {
    const grid = document.getElementById('js-weather-grid');
    if (!grid) return;
    const cities = ["Civitanova", "Ancona", "Macerata", "Pesaro", "Fermo"];
    grid.innerHTML = cities.map(city => `
        <div class="weather-item">
            <span class="w-name">${city}</span>
            <span class="w-icon">${Math.random() > 0.5 ? '🌤️' : '⛅'}</span>
            <span class="w-temp">${Math.floor(Math.random() * 6 + 10)}°</span>
        </div>
    `).join('');
}

function startAgentScanner() {
    if (!newsData || newsData.length === 0) return;
    activeUpdates = newsData.slice(0, 15).map(n => ({ source: n.source_name.toUpperCase(), text: n.original_title, time: n.date.split(' ').pop() }));
    renderRadarTicker();
    setInterval(() => {
        const up = newsData[Math.floor(Math.random() * newsData.length)];
        const time = new Date().toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' });
        activeUpdates.unshift({ source: up.source_name.toUpperCase(), text: up.original_title, time: time });
        if (activeUpdates.length > 15) activeUpdates.pop();
        renderRadarTicker();
    }, 4500);
}

function renderRadarTicker() {
    const track = document.getElementById('js-radar-track');
    if (track) track.innerHTML = activeUpdates.map(up => `<span>[${up.time}] ${up.source}: ${up.text}</span>`).join('');
}

function startTrafficTimer() {
    let s = 30;
    setInterval(() => {
        s = s <= 0 ? 30 : s - 1;
        const el = document.getElementById('js-traffic-timer');
        if (el) el.innerText = s + "s";
    }, 1000);
}

function startStatusSimulation() {
    const statusText = document.getElementById('js-writing-status');
    const statuses = ["Scansione Ansa...", "Verifica Lavoro...", "Radar Marche Elite Attivo"];
    let i = 0;
    setInterval(() => {
        if (statusText && !statusText.innerText.includes("Update")) {
            statusText.innerHTML = `<span class="status-dot"></span> ${statuses[i % statuses.length]}`;
            i++;
        }
    }, 6000);
}

function renderTraffic() {
    const list = document.getElementById('js-traffic-list');
    if (!list) return;
    const alerts = [
        { road: "A14", text: "Porto Sant'Elpidio: Flusso regolare" },
        { road: "SS16", text: "Falconara: Rallentamenti locali" },
        { road: "SS77", text: "Civitanova: Traffico intenso" }
    ];
    list.innerHTML = alerts.map(a => `<div class="traffic-item"><span class="t-road">${a.road}</span><span class="t-text">${a.text}</span></div>`).join('');
}

function simulateReport() {
    const topic = prompt("Cosa vuoi segnalare alla redazione?");
    if (topic) alert("Report inviato. Grazie per il contributo a Marche Live.");
}

document.addEventListener('DOMContentLoaded', init);