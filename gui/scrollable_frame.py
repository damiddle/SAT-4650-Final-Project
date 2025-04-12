import tkinter as tk


class ScrollableFrame(tk.Frame):
    """Frame that implements a scrollable area using a Canvas and Scrollbar."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas)

        # Create a window in the canvas to hold the inner frame, and store the window ID
        self.window_id = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        # Update scrollregion of the canvas when the inner frame's size changes
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Update inner frame width to match canvas width when the canvas resizes
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # Bind mouse wheel scrolling events when the mouse enters the canvas
        self.canvas.bind(
            "<Enter>",
            lambda event: self.canvas.bind_all("<MouseWheel>", self.on_mousewheel),
        )
        self.canvas.bind(
            "<Leave>", lambda event: self.canvas.unbind_all("<MouseWheel>")
        )

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def on_frame_configure(self, event):
        # Adjust the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        # Update the inner frame's width to fill the canvas
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def on_mousewheel(self, event):
        # Windows systems usually have event.delta multiples of 120.
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
