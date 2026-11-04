// High-Performance 3D Voxel Orbit & Layer Cutoff Engine
class VoxelViewer3D {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');

    // Camera angles in radians
    this.yaw = 0.85;   // ~50° isometric orbit
    this.pitch = 0.58; // ~33° tilt
    this.zoom = 1.0;
    this.panX = 0;
    this.panY = 0;

    this.maxLayerIdx = 36; // Render all layers by default
    this.soloLayerMode = false;
    this.worldMode = true;
    this.timeOfDay = 'sunset'; // 'sunset', 'day', 'night'

    this.isDragging = false;
    this.isPanning = false;
    this.lastMouseX = 0;
    this.lastMouseY = 0;

    this.colorCache = {};
    this.initEvents();
  }

  initEvents() {
    window.addEventListener('resize', () => this.resizeCanvas());

    this.canvas.addEventListener('mousedown', (e) => {
      this.lastMouseX = e.clientX;
      this.lastMouseY = e.clientY;
      if (e.button === 2 || e.shiftKey) {
        this.isPanning = true;
      } else {
        this.isDragging = true;
      }
      this.canvas.style.cursor = 'grabbing';
    });

    this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());

    window.addEventListener('mousemove', (e) => {
      if (!this.isDragging && !this.isPanning) return;
      const dx = e.clientX - this.lastMouseX;
      const dy = e.clientY - this.lastMouseY;
      this.lastMouseX = e.clientX;
      this.lastMouseY = e.clientY;

      if (this.isDragging) {
        this.yaw += dx * 0.007;
        this.pitch = Math.max(0.12, Math.min(1.35, this.pitch + dy * 0.005));
        this.render();
      } else if (this.isPanning) {
        this.panX += dx;
        this.panY += dy;
        this.render();
      }
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
      this.isPanning = false;
      this.canvas.style.cursor = 'grab';
    });

    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.15 : 0.85;
      this.zoom = Math.max(0.35, Math.min(3.5, this.zoom * zoomFactor));
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
    this.centerView();
    this.render();
  }

  centerView() {
    const parent = this.canvas.parentElement;
    const w = parent ? parent.clientWidth : 900;
    const h = parent ? parent.clientHeight : 650;
    this.panX = w / 2;
    this.panY = h / 2 + 40;
  }

  rotate(deltaSteps) {
    this.yaw += deltaSteps * (Math.PI / 4);
    this.render();
  }

  setMaxLayer(layerIdx) {
    this.maxLayerIdx = layerIdx;
    this.render();
  }

  setSoloLayer(enable) {
    this.soloLayerMode = enable;
    this.render();
  }

  setWorldMode(enable) {
    this.worldMode = enable;
    this.render();
  }

  setTimeOfDay(time) {
    this.timeOfDay = time;
    this.colorCache = {};
    this.render();
  }

  shade(hex, factor) {
    if (!hex || hex === 'transparent' || hex.startsWith('rgba')) return hex;
    const key = hex + '_' + factor + '_' + this.timeOfDay;
    if (this.colorCache[key]) return this.colorCache[key];

    let r = parseInt(hex.substring(1, 3), 16);
    let g = parseInt(hex.substring(3, 5), 16);
    let b = parseInt(hex.substring(5, 7), 16);

    // Apply Time of Day Lighting Model
    if (this.timeOfDay === 'sunset') {
      r = Math.min(255, r * 1.18 + 20);
      g = Math.min(255, g * 0.94);
      b = Math.min(255, b * 0.76);
    } else if (this.timeOfDay === 'night') {
      r = Math.max(12, r * 0.38);
      g = Math.max(16, g * 0.44);
      b = Math.max(28, b * 0.65);
    }

    r = Math.min(255, Math.max(0, Math.floor(r * factor)));
    g = Math.min(255, Math.max(0, Math.floor(g * factor)));
    b = Math.min(255, Math.max(0, Math.floor(b * factor)));

    const res = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    this.colorCache[key] = res;
    return res;
  }

  renderSky(ctx, w, h) {
    const grad = ctx.createLinearGradient(0, 0, 0, h);
    if (this.timeOfDay === 'sunset') {
      grad.addColorStop(0, '#1e1b4b');   // Deep twilight indigo
      grad.addColorStop(0.4, '#b45309'); // Warm orange horizon
      grad.addColorStop(0.7, '#f59e0b'); // Golden amber
      grad.addColorStop(1, '#1e293b');   // Valley floor dark
    } else if (this.timeOfDay === 'night') {
      grad.addColorStop(0, '#030712');
      grad.addColorStop(0.6, '#0f172a');
      grad.addColorStop(1, '#020617');
    } else {
      // Day
      grad.addColorStop(0, '#38bdf8');
      grad.addColorStop(0.6, '#bae6fd');
      grad.addColorStop(1, '#64748b');
    }
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    // Draw Sun or Moon
    if (this.timeOfDay === 'sunset') {
      ctx.fillStyle = 'rgba(251, 191, 36, 0.85)';
      ctx.beginPath();
      ctx.arc(w * 0.22, h * 0.48, 38, 0, Math.PI * 2);
      ctx.fill();
      // Glow
      ctx.fillStyle = 'rgba(251, 146, 60, 0.22)';
      ctx.beginPath();
      ctx.arc(w * 0.22, h * 0.48, 90, 0, Math.PI * 2);
      ctx.fill();
    } else if (this.timeOfDay === 'night') {
      ctx.fillStyle = '#f8fafc';
      ctx.beginPath();
      ctx.arc(w * 0.78, h * 0.2, 22, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  render() {
    const data = window.MANSION_DATA;
    if (!data) return;

    const ctx = this.ctx;
    const parent = this.canvas.parentElement;
    const w = parent ? parent.clientWidth : 900;
    const h = parent ? parent.clientHeight : 650;

    ctx.clearRect(0, 0, w, h);
    this.renderSky(ctx, w, h);

    const W = data.dimensions.width;
    const D = data.dimensions.depth;
    const layerCount = data.layers.length;

    const cosY = Math.cos(this.yaw);
    const sinY = Math.sin(this.yaw);
    const cosP = Math.cos(this.pitch);
    const sinP = Math.sin(this.pitch);

    const voxelScale = 6.2 * this.zoom;
    const cx = W / 2; // 35
    const cz = D / 2; // 25
    const cy = 17;    // EG Ground floor level (Y=126) is center

    const startLayer = this.soloLayerMode ? this.maxLayerIdx : 0;
    const endLayer = Math.min(layerCount - 1, this.maxLayerIdx);

    const visibleVoxels = [];

    // Collect Building Voxels with Culling
    for (let lIdx = startLayer; lIdx <= endLayer; lIdx++) {
      const layer = data.layers[lIdx];
      const grid = layer.grid;
      const aboveGrid = (lIdx + 1 < layerCount) ? data.layers[lIdx + 1].grid : null;
      const belowGrid = (lIdx > 0) ? data.layers[lIdx - 1].grid : null;

      for (let z = 0; z < D; z++) {
        for (let x = 0; x < W; x++) {
          const bId = grid[z][x];
          if (bId === 0) continue;

          // Occlusion check: Is this block completely surrounded by solid blocks?
          const isTopCovered = (aboveGrid && !this.soloLayerMode && aboveGrid[z][x] !== 0);
          const isBottomCovered = (belowGrid && !this.soloLayerMode && belowGrid[z][x] !== 0);
          const isLeftCovered = (x > 0 && grid[z][x - 1] !== 0);
          const isRightCovered = (x < W - 1 && grid[z][x + 1] !== 0);
          const isFrontCovered = (z < D - 1 && grid[z + 1][x] !== 0);
          const isBackCovered = (z > 0 && grid[z - 1][x] !== 0);

          // If completely occluded on all sides and not solo, cull it!
          if (isTopCovered && isBottomCovered && isLeftCovered && isRightCovered && isFrontCovered && isBackCovered && !this.soloLayerMode) {
            continue;
          }

          const rx = x - cx;
          const rz = z - cz;
          const ry = (lIdx - cy);

          // 3D Matrix Rotation
          const tx = rx * cosY - rz * sinY;
          const tz = rx * sinY + rz * cosY;
          const ty = ry;

          const screenX = tx * voxelScale;
          const screenY = (tz * sinP - ty * cosP) * voxelScale;
          const depth = tz * cosP + ty * sinP;

          visibleVoxels.push({
            sx: screenX,
            sy: screenY,
            depth: depth,
            blockId: bId,
            isTopCovered: isTopCovered,
            isTerrain: false
          });
        }
      }
    }

    // Add Mountain Terrain if World Mode is ON
    if (this.worldMode) {
      this.generateTerrainVoxels(visibleVoxels, cosY, sinY, cosP, sinP, voxelScale, cx, cz, cy);
    }

    // Sort back to front (Painter's algorithm)
    visibleVoxels.sort((a, b) => a.depth - b.depth);

    ctx.save();
    ctx.translate(this.panX, this.panY);

    // Pink Beacon Beam
    if (this.worldMode) {
      this.renderBeaconBeam(ctx, cosY, sinY, cosP, sinP, voxelScale, cx, cz, cy);
    }

    // Draw Voxels
    const tileW = 4.2 * this.zoom;
    const tileH = 2.6 * this.zoom;
    const vH = 5.2 * this.zoom;

    for (let i = 0; i < visibleVoxels.length; i++) {
      const v = visibleVoxels[i];
      const meta = data.palette[v.blockId];
      if (!meta) continue;

      const baseColor = meta.color;
      const sx = v.sx;
      const sy = v.sy;

      // Glow effect for Sea Lanterns, Water, Soul Fire & Copper Bulbs
      if (v.blockId === 23 || v.blockId === 17 || v.blockId === 21 || v.blockId === 18) {
        if (this.timeOfDay === 'night' || this.timeOfDay === 'sunset') {
          ctx.fillStyle = (v.blockId === 23) ? 'rgba(56, 189, 248, 0.28)' :
                          (v.blockId === 17) ? 'rgba(2, 132, 199, 0.22)' :
                          (v.blockId === 21) ? 'rgba(56, 189, 248, 0.32)' : 'rgba(245, 158, 11, 0.25)';
          ctx.beginPath();
          ctx.arc(sx, sy - vH / 2, tileW * 2.2, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      // Top Face
      if (!v.isTopCovered) {
        ctx.fillStyle = this.shade(baseColor, 1.15);
        ctx.beginPath();
        ctx.moveTo(sx, sy - vH);
        ctx.lineTo(sx + tileW, sy - vH + tileH / 2);
        ctx.lineTo(sx, sy - vH + tileH);
        ctx.lineTo(sx - tileW, sy - vH + tileH / 2);
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = 'rgba(0,0,0,0.15)';
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }

      // Left Face
      ctx.fillStyle = this.shade(baseColor, 0.82);
      ctx.beginPath();
      ctx.moveTo(sx - tileW, sy - vH + tileH / 2);
      ctx.lineTo(sx, sy - vH + tileH);
      ctx.lineTo(sx, sy + tileH);
      ctx.lineTo(sx - tileW, sy + tileH / 2);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,0.20)';
      ctx.lineWidth = 0.5;
      ctx.stroke();

      // Right Face
      ctx.fillStyle = this.shade(baseColor, 0.65);
      ctx.beginPath();
      ctx.moveTo(sx, sy - vH + tileH);
      ctx.lineTo(sx + tileW, sy - vH + tileH / 2);
      ctx.lineTo(sx + tileW, sy + tileH / 2);
      ctx.lineTo(sx, sy + tileH);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,0.25)';
      ctx.lineWidth = 0.5;
      ctx.stroke();
    }

    // Compass and Status HUD
    this.drawHUD(ctx, w, h);

    ctx.restore();
  }

  generateTerrainVoxels(list, cosY, sinY, cosP, sinP, scale, cx, cz, cy) {
    const step = 3;
    // Mountain terrain around 70x50 mansion
    for (let tz = -16; tz <= 64; tz += step) {
      for (let tx = -16; tx <= 86; tx += step) {
        // Skip mansion footprint
        if (tx >= 4 && tx <= 65 && tz >= 2 && tz <= 48) continue;

        let ty = 0; // Plateau height
        let bId = 15; // Stone

        // Cliff drop at north (tz < 4)
        if (tz < 4) {
          const drop = Math.min(22, (4 - tz) * 1.5);
          ty = -Math.floor(drop);
          bId = 8; // Deepslate cliff wall
        } else if (tz > 48) {
          // Driveway / slope
          ty = -Math.floor((tz - 48) * 0.35);
          bId = 15;
        }

        const rx = tx - cx;
        const rz = tz - cz;
        const ry = ty;

        const tx_rot = rx * cosY - rz * sinY;
        const tz_rot = rx * sinY + rz * cosY;

        const sx = tx_rot * scale;
        const sy = (tz_rot * sinP - ry * cosP) * scale;
        const depth = tz_rot * cosP + ry * sinP;

        list.push({
          sx: sx,
          sy: sy,
          depth: depth - 120, // push terrain slightly back
          blockId: bId,
          isTopCovered: false,
          isTerrain: true
        });
      }
    }
  }

  renderBeaconBeam(ctx, cosY, sinY, cosP, sinP, scale, cx, cz, cy) {
    // Pink Beacon Beam from screenshot at X: -657 (dx = +5, dz = -10)
    const bx = 40 - cx;
    const bz = 15 - cz;
    const by = 0;

    const rx = bx * cosY - bz * sinY;
    const rz = bx * sinY + bz * cosY;

    const sx = rx * scale;
    const sy = (rz * sinP - by * cosP) * scale;

    const beamH = 350 * this.zoom;

    // Glowing pink column
    const grad = ctx.createLinearGradient(sx - 10, sy, sx + 10, sy);
    grad.addColorStop(0, 'rgba(236, 72, 153, 0.1)');
    grad.addColorStop(0.5, 'rgba(244, 114, 182, 0.85)');
    grad.addColorStop(1, 'rgba(236, 72, 153, 0.1)');

    ctx.fillStyle = grad;
    ctx.fillRect(sx - 4 * this.zoom, sy - beamH, 8 * this.zoom, beamH);
  }

  drawHUD(ctx, w, h) {
    ctx.save();
    // Orientation Compass Indicator
    const cosY = Math.cos(this.yaw);
    const sinY = Math.sin(this.yaw);

    const compX = -this.panX + 60;
    const compY = -this.panY + 60;

    ctx.fillStyle = 'rgba(15, 23, 42, 0.75)';
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    ctx.beginPath();
    ctx.arc(compX, compY, 26, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // North Pointer (Red)
    const nx = compX + sinY * 18;
    const ny = compY - cosY * 18;
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(compX, compY);
    ctx.lineTo(nx, ny);
    ctx.stroke();

    ctx.fillStyle = '#ef4444';
    ctx.font = 'bold 9px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('N', nx, ny - 3);

    // South Pointer (Yellow)
    const sx = compX - sinY * 14;
    const sy = compY + cosY * 14;
    ctx.strokeStyle = '#fbbf24';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(compX, compY);
    ctx.lineTo(sx, sy);
    ctx.stroke();

    ctx.restore();
  }
}

window.VoxelViewer3D = VoxelViewer3D;
