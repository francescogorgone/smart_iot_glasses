import time #needed for the sleep function
import subprocess #needed for espeak

# Path of the file
file_path = "/home/user/your/path/detection_log.txt"

def read_new_lines():
    with open(file_path, "r") as file: #read ('r') the file
        file.seek(0, 2)  # move the cursor from the start (0) to the end (2) of the file
        while True:
            linea = file.readline()
            if not linea:  # No new line
                time.sleep(1)  # Wait 1 second
                continue
            # Read the text with eSpeak
            subprocess.run(["espeak", linea.strip()])

if __name__ == "__main__":
    try:
        read_new_lines()
    except KeyboardInterrupt:
        print("Stopped")

