

import tkinter as tk
from gui_app import ReliableStarGUI
from messenger import ReliableMessenger

def main():
    messenger = ReliableMessenger()  # create the logic instance
    root = tk.Tk()
    app = ReliableStarGUI(root, messenger)  # pass messenger to GUI
    root.mainloop()

if __name__ == "__main__":
    main() 
    
