import os
from PIL import Image

# Define input and output directories
input_folder = '/Users/satvikchaudhary/Desktop/IdealImages'
output_folder = '/Users/satvikchaudhary/Desktop/IdealImages2.0'

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Define crop percentages
crop_left_percentage = 0.17  # 17% from the left
crop_right_percentage = 0.35  # 35% from the right

# Process all .png images in the folder
for filename in os.listdir(input_folder):
    if filename.endswith('.png'):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        # Open the image
        with Image.open(input_path) as img:
            width, height = img.size

            # Calculate crop boundaries
            crop_left = int(width * crop_left_percentage)
            crop_right = int(width * (1 - crop_right_percentage))

            # Crop the image (cutting off 17% from left and 35% from right)
            cropped_img = img.crop((crop_left, 0, crop_right, height))

            # Save the cropped image
            cropped_img.save(output_path)

print(f"All images have been cropped and saved to {output_folder}")
