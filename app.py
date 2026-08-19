import tkinter as tk
from database import BaseDatos
from gui_main import Interfaz

def main():

    BaseDatos().iniciar_db() 
    
    root = tk.Tk()

    app = Interfaz(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()
