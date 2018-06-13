import importer as imp

def main():
    imp.import_map(
        "map_importer/map0/map.png",
        "map_importer/map0/objectlist.json",
        "map_importer/map0/levelmap.json"
    )
    imp.import_map(
        "map_importer/map1/map.png",
        "map_importer/map1/levelfile.json",
        "map_importer/map1/levelmap.json"
    )


if __name__ == "__main__":
    main()