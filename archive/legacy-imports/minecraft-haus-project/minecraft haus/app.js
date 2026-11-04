// Main Application Controller for Minecraft Cliffside Mega Mansion
document.addEventListener('DOMContentLoaded', () => {
  const data = window.MANSION_DATA;
  if (!data) {
    console.error("MANSION_DATA not loaded!");
    return;
  }

  // --- STATE ---
  let currentLayerIdx = 17; // Start at EG 0 (Y = 126, index 17)
  let activeTab = 'layers';
  let viewerMode = '2d'; // '2d', '3d', or 'split'
  let completedLayers = {};
  let checkedMaterials = {};
  let currentMaterialFilter = 'ALL';
  let materialSearchTerm = '';
  let activeSelectedBlock = null;

  // Load saved state from localStorage
  try {
    const savedLayers = localStorage.getItem('mansion_completed_layers_v2');
    if (savedLayers) completedLayers = JSON.parse(savedLayers);
    const savedMats = localStorage.getItem('mansion_checked_materials_v2');
    if (savedMats) checkedMaterials = JSON.parse(savedMats);
  } catch (e) {
    console.warn("Could not read localStorage", e);
  }

  // Initialize Viewers
  const viewer2d = new LayerViewer2D('canvas2d', 'viewerTooltip');
  const viewer3d = new VoxelViewer3D('canvas3d');

  // Audio Synthesizer (Zero external audio files needed)
  let soundEnabled = true;
  function playClickSound(freq = 600, duration = 0.04) {
    if (!soundEnabled) return;
    try {
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch (e) {}
  }

  // DOM Elements
  const navButtons = document.querySelectorAll('.nav-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  // Workstation DOM
  const mode2dBtn = document.getElementById('mode2dBtn');
  const mode3dBtn = document.getElementById('mode3dBtn');
  const modeSplitBtn = document.getElementById('modeSplitBtn');
  const splitCockpitContainer = document.getElementById('splitCockpitContainer');
  const canvas2dWrapper = document.getElementById('canvas2dWrapper');
  const canvas3dWrapper = document.getElementById('canvas3dWrapper');

  const layerSlider = document.getElementById('layerSlider');
  const layerNameDisplay = document.getElementById('layerNameDisplay');
  const layerPrevBtn = document.getElementById('layerPrevBtn');
  const layerNextBtn = document.getElementById('layerNextBtn');
  const layerCompleteBtn = document.getElementById('layerCompleteBtn');
  const layerCompleteIcon = document.getElementById('layerCompleteIcon');

  const layerCatBadge = document.getElementById('layerCatBadge');
  const layerYBadge = document.getElementById('layerYBadge');
  const layerRelYBadge = document.getElementById('layerRelYBadge');
  const layerDesc = document.getElementById('layerDesc');
  const layerMilestones = document.getElementById('layerMilestones');
  const blockLegendList = document.getElementById('blockLegendList');

  const spotlightBanner = document.getElementById('spotlightBanner');
  const spotlightBlockName = document.getElementById('spotlightBlockName');
  const resetSpotlightBtn = document.getElementById('resetSpotlightBtn');

  const headerProgressFill = document.getElementById('headerProgressFill');
  const headerProgressText = document.getElementById('headerProgressText');

  // Active Block Inspector DOM
  const inspBlockIcon = document.getElementById('inspBlockIcon');
  const inspBlockName = document.getElementById('inspBlockName');
  const inspBlockCoords = document.getElementById('inspBlockCoords');
  const inspRelOffset = document.getElementById('inspRelOffset');
  const copyTpCmdBtn = document.getElementById('copyTpCmdBtn');
  const copySetblockCmdBtn = document.getElementById('copySetblockCmdBtn');

  // Initial Setup
  layerSlider.max = data.layers.length - 1;
  layerSlider.value = currentLayerIdx;
  updateGlobalProgress();
  updateLayerUI();

  // --- TAB NAVIGATION ---
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;
      playClickSound(520);
      switchTab(target);
    });
  });

  function switchTab(tabId) {
    activeTab = tabId;
    navButtons.forEach(b => b.classList.toggle('active', b.dataset.tab === tabId));
    tabContents.forEach(c => c.classList.toggle('active', c.id === 'tab_' + tabId));

    if (tabId === 'layers') {
      setTimeout(() => {
        applyViewerMode(viewerMode);
      }, 50);
    } else if (tabId === 'materials') {
      renderMaterialsTab();
    } else if (tabId === 'rooms') {
      renderRoomsTab();
    } else if (tabId === 'redstone') {
      renderRedstoneTab();
    } else if (tabId === 'phases') {
      renderPhasesTab();
    }
  }

  // --- VIEWER MODE TOGGLE (2D / 3D / SPLIT COCKPIT) ---
  function applyViewerMode(mode) {
    viewerMode = mode;
    mode2dBtn.classList.toggle('active', mode === '2d');
    mode3dBtn.classList.toggle('active', mode === '3d');
    modeSplitBtn.classList.toggle('active', mode === 'split');

    const controls3d = [
      document.getElementById('toggleWorld3dBtn'),
      document.getElementById('timeOfDay3dBtn'),
      document.getElementById('rotate3dBtn')
    ];

    if (mode === '2d') {
      splitCockpitContainer.classList.remove('canvas-split-grid');
      canvas2dWrapper.style.display = 'block';
      canvas3dWrapper.style.display = 'none';
      controls3d.forEach(el => el.style.display = 'none');
      viewer2d.resizeCanvas();
    } else if (mode === '3d') {
      splitCockpitContainer.classList.remove('canvas-split-grid');
      canvas2dWrapper.style.display = 'none';
      canvas3dWrapper.style.display = 'block';
      controls3d.forEach(el => el.style.display = 'inline-flex');
      viewer3d.resizeCanvas();
      viewer3d.setMaxLayer(currentLayerIdx);
    } else if (mode === 'split') {
      // Split Cockpit: Both side by side!
      splitCockpitContainer.classList.add('canvas-split-grid');
      canvas2dWrapper.style.display = 'block';
      canvas3dWrapper.style.display = 'block';
      controls3d.forEach(el => el.style.display = 'inline-flex');
      viewer2d.resizeCanvas();
      viewer3d.resizeCanvas();
      viewer3d.setMaxLayer(currentLayerIdx);
    }
  }

  mode2dBtn.addEventListener('click', () => { playClickSound(600); applyViewerMode('2d'); });
  mode3dBtn.addEventListener('click', () => { playClickSound(600); applyViewerMode('3d'); });
  modeSplitBtn.addEventListener('click', () => { playClickSound(750); applyViewerMode('split'); });

  // --- 2D CANVAS CONTROLS ---
  document.getElementById('toggleGhostBtn').addEventListener('click', (e) => {
    viewer2d.showGhost = !viewer2d.showGhost;
    e.target.classList.toggle('active', viewer2d.showGhost);
    playClickSound(650);
    viewer2d.render();
  });

  document.getElementById('toggleGridBtn').addEventListener('click', (e) => {
    viewer2d.showGrid = !viewer2d.showGrid;
    e.target.classList.toggle('active', viewer2d.showGrid);
    playClickSound(650);
    viewer2d.render();
  });

  document.getElementById('toggleCoordsBtn').addEventListener('click', (e) => {
    viewer2d.showCoords = !viewer2d.showCoords;
    e.target.classList.toggle('active', viewer2d.showCoords);
    playClickSound(650);
    viewer2d.render();
  });

  document.getElementById('toggleGlyphsBtn').addEventListener('click', (e) => {
    viewer2d.showGlyphs = !viewer2d.showGlyphs;
    e.target.classList.toggle('active', viewer2d.showGlyphs);
    playClickSound(650);
    viewer2d.render();
  });

  document.getElementById('zoomInBtn').addEventListener('click', () => {
    viewer2d.zoom = Math.min(4.0, viewer2d.zoom * 1.25);
    viewer3d.zoom = Math.min(3.5, viewer3d.zoom * 1.25);
    playClickSound(700);
    if (viewerMode !== '3d') viewer2d.render();
    if (viewerMode !== '2d') viewer3d.render();
  });

  document.getElementById('zoomOutBtn').addEventListener('click', () => {
    viewer2d.zoom = Math.max(0.4, viewer2d.zoom * 0.8);
    viewer3d.zoom = Math.max(0.35, viewer3d.zoom * 0.8);
    playClickSound(550);
    if (viewerMode !== '3d') viewer2d.render();
    if (viewerMode !== '2d') viewer3d.render();
  });

  document.getElementById('zoomResetBtn').addEventListener('click', () => {
    playClickSound(500);
    viewer2d.fitToScreen();
    viewer2d.render();
    viewer3d.centerView();
    viewer3d.render();
  });

  // --- 3D CANVAS CONTROLS ---
  document.getElementById('toggleWorld3dBtn').addEventListener('click', (e) => {
    viewer3d.worldMode = !viewer3d.worldMode;
    e.target.classList.toggle('active', viewer3d.worldMode);
    playClickSound(600);
    viewer3d.render();
  });

  const timeBtn = document.getElementById('timeOfDay3dBtn');
  const times = ['sunset', 'day', 'night'];
  const timeLabels = { sunset: '🌅 Sonnenuntergang', day: '☀️ Tag', night: '🌙 Nacht' };
  timeBtn.addEventListener('click', () => {
    const nextIdx = (times.indexOf(viewer3d.timeOfDay) + 1) % times.length;
    const nextTime = times[nextIdx];
    viewer3d.setTimeOfDay(nextTime);
    timeBtn.innerText = timeLabels[nextTime];
    playClickSound(700);
  });

  document.getElementById('rotate3dBtn').addEventListener('click', () => {
    playClickSound(650);
    viewer3d.rotate(1);
  });

  // --- LAYER NAVIGATION & SLIDER ---
  function changeLayer(newIdx) {
    if (newIdx < 0 || newIdx >= data.layers.length) return;
    currentLayerIdx = newIdx;
    layerSlider.value = currentLayerIdx;
    playClickSound(580 + currentLayerIdx * 10);
    updateLayerUI();
  }

  layerSlider.addEventListener('input', (e) => {
    currentLayerIdx = parseInt(e.target.value, 10);
    updateLayerUI();
  });

  layerPrevBtn.addEventListener('click', () => changeLayer(currentLayerIdx - 1));
  layerNextBtn.addEventListener('click', () => changeLayer(currentLayerIdx + 1));

  // Quick Jump Chips
  const jumpChips = document.querySelectorAll('.quick-jump-chip');
  jumpChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const targetIdx = parseInt(chip.dataset.layerIdx, 10);
      changeLayer(targetIdx);
    });
  });

  // Layer Complete Checkbox Toggle
  layerCompleteBtn.addEventListener('click', () => {
    completedLayers[currentLayerIdx] = !completedLayers[currentLayerIdx];
    try {
      localStorage.setItem('mansion_completed_layers_v2', JSON.stringify(completedLayers));
    } catch (e) {}
    playClickSound(completedLayers[currentLayerIdx] ? 880 : 440, 0.08);
    updateGlobalProgress();
    updateLayerCompleteBtnState();
  });

  function updateLayerCompleteBtnState() {
    const isDone = !!completedLayers[currentLayerIdx];
    layerCompleteIcon.innerText = isDone ? '✅' : '⬜';
    layerCompleteBtn.classList.toggle('bg-emerald-950/40', isDone);
    layerCompleteBtn.classList.toggle('border-emerald-400', isDone);
  }

  function updateGlobalProgress() {
    const total = data.layers.length;
    const doneCount = Object.values(completedLayers).filter(Boolean).length;
    const pct = Math.round((doneCount / total) * 100);

    headerProgressFill.style.width = pct + '%';
    headerProgressText.innerText = `${pct}% (${doneCount}/${total})`;
  }

  // Spotlight Filter Reset
  resetSpotlightBtn.addEventListener('click', () => {
    viewer2d.setHighlight(null);
    spotlightBanner.style.display = 'none';
    playClickSound(500);
    renderBlockLegendList(data.layers[currentLayerIdx]);
  });

  // --- UPDATE LAYER UI ---
  function updateLayerUI() {
    const layer = data.layers[currentLayerIdx];
    if (!layer) return;

    // Update Slider Label
    layerNameDisplay.innerText = `Schicht ${currentLayerIdx + 1} von ${data.layers.length}: ${layer.name} (${layer.yLevel})`;

    // Update Category Badges
    layerCatBadge.innerText = layer.category;
    layerYBadge.innerText = layer.yLevel;
    layerRelYBadge.innerText = layer.relativeY || 'EG';

    // Update Description & Milestones
    layerDesc.innerText = layer.description;
    layerMilestones.innerHTML = layer.keyFeatures.map(f => `<li>${f}</li>`).join('');

    // Update Block Legend
    renderBlockLegendList(layer);

    // Update Quick Jump Active Chip
    jumpChips.forEach(chip => {
      const idx = parseInt(chip.dataset.layerIdx, 10);
      chip.classList.toggle('active', idx === currentLayerIdx);
    });

    // Update Checkbox
    updateLayerCompleteBtnState();

    // Notify Viewers
    viewer2d.setLayer(currentLayerIdx);
    if (viewerMode === '3d' || viewerMode === 'split') {
      viewer3d.setMaxLayer(currentLayerIdx);
    }
  }

  function renderBlockLegendList(layer) {
    blockLegendList.innerHTML = '';
    const counts = layer.counts || {};

    const sortedIds = Object.keys(counts).sort((a, b) => counts[b] - counts[a]);

    if (sortedIds.length === 0) {
      blockLegendList.innerHTML = '<span class="text-xs text-gray-500 italic">Keine Blöcke auf dieser Schicht</span>';
      return;
    }

    sortedIds.forEach(bId => {
      const meta = data.palette[bId];
      if (!meta) return;

      const count = counts[bId];
      const isSpotlighted = (viewer2d.highlightBlockId === bId);

      const item = document.createElement('div');
      item.className = 'block-legend-item' + (isSpotlighted ? ' active' : '');
      item.innerHTML = `
        <div class="flex items-center gap-2 min-w-0">
          <span class="block-color-dot" style="background:${meta.color}; border:1px solid ${meta.border}"></span>
          <span class="text-xs text-gray-200 truncate">${meta.glyph ? meta.glyph + ' ' : ''}${meta.name}</span>
        </div>
        <span class="block-count-badge">${count}×</span>
      `;

      item.addEventListener('click', () => {
        viewer2d.setHighlight(bId);
        playClickSound(680);
        if (viewer2d.highlightBlockId) {
          spotlightBanner.style.display = 'flex';
          spotlightBlockName.innerText = meta.name;
        } else {
          spotlightBanner.style.display = 'none';
        }
        renderBlockLegendList(layer);
      });

      blockLegendList.appendChild(item);
    });
  }

  // --- ACTIVE BLOCK INSPECTOR (EVENTS FROM VIEWER2D) ---
  window.addEventListener('block-selected', (e) => {
    const d = e.detail;
    activeSelectedBlock = d;

    const card = document.getElementById('activeBlockCard');
    card.classList.add('active');

    inspBlockIcon.innerText = d.meta.glyph || '🧱';
    inspBlockName.innerText = d.meta.name;
    inspBlockCoords.innerText = `X: ${d.x} | Y: ${d.y} | Z: ${d.z}`;
    inspRelOffset.innerText = `dx: ${d.dx >= 0 ? '+' : ''}${d.dx}, dz: ${d.dz >= 0 ? '+' : ''}${d.dz}`;

    playClickSound(720);
  });

  copyTpCmdBtn.addEventListener('click', () => {
    if (!activeSelectedBlock) return;
    const cmd = `/tp @s ${activeSelectedBlock.x} ${activeSelectedBlock.y} ${activeSelectedBlock.z}`;
    navigator.clipboard.writeText(cmd);
    copyTpCmdBtn.innerText = '✅ Kopiert!';
    playClickSound(800);
    setTimeout(() => { copyTpCmdBtn.innerText = '📋 Kopiere /tp'; }, 1800);
  });

  copySetblockCmdBtn.addEventListener('click', () => {
    if (!activeSelectedBlock) return;
    const blockNameLower = activeSelectedBlock.meta.name.toLowerCase();
    let mcId = 'minecraft:brick_block';
    if (blockNameLower.includes('quarztreppe')) mcId = 'minecraft:quartz_stairs';
    else if (blockNameLower.includes('quarzsäule')) mcId = 'minecraft:quartz_pillar';
    else if (blockNameLower.includes('quarz')) mcId = 'minecraft:smooth_quartz';
    else if (blockNameLower.includes('tiefenschiefer')) mcId = 'minecraft:deepslate_bricks';
    else if (blockNameLower.includes('glas')) mcId = 'minecraft:glass';
    else if (blockNameLower.includes('fichte')) mcId = 'minecraft:spruce_planks';
    else if (blockNameLower.includes('eiche')) mcId = 'minecraft:dark_oak_planks';
    else if (blockNameLower.includes('wasser')) mcId = 'minecraft:water';

    const cmd = `/setblock ${activeSelectedBlock.x} ${activeSelectedBlock.y} ${activeSelectedBlock.z} ${mcId}`;
    navigator.clipboard.writeText(cmd);
    copySetblockCmdBtn.innerText = '✅ Kopiert!';
    playClickSound(800);
    setTimeout(() => { copySetblockCmdBtn.innerText = '📋 Kopiere /setblock'; }, 1800);
  });

  document.getElementById('copyCenterTpBtn').addEventListener('click', () => {
    navigator.clipboard.writeText('/tp @s -662 127 790');
    playClickSound(850);
    alert('Befehl "/tp @s -662 127 790" in die Zwischenablage kopiert!');
  });

  // Sound Toggle
  const soundBtn = document.getElementById('soundToggleBtn');
  soundBtn.addEventListener('click', () => {
    soundEnabled = !soundEnabled;
    soundBtn.classList.toggle('active', soundEnabled);
    soundBtn.innerText = soundEnabled ? '🔊 Sound: An' : '🔇 Sound: Aus';
  });

  // Keyboard Shortcuts
  window.addEventListener('keydown', (e) => {
    if (activeTab !== 'layers') return;
    if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
      changeLayer(currentLayerIdx - 1);
    } else if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
      changeLayer(currentLayerIdx + 1);
    } else if (e.key === 'r' || e.key === 'R') {
      viewer3d.rotate(1);
    } else if (e.key === ' ') {
      // Space toggles ghost
      e.preventDefault();
      viewer2d.showGhost = !viewer2d.showGhost;
      document.getElementById('toggleGhostBtn').classList.toggle('active', viewer2d.showGhost);
      viewer2d.render();
    }
  });

  // --- TAB 2: MATERIAL CALCULATOR & SHULKER BOX PLANNER ---
  function renderMaterialsTab() {
    renderShulkerPackPlan();
    renderMaterialsGrid();
  }

  function renderShulkerPackPlan() {
    const container = document.getElementById('shulkerPackGrid');
    if (!container) return;

    const shulkerPacks = [
      { name: "Shulker 1 & 2: Rote Ziegelsteine", icon: "🧱", color: "#a04739", desc: "4.428 Ziegelsteine (~69 Stacks = 2,5 Shulkerkisten) für die Hauptwände, Kamine und Kellergewölbe." },
      { name: "Shulker 3: Tiefenschiefer & Sockel", icon: "⬛", color: "#313238", desc: "4.676 Tiefenschieferziegel (~73 Stacks = 2,7 Shulkerkisten) für Fundament, Plateauausgleich und Klippenbefestigung." },
      { name: "Shulker 4: Walmdach-Treppen", icon: "▲", color: "#3c3e45", desc: "906 Tiefenschiefer-Treppen (~14 Stacks) für das steile Viktorianische Walmdach und die 4 Gaubendächer." },
      { name: "Shulker 5: Prunk-Quarz & Calcit", icon: "🏛️", color: "#edeae2", desc: "1.326 Quarzblöcke, Säulen, Treppen & Stufen (~21 Stacks = 1 Shulkerkiste) für Portikus, Eckquader und Dachzinnen." },
      { name: "Shulker 6: Fichten- & Eichenholz", icon: "🪵", color: "#6d5236", desc: "7.222 Fichtenbretter (~112 Stacks = 4,2 Shulkerkisten) für alle Etagenböden, Deckenbalken und Treppen." },
      { name: "Shulker 7: Glasscheiben & Scheiben", icon: "🪟", color: "#94a3b8", desc: "320 Glasscheiben & getöntes Glas für Erkerfenster, 2-stöckige Klippenwand und Pool-Sichtkante." },
      { name: "Shulker 8: Redstone & Automation", icon: "⚡", color: "#ef4444", desc: "16 Sticky Pistons, 16 Hebel/Knöpfe, Redstone, Seelensand (Stasis) und Schienen für den Zombie-Kreislauf." },
      { name: "Shulker 9: Kisten & Logistik", icon: "📦", color: "#b45309", desc: "192 Kisten (96 Doppelkisten) + 192 Trichter für das automatische Steampunk-Lager in Keller 1." },
      { name: "Shulker 10: Beleuchtung & Deko", icon: "💡", color: "#38bdf8", desc: "Seelaternen (Pool & Decken), Kupferbirnen, Seelenfeuer, 16 Lesepulte und Braustände." }
    ];

    container.innerHTML = shulkerPacks.map(p => `
      <div class="shulker-box-card" style="border-left: 4px solid ${p.color}">
        <div class="flex items-center gap-3">
          <span class="shulker-icon">${p.icon}</span>
          <div>
            <div class="font-bold text-sm text-gray-100">${p.name}</div>
          </div>
        </div>
        <p class="text-xs text-gray-300 leading-relaxed mt-1">${p.desc}</p>
      </div>
    `).join('');
  }

  function renderMaterialsGrid() {
    const grid = document.getElementById('materialsGrid');
    if (!grid) return;

    const materials = data.materials || [];
    grid.innerHTML = '';

    const filtered = materials.filter(m => {
      const matchCat = (currentMaterialFilter === 'ALL' || m.category === currentMaterialFilter);
      const matchSearch = (!materialSearchTerm || m.name.toLowerCase().includes(materialSearchTerm.toLowerCase()));
      return matchCat && matchSearch;
    });

    if (filtered.length === 0) {
      grid.innerHTML = '<div class="col-span-full text-center text-gray-500 py-8 text-sm italic">Keine passenden Materialien gefunden.</div>';
      return;
    }

    filtered.forEach(mat => {
      const isChecked = !!checkedMaterials[mat.id];
      const card = document.createElement('div');
      card.className = 'material-card' + (isChecked ? ' checked' : '');

      card.innerHTML = `
        <div class="material-card-header">
          <div class="flex items-center gap-2">
            <span class="w-4 h-4 rounded-sm inline-block shadow" style="background:${mat.color};"></span>
            <span class="font-bold text-sm text-gray-100">${mat.glyph ? mat.glyph + ' ' : ''}${mat.name}</span>
          </div>
          <input type="checkbox" class="mat-checkbox" data-id="${mat.id}" ${isChecked ? 'checked' : ''}>
        </div>
        <div class="material-stats">
          <div class="stat-pill"><span class="text-gray-400">Gesamt:</span> <strong class="text-amber-300 font-mono">${mat.count.toLocaleString()}</strong></div>
          <div class="stat-pill"><span class="text-gray-400">Stacks:</span> <strong class="text-sky-300 font-mono">${mat.stacks}</strong></div>
          <div class="stat-pill"><span class="text-gray-400">Shulker:</span> <strong class="text-emerald-300 font-mono">${mat.shulkers}</strong></div>
        </div>
        <div class="text-[11px] text-gray-400 border-t border-gray-800/80 pt-2 flex justify-between">
          <span>Kategorie:</span>
          <span class="text-gray-300">${mat.category}</span>
        </div>
      `;

      const chk = card.querySelector('.mat-checkbox');
      chk.addEventListener('change', (e) => {
        checkedMaterials[mat.id] = e.target.checked;
        card.classList.toggle('checked', e.target.checked);
        try {
          localStorage.setItem('mansion_checked_materials_v2', JSON.stringify(checkedMaterials));
        } catch (err) {}
        playClickSound(e.target.checked ? 750 : 450);
      });

      grid.appendChild(card);
    });
  }

  // Material Filters & Search
  const matFilterBtns = document.querySelectorAll('#matCategoryFilters .filter-pill');
  matFilterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      matFilterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentMaterialFilter = btn.dataset.cat;
      playClickSound(550);
      renderMaterialsGrid();
    });
  });

  const matSearchInput = document.getElementById('matSearchInput');
  if (matSearchInput) {
    matSearchInput.addEventListener('input', (e) => {
      materialSearchTerm = e.target.value.trim();
      renderMaterialsGrid();
    });
  }

  const resetMatsBtn = document.getElementById('resetMaterialChecksBtn');
  if (resetMatsBtn) {
    resetMatsBtn.addEventListener('click', () => {
      if (confirm("Möchtest du wirklich alle Haken in der Materialliste zurücksetzen?")) {
        checkedMaterials = {};
        try { localStorage.removeItem('mansion_checked_materials_v2'); } catch(e){}
        playClickSound(400);
        renderMaterialsGrid();
      }
    });
  }

  // --- TAB 3: ROOM ATLAS ---
  function renderRoomsTab() {
    const grid = document.getElementById('roomsGrid');
    if (!grid) return;

    grid.innerHTML = (data.rooms || []).map(r => `
      <div class="room-card">
        <div class="flex items-center justify-between mb-2">
          <span class="room-level-badge">${r.level}</span>
          <span class="text-xs text-gray-400 font-mono">${r.dimensions}</span>
        </div>
        <h3 class="room-title">${r.name}</h3>
        <p class="room-desc">${r.desc}</p>
        <div class="text-xs text-sky-400 font-mono mb-3">📍 ${r.coords}</div>
        <div class="text-[11px] uppercase font-bold text-gray-400 tracking-wider mb-1.5">Highlights:</div>
        <ul class="room-highlights text-xs">
          ${r.highlights.map(h => `<li>${h}</li>`).join('')}
        </ul>
      </div>
    `).join('');
  }

  // --- TAB 4: REDSTONE & BLUEPRINTS ---
  function renderRedstoneTab() {
    const grid = document.getElementById('redstoneGrid');
    if (!grid) return;

    grid.innerHTML = (data.redstoneGuides || []).map(rg => `
      <div class="card border-red-500/20 bg-gradient-to-br from-gray-900 to-red-950/20">
        <div class="flex items-center justify-between mb-2">
          <span class="tag bg-red-900/60 text-red-200 border-red-700/60">${rg.category}</span>
          <span class="text-xs text-gray-400 font-mono">${rg.level}</span>
        </div>
        <h3 class="card-title text-red-300 text-lg">${rg.name}</h3>
        <p class="text-xs text-gray-300 leading-relaxed mb-3">${rg.desc}</p>
        
        <div class="bg-black/50 p-3 rounded-lg border border-red-900/40 text-xs text-gray-300 mb-3">
          <strong class="text-red-400">Funktionsweise:</strong> ${rg.mechanic}
        </div>

        ${rg.steps ? `
          <h4 class="text-[11px] uppercase font-bold text-gray-400 tracking-wider mb-1.5">Bedienung & Ablauf:</h4>
          <ol class="list-decimal list-inside text-xs text-gray-300 space-y-1 mb-3">
            ${rg.steps.map(s => `<li>${s}</li>`).join('')}
          </ol>
        ` : ''}

        ${rg.triggers ? `
          <h4 class="text-[11px] uppercase font-bold text-gray-400 tracking-wider mb-1.5">Auslöser & Trigger:</h4>
          <ul class="list-disc list-inside text-xs text-gray-300 space-y-1 mb-3">
            ${rg.triggers.map(t => `<li>${t}</li>`).join('')}
          </ul>
        ` : ''}

        <h4 class="text-[11px] uppercase font-bold text-amber-400 tracking-wider mb-1.5">Benötigte Bauteile:</h4>
        <ul class="grid grid-cols-1 md:grid-cols-2 gap-1 text-xs text-gray-300">
          ${rg.materials.map(m => `<li>▫ ${m}</li>`).join('')}
        </ul>
      </div>
    `).join('');
  }

  // --- TAB 5: SERVER PHASES ---
  function renderPhasesTab() {
    const container = document.getElementById('phasesTimeline');
    if (!container) return;

    let savedPhaseChecks = {};
    try {
      const s = localStorage.getItem('mansion_phase_checks');
      if (s) savedPhaseChecks = JSON.parse(s);
    } catch(e){}

    container.innerHTML = (data.phases || []).map(p => `
      <div class="phase-card">
        <div class="flex items-center justify-between mb-2">
          <span class="tag bg-amber-900/40 text-amber-300 border-amber-600/40">Phase ${p.id}</span>
          <span class="text-xs text-emerald-400 font-mono">${p.yRange}</span>
        </div>
        <h3 class="card-title text-base">${p.name}</h3>
        <p class="text-xs text-gray-400 mb-3">${p.focus}</p>

        <ul class="space-y-2 text-xs">
          ${p.checklist.map((c, i) => {
            const key = `p${p.id}_${i}`;
            const isChecked = !!savedPhaseChecks[key];
            return `
              <li class="flex items-start gap-2 text-gray-200">
                <input type="checkbox" class="phase-chk mt-0.5" data-key="${key}" ${isChecked ? 'checked' : ''}>
                <span class="${isChecked ? 'line-through text-gray-500' : ''}">${c}</span>
              </li>
            `;
          }).join('')}
        </ul>
      </div>
    `).join('');

    const chks = container.querySelectorAll('.phase-chk');
    chks.forEach(chk => {
      chk.addEventListener('change', (e) => {
        savedPhaseChecks[e.target.dataset.key] = e.target.checked;
        try {
          localStorage.setItem('mansion_phase_checks', JSON.stringify(savedPhaseChecks));
        } catch(err){}
        playClickSound(e.target.checked ? 720 : 420);
        renderPhasesTab();
      });
    });
  }

  // --- TAB 6: BEFORE / AFTER INTERACTIVE COMPARISON SLIDER ---
  const compareContainer = document.getElementById('compareContainer');
  const compareAfterImg = document.getElementById('compareAfterImg');
  const compareSliderLine = document.getElementById('compareSliderLine');
  let isComparing = false;

  function updateCompareSlider(x) {
    if (!compareContainer || !compareAfterImg || !compareSliderLine) return;
    const rect = compareContainer.getBoundingClientRect();
    const pos = Math.max(0, Math.min(rect.width, x - rect.left));
    const pct = (pos / rect.width) * 100;

    compareSliderLine.style.left = pct + '%';
    compareAfterImg.style.clipPath = `polygon(${pct}% 0, 100% 0, 100% 100%, ${pct}% 100%)`;
  }

  if (compareContainer) {
    compareContainer.addEventListener('mousedown', (e) => {
      isComparing = true;
      updateCompareSlider(e.clientX);
    });

    window.addEventListener('mousemove', (e) => {
      if (isComparing) updateCompareSlider(e.clientX);
    });

    window.addEventListener('mouseup', () => {
      isComparing = false;
    });

    // Touch support for mobile / tablets
    compareContainer.addEventListener('touchmove', (e) => {
      if (e.touches && e.touches[0]) updateCompareSlider(e.touches[0].clientX);
    });

    // Set initial 50% split
    setTimeout(() => {
      if (compareContainer) {
        const rect = compareContainer.getBoundingClientRect();
        updateCompareSlider(rect.left + rect.width / 2);
      }
    }, 200);
  }

  // Support URL hash navigation (e.g. #materials, #split, #world, #3d)
  function handleUrlHash() {
    const hash = window.location.hash.replace('#', '');
    if (!hash) return;
    if (hash === 'split') {
      switchTab('layers');
      applyViewerMode('split');
    } else if (hash === '3d') {
      switchTab('layers');
      applyViewerMode('3d');
    } else if (hash === '2d') {
      switchTab('layers');
      applyViewerMode('2d');
    } else if (['layers', 'materials', 'rooms', 'redstone', 'phases', 'world', 'photos'].includes(hash)) {
      switchTab(hash);
    }
  }

  // Initial tab render & hash check
  setTimeout(() => {
    applyViewerMode('2d');
    handleUrlHash();
  }, 100);

  window.addEventListener('hashchange', handleUrlHash);

});

