import tkinter as tk
from tkinter import PhotoImage
import time

class StopwatchApp:
    def __init__(self, root):
        self.root = root

        self.running = False
        self.start_time = 0
        self.elapsed_time = 0

        self.label = tk.Label(root, text="00:00:00", font=("Sitka", 20), fg='grey', width=11)
        self.label.place(x=0, y=400)

        self.start_pause_button = tk.Button(root,
                                            text="Start",
                                            font=("Sitka", 5),
                                            bg="white",
                                            width=23,
                                            command=self.start_pause_stopwatch,
                                            pady=5,
                                            padx=20)
        self.start_pause_button.place(x=44, y=440)

        self.reset_button = tk.Button(root,
                                      text="Reset",
                                      font=("Sitka", 5),
                                      bg="white",
                                      command=self.reset_stopwatch,
                                      pady=5,
                                      padx=20)
        self.reset_button.place(x=4, y=440)

    def update_time(self):
        if self.running:
            self.elapsed_time = time.time() - self.start_time
        hours, rem = divmod(int(self.elapsed_time), 3600)
        minutes, seconds = divmod(rem, 60)
        self.label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}", bg="white")
        self.root.after(1000, self.update_time)

    def start_pause_stopwatch(self):
        if not self.running:
            if self.elapsed_time == 0:
                self.start_time = time.time()
            else:
                self.start_time = time.time() - self.elapsed_time
            self.start_pause_button.config(text="Pause")
        else:
            self.elapsed_time = time.time() - self.start_time
            self.start_pause_button.config(text="Resume")
        self.running = not self.running

    def reset_stopwatch(self):
        self.running = False
        self.start_pause_button.config(text="Start")
        self.elapsed_time = 0
        self.label.config(text="00:00:00")


# --------------------------------------------------------

def update():
    time_string = strftime("%H:%M:%S")
    time_label.config(text=time_string, bg="white", font=("Sitka",8))

    #  day_string = strftime("%A")
    #  day_label.config(text=day_string)

    # date_string = strftime("%B %d, %Y")
    # date_label.config(text=date_string)

    window.after(1000, update)  #update každých 1000ms - recursife function update


def scroll_background():
    global offset, direction
    canvas.delete("background")  # Clear previous background

    # Update the offset based on the direction
    offset += direction * scroll_speed

    # Check if the offset reaches the window boundaries
    if offset <= -image.width() + canvas.winfo_width() or offset >= 2:
        direction *= -1  # Reverse the direction

    canvas.create_image(offset, 0, anchor=tk.NW, image=image, tags="background")
    window.after(100 // update_rate, scroll_background)  # Call the function again after 50ms


# Create the main window
window = tk.Tk()
window.title("Storm cloud hills")
window.geometry("290x600")

# Load the image
image = PhotoImage(file="background2.png")  # Replace with your image file path

# Create a canvas to place the image on
canvas = tk.Canvas(window, width=image.width(), height=image.height())
canvas.pack()

# Place the initial background image
canvas.create_image(0, 0, anchor=tk.NW, image=image, tags="background")
offset = 1  # Initial offset
direction = 1  # Initial direction (1 for right, -1 for left)

# Set scroll speed and update rate (adjust as needed)
scroll_speed = 0.5  # Change this value to control the speed of scrolling
update_rate = 30  # Number of updates per second

# Add other widgets on top of the image if needed
label = tk.Label(window,
                 text="Storm cloud hills..           ",
                 font=("Sitka", 14),
                 fg="grey",
                 bg="white",
                 width=20,
                 justify='left')
label.place(x=0, y=225)


label = tk.Label(window,
                 text="v0.1",
                 font=("Sitka", 5),
                 fg="grey",
                 bg="white",
                 width=20,
                 justify='left')
label.place(x=0, y=255)

label_focused = tk.Label(window,
                 text="Focused for:                                 ",
                 font=("Sitka", 8),
                 fg="grey",
                 bg="white",
                 width=20,
                 justify='left', padx=29)
label_focused.place(x=0, y=380)

time_label = tk.Label(window, font=('Sitka',20), fg="grey", bg='White', padx=10, pady=2)
time_label.place(x=210, y=20)

# day_label = tk.Label(window, font=('Sitka',10), fg="grey")
# day_label.place(x=30, y=270)

# date_label = tk.Label(window, font=('Sitka',10), fg="grey")
# date_label.place(x=30, y=290)

ikona = PhotoImage(file='sorm cloud log 1.png')  # vložil jsem do projektu png. A tímhle ikonu převedu na Photoimage
window.iconphoto(True, ikona)  # nastavím novou ikonu okna


update()


# Start the scrolling animation
scroll_background()
app = StopwatchApp(window)
app.update_time()
# Run the Tkinter main loop
window.mainloop()
