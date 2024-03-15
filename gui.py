import tkinter as tk
from tkinter import filedialog
import json
import subprocess
import time
import os

def is_docker_compose_up():
    result = subprocess.run(["docker", "ps"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    total_containers = result.stdout.count("Up") 
    expected_total_containers = 3 + int(os.environ["NUM_WORKERS"])
    return total_containers == expected_total_containers

def submit_input():
    filename = label_filename.cget("text")
    centroids = int(centroids_var.get())
    parts = int(parts_var.get())
    num_workers = int(workers_var.get())

    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        config["k_mean"]["parts"] = int(parts)
        config["k_mean"]["centers"] = int(centroids)

        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=2)
        
        os.environ["NUM_WORKERS"] = str(num_workers)

        print("Config updated successfully.")
        print(is_docker_compose_up())
        if not is_docker_compose_up():
            subprocess.Popen(["docker", "compose", "up"], stdout=subprocess.DEVNULL)
            while not is_docker_compose_up():
                time.sleep(1)
        
        result = subprocess.run(["python", "client/task.py", filename], stdout=subprocess.PIPE, text=True)
        result_window = tk.Toplevel(root)
        result_window.title("Result Window")

        result_label = tk.Label(result_window, text=f"Task ID: {result.stdout}")
        result_label.pack(pady=10)

        subprocess.Popen(["python", "client/result.py", result.stdout], stdout=subprocess.PIPE, text=True)
        save_button = tk.Button(result_window, text="Save", command=lambda: save_result(result.stdout))
        save_button.pack(pady=10)

    except Exception as e:
        print(f"Error: {e}")

def browse_file():
    file_path = filedialog.askopenfilename()
    label_filename.config(text=file_path)

def save_result(task_id):
    print(["python", "client/result.py", task_id])
    subprocess.Popen(["python", "client/result.py", task_id[:-1]], stdout=subprocess.PIPE, text=True)
    print(f"Result saved for Task ID: {task_id}")

root = tk.Tk()
root.title("File Processing GUI")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x_coordinate = (screen_width - root.winfo_reqwidth()) // 2
y_coordinate = (screen_height - root.winfo_reqheight()) // 2

root.geometry(f"+{x_coordinate}+{y_coordinate}")

label_filename = tk.Label(root, text="No file selected")
label_filename.pack(pady=5)

browse_button = tk.Button(root, text="Browse", command=browse_file)
browse_button.pack(pady=5)

label_centroids = tk.Label(root, text="Number of Centroids")
label_centroids.pack(pady=5)

centroids_var = tk.IntVar()
entry_centroids = tk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL, variable=centroids_var, length=300)
entry_centroids.pack(pady=5)

label_parts = tk.Label(root, text="Number of Parts")
label_parts.pack(pady=5)

parts_var = tk.IntVar()
entry_parts = tk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL, variable=parts_var, length=300)
entry_parts.pack(pady=5)

label_workers = tk.Label(root, text="Number of Workers")
label_workers.pack(pady=5)

workers_var = tk.IntVar()
entry_workers = tk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL, variable=workers_var, length=300)
entry_workers.pack(pady=5)

submit_button = tk.Button(root, text="Submit", command=submit_input)
submit_button.pack(pady=10)

root.mainloop()
