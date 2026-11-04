from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import numpy as np

# Load world screenshot
world_bg = Image.open('Fotos/image.png').convert('RGBA')
W_bg, H_bg = world_bg.size

# Let's inspect the vorlage mansion crop
vorlage_crop = Image.open('vorlage_mansion_crop.png').convert('RGBA')
# The vorlage crop is (335, 210)
# Let's remove any blue sky background from the crop so only the building and roof remains
arr = np.array(vorlage_crop)
r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]
# Sky in vorlage is bright blue/grey: b > 140 and b > r + 15
sky_mask = (b > 135) & (b > r + 10) & (arr.shape[0] < 120)
# Make sky transparent
arr[sky_mask, 3] = 0
clean_building = Image.fromarray(arr)

# The mansion should fill the plateau trench properly (~780 px wide instead of 644)
target_w = 780
aspect = clean_building.size[1] / clean_building.size[0]
target_h = int(target_w * aspect * 1.15) # Slightly taller for Victorian vertical grandeur

building_scaled = clean_building.resize((target_w, target_h), Image.Resampling.LANCZOS)

# Enhance sunset golden-hour warmth and contrast to match image.png
enhancer_color = ImageEnhance.Color(building_scaled)
building_warm = enhancer_color.enhance(1.25)

enhancer_bright = ImageEnhance.Brightness(building_warm)
building_warm = enhancer_bright.enhance(0.95)

enhancer_contrast = ImageEnhance.Contrast(building_warm)
building_warm = enhancer_contrast.enhance(1.18)

# Add warm sunset gradient tint (golden sunlight from the front-left)
tint = Image.new('RGBA', building_warm.size, (255, 175, 105, 0))
tint_arr = np.array(tint)
for y in range(target_h):
    alpha = int(45 * (1.0 - y / target_h * 0.4)) # warmer at top
    tint_arr[y, :, 3] = alpha
tint_img = Image.fromarray(tint_arr)
building_final = Image.alpha_composite(building_warm, tint_img)

# Position on the plateau
# Plateau base is around y=485..510, center x=980
pos_x = 980 - target_w // 2
pos_y = 510 - target_h + 30

# Create composite
composite = world_bg.copy()

# Add building shadow onto the plateau terrain behind/around it
shadow = Image.new('RGBA', (target_w + 80, 70), (20, 15, 10, 110))
shadow = shadow.filter(ImageFilter.GaussianBlur(16))
composite.alpha_composite(shadow, (pos_x - 40, pos_y + target_h - 40))

# Composite building
composite.alpha_composite(building_final, (pos_x, pos_y))

# Add soft chimney smoke drifting to the right
smoke_canvas = Image.new('RGBA', composite.size, (0, 0, 0, 0))
draw = ImageDraw.Draw(smoke_canvas)
# Left chimney around x = pos_x + 160, y = pos_y + 35
# Right chimney around x = pos_x + target_w - 180, y = pos_y + 35
for (cx, cy) in [(pos_x + int(target_w * 0.22), pos_y + 25), (pos_x + int(target_w * 0.78), pos_y + 25)]:
    for i in range(12):
        sx = cx + i * 8 + int(np.sin(i) * 6)
        sy = cy - i * 14
        r_smoke = 6 + i * 3
        alpha = max(0, 120 - i * 10)
        draw.ellipse([sx - r_smoke, sy - r_smoke, sx + r_smoke, sy + r_smoke], fill=(235, 230, 220, alpha))

smoke_blurred = smoke_canvas.filter(ImageFilter.GaussianBlur(6))
composite = Image.alpha_composite(composite, smoke_blurred)

# Save high-res render
composite.save('mansion_in_world_render.png')
print("Successfully generated high-resolution in-world render at mansion_in_world_render.png")
