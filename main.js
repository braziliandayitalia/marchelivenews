let newsData = [];
let curiosityData = null;
let recipeData = null;
let currentCategory = 'all';
let currentProvince = 'all';
let activeUpdates = [];

// Funzione principale di caricamento dati
async function loadAllData() {
    console.log("🚀 AGENTE: Inizializzazione sistema professionale...");

    // Verifica versione per pulizia cache (Bumping to 2.4 for professional update)
    const currentVersion = '2.4';
    if (localStorage.getItem('marche_live_version') !== currentVersion) {
        if ('caches' in window) {
            try {
                const keys = await caches.keys();
                await Promise.all(keys.map(key => caches.delete(key)));
            } catch (e) { console.log("Cache clear skip"); }
        }
        localStorage.setItem('marche_live_version', currentVersion);
    }

    // Caricamento Notizie (include Lavoro e Sport)
    try {
        const newsRes = await fetch('news.json');
        const data = await newsRes.json();
        newsData = data.articles || data;
        
        if (data.last_update) {
            document.getElementById('js-writing-status').innerHTML = `<span class="status-dot"></span> Radar Sincronizzato - Ultimo Update: ${data.last_update}`;
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

    // Caricamento Ricetta (Autentica)
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
    
    // Filtro Combinato
    let filtered = newsData;
    if (currentCategory !== 'all') {
        filtered = filtered.filter(n => n.category === currentCategory);
    }
    if (currentProvince !== 'all') {
        filtered = filtered.filter(n => n.province === currentProvince || n.province === 'MARCHE');
    }

    if (filtered.length === 0) {
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 100px 20px; color: var(--text-dim);">
            <div style="font-size: 3rem; margin-bottom: 20px; opacity: 0.3;">📡</div>
            <h3>Nessun aggiornamento radar trovato.</h3>
            <p>L'agente sta cercando nuovi contenuti per questa categoria/provincia.</p>
        </div>`;
        return;
    }

    grid.innerHTML = filtered.map(news => {
        const isJob = news.category === 'lavoro';
        const cardClass = news.size === 'big' || news.size === 'wide' ? 'big-card' : '';
        const jobStyle = isJob ? 'border: 1px solid var(--accent-blue); background: rgba(59, 130, 246, 0.05);' : '';
        
        return `
            <div class="bento-item ${cardClass}" onclick="openArticle(${news.id})" style="${jobStyle}">
                <img src="${news.image}" class="bento-img" alt="${news.title}">
                <div class="bento-content">
                    <span class="bento-tag" style="${isJob ? 'background: var(--accent-blue); color: #fff;' : ''}">${news.tag}</span>
                    <h3 class="bento-title">${news.title}</h3>
                    <div class="bento-footer">
                        <span class="bento-province">${news.province}</span>
                        <span class="bento-more">${isJob ? 'DETTAGLI_LAVORO' : 'LEGGI_NOTIZIA'} ↗</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function renderCuriosity() {
    const container = document.getElementById('js-curiosity-content');
    if (!container || !curiosityData) return;
    container.innerHTML = `
        <div class="curiosity-card">
            <img src="${curiosityData.img}" alt="${curiosityData.title}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 8px; margin-bottom: 15px;">
            <h4 style="color: var(--accent-blue); margin-bottom: 10px;">${curiosityData.title}</h4>
            <p style="font-size: 0.9rem; line-height: 1.5; color: #cbd5e1;">${curiosityData.content}</p>
        </div>
    `;
}

function renderRecipe() {
    const container = document.getElementById('js-recipe-content');
    if (!container || !recipeData) return;
    container.innerHTML = `
        <div class="recipe-card" onclick="openRecipe()" style="cursor: pointer;">
            <img src="${recipeData.img}" alt="${recipeData.title}" style="width: 100%; height: 150px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;">
            <h4 style="color: #fff;">${recipeData.title}</h4>
            <p style="font-size: 0.8rem; color: #94a3b8; margin: 5px 0;">${recipeData.summary}</p>
            <div style="font-size: 0.75rem; color: var(--accent-gold); font-weight: 600;">🍷 ABBINAMENTO: ${recipeData.wine}</div>
        </div>
    `;
}

function renderWeather() {
    const grid = document.getElementById('js-weather-grid');
    if (!grid) return;
    const cities = [
        { name: "Civitanova", icon: "🌤️", temp: "16°" },
        { name: "Ancona", icon: "🌧️", temp: "14°" },
        { name: "Macerata", icon: "⛅", temp: "13°" },
        { name: "Pesaro", icon: "🌬️", temp: "12°" },
        { name: "Fermo", icon: "🌤️", temp: "15°" }
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
        { road: "A14", text: "Civitanova-Ancona sud: Regolare" },
        { road: "SS16", text: "Porto Recanati: Traffico intenso" },
        { road: "Superst. 77", text: "Macerata-Civitanova: Fluido" }
    ];
    list.innerHTML = alerts.map(a => `
        <div class="traffic-item">
            <span class="t-road">${a.road}</span>
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
    const isJob = news.category === 'lavoro';
    const modal = document.getElementById('js-article-modal');
    const content = document.getElementById('js-modal-content');
    
    content.innerHTML = `
        <img src="${news.image}" alt="${news.title}" style="max-height: 400px; width: 100%; object-fit: cover;">
        <div class="m-body">
            <span class="bento-tag" style="${isJob ? 'background: var(--accent-blue);' : ''}">${news.tag}</span>
            <div style="font-size: 0.8rem; color: #94a3b8; margin: 10px 0;">Fonte: ${news.source_name} | Provincia: ${news.province} | ${news.date}</div>
            <h2 style="font-size: 2.2rem; margin: 20px 0; color: #fff; line-height: 1.2;">${news.original_title || news.title}</h2>
            <div class="m-text" style="line-height: 1.8; font-size: 1.1rem; color: #cbd5e1; margin-bottom: 30px;">
                ${news.summary}
            </div>
            <a href="${news.source_url}" target="_blank" class="btn-report" style="display: block; text-align: center; background: var(--accent-blue); color: #fff; text-decoration: none; font-weight: 800; border-radius: 8px; padding: 18px;">
                ${isJob ? '📄 CANDIDATI ORA / CONTATTA' : '🌐 LEGGI ARTICOLO COMPLETO'}
            </a>
        </div>
    `;
    modal.classList.add('active');
}

function openRecipe() {
    if (!recipeData) return;
    const modal = document.getElementById('js-article-modal');
    const content = document.getElementById('js-modal-content');
    content.innerHTML = `
        <img src="${recipeData.img}" alt="${recipeData.title}" style="max-height: 400px; width: 100%; object-fit: cover;">
        <div class="m-body">
            <span class="bento-tag">ECCELLENZA_MARCHIGIANA</span>
            <h2 style="font-size: 2.5rem; margin: 20px 0; color: #fff;">${recipeData.title}</h2>
            <div class="wine-pairing" style="background: rgba(190, 18, 60, 0.1); border: 1px solid #be123c; padding: 20px; border-radius: 12px; margin-bottom: 30px;">
                <strong style="color: #fb7185; font-size: 1.1rem;">🍷 IL CONSIGLIO DEL SOMMELIER:</strong>
                <p style="margin-top: 10px; font-size: 1rem; color: #fff; font-weight: 700;">${recipeData.wine}</p>
            </div>
            <div class="recipe-ingredients">
                <h3 style="color: var(--accent-blue); border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">Cosa ti serve</h3>
                <ul style="margin: 20px 0; padding-left: 20px; line-height: 2; color: #cbd5e1;">
                    ${recipeData.ingredients.map(i => `<li>${i}</li>`).join('')}
                </ul>
            </div>
            <div class="recipe-steps">
                <h3 style="color: var(--accent-blue); border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">Come procedere</h3>
                <ol style="margin: 20px 0; padding-left: 20px; line-height: 2; color: #cbd5e1;">
                    ${recipeData.steps.map(s => `<li>${s}</li>`).join('')}
                </ol>
            </div>
            <button class="btn-report" onclick="window.print()" style="margin-top: 30px; background: #fff; color: #000; width: 100%; border: none; font-weight: 800; border-radius: 8px;">🖨️ STAMPA RICETTA (PDF)</button>
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
            window.scrollTo({ top: document.querySelector('.main-layout-wrapper').offsetTop - 100, behavior: 'smooth' });
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
    const statuses = ["Scansione Ansa...", "Verifica Offerte Lavoro...", "Radar Marche Attivo", "Sincronizzazione Sport..."];
    let i = 0;
    setInterval(() => {
        if (!statusText.innerText.includes("Ultimo Update")) {
            statusText.innerHTML = `<span class="status-dot"></span> ${statuses[i % statuses.length]}`; 
            i++;
        }
    }, 8000);
}

function startAgentScanner() {
    if (!newsData || newsData.length === 0) return;

    // Mix news and jobs in the ticker
    activeUpdates = newsData.slice(0, 12).map(n => ({
        source: n.source_name.toUpperCase(),
        text: n.original_title,
        time: n.date.split(' ').pop(),
        type: n.category
    }));
    
    renderRadarTicker();

    setInterval(() => {
        const up = newsData[Math.floor(Math.random() * newsData.length)];
        const time = new Date().toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' });
        activeUpdates.unshift({ source: up.source_name.toUpperCase(), text: up.original_title, time: time, type: up.category });
        if (activeUpdates.length > 12) activeUpdates.pop();
        renderRadarTicker();
    }, 5000);
}

function renderRadarTicker() {
    const track = document.getElementById('js-radar-track');
    if (!track) return;
    track.innerHTML = activeUpdates.map(up => `
        <span style="${up.type === 'lavoro' ? 'color: var(--accent-blue);' : ''}">
            [${up.time}] ${up.source}: ${up.text}
        </span>
    `).join('');
}

function simulateReport() {
    const topic = prompt("Cosa vuoi segnalare alla redazione?");
    if (topic) alert("Copia ricevuta. La tua segnalazione è stata inviata al sistema di monitoraggio Marche Live.");
}

document.addEventListener('DOMContentLoaded', init);