from visualize import Visualize

if __name__ == "__main__":
    print("Choose mode: ")
    print("1. Visualize Game")

    choice = int(input("Enter 1 or 2: "))
    if choice == 1:
        Visualize()
    else:
        print("Invalid choice.")