import os

# Path to your folder
folder_path = "/Users/satvikchaudhary/Desktop/IdealImages"

# List all items in the folder
items = os.listdir(folder_path)

# Count items
item_count = len(items)

print(f"Total number of items in '{folder_path}': {item_count}")
