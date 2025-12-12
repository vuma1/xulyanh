"""
PhotoLab - Professional Photo Editor
main.py - Entry point của ứng dụng
"""
import tkinter as tk
from ui import PhotoLabApp


def main():
    """Khởi chạy ứng dụng PhotoLab"""
    root = tk.Tk()
    app = PhotoLabApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
