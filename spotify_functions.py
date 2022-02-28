import requests
import logging
from PIL import Image
from pprint import pprint
from io import BytesIO 
import numpy as np

SPOTIFY_ACCESS_TOKEN = ''
SPOTIFY_GET_TRACKS_URL = 'https://api.spotify.com/v1/me/tracks'

#Collects urls of the highest resolution album cover for every liked song in users library(duplicates excluded) into a list
def collect_album_covers():

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
		#Collect response in JSON format
		track_set_url = f"{SPOTIFY_GET_TRACKS_URL}?limit={limit}&offset={offset}"
		response = requests.get(track_set_url, headers={"Authorization": f"Bearer {SPOTIFY_ACCESS_TOKEN}"})
		resp_json = response.json()

		items = resp_json['items']

		#This will happen if you are at the end of available songs in the library
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

	return album_covers


#Creates a collage image of all of a users liked song album covers and saves it to the images folder
def get_album_artwork():
	
	#Assemble the album covers into a list of urls
	album_covers = collect_album_covers()

	logging.info("Liked tracks read")
	
	#Build the 1920x1080 image
	album_collage = Image.new("RGBA", (1920, 1080), color=(255,255,255,255))

	logging.info(f"album_covers length: {len(album_covers)}")

	#The length of one side of an album displayed in the collage is equal to the square root of (the area of the walpaper(1920x1080) divided by the number of albums)
	#unless of course there are more than 2073600 albums, then they are the size of a single pixel
	if (len(album_covers) < 2073600):
		dimension = int(np.sqrt(2073600 / len(album_covers)))
	else:
		dimension = 1

	#Tweak the size of the dimension so that there are albums completely covering the image
	while(len(album_covers) < (int(1080/dimension) * int(1920/dimension))):
		dimension+=1

	logging.info("Building Image")

	n = 0

	#Pull the album image from the url in album_covers, resize it and add to the image
	for i in range (0,1080,dimension):
		for j in range(0,1920,dimension):
			try:
				second_response = requests.get(album_covers[n])
				image = Image.open(BytesIO(second_response.content))
			except Exception:
				#If for some reason getting the image fails the image is replaced with a black square
				image = Image.new("RGB", (dimension,dimension))

			image = image.resize((dimension,dimension))
			album_collage.paste(image, (j,i))
			n+=1

	logging.info('Preparing to save')

	#Save the collage image to images folder
	album_collage.save("images/collage.png")

	logging.info('Saved')