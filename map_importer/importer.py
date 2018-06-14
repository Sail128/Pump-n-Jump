import sys
import json as json
from PIL import Image

#black values in the image will be key 0 and left empty by the rendering engine
def import_map(imgpath, objlistpath, outputpath):
    objfile = open(objlistpath)
    objdict = json.load(objfile)
    objfile.close()
    objlist = objdict["objects"] if "objects" in objdict else print("key error 'objects' in objectlist file")
    empty = objdict["empty"] if "empty" in objdict else [0,0,0]
    keylist = []
    keylist.append(tuple(empty))
    for x in objlist:
        keylist.append(tuple(x["colorval"]))
    print(keylist)
    im = Image.open(imgpath)
    size = im.size
    levelmap = im.load()
    maparray = []
    for y in range(size[1]):
        row = []
        for x in range(size[0]):
            row.append(keylist.index(levelmap[x,y][:3]))
        maparray.append(row)

    objdict["map"] = maparray
    outfiledata = { "objects": objlist,
                    "map": maparray
    }

    outfile = open(outputpath,"w")
    outfile.write(json.dumps(objdict))
    outfile.close()

##tool for converting an image with a list to a relevant map file
#usage: python importer.py "imagepath" "objlistpath" "outputpath"
#all paths are reletive to th importer.py script
def main(args:list):
    print("importing map")
    if len(args) == 4:
        imgpath = args[1]
        objlistpath = args[2]
        outputpath = args[3]
    else:
        imgpath = input("image path: ")
        objlistpath = input("object list path: ")
        outputpath = input("output file path: ")
    import_map(imgpath, objlistpath, outputpath)




if __name__ == "__main__":
    main(sys.argv)