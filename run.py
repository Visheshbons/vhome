import subprocess

print("\nWelcome to the VHome portal!\n")
print("Choose a device:\n")
print("(1) | Light   | CLIENT")
print("(2) | Camera  | CLIENT")
print("(3) | Speaker | CLIENT")
print("\n(4) | Server  | SERVER\n")


def loop():
    CHOICE = input("Enter your choice (number): ")

    if CHOICE == "1":
        print("\nLight selected")
        print("Running 'src/client/light.py'...\n\n")
        subprocess.run(["python", "src/client/light.py"])
    elif CHOICE == "2":
        print("\nCamera selected")
        print("Running 'src/client/camera.py'...\n\n")
        subprocess.run(["python", "src/client/camera.py"])
    elif CHOICE == "3":
        print("\nSpeaker selected")
        print("Running 'src/client/speaker.py'...\n\n")
        subprocess.run(["python", "src/client/speaker.py"])
    elif CHOICE == "4":
        print("\nServer selected")
        print("Running 'server.js'...\n\n")
        subprocess.run(["node", "server.js"])
    elif CHOICE == "help":
        print("\nAvailable commands:")
        print("(1) | Light   | CLIENT")
        print("(2) | Camera  | CLIENT")
        print("(3) | Speaker | CLIENT")
        print("(4) | Server  | SERVER")
    else:
        print("\nInvalid choice")
        loop()


loop()
