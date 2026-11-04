# Blackthorn Estate — Terrain Blueprint Studio

A browser-based planning workspace for the six-resident Victorian/Gothic cliffside estate.

## Start

Linux:
```bash
chmod +x start.sh
./start.sh
```
Windows: double-click `start.bat`.

Open http://localhost:8000. No npm dependencies or external services are required.

## Project data
- User-provided anchor: X=-662, Y=126, Z=790
- User-provided seed: -4815224116428668341 (not independently verified from the supplied level.dat)
- Uploaded Paper world metadata identifies Paper / Minecraft 26.3, DataVersion 5023. The requested 26.2 is therefore not confirmed by this upload.
- `terrain.json` contains 13,736 sampled WORLD_SURFACE heightmap columns for X=-780..-645 and Z=740..840, read from the uploaded MCA region files.
- `assets/terrain-heightmap.png` is a visualization of those heights.

## Important terrain finding
The steep drop is on the WEST (negative X) side of the surveyed area, not east of the anchor. The anchor is on the higher plateau at approximately Y=127–128. The concept therefore places the main entrance to the EAST (+X) and the terraces / pool / panorama rooms to the WEST (-X).

## Included features
- Terrain heightmap and terrain explorer
- Floorplan explorer for seven levels with absolute coordinate ranges
- Six private residence summaries
- Survival-oriented material palette
- Construction phases with local checklists
- JSON export of checklist progress

## Accuracy / limitations
This is a terrain-informed architectural layout, not yet a block-exact schematic. The block palette was additionally sampled at representative points: at the anchor (-662,790), grass_block is at Y=126, dirt below, and stone from approximately Y=122. At (-775,790), exposed stone begins at Y=96 and the surface is around Y=97. This confirms a rocky western slope. A complete block-by-block classification of every plot chunk, water and underground cavities is still outstanding; exact excavation and material counts must wait for that scan. Floor plans are a concrete coordinate-based design proposal, not a Litematica/WorldEdit export.
