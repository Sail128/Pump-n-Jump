import json

def main():
    infile = open("assets/basetiles.json")
    indct = json.load(infile)
    infile.close()
    colorfile = open("assets/colorfile.json")
    colordict = json.load(colorfile)
    colorfile.close()
    outdct = dict()
    outdct["sprite sheet"] = "assets\\"+indct["meta"]["image"]
    outdct["objects"] = list()

    for x in indct["frames"]:
        y = dict()
        y["id"] = x["filename"]
        y["imageat"] = [ val for key,val in x["frame"].items()]
        y["collision"] = True
        y["oncollision"] = None
        y["solid"] = True
        y["box"] = [val for key,val in x["sourceSize"].items()]
        y["friction"] = 300
        y["colorval"] = colordict[ y["id"]]
        
        outdct["objects"].append(y)

    levelfile = open("assets/levelfile.json", "w")
    levelfile.write(json.dumps(outdct))
    levelfile.close()
    


if __name__ == "__main__":
    main()