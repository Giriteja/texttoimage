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
from io import BytesIO
from openai import OpenAI
import webbrowser
import os

#export GOOGLE_APPLICATION_CREDENTIALS="learninpad-4341edd012dc.json"
from google.oauth2 import service_account
from google.cloud import storage
import os

# Function to create GCP credentials from environment variables
def create_gcp_credentials():
    credentials = service_account.Credentials.from_service_account_info({
        "type": "service_account",
        "project_id": os.getenv("project_id"),
        "private_key_id": os.getenv("private_key_id"),
        "private_key": os.getenv("private_key").replace('\\n', '\n'),
        "client_email": os.getenv("client_email"),
        "client_id": os.getenv("client_id"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("client_x509_cert_url")
    })
    return credentials

# Use the custom credentials when initializing the storage client
storage_client = storage.Client(credentials=create_gcp_credentials())


# Replace YOUR_API_KEY with your OpenAI API key
client = OpenAI(api_key = os.getenv("openaikey"))

chatgpt_headers = {
    "content-type": "application/json",
    "Authorization":"Bearer {}".format(os.getenv("openaikey"))}
    
    
import requests
import json
from pprint import pprint


from os import path
import urllib.request


from google.cloud import storage

#storage_client = storage.Client()

st.title("Story Illustriator")

def upload_blob_from_memory(bucket_name, destination_blob_name, contents):
    """Uploads a file to the bucket from memory."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(contents)

    print(f"File uploaded to {destination_blob_name}.")
    
    
def upload_image_data(bucket_name, destination_blob_name, image_data):
    """Uploads image data to the specified bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(image_data, content_type='image/jpeg')

    print(f"Image uploaded to {destination_blob_name}.")
    
    
def get_image_data(bucket_name, blob_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    img_data = blob.download_as_bytes()
    return img_data

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
    
    
def generate_images(prompts, fname,lesson_name):
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
		
		bucket_name = 'lp_text_to_content'  # Replace with your bucket name
		folder_name = 'SSC_Telangana/'+class_name+"/"+subject_name+'/'+lesson_name+'/'# Replace with your folder name and include the trailing '/'
		destination_blob_name = folder_name + f"{idx+1}.jpg"  # The 'folder' and file name in the bucket

		# Assuming 'image_content' is the byte content of the image
		upload_blob_from_memory(bucket_name, destination_blob_name, response.content)

		#print(f"Image {i + 1}/{num_images} saved as '{image_filename}'")
            
		# Daily motivation, personal growth and positivity


class_name = st.text_input("Enter Class Number")
subject_name = st.selectbox(
   "Select Subject Name",
   ("English", "Social")
   
)
lesson_name = st.text_input("Enter Lesson Number")
txt = st.text_area("Enter the Paragraph")

submit=st.button("Submit")

if(submit):
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




	generate_images(texts, current_foldername,lesson_name)
	
	# Define the folder path where your images are located
	image_folder = "/home/giriteja/Downloads/"+current_foldername
	    
	    
	bucket_name = 'lp_text_to_content'  # Replace with your bucket name
	folder_name = 'SSC_Telangana/'+class_name+"/"+subject_name+'/'+lesson_name+'/' # Replace with your folder name and in
	# Open the image
	blobs = storage_client.list_blobs(bucket_name, prefix=folder_name)

	for idx,blob in enumerate(blobs):
		if blob.name.endswith('.jpg') or blob.name.endswith('.png'):
			# Get image data
			img_data = get_image_data(bucket_name, blob.name)
			# Open the image
			image = Image.open(BytesIO(img_data))

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
			#new_image.save(current_foldername+"/"+output_image_path)
			#st.image(current_foldername+"/"+output_image_path)
			buffer = BytesIO()
			new_image.save(buffer, format="JPEG")  # or "PNG", depending on your image format
			buffer.seek(0)
			image_data = buffer.getvalue()
			destination_blob_name =blob.name
			st.write(destination_blob_name)
			upload_image_data(bucket_name, destination_blob_name, image_data)
			# Close the images
			image.close()
			new_image.close()

			print(f"Text added to the image and saved as {output_image_path}")
			
		
	

		




	
