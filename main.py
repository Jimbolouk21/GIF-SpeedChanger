import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageSequence

# --- Global Variables ---
thumbnails_cache = []
selected_gif_path = None
original_duration_sec = 0.0
original_size_kb = 0.0
items_count = 0

# --- Colors (Dark Theme) ---
BG_COLOR = "#121212"
CARD_BG = "#1E1E1E"
CARD_SEL_BG = "#382347"
TEXT_COLOR = "#FFFFFF"
TEXT_MUTED = "#888888"
ACCENT_COLOR = "#BB86FC"
SUCCESS_COLOR = "#03DAC6"
BTN_BG = "#2C2C2C"

def update_final_info(*args):
    if not selected_gif_path: 
        return
    try:
        speed = float(speed_var.get())
        if speed > 0:
            # Υπολογισμός τελικής διάρκειας
            new_dur = original_duration_sec / speed
            final_info_label.config(text=f"New Duration: {new_dur:.2f} s", fg=SUCCESS_COLOR)
            
            # Υπολογισμός εκτιμώμενου τελικού μεγέθους 
            # (Αν αλλάζει η ταχύτητα, αλλάζουν ανάλογα και τα καρέ που αποθηκεύονται)
            estimated_size_kb = original_size_kb / speed
            if estimated_size_kb > 1024:
                size_str = f"{estimated_size_kb/1024.0:.2f} MB"
            else:
                size_str = f"{estimated_size_kb:.1f} KB"
                
            final_size_label.config(text=f"Est. Size: {size_str}", fg=SUCCESS_COLOR)
        else:
            final_info_label.config(text="Invalid Speed", fg="#FF5252")
            final_size_label.config(text="Est. Size: -", fg=TEXT_MUTED)
    except ValueError:
        final_info_label.config(text="New Duration: -", fg=TEXT_MUTED)
        final_size_label.config(text="Est. Size: -", fg=TEXT_MUTED)

def set_speed(val):
    speed_var.set(str(val))

def on_select_card(path, filename, card_widget):
    global selected_gif_path, original_duration_sec, original_size_kb
    selected_gif_path = path
    
    for child in grid_frame.winfo_children():
        child.config(bg=CARD_BG, bd=1)
        for w in child.winfo_children():
            w.config(bg=CARD_BG)
            
    card_widget.config(bg=CARD_SEL_BG, bd=2)
    for w in card_widget.winfo_children():
        w.config(bg=CARD_SEL_BG)
        
    selected_label.config(text=f"Selected: {filename}", fg=ACCENT_COLOR)

    size_kb = os.path.getsize(path) / 1024.0
    original_size_kb = size_kb
    size_str = f"{size_kb/1024.0:.2f} MB" if size_kb > 1024 else f"{size_kb:.1f} KB"
    
    try:
        img = Image.open(path)
        durs = [max(20, f.info.get('duration', 100)) for f in ImageSequence.Iterator(img)]
        original_duration_sec = sum(durs) / 1000.0
    except Exception:
        original_duration_sec = 0.0

    initial_info_label.config(text=f"Original: {original_duration_sec:.2f} s | Size: {size_str}")
    update_final_info()

def add_gif_to_grid(full_path, file, folder_name):
    global items_count
    try:
        img = Image.open(full_path)
        img.seek(0)
        img.thumbnail((250, 250))
        photo = ImageTk.PhotoImage(img)
        thumbnails_cache.append(photo)
        
        card = tk.Frame(grid_frame, bg=CARD_BG, bd=1, relief="solid")
        
        row = items_count // 2
        col = items_count % 2
        card.grid(row=row, column=col, padx=4, pady=6, sticky="nsew")
        
        img_lbl = tk.Label(card, image=photo, bg=CARD_BG)
        img_lbl.pack(pady=4)
        
        display_name = file if len(file) <= 16 else file[:13] + "..."
        txt_lbl = tk.Label(card, text=f"{display_name}\n({folder_name})", font=("Arial", 8, "bold"), bg=CARD_BG, fg=TEXT_COLOR)
        txt_lbl.pack(pady=(0, 4))
        
        for w in (card, img_lbl, txt_lbl):
            w.bind("<Button-1>", lambda e, p=full_path, f=file, c=card: on_select_card(p, f, c))
            
        items_count += 1
        return True
    except Exception:
        return False

def scan_gifs():
    global thumbnails_cache, selected_gif_path, items_count
    thumbnails_cache.clear()
    selected_gif_path = None
    items_count = 0
    selected_label.config(text="Selected: None", fg=TEXT_MUTED)
    initial_info_label.config(text="Original: - | Size: -")
    final_info_label.config(text="New Duration: -", fg=TEXT_MUTED)
    final_size_label.config(text="Est. Size: -", fg=TEXT_MUTED)
    
    for widget in grid_frame.winfo_children():
        widget.destroy()
        
    status_label.config(text="Scanning device folders...")
    root.update()
    
    search_dirs = [
        "/storage/emulated/0/Download",
        "/storage/emulated/0/Pictures",
        "/storage/emulated/0/DCIM",
        "/storage/emulated/0/Movies",
        "/storage/emulated/0/Documents",
        "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Animated Gifs",
        "/storage/emulated/0/Android/media/org.telegram.messenger/Telegram/Telegram Documents",
        "/storage/emulated/0/viber/media/Viber Animated Gifs"
    ]
    
    found_count = 0
    for b_dir in search_dirs:
        if os.path.exists(b_dir):
            try:
                for current_root, dirs, files in os.walk(b_dir):
                    for file in files:
                        if file.lower().endswith(".gif"):
                            full_path = os.path.join(current_root, file)
                            folder_name = os.path.basename(current_root)
                            if add_gif_to_grid(full_path, file, folder_name):
                                found_count += 1
            except Exception:
                continue
                
    if found_count == 0:
        status_label.config(text="No GIFs found automatically.")
    else:
        status_label.config(text=f"Found {found_count} GIF(s)!")

def browse_manual():
    filepath = filedialog.askopenfilename(title="Select GIF", filetypes=[("GIF Files", "*.gif")])
    if filepath:
        filename = os.path.basename(filepath)
        folder = os.path.basename(os.path.dirname(filepath))
        if add_gif_to_grid(filepath, filename, folder):
            cards = grid_frame.winfo_children()
            if cards:
                on_select_card(filepath, filename, cards[-1])

def process_gif():
    if not selected_gif_path:
        messagebox.showerror("Error", "Please select a GIF first!")
        return
        
    try:
        speed = float(speed_var.get())
        if speed <= 0: raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Enter a valid speed number (e.g. 2.0)")
        return
        
    dir_name = os.path.dirname(selected_gif_path)
    base_name = os.path.splitext(os.path.basename(selected_gif_path))[0]
    
    suffix = "fast" if speed > 1.0 else ("slow" if speed < 1.0 else "mod")
    out_name = f"{base_name}_{suffix}_{speed}x.gif"
    output_path = os.path.join(dir_name, out_name)
    
    try:
        img = Image.open(selected_gif_path)
        frames = []
        durations = []
        
        for frame in ImageSequence.Iterator(img):
            frames.append(frame.copy())
            d = frame.info.get('duration', 100)
            durations.append(d if d > 0 else 100)

        new_durations = [max(20, int(d / speed)) for d in durations]

        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=new_durations,
            loop=img.info.get('loop', 0),
            disposal=img.info.get('disposal', 2)
        )
        messagebox.showinfo("Success!", f"Saved next to original:\n\n{out_name}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed:\n{str(e)}")


# --- UI Setup ---
root = tk.Tk()
root.title("GIF Speed Changer Pro")
root.geometry("520x800")
root.configure(bg=BG_COLOR)

top_frame = tk.Frame(root, bg=BG_COLOR, padx=10, pady=5)
top_frame.pack(fill="x")

tk.Button(top_frame, text="🔍 SCAN DEVICE FOR GIFs", font=("Arial", 10, "bold"), bg=ACCENT_COLOR, fg="#000", relief="flat", pady=8, command=scan_gifs).pack(fill="x", pady=2)
tk.Button(top_frame, text="📂 BROWSE FILE MANUALLY", font=("Arial", 9, "bold"), bg=BTN_BG, fg=TEXT_COLOR, relief="flat", pady=5, command=browse_manual).pack(fill="x", pady=2)

status_label = tk.Label(top_frame, text="Tap Scan or Browse to load GIFs", font=("Arial", 8), bg=BG_COLOR, fg=TEXT_MUTED)
status_label.pack(pady=2)

frame_container = tk.Frame(root, bg=BG_COLOR)
frame_container.pack(fill="both", expand=True, padx=5, pady=5)

canvas = tk.Canvas(frame_container, bg=BG_COLOR, highlightthickness=0)
scrollbar = tk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
grid_frame = tk.Frame(canvas, bg=BG_COLOR)

grid_frame.columnconfigure(0, weight=1)
grid_frame.columnconfigure(1, weight=1)

grid_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=grid_frame, anchor="nw", width=480)
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Κάτω Πάνελ
bottom_frame = tk.Frame(root, bg=CARD_BG, padx=10, pady=8)
bottom_frame.pack(fill="x", side="bottom")

selected_label = tk.Label(bottom_frame, text="Selected: None", font=("Arial", 10, "bold"), bg=CARD_BG, fg=TEXT_MUTED)
selected_label.pack()

initial_info_label = tk.Label(bottom_frame, text="Original: - | Size: -", font=("Arial", 8), bg=CARD_BG, fg=TEXT_COLOR)
initial_info_label.pack()

# Προσθήκη ετικέτας τελικού μεγέθους
info_dur_size = tk.Frame(bottom_frame, bg=CARD_BG)
info_dur_size.pack(pady=2)

final_info_label = tk.Label(info_dur_size, text="New Duration: -", font=("Arial", 9, "bold"), bg=CARD_BG, fg=TEXT_COLOR)
final_info_label.pack(side="left", padx=5)

final_size_label = tk.Label(info_dur_size, text="Est. Size: -", font=("Arial", 9, "bold"), bg=CARD_BG, fg=TEXT_COLOR)
final_size_label.pack(side="left", padx=5)

speed_var = tk.StringVar(value="2.0")
speed_var.trace_add("write", update_final_info)

speed_ctrl = tk.Frame(bottom_frame, bg=CARD_BG)
speed_ctrl.pack(pady=4)

tk.Label(speed_ctrl, text="Speed:", font=("Arial", 9, "bold"), bg=CARD_BG, fg=TEXT_COLOR).pack(side="left")
tk.Entry(speed_ctrl, textvariable=speed_var, width=5, font=("Arial", 11, "bold"), justify="center", bg=BG_COLOR, fg=ACCENT_COLOR, insertbackground=TEXT_COLOR).pack(side="left", padx=5)

preset_frame = tk.Frame(bottom_frame, bg=CARD_BG)
preset_frame.pack(fill="x", pady=2)
speeds = [("0.5x", 0.5), ("1.0x", 1.0), ("1.5x", 1.5), ("2.0x", 2.0), ("3.0x", 3.0), ("4.0x", 4.0), ("5.0x", 5.0)]
for txt, val in speeds:
    tk.Button(preset_frame, text=txt, font=("Arial", 8, "bold"), bg=BTN_BG, fg=TEXT_COLOR, relief="flat", command=lambda v=val: set_speed(v)).pack(side="left", expand=True, fill="x", padx=1)

tk.Button(bottom_frame, text="⚡ PROCESS & SAVE GIF", font=("Arial", 10, "bold"), bg=SUCCESS_COLOR, fg="#000", relief="flat", pady=8, command=process_gif).pack(fill="x", pady=(6, 0))

root.mainloop()
