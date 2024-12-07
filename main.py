from visualize import Visualize
from robot import threeBot

if __name__ == "__main__":
    print("Choose mode: ")
    print("1. Visualize Game")
    print("2. Run AI-only game (threeBot)")

    choice = int(input("Enter 1 or 2: "))
    if choice == 1:
        Visualize()
    elif choice == 2:
        threeBot()
    else:
        print("Invalid choice.")