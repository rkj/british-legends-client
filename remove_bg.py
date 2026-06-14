from PIL import Image

def make_white_transparent_smooth(image_path, out_path):
    img = Image.open(image_path).convert("RGBA")
    data = img.getdata()

    new_data = []
    for item in data:
        r, g, b, a = item
        
        # Calculate how white the pixel is. White is 255, 255, 255
        # The background is white, the gold is dark/yellowish
        avg = (r + g + b) / 3.0
        
        if avg > 245:
            # Pure white or almost pure white -> transparent
            new_data.append((r, g, b, 0))
        elif avg > 210:
            # Edge pixels - make them partially transparent
            ratio = (245 - avg) / 35.0
            new_a = int(255 * ratio)
            new_data.append((r, g, b, new_a))
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save(out_path, "PNG")

if __name__ == "__main__":
    make_white_transparent_smooth('gold-divider-v.png', 'gold-divider-v.png')
    print("Done")
