
import serial
import tkinter as tk
import threading
import queue

# Serial configuration
esp32 = serial.Serial("COM5", 115200, timeout=0.2)

# Queue for received serial messages
serial_queue = queue.Queue()


# Background thread: receive data from ESP32
def serial_receiver():

    while esp32.is_open:

        try:
            if esp32.in_waiting:
                data = esp32.readline().decode("utf-8", errors="replace").strip()

                if data:
                    serial_queue.put(data)

        except serial.SerialException:
            break


# START button function
def start_button_clicked():

    esp32.write(b"START\n")

    status_label.config(text="START command sent!")
    tsf_label.config(text="Waiting for TSF...")


# Read received messages and update GUI
def update_gui():

    while not serial_queue.empty():

        message = serial_queue.get()

        # Print received message in terminal
        print("ESP32:", message)

        # Check whether the message contains TSF
        if message.startswith("TSF:"):

            tsf_value = message.replace("TSF:", "").strip()

            tsf_label.config(text=f"TSF: {tsf_value}")

            status_label.config(text="TSF received successfully!")

    # Check again after 50 ms
    root.after(50, update_gui)


# Close application safely
def close_application():

    if esp32.is_open:
        esp32.close()

    root.destroy()


# Create GUI
root = tk.Tk()
root.title("ESP32 TSF Controller")
root.geometry("400x250")

# Title
title_label = tk.Label(
    root,
    text="ESP32 TSF Controller",
    font=("Arial", 16)
)
title_label.pack(pady=20)

# START button
start_button = tk.Button(
    root,
    text="START",
    font=("Arial", 14),
    command=start_button_clicked
)
start_button.pack(pady=10)

# Status
status_label = tk.Label(
    root,
    text="Waiting...",
    font=("Arial", 11)
)
status_label.pack(pady=10)

# TSF display
tsf_label = tk.Label(
    root,
    text="TSF: Not received",
    font=("Arial", 14, "bold")
)
tsf_label.pack(pady=10)


# Start background serial receiver
receiver_thread = threading.Thread(
    target=serial_receiver,
    daemon=True
)
receiver_thread.start()

# Start GUI serial-message polling
root.after(50, update_gui)

# Handle window closing
root.protocol("WM_DELETE_WINDOW", close_application)

# Run GUI
root.mainloop()
