from PIL import Image
import io

# Example Usage
image_path = "WhatsApp Image 2025-01-08 at 21.41.18_e4f3b0ce.jpg"  # Replace with your image path
output_path = "output.jpg"  # Replace with your output path



def image_to_bytes(image_path, output_format='PNG'):
    """
    Convert an image to bytes.

    Args:
        image_path (str): Path to the image file.
        output_format (str): Format to save the image (e.g., 'PNG', 'JPEG').

    Returns:
        bytes: The image data as bytes.
    """
    # Open the image file
    with Image.open(image_path) as img:
        # Convert the image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=output_format)
        img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def bytes_to_image(bytes:bytes,output_path):
    image = Image.open(io.BytesIO(bytes))
    image.save(output_path)
    

def save_bytes_to_file(byte_data, output_path):
    """
    Save bytes to a file.

    Args:
        byte_data (bytes): The byte data to save.
        output_path (str): Path to save the byte data.
    """
    with open(output_path, 'wb') as f:
        f.write(byte_data)
    print(f"Bytes saved to '{output_path}'.")

def main():
    # Path to the input image
    image_path = 'WhatsApp Image 2025-01-08 at 21.41.18_e4f3b0ce.jpg'  # Replace with your image path

    # Convert the image to bytes
    image_bytes = image_to_bytes(image_path, output_format='PNG')
    print(f"Image converted to bytes (size: {len(image_bytes)} bytes)")

    bytes_to_image(image_bytes,output_path)


    # Optionally, save the bytes to a file
    save_bytes_to_file(image_bytes, 'output_image_bytes.bin')

if __name__ == '__main__':
    main()