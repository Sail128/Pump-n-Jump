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
    imp.import_map(
        "map_importer/map2/map.png",
        "map_importer/map2/levelfile.json",
        "map_importer/map2/levelmap.json"
    )
    imp.import_map(
        "map_importer/mapend/map.png",
        "map_importer/mapend/levelfile.json",
        "map_importer/mapend/levelmap.json"
    )


if __name__ == "__main__":
    main()