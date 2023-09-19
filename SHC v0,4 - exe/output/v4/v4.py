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
                                            font=("Sitka", 8),
                                            bg="white",
                                            fg="grey",
                                            width=22,
                                            command=self.start_pause_stopwatch)
        self.start_pause_button.place(x=41, y=440)

        self.reset_button = tk.Button(root,
                                      text="Reset",
                                      font=("Sitka", 8),
                                      fg="grey",
                                      bg="white",
                                      command=self.reset_stopwatch)
        self.reset_button.place(x=2, y=440)

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

def update_time_label():
    time_string = time.strftime("%H:%M:%S")
    time_label.config(text=time_string)
    window.after(1000, update_time_label)

def scroll_background():
    global offset, direction
    canvas.delete("background")
    offset += direction * scroll_speed
    if offset <= -image.width() + canvas.winfo_width() or offset >= 2:
        direction *= -1
    canvas.create_image(offset, 0, anchor=tk.NW, image=image, tags="background")
    window.after(1000 // update_rate, scroll_background)

window = tk.Tk()
window.title("Storm Cloud Hills")
window.geometry("290x600")

image = PhotoImage(file="background2.png")
canvas = tk.Canvas(window, width=image.width(), height=image.height())
canvas.pack()

canvas.create_image(0, 0, anchor=tk.NW, image=image, tags="background")
offset = 1
direction = 1

scroll_speed = 0.5
update_rate = 60

label_text = [
    ("Storm cloud hills..         ", 14),
    ("v0.1                      ", 8),
]
labels = []

for i, (text, font_size) in enumerate(label_text):
    label = tk.Label(window, text=text, font=("Sitka", font_size), fg="grey", bg="white", width=20, justify='left')
    label.place(x=0, y=255 + i * 30)
    labels.append(label)

time_label = tk.Label(window, font=('Sitka', 10), fg="grey", bg='white', padx=10, pady=2)
time_label.place(x=205, y=20)

focused_label = tk.Label(window, font=('Sitka', 7), text="Focused for:", fg="grey", bg='white', padx=10, pady=2)
focused_label.place(x=0, y=378)

ikona = PhotoImage(file='storm cloud log 1.png')
window.iconphoto(True, ikona)

update_time_label()
scroll_background()
app = StopwatchApp(window)
app.update_time()

window.mainloop()
