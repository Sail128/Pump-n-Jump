import game as g

def main():
    print("Starting the game")
    game = g.Game()
    game.setLevelDir("levels")
    game.setLevelList(["start.json", "level1.json"])
    game.start()
    game.run()
    print("game closed")

if __name__ == "__main__":
    main()