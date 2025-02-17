import tkinter as tk
from tkinter import ttk
import numpy as np
import pyaudio
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.signal import butter, lfilter
import rtlsdr
import scapy.all as scapy
import serial
import time
import bluetooth
import os
import threading
import csv

def is_root():
    return os.geteuid() == 0

class SignalScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Signal Scanner")
        
        self.label = tk.Label(root, text="Select Signal Type:")
        self.label.pack()
        
        self.signal_type = tk.StringVar()
        self.signal_dropdown = ttk.Combobox(root, textvariable=self.signal_type)
        self.signal_dropdown['values'] = ("Audio", "RF", "WiFi", "Bluetooth", "Electrical")
        self.signal_dropdown.pack()
        
        self.start_button = tk.Button(root, text="Start Scan", command=self.start_scan)
        self.start_button.pack()
        
        self.stop_button = tk.Button(root, text="Stop Scan", command=self.stop_scan, state=tk.DISABLED)
        self.stop_button.pack()
        
        self.filter_label = tk.Label(root, text="Select Filter:")
        self.filter_label.pack()
        
        self.filter_type = tk.StringVar()
        self.filter_dropdown = ttk.Combobox(root, textvariable=self.filter_type)
        self.filter_dropdown['values'] = ("None", "Low-pass", "High-pass")
        self.filter_dropdown.pack()
        
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack()
        
        self.scanning = False  # کنترل فرآیند اسکن
    
    def start_scan(self):
        if self.scanning:
            return
        self.scanning = True
        self.stop_button.config(state=tk.NORMAL)
        signal = self.signal_type.get()
        scan_methods = {
            "Audio": self.scan_audio,
            "RF": self.scan_rf,
            "WiFi": self.scan_wifi,
            "Bluetooth": self.scan_bluetooth,
            "Electrical": self.scan_electrical
        }
        if signal in scan_methods:
            threading.Thread(target=scan_methods[signal]).start()
        else:
            self.display_message("Invalid Selection")
    
    def stop_scan(self):
        self.scanning = False
        self.stop_button.config(state=tk.DISABLED)
    
    def display_message(self, message):
        self.ax.clear()
        self.ax.set_title(message)
        self.canvas.draw()
    
    def butter_filter(self, data, cutoff, fs, btype):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(5, normal_cutoff, btype=btype, analog=False)
        return lfilter(b, a, data)
    
    def compute_fft(self, data, rate):
        n = len(data)
        freq = np.fft.fftfreq(n, d=1/rate)
        fft_values = np.abs(np.fft.fft(data))
        return freq[:n//2], fft_values[:n//2]
    
    def scan_audio(self):
        try:
            CHUNK, RATE, FORMAT, CHANNELS = 1024, 44100, pyaudio.paInt16, 1
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            while self.scanning:
                data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
                filter_type = self.filter_type.get()
                if filter_type == "Low-pass":
                    data = self.butter_filter(data, 1000, RATE, 'low')
                elif filter_type == "High-pass":
                    data = self.butter_filter(data, 1000, RATE, 'high')
                freq, fft_values = self.compute_fft(data, RATE)
                self.ax.clear()
                self.ax.plot(freq, fft_values)
                self.ax.set_title("Audio Signal - Frequency Spectrum (FFT)")
                self.canvas.draw()
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            self.display_message(f"Audio Scan Error: {e}")
    
    def scan_rf(self):
        try:
            sdr = rtlsdr.RtlSdr()
            sdr.sample_rate, sdr.center_freq, sdr.gain = 2.048e6, 100e6, 4
            while self.scanning:
                samples = np.abs(sdr.read_samples(1024))
                freq, fft_values = self.compute_fft(samples, sdr.sample_rate)
                self.ax.clear()
                self.ax.plot(freq, fft_values)
                self.ax.set_title("RF Signal - Frequency Spectrum (FFT)")
                self.canvas.draw()
            sdr.close()
        except Exception as e:
            self.display_message(f"RF Scan Error: {e}")
    
    def scan_wifi(self):
        if not is_root():
            self.display_message("WiFi Scan requires root privileges!")
            return
        try:
            while self.scanning:
                packets = scapy.sniff(count=100)
                signal_strength = [len(p) for p in packets]
                self.ax.clear()
                self.ax.plot(signal_strength)
                self.ax.set_title("WiFi Signal Strength")
                self.canvas.draw()
        except Exception as e:
            self.display_message(f"WiFi Scan Error: {e}")
    
    def scan_bluetooth(self):
        try:
            while self.scanning:
                nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True)
                self.ax.clear()
                self.ax.bar(range(len(nearby_devices)), [1] * len(nearby_devices))
                self.ax.set_title("Bluetooth Devices Detected")
                self.ax.set_xticks(range(len(nearby_devices)))
                self.ax.set_xticklabels([name for _, name in nearby_devices], rotation=45, ha="right")
                self.canvas.draw()
        except Exception as e:
            self.display_message(f"Bluetooth Scan Error: {e}")
    
    def scan_electrical(self):
        try:
            ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
            while self.scanning:
                data = [int(ser.readline().strip()) for _ in range(100) if ser.readline().strip()]
                self.ax.clear()
                self.ax.plot(data)
                self.ax.set_title("Electrical Signal")
                self.canvas.draw()
            ser.close()
        except Exception as e:
            self.display_message(f"Electrical Scan Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SignalScannerApp(root)
    root.mainloop()
