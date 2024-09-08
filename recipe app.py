import tkinter as tk
from tkinter import scrolledtext
from tkinter import PhotoImage
import requests
from PIL import Image, ImageTk, UnidentifiedImageError
from io import BytesIO

def get_recipe(api_key, query):
    base_url = "https://api.spoonacular.com/recipes/search"

    params = {
        'apiKey': api_key,
        'query': query,
        'number': 5,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()

        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)

        for result in data['results']:
            recipe_id = result['id']
            recipe_title = result['title']

            # Fetch and display ingredients and instructions
            recipe_details = get_recipe_details(api_key, recipe_id)
            if recipe_details:
                # Display recipe information on the left
                result_text.insert(tk.END, f"Title: {recipe_title}\n")
                result_text.insert(tk.END, f"ID: {recipe_id}\n")

                result_text.insert(tk.END, "Ingredients:\n")
                for ingredient in recipe_details.get('extendedIngredients', []):
                    ingredient_name = ingredient.get('originalString', ingredient.get('name', 'Unknown Ingredient'))
                    result_text.insert(tk.END, f"- {ingredient_name}\n")

                result_text.insert(tk.END, "Instructions:\n")
                for step in recipe_details.get('analyzedInstructions', []):
                    for instruction in step.get('steps', []):
                        result_text.insert(tk.END, f"{instruction['number']}. {instruction['step']}\n")

                # Fetch and display image from Unsplash based on the user's query
                image_url = get_unsplash_image(unsplash_api_key, query)
                try:
                    if image_url:
                        response = requests.get(image_url)
                        response.raise_for_status()

                        # Check if the content type is image
                        if response.headers['content-type'].startswith('image'):
                            image_data = response.content

                            # Display recipe image in the middle with additional vertical padding
                            update_image(image_data)

                        else:
                            result_text.insert(tk.END, "Invalid image content\n")
                    else:
                        result_text.insert(tk.END, "No image URL provided\n")

                except (requests.exceptions.RequestException, UnidentifiedImageError) as e:
                    result_text.insert(tk.END, f"Error fetching image: {e}\n")

                result_text.insert(tk.END, "--------\n")

        result_text.config(state=tk.DISABLED)

    except requests.exceptions.RequestException as e:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Error: {e}\n")
        result_text.config(state=tk.DISABLED)

def update_image(image_data):
    # Clear previous image label
    for widget in root.winfo_children():
        if isinstance(widget, tk.Label) and hasattr(widget, 'is_image_label') and widget.is_image_label:
            widget.destroy()

    # Display recipe image in the middle with additional vertical padding
    image = Image.open(BytesIO(image_data))
    image = image.resize((150, 150), Image.BICUBIC)  # Adjust the size as needed
    photo_image = ImageTk.PhotoImage(image)
    image_label = tk.Label(root, image=photo_image)
    image_label.image = photo_image
    image_label.is_image_label = True
    image_label.pack(side=tk.TOP, pady=20)  # Adjust the padding as needed

def get_recipe_details(api_key, recipe_id):
    details_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"

    params = {
        'apiKey': api_key,
    }

    try:
        response = requests.get(details_url, params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching recipe details: {e}")
        return None

def get_unsplash_image(api_key, query):
    unsplash_url = "https://api.unsplash.com/photos/random"

    headers = {
        'Authorization': f'Client-ID {api_key}',
    }

    params = {
        'query': query,
    }

    try:
        response = requests.get(unsplash_url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        if 'urls' in data and 'regular' in data['urls']:
            return data['urls']['regular']
        else:
            print("Invalid Unsplash API response:", data)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Unsplash image: {e}")

    return ''

# Replace 'YOUR_API_KEY' and 'YOUR_UNSPLASH_API_KEY' with your actual API keys
api_key = 'YOUR_API_KEY'
unsplash_api_key = 'YOUR_UNSPLASH_API_KEY'

root = tk.Tk()
root.title("Recipe App")

bg_color = "#ce84ad"
root.configure(bg=bg_color)

label = tk.Label(root, text="Enter recipe query:", bg="#CE96A6", fg="#EBEBEB", font=("Rubik", 14))
label.pack(pady=10)

entry = tk.Entry(root, width=30, bg="#D1A7A0", font=("Rubik", 12))
entry.pack(pady=10)

search_button = tk.Button(root, text="Search", command=lambda: get_recipe(api_key, entry.get()), bg="#CE96A6", fg="#EBEBEB", font=("Rubik", 12))
search_button.pack(pady=10)

result_text = scrolledtext.ScrolledText(root, width=80, height=20, state=tk.DISABLED, bg="#E5C2C0", fg="#333333", font=("Rubik", 10))
result_text.pack(pady=10)

root.mainloop()
