import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import csv
import os
import psutil

MAX_ENTRIES = 18000  # 5 saatlik veri
LOG_FILE = "sistem_log.csv"

cpu_history = deque(maxlen=300)
ram_history = deque(maxlen=300)
disk_history = deque(maxlen=300)
net_sent_history = deque(maxlen=300)
net_recv_history = deque(maxlen=300)

prev_net = psutil.net_io_counters()

# Log dosyasını kontrol et
def trim_log_file():
    if not os.path.exists(LOG_FILE):
        return
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
    if len(lines) > MAX_ENTRIES:
        with open(LOG_FILE, "w") as f:
            f.writelines(lines[-MAX_ENTRIES:])

# Log verisi yaz
def log_data(cpu, ram, disk, net_sent, net_recv):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([now, cpu, ram, disk, net_sent, net_recv])
    trim_log_file()

# Uyarı göster

def check_thresholds(cpu, ram, disk):
    alerts = []
    if cpu > 90:
        alerts.append("CPU kullanımı %90'ın üzerinde!")
    if ram > 90:
        alerts.append("RAM kullanımı %90'ın üzerinde!")
    if disk > 90:
        alerts.append("Disk kullanımı %90'ın üzerinde!")
    if alerts:
        messagebox.showwarning("Uyarı", "\n".join(alerts))

# Grafik güncelle
def update_plot(frame):
    global prev_net

    result = subprocess.run(["./monitor"], stdout=subprocess.PIPE, text=True)
    try:
        cpu_str, ram_str = result.stdout.strip().split()
        cpu = float(cpu_str)
        ram = float(ram_str)
    except ValueError:
        cpu, ram = 0, 0

    disk = psutil.disk_usage('/').percent
    current_net = psutil.net_io_counters()
    net_sent = (current_net.bytes_sent - prev_net.bytes_sent) / 1024
    net_recv = (current_net.bytes_recv - prev_net.bytes_recv) / 1024
    prev_net = current_net

    cpu_history.append(cpu)
    ram_history.append(ram)
    disk_history.append(disk)
    net_sent_history.append(net_sent)
    net_recv_history.append(net_recv)

    log_data(cpu, ram, disk, net_sent, net_recv)
    check_thresholds(cpu, ram, disk)

    for ax in axs:
        ax.clear()
        ax.set_facecolor("#1e1e1e")
        ax.tick_params(colors="white")

    axs[0].plot(cpu_history, label="CPU %", color="skyblue", linewidth=1.5)
    axs[0].set_title("CPU Kullanımı", color="white")
    axs[0].set_ylim(0, 100)
    axs[0].legend()

    axs[1].plot(ram_history, label="RAM %", color="lime", linewidth=1.5)
    axs[1].set_title("RAM Kullanımı", color="white")
    axs[1].set_ylim(0, 100)
    axs[1].legend()

    axs[2].plot(disk_history, label="Disk %", color="orange", linewidth=1.5)
    axs[2].set_title("Disk Kullanımı", color="white")
    axs[2].set_ylim(0, 100)
    axs[2].legend()

    axs[3].plot(net_sent_history, label="Net Gönderilen (KB/s)", color="red", linewidth=1.2)
    axs[3].plot(net_recv_history, label="Net Alınan (KB/s)", color="yellow", linewidth=1.2)
    axs[3].set_title("Ağ Kullanımı", color="white")
    axs[3].legend()

# Log dosyasını aç
def open_log():
    if not os.path.exists(LOG_FILE):
        messagebox.showinfo("Log Bilgisi", "Henüz log oluşturulmadı.")
        return
    os.system(f"xdg-open {LOG_FILE}")  # Linux için. Windows: os.startfile(LOG_FILE)

# Log temizle
def clear_log():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        messagebox.showinfo("Başarılı", "Log dosyası silindi.")

# Tkinter GUI
root = tk.Tk()
root.title("Sistem İzleme Aracı - Gelişmiş")
root.geometry("1000x800")
root.configure(bg="#2e2e2e")

# Butonlar
frame_top = ttk.Frame(root)
frame_top.pack(pady=10)

style = ttk.Style()
style.theme_use('clam')
style.configure("TButton", foreground="white", background="#444")

btn_open = ttk.Button(frame_top, text="Log'u Aç", command=open_log)
btn_clear = ttk.Button(frame_top, text="Log'u Temizle", command=clear_log)
btn_open.pack(side="left", padx=10)
btn_clear.pack(side="left", padx=10)

# Grafik alanı
fig, axs = plt.subplots(4, 1, figsize=(10, 8))
fig.patch.set_facecolor('#2e2e2e')
fig.tight_layout(pad=3.5)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

ani = animation.FuncAnimation(fig, update_plot, interval=1000)
root.mainloop()

