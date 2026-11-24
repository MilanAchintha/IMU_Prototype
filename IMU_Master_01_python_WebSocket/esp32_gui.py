
import serial
import tkinter as tk
import threading
import queue

esp32 = serial.Serial(
    port="COM5",
    baudrate=115200,
    timeout=0.2
)

serial_queue = queue.Queue()
def calculate_future_tsf(received_tsf):
    delay_seconds = 5
    delay_us = delay_seconds * 1_000_000
    future_tsf = received_tsf + delay_us
    print("\n========== FUTURE TSF ==========")

    print("Received TSF :", received_tsf, "us")

    print("Delay        :", delay_seconds, "seconds")

    print("Future TSF   :", future_tsf, "us")

    print("================================\n")

    return future_tsf
def serial_receiver():
    while esp32.is_open:
        try:
            if esp32.in_waiting:
                data = esp32.readline().decode(
                    "utf-8",
                    errors="replace"
                ).strip()
                if data:
                    serial_queue.put(data)
        except serial.SerialException:
            print("Serial connection error!")
            break
def start_button_clicked():
    try:
        esp32.write(b"START\n")
        status_label.config(text="START command sent!")
        tsf_label.config(text="Received TSF: Waiting...")
        future_label.config(text="Future TSF: Waiting...")
        print("START command sent to ESP32 master.")
    except serial.SerialException:
        status_label.config(text="Serial communication error!")
def update_gui():
    while not serial_queue.empty():
        message = serial_queue.get()
        print("ESP32:", message)
        if message.startswith("TSF:"):
            try:
                tsf_value = message.replace("TSF:", "")
                tsf_value = tsf_value.replace("us", "").strip()
                received_tsf = int(tsf_value)
                future_tsf = calculate_future_tsf(received_tsf)
                tsf_label.config(
                    text=f"Received TSF: {received_tsf} us"
                )
                future_label.config(
                    text=f"Future TSF: {future_tsf} us"
                )
                status_label.config(
                    text="Future TSF calculated successfully!"
                )
            except ValueError:
                print("Invalid TSF timestamp received:", message)
    root.after(50, update_gui)
def close_application():
    if esp32.is_open:
        esp32.close()
    root.destroy()
root = tk.Tk()
root.title("ESP32 TSF Controller")
root.geometry("550x350")
title_label = tk.Label(
    root,
    text="ESP32 TSF Controller",
    font=("Arial", 18, "bold")
)
title_label.pack(pady=20)
start_button = tk.Button(
    root,
    text="START",
    font=("Arial", 14),
    width=15,
    command=start_button_clicked
)
start_button.pack(pady=10)
status_label = tk.Label(
    root,
    text="Waiting for START command...",
    font=("Arial", 11)
)
status_label.pack(pady=10)
tsf_label = tk.Label(
    root,
    text="Received TSF: Not received",
    font=("Arial", 12)
)
tsf_label.pack(pady=10)
future_label = tk.Label(
    root,
    text="Future TSF: Not calculated",
    font=("Arial", 12, "bold")
)
future_label.pack(pady=10)
receiver_thread = threading.Thread(
    target=serial_receiver,
    daemon=True
)
receiver_thread.start()
root.after(50, update_gui)
root.protocol(
    "WM_DELETE_WINDOW",
    close_application
)
root.mainloop()
