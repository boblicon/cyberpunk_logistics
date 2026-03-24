import customtkinter as ctk
import math
import random
import auth

COLORS = {
    "bg_dark":       "#0a0a12",
    "bg_panel":      "#12111f",
    "bg_card":       "#1a1830",
    "accent_cyan":   "#00d4ff",
    "accent_green":  "#39ff14",
    "accent_red":    "#ff003c",
    "accent_yellow": "#fcee09",
    "accent_purple": "#bd00ff",
    "accent_pink":   "#ff2a6d",
    "text_primary":  "#e0f7fa",
    "text_secondary":"#7b8cad",
    "text_muted":    "#3d4a6b",
    "border":        "#2a1f4e",
    "input_bg":      "#0f0e1a",
}


class AuthWindow(ctk.CTk):

    def __init__(self, on_success_callback):
        super().__init__()

        self.on_success = on_success_callback
        self._glitch_active = False
        self._anim_phase = 0.0

        self._blobs = []
        for _ in range(5):
            self._blobs.append({
                "x": random.uniform(50, 450),
                "y": random.uniform(50, 610),
                "r": random.uniform(60, 120),
                "dx": random.uniform(-0.15, 0.15),
                "dy": random.uniform(-0.1, 0.1),
                "color": random.choice(["#00d4ff", "#bd00ff", "#39ff14"]),
                "alpha": random.uniform(0.02, 0.04),
            })

        self.title("NCDS // AUTHENTICATION TERMINAL")
        self.geometry("500x660")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])

        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - 500) // 2
        y = (screen_h - 660) // 2
        self.geometry(f"500x660+{x}+{y}")

        self.bg_canvas = ctk.CTkCanvas(self, bg=COLORS["bg_dark"], highlightthickness=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._draw_static_bg()
        self._animate_blobs()

        card = ctk.CTkFrame(self, corner_radius=4, fg_color=COLORS["bg_panel"],
                            border_width=1, border_color=COLORS["border"])
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.84)

        ctk.CTkFrame(card, fg_color=COLORS["accent_cyan"], height=2,
                      corner_radius=0).pack(fill="x")

        icon_frame = ctk.CTkFrame(card, fg_color=COLORS["bg_card"],
                                  corner_radius=4, width=70, height=70,
                                  border_width=1, border_color=COLORS["accent_cyan"])
        icon_frame.pack(pady=(24, 0))
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(icon_frame, text="⬡", font=("Consolas", 36),
                     text_color=COLORS["accent_cyan"]).place(
            relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text="// AUTHENTICATE",
                     font=("Consolas", 20, "bold"),
                     text_color=COLORS["accent_cyan"]).pack(pady=(14, 0))

        ctk.CTkLabel(card, text="NIGHT CITY DELIVERY SYSTEMS",
                     font=("Consolas", 10),
                     text_color=COLORS["text_muted"]).pack(pady=(2, 18))

        inputs_frame = ctk.CTkFrame(card, fg_color="transparent")
        inputs_frame.pack(fill="x", padx=28)

        ctk.CTkLabel(inputs_frame, text="► USER_ID", font=("Consolas", 10, "bold"),
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 4))

        self.login_entry = ctk.CTkEntry(
            inputs_frame,
            placeholder_text="enter_username",
            height=40, corner_radius=2,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["accent_cyan"],
            placeholder_text_color=COLORS["text_muted"],
            font=("Consolas", 12)
        )
        self.login_entry.pack(fill="x", pady=(0, 10))
        self.login_entry.bind("<FocusIn>",
            lambda e: self.login_entry.configure(border_color=COLORS["accent_cyan"]))
        self.login_entry.bind("<FocusOut>",
            lambda e: self.login_entry.configure(border_color=COLORS["border"]))

        ctk.CTkLabel(inputs_frame, text="► PASS_KEY", font=("Consolas", 10, "bold"),
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 4))

        self.password_entry = ctk.CTkEntry(
            inputs_frame,
            placeholder_text="enter_password",
            show="●", height=40, corner_radius=2,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["accent_cyan"],
            placeholder_text_color=COLORS["text_muted"],
            font=("Consolas", 12)
        )
        self.password_entry.pack(fill="x")
        self.password_entry.bind("<FocusIn>",
            lambda e: self.password_entry.configure(border_color=COLORS["accent_cyan"]))
        self.password_entry.bind("<FocusOut>",
            lambda e: self.password_entry.configure(border_color=COLORS["border"]))

        self.password_entry.bind("<Return>", lambda e: self.login())
        self.login_entry.bind("<Return>", lambda e: self.password_entry.focus())

        self.status_frame = ctk.CTkFrame(card, fg_color="transparent", height=28)
        self.status_frame.pack(fill="x", padx=28, pady=(10, 0))
        self.status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(self.status_frame, text="",
                                         font=("Consolas", 10, "bold"))
        self.status_label.pack()

        buttons_frame = ctk.CTkFrame(card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=28, pady=(12, 6))

        self.login_btn = ctk.CTkButton(
            buttons_frame, text="▶ CONNECT", height=40,
            corner_radius=2, fg_color=COLORS["bg_card"],
            hover_color=COLORS["accent_cyan"],
            border_width=1, border_color=COLORS["accent_cyan"],
            text_color=COLORS["accent_cyan"],
            font=("Consolas", 13, "bold"),
            command=self.login
        )
        self.login_btn.pack(fill="x", pady=(0, 8))

        sep_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent", height=20)
        sep_frame.pack(fill="x", pady=2)
        ctk.CTkFrame(sep_frame, fg_color=COLORS["border"], height=1).place(
            relx=0, rely=0.5, relwidth=0.38)
        ctk.CTkLabel(sep_frame, text="OR", font=("Consolas", 9, "bold"),
                     text_color=COLORS["text_muted"]).pack()
        ctk.CTkFrame(sep_frame, fg_color=COLORS["border"], height=1).place(
            relx=0.62, rely=0.5, relwidth=0.38)

        self.register_btn = ctk.CTkButton(
            buttons_frame, text="■ NEW ACCOUNT", height=40,
            corner_radius=2,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["accent_purple"],
            hover_color=COLORS["accent_purple"],
            text_color=COLORS["accent_purple"],
            font=("Consolas", 12, "bold"),
            command=self.register
        )
        self.register_btn.pack(fill="x")

        ctk.CTkLabel(card, text="NCDS v2.077 // SECURE TERMINAL",
                     font=("Consolas", 8),
                     text_color=COLORS["text_muted"]).pack(pady=(12, 16))

    def _draw_static_bg(self):
        grid_color = "#0e0d1a"
        for gx in range(0, 500, 40):
            self.bg_canvas.create_line(gx, 0, gx, 660, fill=grid_color, width=1, tags="static")
        for gy in range(0, 660, 40):
            self.bg_canvas.create_line(0, gy, 500, gy, fill=grid_color, width=1, tags="static")

    def _animate_blobs(self):
        self.bg_canvas.delete("blob")

        for b in self._blobs:
            b["x"] += b["dx"]
            b["y"] += b["dy"]

            if b["x"] < -30 or b["x"] > 530:
                b["dx"] *= -1
            if b["y"] < -30 or b["y"] > 690:
                b["dy"] *= -1

            r_c = int(b["color"][1:3], 16)
            g_c = int(b["color"][3:5], 16)
            b_c = int(b["color"][5:7], 16)
            a = b["alpha"]

            bg_r, bg_g, bg_b = 10, 10, 18
            r = int(bg_r + (r_c - bg_r) * a)
            g = int(bg_g + (g_c - bg_g) * a)
            bl = int(bg_b + (b_c - bg_b) * a)
            color = f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,bl)):02x}"

            rad = b["r"]
            self.bg_canvas.create_oval(
                b["x"] - rad, b["y"] - rad,
                b["x"] + rad, b["y"] + rad,
                fill=color, outline="", tags="blob"
            )

        self.after(80, self._animate_blobs)

    def _show_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)
        self.after(4000, lambda: self.status_label.configure(text=""))

    def login(self):
        username = self.login_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self._show_status("▲ FILL ALL FIELDS", COLORS["accent_red"])
            self._glitch_effect()
            return

        self.login_btn.configure(text="◆ CONNECTING...", state="disabled")
        self.update()

        success, message = auth.login(username, password)

        if success:
            self._show_status("● ACCESS GRANTED", COLORS["accent_green"])
            self.update()
            self.after(600, lambda: (self.destroy(), self.on_success()))
        else:
            self.login_btn.configure(text="▶ CONNECT", state="normal")
            self._show_status(f"✕ {message.upper()}", COLORS["accent_red"])
            self._glitch_effect()
            self._shake_window()

    def register(self):
        username = self.login_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self._show_status("▲ FILL ALL FIELDS", COLORS["accent_red"])
            self._glitch_effect()
            return

        self.register_btn.configure(text="◆ CREATING...", state="disabled")
        self.update()

        success, message = auth.register(username, password)

        self.register_btn.configure(text="■ NEW ACCOUNT", state="normal")

        if success:
            self._show_status(f"● {message.upper()}", COLORS["accent_green"])
        else:
            self._show_status(f"✕ {message.upper()}", COLORS["accent_red"])
            self._glitch_effect()

    def _shake_window(self):
        x = self.winfo_x()
        y = self.winfo_y()
        offsets = [12, -12, 10, -10, 6, -6, 3, -3, 0]

        def shake(i=0):
            if i < len(offsets):
                self.geometry(f"+{x + offsets[i]}+{y}")
                self.after(35, lambda: shake(i + 1))
        shake()

    def _glitch_effect(self):
        if self._glitch_active:
            return
        self._glitch_active = True
        original_border = COLORS["border"]

        def flash(step=0):
            if step < 6:
                color = COLORS["accent_red"] if step % 2 == 0 else original_border
                self.login_entry.configure(border_color=color)
                self.password_entry.configure(border_color=color)
                self.after(60, lambda: flash(step + 1))
            else:
                self.login_entry.configure(border_color=original_border)
                self.password_entry.configure(border_color=original_border)
                self._glitch_active = False
        flash()