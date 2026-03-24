import customtkinter as ctk
import math
import random

COLORS = {
    "bg_dark":       "#0a0a12",
    "bg_card":       "#1a1830",
    "accent_cyan":   "#00d4ff",
    "accent_green":  "#39ff14",
    "accent_purple": "#bd00ff",
    "accent_yellow": "#fcee09",
    "text_primary":  "#e0f7fa",
    "text_muted":    "#3d4a6b",
    "border":        "#2a1f4e",
}

LOADING_MESSAGES = [
    "INITIALIZING NEURAL INTERFACE",
    "CONNECTING TO NIGHT CITY GRID",
    "LOADING DELIVERY PROTOCOLS",
    "SYNCING COURIER DATABASE",
    "CALIBRATING ROUTE ENGINE",
    "ESTABLISHING SECURE LINK",
    "BOOTING NETLOGO SUBSYSTEM",
]


class LoadingScreen(ctk.CTkToplevel):

    def __init__(self, parent=None, text="LOADING SIMULATION ENGINE..."):
        super().__init__(parent)

        self._alive = True
        self.angle = 0
        self.dot_count = 0
        self._msg_index = 0
        self._scanline_offset = 0
        self._glitch_counter = 0

        self.title("")
        self.geometry("440x320")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])
        self.overrideredirect(True)

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 440) // 2
        y = (self.winfo_screenheight() - 320) // 2
        self.geometry(f"+{x}+{y}")

        border = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"],
                               corner_radius=0,
                               border_width=1,
                               border_color=COLORS["accent_cyan"])
        border.pack(fill="both", expand=True, padx=1, pady=1)

        ctk.CTkFrame(border, fg_color=COLORS["accent_cyan"], height=2,
                      corner_radius=0).pack(fill="x")

        header = ctk.CTkFrame(border, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(10, 0))
        ctk.CTkLabel(header, text="// SYSTEM BOOT",
                     font=("Consolas", 10, "bold"),
                     text_color=COLORS["accent_cyan"]).pack(side="left")
        self._time_label = ctk.CTkLabel(header, text="00:00",
                                         font=("Consolas", 9),
                                         text_color=COLORS["text_muted"])
        self._time_label.pack(side="right")

        self.spinner_canvas = ctk.CTkCanvas(
            border, bg=COLORS["bg_dark"],
            highlightthickness=0,
            width=100, height=100
        )
        self.spinner_canvas.pack(pady=(12, 10))

        self.label = ctk.CTkLabel(
            border, text=text,
            font=("Consolas", 12, "bold"),
            text_color=COLORS["text_primary"]
        )
        self.label.pack()

        self.sublabel = ctk.CTkLabel(
            border, text="// STANDBY",
            font=("Consolas", 9),
            text_color=COLORS["text_muted"]
        )
        self.sublabel.pack(pady=(4, 0))

        progress_frame = ctk.CTkFrame(border, fg_color="transparent")
        progress_frame.pack(fill="x", padx=30, pady=(14, 0))

        self.progress = ctk.CTkProgressBar(
            progress_frame, width=250, height=3,
            corner_radius=0,
            fg_color=COLORS["bg_card"],
            progress_color=COLORS["accent_cyan"],
            mode="indeterminate"
        )
        self.progress.pack(fill="x")
        self.progress.start()

        bottom = ctk.CTkFrame(border, fg_color="transparent")
        bottom.pack(fill="x", padx=16, pady=(8, 10))
        self._status_dots = ctk.CTkLabel(bottom, text="● ● ●",
                                          font=("Consolas", 8),
                                          text_color=COLORS["accent_cyan"])
        self._status_dots.pack(side="left")
        ctk.CTkLabel(bottom, text="NCDS v2.077",
                     font=("Consolas", 8),
                     text_color=COLORS["text_muted"]).pack(side="right")

        ctk.CTkFrame(border, fg_color=COLORS["accent_purple"], height=1,
                      corner_radius=0).pack(fill="x", side="bottom")

        self._start_time = self.after(0, lambda: None)
        self._elapsed = 0

        self._animate_spinner()
        self._animate_dots()
        self._animate_messages()
        self._animate_timer()

        self.lift()
        self.grab_set()

    def _animate_spinner(self):
        if not self._alive:
            return

        self.spinner_canvas.delete("all")

        cx, cy = 50, 50
        r = 30
        num_segments = 16
        t = self.angle * 0.05

        for i in range(num_segments):
            angle = math.radians(self.angle + i * (360 / num_segments))
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)

            alpha = (i + 1) / num_segments
            size = 1.5 + 3 * alpha

            r_c = int(0 + (189 - 0) * (1 - alpha))
            g_c = int(212 + (0 - 212) * (1 - alpha))
            b_c = 255
            color = f"#{max(0,min(255,r_c)):02x}{max(0,min(255,g_c)):02x}{max(0,min(255,b_c)):02x}"

            self.spinner_canvas.create_oval(
                x - size * 1.8, y - size * 1.8,
                x + size * 1.8, y + size * 1.8,
                fill="", outline=color, width=1
            )
            self.spinner_canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill=color, outline=""
            )

        inner_r = 12
        hex_angle = self.angle * 0.7
        hex_points = []
        for i in range(6):
            a = math.radians(hex_angle + i * 60)
            hx = cx + inner_r * math.cos(a)
            hy = cy + inner_r * math.sin(a)
            hex_points.extend([hx, hy])
        self.spinner_canvas.create_polygon(
            hex_points, fill="", outline=COLORS["accent_cyan"], width=1
        )

        pulse = math.sin(t * 3) * 2 + 4
        self.spinner_canvas.create_oval(
            cx - pulse, cy - pulse, cx + pulse, cy + pulse,
            fill=COLORS["accent_cyan"], outline=""
        )

        self.angle = (self.angle + 6) % 360
        self.after(35, self._animate_spinner)

    def _animate_dots(self):
        if not self._alive:
            return
        self.dot_count = (self.dot_count + 1) % 4

        dots_display = ""
        for i in range(3):
            if i < self.dot_count:
                dots_display += "● "
            else:
                dots_display += "○ "

        self._status_dots.configure(text=dots_display.strip())

        cursor = "█" if self.dot_count % 2 == 0 else " "
        current = LOADING_MESSAGES[self._msg_index % len(LOADING_MESSAGES)]
        self.sublabel.configure(text=f"// {current}{cursor}")

        self.after(400, self._animate_dots)

    def _animate_messages(self):
        if not self._alive:
            return
        self._msg_index += 1
        self.after(2000, self._animate_messages)

    def _animate_timer(self):
        if not self._alive:
            return
        self._elapsed += 1
        secs = self._elapsed // 2
        mins = secs // 60
        secs = secs % 60
        self._time_label.configure(text=f"{mins:02d}:{secs:02d}")
        self.after(500, self._animate_timer)

    def finish(self):
        self._alive = False
        try:
            self.progress.stop()
            self.grab_release()
            self.destroy()
        except Exception:
            pass