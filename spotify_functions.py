import requests
import logging
from PIL import Image
from pprint import pprint
from io import BytesIO 
import numpy as np

SPOTIFY_ACCESS_TOKEN = ''
SPOTIFY_GET_TRACKS_URL = 'https://api.spotify.com/v1/me/tracks'

def get_album_artwork():
	
	album_covers = []

	#Used to build request url for up to 50 liked songs at a time
	limit = 50
	offset = 0

	#Logging
	level = logging.INFO
	fmt = '[%(levelname)s] %(asctime)s - %(message)s'
	logging.basicConfig(level=level, format=fmt)
	logging.info("Reading liked tracks")

	#Save album covers in url form to album_covers list
	while(True):
		track_set_url = f"{SPOTIFY_GET_TRACKS_URL}?limit={limit}&offset={offset}"
		response = requests.get(track_set_url, headers={"Authorization": f"Bearer {SPOTIFY_ACCESS_TOKEN}"})
		resp_json = response.json()

		items = resp_json['items']

		#This will happen if you are at the end of available albums 
		if(len(items) < 1):
			break

		for item in items:
			#Just in case no album artwork present
			if(len(item['track']['album']['images']) != 0):
				album_covers.append(item['track']['album']['images'][0]['url'])

		#Remove duplicate urls(for the same albums)
		album_covers = list(dict.fromkeys(album_covers))

		#Increase offset for the next request
		offset += 50

	logging.info("Liked tracks read")
	
	#Build the image
	album_collage = Image.new("RGBA", (1920, 1080), color=(255,255,255,255))

	n = 0

	logging.info(f"album_covers length: {len(album_covers)}")

	dimension = int(np.sqrt(2073600 / len(album_covers)))

	#Tweak the size of the dimension so that there are albums completely covering the image
	while(len(album_covers) < (int(1080/dimension) * int(1920/dimension))):
		dimension+=1

	logging.info("Building Image")

	#Pull the album image from the url in album_covers, resize it and add to the image
	for i in range (0,1080,dimension):
		for j in range(0,1920,dimension):
			try:
				second_response = requests.get(album_covers[n])
				image = Image.open(BytesIO(second_response.content))
			except Exception:
				image = Image.new("RGB", (dimension,dimension))

			image = image.resize((dimension,dimension))
			album_collage.paste(image, (j,i))
			n+=1

	logging.info('Preparing to save')

	#Save the collage image to images folder
	album_collage.save("images/collage.png")

	logging.info('Saved')