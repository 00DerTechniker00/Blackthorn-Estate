// Advanced 2D Top-Down Blueprint Canvas Engine
class LayerViewer2D {
  constructor(canvasId, tooltipId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.tooltip = document.getElementById(tooltipId);

    // State
    this.currentLayerIdx = 17; // Start at EG 0 (Y=126, index 17)
    this.showGhost = true;
    this.showGrid = true;
    this.showCoords = true;
    this.showGlyphs = true;
    this.highlightBlockId = null;

    // Viewport & Pan / Zoom
    this.zoom = 1.0;
    this.panX = 0;
    this.panY = 0;
    this.isDragging = false;
    this.dragStartX = 0;
    this.dragStartY = 0;

    this.hoverCell = null;
    this.selectedCell = null;

    this.initEvents();
  }

  initEvents() {
    window.addEventListener('resize', () => this.resizeCanvas());

    this.canvas.addEventListener('mousedown', (e) => {
      this.isDragging = true;
      this.dragStartX = e.clientX - this.panX;
      this.dragStartY = e.clientY - this.panY;
      this.canvas.style.cursor = 'grabbing';
    });

    window.addEventListener('mousemove', (e) => {
      if (this.isDragging) {
        this.panX = e.clientX - this.dragStartX;
        this.panY = e.clientY - this.dragStartY;
        this.render();
      } else {
        this.handleHover(e);
      }
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
      this.canvas.style.cursor = 'grab';
    });

    this.canvas.addEventListener('click', (e) => {
      this.handleClick(e);
    });

    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.15 : 0.85;
      const newZoom = Math.max(0.4, Math.min(4.0, this.zoom * zoomFactor));

      const rect = this.canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      this.panX = mouseX - (mouseX - this.panX) * (newZoom / this.zoom);
      this.panY = mouseY - (mouseY - this.panY) * (newZoom / this.zoom);
      this.zoom = newZoom;
      this.render();
    });

    this.canvas.addEventListener('mouseleave', () => {
      if (this.tooltip) this.tooltip.style.display = 'none';
      this.hoverCell = null;
      this.render();
    });
  }

  resizeCanvas() {
    const parent = this.canvas.parentElement;
    if (!parent) return;

    const dpr = window.devicePixelRatio || 1;
    const w = parent.clientWidth || 900;
    const h = parent.clientHeight || 650;

    this.canvas.width = w * dpr;
    this.canvas.height = h * dpr;
    this.canvas.style.width = w + 'px';
    this.canvas.style.height = h + 'px';

    this.ctx.scale(dpr, dpr);
    this.fitToScreen();
    this.render();
  }

  fitToScreen() {
    const data = window.MANSION_DATA;
    if (!data) return;

    const parent = this.canvas.parentElement;
    const w = parent ? parent.clientWidth : 900;
    const h = parent ? parent.clientHeight : 650;

    const baseCellSize = 14;
    const gridW = data.dimensions.width * baseCellSize;
    const gridH = data.dimensions.depth * baseCellSize;

    const scaleX = (w - 80) / gridW;
    const scaleY = (h - 80) / gridH;
    this.zoom = Math.min(scaleX, scaleY, 1.8);

    this.panX = (w - gridW * this.zoom) / 2;
    this.panY = (h - gridH * this.zoom) / 2;
  }

  setLayer(idx) {
    const data = window.MANSION_DATA;
    if (!data) return;
    this.currentLayerIdx = Math.max(0, Math.min(data.layers.length - 1, idx));
    this.render();
  }

  setHighlight(blockId) {
    this.highlightBlockId = (this.highlightBlockId === blockId) ? null : blockId;
    this.render();
  }

  getCellFromMouse(e) {
    const data = window.MANSION_DATA;
    if (!data) return null;

    const rect = this.canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const cellSize = 14 * this.zoom;
    const cellX = Math.floor((mouseX - this.panX) / cellSize);
    const cellZ = Math.floor((mouseY - this.panY) / cellSize);

    if (cellX >= 0 && cellX < data.dimensions.width && cellZ >= 0 && cellZ < data.dimensions.depth) {
      return { x: cellX, z: cellZ, clientX: e.clientX, clientY: e.clientY };
    }
    return null;
  }

  handleHover(e) {
    const cell = this.getCellFromMouse(e);
    const data = window.MANSION_DATA;

    if (cell && data && this.tooltip) {
      this.hoverCell = cell;
      const curLayer = data.layers[this.currentLayerIdx];
      const blockId = curLayer.grid[cell.z][cell.x];
      const meta = data.palette[blockId] || { name: 'Unbekannt', color: '#fff', border: '#888', glyph: '' };

      const anchor = data.dimensions.anchor || { x: -662, z: 790 };
      const inGameX = anchor.x + (cell.x - 35);
      const inGameZ = anchor.z + (cell.z - 25);
      const inGameY = curLayer.yLevel;

      this.tooltip.style.display = 'block';
      this.tooltip.style.left = Math.min(window.innerWidth - 240, cell.clientX + 16) + 'px';
      this.tooltip.style.top = Math.min(window.innerHeight - 150, cell.clientY + 16) + 'px';

      this.tooltip.innerHTML = `
        <div class="tooltip-header flex items-center gap-2">
          <span class="w-3.5 h-3.5 rounded-sm inline-block shadow-sm" style="background:${meta.color}; border:1px solid ${meta.border}"></span>
          <span class="font-bold text-amber-300 text-sm">${meta.glyph ? meta.glyph + ' ' : ''}${meta.name}</span>
        </div>
        <div class="tooltip-coords mt-1.5 text-xs text-gray-200">
          <div><strong class="text-emerald-400">In-Game:</strong> X: ${inGameX} | ${inGameY} | Z: ${inGameZ}</div>
          <div class="text-gray-400 text-[11px] mt-0.5">Raster: [${cell.x}, ${cell.z}] (dx: ${cell.x - 35 >= 0 ? '+' : ''}${cell.x - 35}, dz: ${cell.z - 25 >= 0 ? '+' : ''}${cell.z - 25})</div>
        </div>
        <div class="text-[11px] text-gray-400 mt-1 border-t border-gray-700/60 pt-1 flex justify-between">
          <span>${curLayer.category}</span>
          <span class="text-amber-400 font-mono">${curLayer.relativeY}</span>
        </div>
      `;
      this.render();
    } else {
      if (this.tooltip) this.tooltip.style.display = 'none';
      if (this.hoverCell) {
        this.hoverCell = null;
        this.render();
      }
    }
  }

  handleClick(e) {
    const cell = this.getCellFromMouse(e);
    const data = window.MANSION_DATA;
    if (!cell || !data) return;

    this.selectedCell = cell;
    const curLayer = data.layers[this.currentLayerIdx];
    const blockId = curLayer.grid[cell.z][cell.x];
    const meta = data.palette[blockId];

    const anchor = data.dimensions.anchor || { x: -662, z: 790 };
    const inGameX = anchor.x + (cell.x - 35);
    const inGameZ = anchor.z + (cell.z - 25);
    const inGameY = parseInt(curLayer.yLevel.replace(/\D/g, '')) || 126;

    // Trigger Custom Event for App Inspector
    window.dispatchEvent(new CustomEvent('block-selected', {
      detail: {
        blockId: blockId,
        meta: meta,
        gridX: cell.x,
        gridZ: cell.z,
        dx: cell.x - 35,
        dz: cell.z - 25,
        x: inGameX,
        y: inGameY,
        z: inGameZ,
        layerName: curLayer.name
      }
    }));

    this.render();
  }

  render() {
    const data = window.MANSION_DATA;
    if (!data) return;

    const ctx = this.ctx;
    const parent = this.canvas.parentElement;
    const w = parent ? parent.clientWidth : 900;
    const h = parent ? parent.clientHeight : 650;

    ctx.clearRect(0, 0, w, h);

    const cellSize = 14 * this.zoom;
    const curLayer = data.layers[this.currentLayerIdx];
    const prevLayer = this.currentLayerIdx > 0 ? data.layers[this.currentLayerIdx - 1] : null;

    ctx.save();
    ctx.translate(this.panX, this.panY);

    // 1. Draw Ghost Layer (Schattenschicht)
    if (this.showGhost && prevLayer) {
      ctx.globalAlpha = 0.25;
      for (let z = 0; z < data.dimensions.depth; z++) {
        for (let x = 0; x < data.dimensions.width; x++) {
          const bId = prevLayer.grid[z][x];
          if (bId !== 0) {
            const meta = data.palette[bId];
            ctx.fillStyle = meta.color;
            ctx.fillRect(x * cellSize, z * cellSize, cellSize, cellSize);
            ctx.strokeStyle = meta.border || '#555';
            ctx.lineWidth = 0.6;
            ctx.strokeRect(x * cellSize, z * cellSize, cellSize, cellSize);
          }
        }
      }
      ctx.globalAlpha = 1.0;
    }

    // 2. Draw Active Layer Blocks & Grid
    for (let z = 0; z < data.dimensions.depth; z++) {
      for (let x = 0; x < data.dimensions.width; x++) {
        const bId = curLayer.grid[z][x];
        const px = x * cellSize;
        const pz = z * cellSize;

        if (bId !== 0) {
          const meta = data.palette[bId];
          const isHighlighted = (this.highlightBlockId === null || this.highlightBlockId === bId.toString());

          ctx.fillStyle = isHighlighted ? meta.color : 'rgba(40,42,48,0.35)';
          ctx.fillRect(px, pz, cellSize, cellSize);

          ctx.strokeStyle = isHighlighted ? (meta.border || '#333') : '#444';
          ctx.lineWidth = isHighlighted && this.highlightBlockId ? 1.5 : 0.8;
          ctx.strokeRect(px, pz, cellSize, cellSize);

          // Subtle 3D Bevel on blocks when zoomed in
          if (cellSize >= 14 && isHighlighted) {
            ctx.fillStyle = 'rgba(255,255,255,0.18)';
            ctx.fillRect(px, pz, cellSize, 1.5);
            ctx.fillRect(px, pz, 1.5, cellSize);
            ctx.fillStyle = 'rgba(0,0,0,0.22)';
            ctx.fillRect(px, pz + cellSize - 1.5, cellSize, 1.5);
            ctx.fillRect(px + cellSize - 1.5, pz, 1.5, cellSize);

            // Draw Block Glyph/Icon if zoomed in
            if (this.showGlyphs && cellSize >= 18 && meta.glyph) {
              ctx.font = `${Math.floor(cellSize * 0.58)}px sans-serif`;
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillText(meta.glyph, px + cellSize / 2, pz + cellSize / 2 + 1);
            }
          }
        } else if (this.showGrid) {
          // Empty slot in grid
          ctx.strokeStyle = 'rgba(255,255,255,0.04)';
          ctx.lineWidth = 0.5;
          ctx.strokeRect(px, pz, cellSize, cellSize);
        }
      }
    }

    // 3. Highlight Selected Cell
    if (this.selectedCell) {
      const sx = this.selectedCell.x * cellSize;
      const sz = this.selectedCell.z * cellSize;
      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 2.5;
      ctx.strokeRect(sx, sz, cellSize, cellSize);
      ctx.fillStyle = 'rgba(16, 185, 129, 0.28)';
      ctx.fillRect(sx, sz, cellSize, cellSize);
    }

    // 4. Highlight Hover Cell
    if (this.hoverCell) {
      const hx = this.hoverCell.x * cellSize;
      const hz = this.hoverCell.z * cellSize;
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 2;
      ctx.strokeRect(hx, hz, cellSize, cellSize);
      ctx.fillStyle = 'rgba(245, 158, 11, 0.22)';
      ctx.fillRect(hx, hz, cellSize, cellSize);
    }

    // 5. Compass & Orientation Guide Labels
    const totalW = data.dimensions.width * cellSize;
    const totalH = data.dimensions.depth * cellSize;
    const midX = totalW / 2;

    ctx.font = `bold ${Math.max(10, Math.floor(12 * this.zoom))}px sans-serif`;

    // North-East / Top: Infinity Pool & Cliff Edge
    ctx.fillStyle = '#38bdf8';
    ctx.textAlign = 'center';
    ctx.fillText('🌊 NORD-OSTEN • KLIPPENKANTE & INFINITY-POOL (Abgrund zum Tal)', midX, -16);

    // South-West / Bottom: Portico & Driveway
    ctx.fillStyle = '#fbbf24';
    ctx.fillText('☀️ SÜD-WESTEN • HAUPTPORTAL & AUFFAHRT (Blick in Abendsonne)', midX, totalH + 26);

    // West / Left
    ctx.fillStyle = '#9ca3af';
    ctx.textAlign = 'right';
    ctx.fillText('⛰️ NW: Berggrat', -14, totalH / 2);

    // East / Right
    ctx.textAlign = 'left';
    ctx.fillText('🌄 SO: Hochplateau', totalW + 14, totalH / 2);

    // 6. In-Game Coordinate Rulers along edges
    if (this.showCoords && cellSize >= 11) {
      ctx.fillStyle = '#64748b';
      ctx.font = `${Math.max(8, Math.floor(9 * this.zoom))}px monospace`;
      ctx.textAlign = 'center';

      const anchor = data.dimensions.anchor || { x: -662, z: 790 };

      // Top X coordinates (every 5 blocks)
      for (let x = 0; x < data.dimensions.width; x += 5) {
        const inX = anchor.x + (x - 35);
        ctx.fillText(inX.toString(), x * cellSize + cellSize / 2, -4);
      }

      // Left Z coordinates (every 5 blocks)
      ctx.textAlign = 'right';
      for (let z = 0; z < data.dimensions.depth; z += 5) {
        const inZ = anchor.z + (z - 25);
        ctx.fillText(inZ.toString(), -4, z * cellSize + cellSize / 2 + 3);
      }
    }

    ctx.restore();
  }
}

window.LayerViewer2D = LayerViewer2D;
