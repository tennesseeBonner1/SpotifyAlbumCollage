import requests
from PIL import Image
from io import BytesIO 
import numpy as np
from auth import *

SPOTIFY_GET_TRACKS_URL = 'https://api.spotify.com/v1/me/tracks'

#Collects urls of the highest resolution album cover for every liked song in users library(duplicates excluded) into a list
def collect_album_covers():

	album_covers = set()

	#Used to build request url for up to 50 liked songs at a time
	limit = 50

	access_token = get_access_token()

	print("Assembling list of all album image urls...")
	#Save album covers in url form to album_covers list

	track_get_url = f"{SPOTIFY_GET_TRACKS_URL}?limit={limit}"
	headers = {"Authorization": f"Bearer {access_token}"}

	with requests.Session() as session:
		session.headers.update(headers)

		tracks_read = 0

		while(track_get_url):
			response = session.get(track_get_url)
			response.raise_for_status()

			resp_json = response.json()

			items = resp_json['items']

			for item in items:
				images = item['track']['album']['images']
				
				#Just in case no album artwork present
				if images:
					album_covers.add(images[0]['url'])

			track_get_url = resp_json["next"]
			tracks_read += len(items)
			print(f"\r{tracks_read} tracks read", end="", flush=True)

	print(f"\nAlbum cover image urls collected.")

	return list(album_covers)


#Creates a collage image of all of a users liked song album covers and saves it to the images folder
def get_album_artwork():
	
	#Assemble the album covers into a list of urls
	album_covers = collect_album_covers()

	print("Liked tracks read")
	
	#Build the 1920x1080 image
	album_collage = Image.new("RGBA", (1920, 1080), color=(255,255,255,255))

	print(f"album_covers length: {len(album_covers)}")

	#The length of one side of an album displayed in the collage is equal to the square root of (the area of the walpaper(1920x1080) divided by the number of albums)
	#unless of course there are more than 2073600 albums, then they are the size of a single pixel
	if (len(album_covers) < 2073600):
		dimension = int(np.sqrt(2073600 / len(album_covers)))
	else:
		dimension = 1

	#Tweak the size of the dimension so that there are albums completely covering the image
	while(len(album_covers) < (int(1080/dimension) * int(1920/dimension))):
		dimension+=1

	print("Building Image")

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
			print(f"\rImage {n} added", end="", flush=True)

	print('\nPreparing to save')

	#Save the collage image to images folder
	album_collage.save("images/collage.png")

	print('Saved')
