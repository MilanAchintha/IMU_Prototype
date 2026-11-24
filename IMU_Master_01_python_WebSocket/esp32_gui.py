
import serial
import tkinter as tk
import threading
import queue


# ==========================================================
# 1. SERIAL CONFIGURATION
# ==========================================================

# Change COM5 to the actual COM port of your ESP32 master.
# timeout=0.2 means the serial read operation waits up to
# 0.2 seconds before returning if no data is available.

esp32 = serial.Serial(
    port="COM5",
    baudrate=115200,
    timeout=0.2
)


# Queue used to transfer received serial messages
# from the background thread to the GUI thread.

serial_queue = queue.Queue()


# ==========================================================
# 2. FUTURE TSF CALCULATION
# ==========================================================

def calculate_future_tsf(received_tsf):

    # Set how far into the future we want to schedule an event.
    delay_seconds = 5

    # Convert seconds into microseconds.
    # TSF timestamps are measured in microseconds.
    delay_us = delay_seconds * 1_000_000

    # Calculate the future TSF timestamp.
    future_tsf = received_tsf + delay_us

    # Print the calculation results in the terminal.
    print("\n========== FUTURE TSF ==========")

    print("Received TSF :", received_tsf, "us")

    print("Delay        :", delay_seconds, "seconds")

    print("Future TSF   :", future_tsf, "us")

    print("================================\n")

    return future_tsf


# ==========================================================
# 3. BACKGROUND SERIAL RECEIVER THREAD
# ==========================================================

def serial_receiver():

    # Continue receiving while the serial connection is open.
    while esp32.is_open:

        try:

            # Check whether data is available from the ESP32.
            if esp32.in_waiting:

                # Read one complete line from the ESP32.
                data = esp32.readline().decode(
                    "utf-8",
                    errors="replace"
                ).strip()

                # Put received messages into the queue.
                if data:
                    serial_queue.put(data)

        except serial.SerialException:

            print("Serial connection error!")
            break


# ==========================================================
# 4. START BUTTON FUNCTION
# ==========================================================

def start_button_clicked():

    try:

        # Send START command to the ESP32 master.
        esp32.write(b"START\n")

        # Update GUI status.
        status_label.config(text="START command sent!")

        # Clear previous TSF display.
        tsf_label.config(text="Received TSF: Waiting...")

        future_label.config(text="Future TSF: Waiting...")

        print("START command sent to ESP32 master.")

    except serial.SerialException:

        status_label.config(text="Serial communication error!")


# ==========================================================
# 5. PROCESS RECEIVED SERIAL MESSAGES
# ==========================================================

def update_gui():

    # Process all messages currently waiting in the queue.
    while not serial_queue.empty():

        message = serial_queue.get()

        # Print every received message in the terminal.
        print("ESP32:", message)

        # Check whether the message contains a TSF timestamp.
        if message.startswith("TSF:"):

            try:

                # Remove TSF: and us from the received message.
                tsf_value = message.replace("TSF:", "")
                tsf_value = tsf_value.replace("us", "").strip()

                # Convert the TSF string into an integer.
                received_tsf = int(tsf_value)

                # Calculate the future TSF timestamp.
                future_tsf = calculate_future_tsf(received_tsf)

                # Display received TSF in the GUI.
                tsf_label.config(
                    text=f"Received TSF: {received_tsf} us"
                )

                # Display calculated future TSF in the GUI.
                future_label.config(
                    text=f"Future TSF: {future_tsf} us"
                )

                # Update status.
                status_label.config(
                    text="Future TSF calculated successfully!"
                )

            except ValueError:

                print("Invalid TSF timestamp received:", message)

    # Run this function again after 50 milliseconds.
    root.after(50, update_gui)


# ==========================================================
# 6. CLOSE APPLICATION SAFELY
# ==========================================================

def close_application():

    # Close serial connection before exiting.
    if esp32.is_open:
        esp32.close()

    # Close GUI window.
    root.destroy()


# ==========================================================
# 7. CREATE GUI WINDOW
# ==========================================================

root = tk.Tk()

root.title("ESP32 TSF Controller")

root.geometry("550x350")


# ==========================================================
# 8. GUI TITLE
# ==========================================================

title_label = tk.Label(
    root,
    text="ESP32 TSF Controller",
    font=("Arial", 18, "bold")
)

title_label.pack(pady=20)


# ==========================================================
# 9. START BUTTON
# ==========================================================

start_button = tk.Button(
    root,
    text="START",
    font=("Arial", 14),
    width=15,
    command=start_button_clicked
)

start_button.pack(pady=10)


# ==========================================================
# 10. STATUS DISPLAY
# ==========================================================

status_label = tk.Label(
    root,
    text="Waiting for START command...",
    font=("Arial", 11)
)

status_label.pack(pady=10)


# ==========================================================
# 11. RECEIVED TSF DISPLAY
# ==========================================================

tsf_label = tk.Label(
    root,
    text="Received TSF: Not received",
    font=("Arial", 12)
)

tsf_label.pack(pady=10)


# ==========================================================
# 12. FUTURE TSF DISPLAY
# ==========================================================

future_label = tk.Label(
    root,
    text="Future TSF: Not calculated",
    font=("Arial", 12, "bold")
)

future_label.pack(pady=10)


# ==========================================================
# 13. START BACKGROUND SERIAL THREAD
# ==========================================================

receiver_thread = threading.Thread(
    target=serial_receiver,
    daemon=True
)

receiver_thread.start()


# ==========================================================
# 14. START GUI MESSAGE PROCESSING
# ==========================================================

# Check the queue every 50 milliseconds.
root.after(50, update_gui)


# ==========================================================
# 15. HANDLE WINDOW CLOSING
# ==========================================================

root.protocol(
    "WM_DELETE_WINDOW",
    close_application
)


# ==========================================================
# 16. RUN GUI
# ==========================================================

root.mainloop()
