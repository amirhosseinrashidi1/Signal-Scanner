# Signal Scanner

A Python-based signal scanning application with a graphical user interface (GUI) using `tkinter`. The app supports scanning various types of signals, including Audio, RF, WiFi, Bluetooth, and Electrical signals. It features real-time visualization of signal data with the option to apply filters such as Low-pass and High-pass.

## Features
- **Signal Types**: Audio, RF, WiFi, Bluetooth, Electrical
- **Real-time FFT**: Visualize frequency spectrum for audio and RF signals
- **Signal Filtering**: Apply Low-pass and High-pass filters
- **Bluetooth Device Detection**: Show detected Bluetooth devices
- **WiFi Signal Strength**: Monitor WiFi signal strength
- **Electrical Signal Visualization**: Plot electrical signal data from a serial connection
- **Multi-threading**: Scan multiple signal types in parallel without blocking the UI

## Requirements
- Python 3.x
- `tkinter`
- `numpy`
- `pyaudio`
- `matplotlib`
- `rtlsdr`
- `scapy`
- `serial`
- `bluetooth`
