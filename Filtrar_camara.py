import tkinter as tk
from modulos import VideoFilter
from modulos_ui import FilterUI

def main():
    video_source = ""
    video_filter = VideoFilter(video_source)

    root = tk.Tk()
    app = FilterUI(root, video_filter)
    root.protocol("WM_DELETE_WINDOW", lambda: (video_filter.release(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    main()