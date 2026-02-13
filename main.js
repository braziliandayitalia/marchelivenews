let newsData = [];
let allRecipes = [];
let allCuriosities = [];
let currentCategory = 'all';
let currentProvince = 'all';
let activeUpdates = [];

const STATIONS = [
    { name: "RADIO SUBASIO", url: "https://icy.unitedradio.it/Subasio.mp3" },
    { name: "RADIO KISS KISS", url: "https://ice08k.fluidstream.net/KissKiss.mp3" },
    { name: "RTL 102.5", url: "https://streamingv2.shoutcast.com/rtl-1025" },
    { name: "RADIO DEEJAY", url: "https://radiodeejay-lh.akamaihd.net/i/RadioDeejay_Live_1@189857/index_128_a-p.m3u8" },
    { name: "RADIO 105", url: "https://icecast.unitedradio.it/Radio105.mp3" },
    { name: "VIRGIN RADIO", url: "https://icecast.unitedradio.it/Virgin.mp3" },
    { name: "RAI RADIO 2", url: "https://icecdn-19d24861e90342cc8decb03c24c8a419.msvdn.net/icecastRelay/S35942484/yp5F67151K92/icecast" },
    { name: "RAI RADIO 3", url: "https://icecdn-19d24861e90342cc8decb03c24c8a419.msvdn.net/icecastRelay/S56630579/yEbkcBtIoSwd/icecast" },
    { name: "RADIO ITALIA", url: "https://radioitaliacom.akamaized.net/hls/live/2093141/radioitalia/playlist.m3u8" },
    { name: "NEWS LIVE (BBC)", url: "https://stream.live.vc.bbcmedia.co.uk/bbc_world_service" }
];
let currentStation = 0;
let isRadioMuted = false;
let lastRadioVol = 0.5;

async function loadAllData() {
    console.log("🚀 AGENTE_ELITE: Inizializzazione sistema...");

    const currentVersion = '2.7';
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
            const statusEl = document.getElementById('js-writing-status');
            if (statusEl) statusEl.innerHTML = `<span class="status-dot"></span> Radar Elite Attivo - Update: ${data.last_update}`;
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
    initMiniRadio();
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

    document.querySelectorAll('.bento-item, .widget-card, .side-panel, .job-hub-premium').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
        observer.observe(el);
    });
}

function renderBentoGrid() {
    const grid = document.getElementById('js-bento-grid');
    if (!grid) return;

    let displayItems = [];

    if (currentCategory === 'ricette') {
        displayItems = allRecipes;
    } else if (currentCategory === 'curiosita') {
        displayItems = allCuriosities;
    } else {
        displayItems = newsData;
        if (currentCategory === 'all') {
            displayItems = displayItems.filter(n => n.category !== 'lavoro');
        } else {
            displayItems = displayItems.filter(n => n.category === currentCategory);
        }
    }

    if (currentProvince !== 'all') {
        displayItems = displayItems.filter(n => n.province === currentProvince || n.province === 'MARCHE');
    }

    const hub = document.getElementById('js-job-hub');
    const bentoWrapper = document.querySelector('.content-section');

    if (currentCategory === 'lavoro') {
        if (hub) hub.style.display = 'block';
        if (bentoWrapper) bentoWrapper.style.display = 'none';
        renderJobHub();
        return;
    } else {
        if (hub) hub.style.display = 'none';
        if (bentoWrapper) bentoWrapper.style.display = 'block';
    }

    grid.innerHTML = displayItems.map(item => {
        const isLavoro = item.category === 'lavoro';
        const cardClass = item.size === 'big' ? 'big-card' : '';
        const tagColor = isLavoro ? '#10b981' : (item.category === 'sport' ? 'var(--accent-gold)' : 'rgba(255,255,255,0.2)');

        return `
            <div class="bento-item ${cardClass}" onclick="openDetail(${item.id}, '${item.category}')">
                <img src="${item.image}" class="bento-img" alt="${item.title}">
                <div class="bento-content">
                    <span class="bento-tag" style="background: ${tagColor}; color: #fff;">
                        ${isLavoro ? '💼 ' : ''}${item.tag || item.category.toUpperCase()}
                    </span>
                    <h3 class="bento-title">${item.title}</h3>
                    <div class="bento-footer">
                        <span class="bento-province">${item.province}</span>
                        <span class="bento-more">APRI ↗</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function renderJobHub() {
    const hubList = document.getElementById('js-job-list');
    const jobStats = document.getElementById('js-job-stats');
    if (!hubList) return;

    const jobs = newsData.filter(n => n.category === 'lavoro');
    const filteredJobs = currentProvince === 'all' ? jobs : jobs.filter(j => j.province === currentProvince || j.province === 'MARCHE');

    if (jobStats) jobStats.innerText = `${filteredJobs.length} Opportunità trovate`;

    hubList.innerHTML = filteredJobs.map(job => `
        <div class="job-card-mini" onclick="openDetail(${job.id}, 'lavoro')">
            <div class="job-card-top">
                <span class="job-card-company">${job.source_name}</span>
            </div>
            <h3 class="job-card-title">${job.original_title || job.title}</h3>
            <div class="job-card-footer">
                <span class="job-card-loc">📍 ${job.province}</span>
            </div>
        </div>
    `).join('');
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
        if (item) openArticleModal(item);
    }
}

function openArticleModal(news) {
    const modal = document.getElementById('js-article-modal');
    const content = document.getElementById('js-modal-content');
    if (!modal || !content) return;

    content.innerHTML = `
        <img src="${news.image}" alt="${news.title}" style="max-height: 400px; width: 100%; object-fit: cover;">
        <div class="m-body">
            <h2 style="color: #fff; margin: 20px 0;">${news.original_title || news.title}</h2>
            <p style="color: #cbd5e1; line-height: 1.8;">${news.summary}</p>
            <a href="${news.source_url}" target="_blank" class="btn-report" style="display: block; text-align: center; margin-top: 20px; background: var(--job-accent); color: #000; text-decoration: none; padding: 15px; border-radius: 6px; font-weight: 800;">VISITA FONTE</a>
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
            renderJobHub();
        });
    });
}

function setupClock() {
    setInterval(() => {
        const el = document.getElementById('js-clock');
        if (el) el.innerText = new Date().toLocaleTimeString('it-IT');
    }, 1000);
}

function renderWeather() {
    const grid = document.getElementById('js-weather-grid');
    if (!grid) return;
    const cities = ["Ancona", "Civitanova", "Macerata", "Pesaro", "Fermo"];
    grid.innerHTML = cities.map(city => `
        <div class="weather-item">
            <span class="w-name">${city}</span>
            <span class="w-temp">${Math.floor(Math.random() * 5 + 10)}°</span>
        </div>
    `).join('');
}

function startAgentScanner() {
    if (!newsData.length) return;
    const radarPool = newsData.filter(n => n.category !== 'lavoro');
    activeUpdates = radarPool.slice(0, 15).map(n => ({ source: n.source_name.toUpperCase(), text: n.original_title, time: n.date.split(' ').pop() }));
    renderRadarTicker();
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
    const statuses = ["Scansione Ansa...", "Verifica Lavoro...", "Radar Elite Attivo"];
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
        { road: "A14", text: "Porto S.Elpidio: OK" },
        { road: "SS16", text: "Falconara: Rallentamenti" },
        { road: "SS77", text: "Civitanova: Intenso" }
    ];
    list.innerHTML = alerts.map(a => `<div class="traffic-item"><span class="t-road">${a.road}</span>: ${a.text}</div>`).join('');
}

// 📻 ELITE RADIO MINI LOGIC
// 📻 MINI RADIO LOGIC (Adattamento Codice Utente)
function initMiniRadio() {
    const audio = document.getElementById("radioAudio");
    const playBtn = document.getElementById("playBtn");
    const muteBtn = document.getElementById("muteBtn");
    const stationName = document.getElementById("stationName");
    const volumeSlider = document.getElementById("volumeSlider");

    if (!audio || !playBtn) return;

    // Inizializzazione stazione
    audio.src = STATIONS[currentStation].url;
    stationName.textContent = STATIONS[currentStation].name;

    document.getElementById("nextBtn").onclick = () => {
        currentStation = (currentStation + 1) % STATIONS.length;
        changeStation();
    };

    document.getElementById("prevBtn").onclick = () => {
        currentStation = (currentStation - 1 + STATIONS.length) % STATIONS.length;
        changeStation();
    };

    let hls = null;

    function changeStation() {
        const url = STATIONS[currentStation].url;
        stationName.textContent = STATIONS[currentStation].name;

        // Reset HLS if existing
        if (hls) {
            hls.destroy();
            hls = null;
        }

        if (url.endsWith(".m3u8")) {
            if (Hls.isSupported()) {
                hls = new Hls();
                hls.loadSource(url);
                hls.attachMedia(audio);
                hls.on(Hls.Events.MANIFEST_PARSED, function () {
                    audio.play().then(() => {
                        playBtn.textContent = "⏸️";
                    }).catch(e => console.warn("HLS play error", e));
                });
            } else if (audio.canPlayType('application/vnd.apple.mpegurl')) {
                // Native Safari support
                audio.src = url;
                audio.play().then(() => {
                    playBtn.textContent = "⏸️";
                });
            }
        } else {
            audio.src = url;
            audio.play().then(() => {
                playBtn.textContent = "⏸️";
            }).catch(e => {
                console.warn("Stream error", e);
                stationName.textContent = "OFFLINE / BLINK";
            });
        }
    }

    playBtn.onclick = () => {
        if (audio.paused) {
            audio.play().then(() => {
                playBtn.textContent = "⏸️";
            }).catch(e => {
                stationName.textContent = "ERRORE CONNESSIONE";
            });
        } else {
            audio.pause();
            playBtn.textContent = "▶️";
        }
    };

    volumeSlider.oninput = (e) => {
        audio.volume = e.target.value / 100;
    };

    muteBtn.onclick = () => {
        audio.muted = !audio.muted;
        muteBtn.textContent = audio.muted ? "🔊" : "🔇";
    };

    // Rende la radio trascinabile
    const radioEl = document.getElementById("draggableRadio");
    const handleEl = document.getElementById("radioHandle");
    if (radioEl && handleEl) {
        initDraggable(radioEl, handleEl);
    }
}

function initDraggable(el, handle) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;

    handle.onmousedown = dragMouseDown;
    handle.ontouchstart = dragMouseDown;

    function dragMouseDown(e) {
        e = e || window.event;
        // Non prevenire l'evento se è touch per permettere lo scrolling se necessario, 
        // ma per un widget flottante lo preveniamo
        if (e.type !== 'touchstart') e.preventDefault();

        const clientX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
        const clientY = e.type === 'touchstart' ? e.touches[0].clientY : e.clientY;

        pos3 = clientX;
        pos4 = clientY;
        document.onmouseup = closeDragElement;
        document.ontouchend = closeDragElement;
        document.onmousemove = elementDrag;
        document.ontouchmove = elementDrag;
    }

    function elementDrag(e) {
        e = e || window.event;
        const clientX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
        const clientY = e.type === 'touchmove' ? e.touches[0].clientY : e.clientY;

        pos1 = pos3 - clientX;
        pos2 = pos4 - clientY;
        pos3 = clientX;
        pos4 = clientY;

        // Nuova posizione
        let newTop = el.offsetTop - pos2;
        let newLeft = el.offsetLeft - pos1;

        // Limiti schermo
        const padding = 10;
        newTop = Math.max(padding, Math.min(window.innerHeight - el.offsetHeight - padding, newTop));
        newLeft = Math.max(padding, Math.min(window.innerWidth - el.offsetWidth - padding, newLeft));

        el.style.top = newTop + "px";
        el.style.left = newLeft + "px";
        el.style.right = "auto"; // Disabilita fixed right
    }

    function closeDragElement() {
        document.onmouseup = null;
        document.ontouchend = null;
        document.onmousemove = null;
        document.ontouchmove = null;
    }
}

document.addEventListener('DOMContentLoaded', init);
