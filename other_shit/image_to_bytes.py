from PIL import Image
import io
import base64

# Load image
image = Image.open("other_shit\\test_1.png")

# Convert to bytes
img_byte_arr = io.BytesIO()
image.save(img_byte_arr, format='PNG')
image_bytes = img_byte_arr.getvalue()
# Convert bytes to base64 string
image_string = base64.b64encode(image_bytes)

# Write string to file
with open('image_bytes.txt', 'w') as f:
    f.write(str(image_string))

print("String saved to image_bytes.txt")
