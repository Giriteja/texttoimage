chatgpt_url = "https://api.openai.com/v1/chat/completions"

import os
import io
import requests
from PIL import Image
import random

import uuid
from getpass import getpass
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from PIL import Image
import glob
import base64
import shutil

from openai import OpenAI
import webbrowser
import os

# Replace YOUR_API_KEY with your OpenAI API key
client = OpenAI(api_key = "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")

chatgpt_headers = {
    "content-type": "application/json",
    "Authorization":"Bearer {}".format('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')}
    
    
import requests
import json
from pprint import pprint

def fetch_imagedescription_and_script(prompt,url,headers):

    # Define the payload for the chat model
    messages = [
        {"role": "system", "content": "You are an expert In dividing paragrpah into subparagraphs and Generating Image Descriptions related to dalle for each Subparagraph."},
        {"role": "user", "content": prompt}
    ]

    chatgpt_payload = {
        "model": "gpt-3.5-turbo-16k",
        "messages": messages,
        "temperature": 1.3,
        "max_tokens": 2000,
        "top_p": 1,
        "stop": ["###"]
    }

    # Make the request to OpenAI's API
    response = requests.post(url, json=chatgpt_payload, headers=headers)
    response_json = response.json()

    # Extract data from the API's response
    st.write(response_json)
    output = json.loads(response_json['choices'][0]['message']['content'].strip())
    pprint (output)
    image_prompts = [k['image_description'] for k in output]
    texts = [k['text'] for k in output]

    return image_prompts, texts
    
    
   
   
def create_download_zip(zip_directory, zip_path, filename='foo.zip'):
    """ 
        zip_directory (str): path to directory  you want to zip 
        zip_path (str): where you want to save zip file
        filename (str): download filename for user who download this
    """
    shutil.make_archive(zip_path, 'zip', zip_directory)
    with open(zip_path, 'rb') as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f'<a href="data:file/zip;base64,{b64}" download=\'{filename}\'>\
            download file \
        </a>'
        st.markdown(href, unsafe_allow_html=True)
    
    
def generate_images(prompts, fname):
    # Call the API
    
	for idx,i in enumerate(prompts):
		response = client.images.generate(
		  model="dall-e-3",
		  prompt="""Generate artistic visuals for this text:"""+i,
		  size="1024x1024",
		  quality="standard",
		  n=1,
		)

		#st.write(response.data[0].url)
		# Send a GET request to the image URL
		response = requests.get(response.data[0].url)
		
		if not os.path.exists(fname):
			os.makedirs(fname)
		# Check if the request was successful
		# Open a file in binary write mode
		image_filename = os.path.join(fname, f"{idx+1}.jpg")
	    
		with open(image_filename, "wb") as file:
			# Write the content of the response to the file
			file.write(response.content)

		#image_filename = os.path.join(fname, f"{i + 1}.jpg")
		#image.save(image_filename)

		#print(f"Image {i + 1}/{num_images} saved as '{image_filename}'")
            
# Daily motivation, personal growth and positivity

txt = st.text_area("Enter the text")

paragraph = """On my way home from the bus stop, my trunk had been carried by a porter. The problem
now was we couldn’t find anyone who could help me carry the trunk to the bus stop. At another
time of the year, we would have easily found someone to help me, but now most of the villagers
were busy in the fields. Nobody had time to spare for me. In fact, carrying the trunk should not
have been such a worry for me except that my education had made me shun physical labour. After
all, I was a government officer and the idea of people seeing me carry my own luggage was not at
all amusing. Otherwise, for a young man like me it should not have been an issue to carry a 20-
kilo chest on my backt"""

if(txt):
	prompt_prefix = """You are tasked with dividing the text into paragraphs and Generating Image Descriptions for each paragraph
	Your goal is to {}.
	Please follow these instructions to create an engaging and impactful Image Descriptions for each subparagraph :
	1. Begin by setting the scene and capturing the viewer's attention with a captivating visual.
	2. For each scene cut, provide a detailed description of the stock image being shown.
	3. Along with each image description, include a corresponding subparagraph that complements and enhances the visual.
	4. Ensure that the sequence of images and text builds excitement and encourages viewers to take action.
	5. Strictly output your response in a JSON list format, adhering to the following sample structure:""".format(txt)

	sample_output="""
	   [
	       { "image_description": "Description of the first image here.", "text": "Text accompanying the first scene cut." },
	       { "image_description": "Description of the second image here.", "text": "Text accompanying the second scene cut." },
	       ...
	   ]"""

	prompt_postinstruction="""By following these instructions, you will create an impactful Image descriptions for subparagraphs.
	Output:""".format(txt)

	prompt = prompt_prefix + sample_output + prompt_postinstruction

	if(txt):
		image_prompts, texts = fetch_imagedescription_and_script(prompt,chatgpt_url,chatgpt_headers)
	st.write("image_prompts: ", image_prompts)
	st.write(texts)
	print (len(texts))


	current_uuid = uuid.uuid4()
	current_foldername = str(current_uuid)
	print (current_foldername)




	generate_images(texts, current_foldername)
	
	# Define the folder path where your images are located
	image_folder = "/home/giriteja/Downloads/"+current_foldername
	    
	    

	# Open the image
	for idx,path in enumerate(sorted(os.listdir(image_folder))):
		# Open the image
		image_path = image_folder+'/'+path  # Replace with your image file path
		image = Image.open(image_path)

		# Get the image's dimensions
		width, height = image.size

		# Define the amount of extra space to add at the bottom
		extra_space = 200  # Adjust as needed

		# Create a new image with the extended height
		new_height = height + extra_space
		new_image = Image.new("RGB", (width, new_height), (255, 255, 255))  # You can specify the background color

		# Paste the original image onto the new image at the top
		new_image.paste(image, (0, 0))

		# Create a drawing context
		draw = ImageDraw.Draw(new_image)

		# Define text content, font, size, color, and position for the bottom space
		text = texts[idx]
		font = ImageFont.truetype("Arial.ttf", 24)  # Use an appropriate font file
		text_color = (0, 0, 0)  # Black
		text_position = (20, height)  # (x, y) coordinates

		# Define the maximum width for text before wrapping
		max_text_width = width - text_position[0]

		# Create a list to store wrapped lines of text
		wrapped_lines = []

		# Split the text into lines to fit within the specified width
		words = text.split()
		line = ""
		for word in words:
			if draw.textsize(line + " " + word, font=font)[0] <= max_text_width:
				line += " " + word
			else:
				wrapped_lines.append(line)
				line = word
		wrapped_lines.append(line)

		# Calculate the total height of the wrapped text
		total_text_height = len(wrapped_lines) * font.getsize(" ")[1]

		# Calculate the vertical position to center the wrapped text
		text_position = (text_position[0], height + extra_space // 2 - total_text_height // 2)

		# Add wrapped text to the image
		for line in wrapped_lines:
		    draw.text(text_position, line.strip(), fill=text_color, font=font)
		    text_position = (text_position[0], text_position[1] + font.getsize(" ")[1])

		# Save the modified image
		output_image_path = path.split('/')[-1]  # Replace with your desired output file path
		new_image.save(current_foldername+"/"+output_image_path)
		st.image(current_foldername+"/"+output_image_path)

		# Close the images
		image.close()
		new_image.close()

		print(f"Text added to the image and saved as {output_image_path}")
		
		
	

		




	
