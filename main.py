import requests
from PIL import Image
from pprint import pprint
from io import BytesIO 
from math import sqrt

SPOTIFY_ACCESS_TOKEN = ''
SPOTIFY_GET_TRACKS_URL = 'https://api.spotify.com/v1/me/tracks'

def get_album_artwork():
	album_covers = []

	print("Reading liked tracks")

	#Used to build request url for up to 50 liked songs at a time
	limit = 50
	offset = 0

	#Save album covers in url form to album_covers list
	while(True):
		track_set_url = SPOTIFY_GET_TRACKS_URL + '?limit='+ str(limit) +'&offset=' + str(offset)
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

		#Increase offset for the next request
		offset += 50

	print("Liked tracks read")
	#Remove duplicate urls(for the same albums)
	album_covers = list(dict.fromkeys(album_covers))

	print("post dict sort")
	#Build the image
	album_collage = Image.new("RGBA", (1920, 1080), color=(255,255,255,255))

	n = 0

	print ('Album cover length' + str(len(album_covers)))

	dimension = int(sqrt(2073600 / len(album_covers)))

	while(len(album_covers) < (int(1080/dimension) * int(1920/dimension))):
		dimension+=1

	print("Pre loops")
	for i in range (0,1080,dimension):
		print("i loop" + str(i))
		for j in range(0,1920,dimension):
			try:
				second_response = requests.get(album_covers[n])
				image = Image.open(BytesIO(second_response.content))
			except Exception:
				image = Image.new("RGB", (dimension,dimension))

			image = image.resize((dimension,dimension))
			album_collage.paste(image, (j,i))
			n+=1

	print('preparing to save')
	album_collage.save("collage.png")
	print('saved')
	#pprint(album_covers, indent=4)


def main():
	get_album_artwork()

	

if __name__ == '__main__':
	main()