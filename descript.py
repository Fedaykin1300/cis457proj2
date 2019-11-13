import json
import os


# dumps = dictionary -> String
# load  = text/binary -> python dictionary

def createJson():
	file_extensions = [".png",".jpg",".jpeg",".gif",".bmp"]
	files = os.listdir()
	imgs = {f for f in files for e in file_extensions if e in f.lower()}
	#print(imgs)
	dic = {}
	dic['files'] = []
	for img in imgs:
		print(img)
		description = input("Descriptions: ")
		file_dic = {}
		file_dic['filename'] = img
		file_dic['descriptions'] = description.split()
		dic['files'].append(file_dic)

	json_val = json.dumps(dic)
	print(type(json_val))
	#print(json.dumps(dic,indent=4))
	fp = open("files.json","w")
	fp.write(json_val)
	fp.close()

def listJson():
	fp = open("files.json","r")
	json_str = fp.read()
	fp.close()
	json_dic = json.loads(json_str)
	print(json.dumps(json_dic,indent=4))

if __name__ == "__main__":
	createJson()
	#listJson()
