import os
from src.gui.main_window import MainWindow

def setup_directories():
    """Create necessary directories if they don't exist"""
    directories = ['dataset', 'temp']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

if __name__ == "__main__":
    setup_directories()
    app = MainWindow()
    app.mainloop() 