import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
import matplotlib
import time
import math
import random
import numpy as np
from collections import deque

matplotlib.rcParams['font.family'] = 'Consolas'

from netlogo_model import NetLogoModel

COLORS = {
    "bg_dark":        "#0a0a12",
    "bg_panel":       "#12111f",
    "bg_card":        "#1a1830",
    "accent_blue":    "#00d4ff",
    "accent_green":   "#39ff14",
    "accent_yellow":  "#fcee09",
    "accent_red":     "#ff003c",
    "accent_cyan":    "#00f0ff",
    "accent_purple":  "#bd00ff",
    "accent_pink":    "#ff2a6d",
    "accent_orange":  "#ff6a00",
    "text_primary":   "#e0f7fa",
    "text_secondary": "#7b8cad",
    "text_muted":     "#3d4a6b",
    "border":         "#2a1f4e",
    "border_glow":    "#00d4ff",
    "chart_line_1":   "#00d4ff",
    "chart_line_2":   "#39ff14",
    "chart_line_3":   "#bd00ff",
    "chart_line_4":   "#fcee09",
    "chart_bg":       "#0c0b18",
    "chart_grid":     "#1a1830",
    "canvas_bg":      "#08070f",
    "neon_glow":      "#00d4ff",
    "danger":         "#ff003c",
    "warning":        "#fcee09",
    "success":        "#39ff14",
}

DISTRICTS = {
    "center":      {"color": "#00d4ff", "alpha": 0.07, "label": "// CENTER"},
    "industrial":  {"color": "#ff6a00", "alpha": 0.05, "label": "// INDUSTRIAL"},
    "residential": {"color": "#39ff14", "alpha": 0.03, "label": "// RESIDENTIAL"},
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def blend_color(hex_color, alpha, bg_r=8, bg_g=7, bg_b=15):
    r_c = int(hex_color[1:3], 16)
    g_c = int(hex_color[3:5], 16)
    b_c = int(hex_color[5:7], 16)
    r = max(0, min(255, int(bg_r + (r_c - bg_r) * alpha)))
    g = max(0, min(255, int(bg_g + (g_c - bg_g) * alpha)))
    b = max(0, min(255, int(bg_b + (b_c - bg_b) * alpha)))
    return f"#{r:02x}{g:02x}{b:02x}"


def to_list(data):
    if data is None:
        return []
    if isinstance(data, np.ndarray):
        if data.size == 0:
            return []
        return data.tolist()
    if isinstance(data, list):
        return data
    try:
        return list(data)
    except (TypeError, ValueError):
        return []


class StatCard(ctk.CTkFrame):
    def __init__(self, master, title, value="0", icon="📊", accent_color="#00d4ff", **kwargs):
        super().__init__(master, corner_radius=4, fg_color=COLORS["bg_card"],
                         border_width=1, border_color=COLORS["border"], **kwargs)
        self.accent_color = accent_color
        self.history = []
        self.max_history = 20

        self.configure(height=90)
        self.pack_propagate(False)

        glow_bar = ctk.CTkFrame(self, fg_color=accent_color, height=2, corner_radius=0)
        glow_bar.pack(fill="x")

        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=20)
        header_frame.pack(fill="x", padx=10, pady=(6, 0))
        header_frame.pack_propagate(False)

        ctk.CTkLabel(header_frame, text=icon, font=("Segoe UI Emoji", 12),
                     anchor="w", width=18).pack(side="left")
        self.title_label = ctk.CTkLabel(header_frame, text=title.upper(),
                                        font=("Consolas", 9, "bold"),
                                        text_color=COLORS["text_muted"], anchor="w")
        self.title_label.pack(side="left", padx=(4, 0))

        self.trend_val = ctk.CTkLabel(header_frame, text="",
                                       font=("Consolas", 9, "bold"),
                                       width=50, anchor="e")
        self.trend_val.pack(side="right")
        self.trend_icon = ctk.CTkLabel(header_frame, text="",
                                        font=("Segoe UI", 11),
                                        width=16, anchor="e")
        self.trend_icon.pack(side="right")

        content_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        content_frame.pack(fill="x", padx=10, pady=(0, 6))
        content_frame.pack_propagate(False)

        self.value_label = ctk.CTkLabel(content_frame, text=value,
                                        font=("Consolas", 24, "bold"),
                                        text_color=accent_color,
                                        anchor="sw", width=90)
        self.value_label.pack(side="left", fill="y")

        self.spark_canvas = ctk.CTkCanvas(content_frame, bg=COLORS["bg_card"],
                                          highlightthickness=0, width=60, height=30)
        self.spark_canvas.pack(side="right", anchor="se", pady=(5, 0))

    def update_data(self, new_value):
        try:
            val = float(new_value)
        except (ValueError, TypeError):
            val = 0.0
        self.history.append(val)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        if isinstance(new_value, float):
            self.value_label.configure(text=f"{val:.2f}")
        else:
            self.value_label.configure(text=str(int(val)))
        self._update_trend()
        self._draw_sparkline()

    def _update_trend(self):
        if len(self.history) < 2:
            self.trend_icon.configure(text="")
            self.trend_val.configure(text="")
            return
        current = self.history[-1]
        previous = self.history[-2]
        if current > previous:
            self.trend_icon.configure(text="▲")
        elif current < previous:
            self.trend_icon.configure(text="▼")
        else:
            self.trend_icon.configure(text="■")
        if len(self.history) >= 5:
            start = self.history[-5]
            if start != 0:
                change = ((current - start) / abs(start)) * 100
                sign = "+" if change > 0 else ""
                color = COLORS["accent_green"] if change >= 0 else COLORS["accent_red"]
                self.trend_val.configure(text=f"{sign}{change:.0f}%", text_color=color)
            else:
                self.trend_val.configure(text="")
        else:
            self.trend_val.configure(text="")

    def _draw_sparkline(self):
        self.spark_canvas.delete("all")
        if len(self.history) < 2:
            return
        w, h = 60, 30
        min_v = min(self.history)
        max_v = max(self.history)
        range_v = max_v - min_v if max_v != min_v else 1
        points = []
        for i, v in enumerate(self.history):
            x = (i / (len(self.history) - 1)) * w
            y = h - ((v - min_v) / range_v) * (h - 4) - 2
            points.append((x, y))
        if len(points) > 1:
            self.spark_canvas.create_line(points, fill=blend_color(self.accent_color, 0.3),
                                          width=5, smooth=True)
            self.spark_canvas.create_line(points, fill=self.accent_color, width=2, smooth=True)
            fill_points = list(points) + [(points[-1][0], h), (points[0][0], h)]
            self.spark_canvas.create_polygon(fill_points, fill=blend_color(self.accent_color, 0.15),
                                             outline="")


class ParameterSlider(ctk.CTkFrame):
    def __init__(self, master, text, icon, min_val, max_val, default,
                 accent_color="#00d4ff", is_float=False, **kwargs):
        super().__init__(master, corner_radius=4, fg_color=COLORS["bg_card"],
                         border_width=1, border_color=COLORS["border"], **kwargs)
        self.is_float = is_float
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(6, 0))
        ctk.CTkLabel(header, text=icon, font=("Segoe UI Emoji", 12)).pack(side="left")
        ctk.CTkLabel(header, text=text.upper(), font=("Consolas", 10, "bold"),
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=(6, 0))
        display_val = f"{default:.1f}" if is_float else str(int(default))
        self.value_label = ctk.CTkLabel(header, text=display_val,
                                        font=("Consolas", 11, "bold"),
                                        text_color=accent_color)
        self.value_label.pack(side="right")
        self.slider = ctk.CTkSlider(
            self, from_=min_val, to=max_val, command=self._on_change,
            button_color=accent_color, button_hover_color=accent_color,
            progress_color=accent_color, fg_color=COLORS["border"], height=12,
        )
        self.slider.set(default)
        self.slider.pack(fill="x", padx=10, pady=(4, 8))

    def _on_change(self, val):
        if self.is_float:
            self.value_label.configure(text=f"{float(val):.1f}")
        else:
            self.value_label.configure(text=str(int(float(val))))

    def get(self):
        return self.slider.get()


class EventLog(ctk.CTkFrame):
    EVENT_TYPES = {
        "delivery":  {"icon": "►", "color": "#39ff14"},
        "new_order": {"icon": "■", "color": "#00d4ff"},
        "assigned":  {"icon": "◆", "color": "#fcee09"},
        "system":    {"icon": "●", "color": "#7b8cad"},
    }

    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=4, fg_color=COLORS["bg_card"],
                         border_width=1, border_color=COLORS["border"], **kwargs)
        self.max_visible = 50
        self.filters = {k: True for k in self.EVENT_TYPES}
        self.batch_buffer = {}
        self.last_flush_time = 0
        self.batch_interval = 0.5
        self.entry_widgets = []
        self._build_ui()

    def _build_ui(self):
        ctk.CTkFrame(self, fg_color=COLORS["accent_cyan"], height=1,
                      corner_radius=0).pack(fill="x")

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(6, 4))
        ctk.CTkLabel(header, text="// EVENT_LOG", font=("Consolas", 11, "bold"),
                     text_color=COLORS["accent_cyan"]).pack(side="left")
        ctk.CTkButton(header, text="CLR", width=32, height=20, corner_radius=2,
                      fg_color=COLORS["border"], hover_color=COLORS["accent_red"],
                      text_color=COLORS["text_muted"], font=("Consolas", 9, "bold"),
                      command=self.clear_log).pack(side="right")

        filters_frame = ctk.CTkFrame(self, fg_color="transparent")
        filters_frame.pack(fill="x", padx=8, pady=(0, 4))
        self.filter_buttons = {}
        for etype, info in self.EVENT_TYPES.items():
            btn = ctk.CTkButton(filters_frame, text=info["icon"], width=28, height=22,
                                corner_radius=2, fg_color=info["color"],
                                font=("Consolas", 10, "bold"),
                                text_color="#0a0a12",
                                command=lambda t=etype: self._toggle_filter(t))
            btn.pack(side="left", padx=2)
            self.filter_buttons[etype] = btn

        ctk.CTkFrame(self, fg_color=COLORS["border"], height=1).pack(fill="x", padx=8, pady=2)
        self.log_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                                  scrollbar_button_color=COLORS["border"])
        self.log_scroll.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        self.empty_label = ctk.CTkLabel(self.log_scroll,
                                         text="// AWAITING INPUT\n// START SIMULATION",
                                         font=("Consolas", 10),
                                         text_color=COLORS["text_muted"],
                                         justify="center")
        self.empty_label.pack(pady=20)

    def _toggle_filter(self, etype):
        self.filters[etype] = not self.filters[etype]
        info = self.EVENT_TYPES[etype]
        self.filter_buttons[etype].configure(
            fg_color=info["color"] if self.filters[etype] else COLORS["bg_dark"])
        self._repack_entries()

    def _repack_entries(self):
        for w, _ in self.entry_widgets:
            w.pack_forget()
        count = 0
        for w, data in self.entry_widgets:
            if not self.filters.get(data["type"], True):
                continue
            if count >= self.max_visible:
                break
            w.pack(fill="x", padx=2, pady=1)
            count += 1
        if count == 0:
            self._show_empty("// NO MATCHING EVENTS" if self.entry_widgets else "// AWAITING INPUT")
        else:
            self._remove_empty()

    def add_event(self, etype, msg, tick):
        if etype not in self.batch_buffer:
            self.batch_buffer[etype] = []
        self.batch_buffer[etype].append((msg, tick))
        if time.time() - self.last_flush_time >= self.batch_interval:
            self._flush_batch(tick)
            self.last_flush_time = time.time()

    def force_flush(self, tick):
        if self.batch_buffer:
            self._flush_batch(tick)

    def _flush_batch(self, tick):
        for etype, messages in self.batch_buffer.items():
            if not messages:
                continue
            count = len(messages)
            msg = messages[0][0] if count == 1 else f"{count} {etype} events"
            self._insert_entry({"type": etype, "message": msg, "tick": tick})
        self.batch_buffer.clear()

    def _insert_entry(self, data):
        self._remove_empty()
        info = self.EVENT_TYPES.get(data["type"], self.EVENT_TYPES["system"])
        entry = ctk.CTkFrame(self.log_scroll, fg_color="transparent", height=24)
        entry.pack_propagate(False)
        ctk.CTkFrame(entry, fg_color=info["color"], width=2, corner_radius=0).pack(
            side="left", fill="y", padx=(0, 6), pady=1)
        ctk.CTkLabel(entry, text=info["icon"], font=("Consolas", 9),
                     text_color=info["color"], width=14).pack(side="left", padx=(0, 4))
        ctk.CTkLabel(entry, text=f"[{data['tick']:04d}]", font=("Consolas", 8),
                     text_color=COLORS["text_muted"], width=42).pack(side="left", padx=(0, 4))
        ctk.CTkLabel(entry, text=data["message"], font=("Consolas", 9),
                     text_color=COLORS["text_secondary"], anchor="w").pack(
            side="left", fill="x", expand=True)
        self.entry_widgets.insert(0, (entry, data))
        if self.filters.get(data["type"], True):
            entry.pack(fill="x", padx=2, pady=1)
            entry.pack_forget()
            first = next((w for w, _ in self.entry_widgets[1:] if w.winfo_manager()), None)
            if first:
                entry.pack(fill="x", padx=2, pady=1, before=first)
            else:
                entry.pack(fill="x", padx=2, pady=1)
        while len(self.entry_widgets) > self.max_visible * 2:
            old, _ = self.entry_widgets.pop()
            old.destroy()

    def _remove_empty(self):
        if hasattr(self, 'empty_label') and self.empty_label:
            try:
                self.empty_label.destroy()
            except Exception:
                pass
            self.empty_label = None

    def _show_empty(self, text):
        self._remove_empty()
        self.empty_label = ctk.CTkLabel(self.log_scroll, text=text, font=("Consolas", 10),
                                         text_color=COLORS["text_muted"], justify="center")
        self.empty_label.pack(pady=20)

    def clear_log(self):
        for w, _ in self.entry_widgets:
            w.destroy()
        self.entry_widgets.clear()
        self.batch_buffer.clear()
        self._show_empty("// LOG CLEARED")


class DeliveryApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.model = NetLogoModel()
        self.running = False
        self.is_setup = False
        self.tick = 0

        self.title("NCDS")
        self.minsize(1100, 650)
        self.configure(fg_color=COLORS["bg_dark"])

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.time_data = []
        self.delivered_data = []
        self.wait_data = []
        self.queue_data = []
        self.efficiency_data = []

        self.pulse_effects = []
        self.delivery_particles = []
        self.prev_orders = set()
        self.prev_delivered = 0
        self.prev_order_count = 0
        self.order_counter = 0
        self.delivery_counter = 0
        self._recent_delivery_points = []
        self._tooltip_id = None
        self._tooltip_bg_id = None
        self._tooltip_items = []

        self.tps_last_time = time.time()
        self.tps_last_tick = 0
        self.tps_value = 0

        self.heatmap_enabled = False
        self.heatmap_data = {}
        self.heatmap_grid_size = 2

        self._scanline_offset = 0

        self.grid_columnconfigure(0, weight=0, minsize=280)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0, minsize=240)
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_center_panel()
        self._build_right_panel()

        self.bind("<space>", lambda e: self._toggle_run())
        self.bind("s", lambda e: self.setup_model())
        self.bind("S", lambda e: self.setup_model())
        self.bind("1", lambda e: self._set_speed(1))
        self.bind("2", lambda e: self._set_speed(5))
        self.bind("3", lambda e: self._set_speed(10))
        self.bind("4", lambda e: self._set_speed(15))
        self.bind("5", lambda e: self._set_speed(25))
       # self.update_idletasks()
       # self.state("zoomed")


    def _build_left_panel(self):
        left_panel = ctk.CTkFrame(self, corner_radius=4, fg_color=COLORS["bg_panel"],
                                  border_width=1, border_color=COLORS["border"])
        left_panel.grid(row=0, column=0, padx=(8, 4), pady=8, sticky="nsew")
        left_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkFrame(left_panel, fg_color=COLORS["accent_purple"], height=2,
                      corner_radius=0).grid(row=0, column=0, sticky="new", padx=0)

        header = ctk.CTkFrame(left_panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 6))
        ctk.CTkLabel(header, text="// SYS_PARAMS", font=("Consolas", 14, "bold"),
                     text_color=COLORS["accent_purple"]).pack(anchor="w")
        ctk.CTkLabel(header, text="CONFIGURE SIMULATION VARIABLES",
                     font=("Consolas", 9),
                     text_color=COLORS["text_muted"]).pack(anchor="w")

        scroll = ctk.CTkScrollableFrame(left_panel, fg_color="transparent",
                                        scrollbar_button_color=COLORS["border"])
        scroll.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))

        self.couriers_slider = ParameterSlider(scroll, "Couriers", "🚴", 1, 20, 10,
                                                accent_color=COLORS["accent_cyan"])
        self.couriers_slider.pack(fill="x", padx=4, pady=3)
        self.customers_slider = ParameterSlider(scroll, "Customers", "👤", 10, 100, 50,
                                                 accent_color=COLORS["accent_pink"])
        self.customers_slider.pack(fill="x", padx=4, pady=3)
        self.order_rate_slider = ParameterSlider(scroll, "Order Rate", "📦", 1, 20, 10,
                                                  accent_color=COLORS["accent_yellow"])
        self.order_rate_slider.pack(fill="x", padx=4, pady=3)
        self.warehouse_slider = ParameterSlider(scroll, "Warehouses", "🏭", 1, 10, 3,
                                                 accent_color=COLORS["accent_purple"])
        self.warehouse_slider.pack(fill="x", padx=4, pady=3)
        self.speed_slider = ParameterSlider(scroll, "Courier Speed", "⚡", 0.1, 2, 1,
                                             accent_color=COLORS["accent_green"],
                                             is_float=True)
        self.speed_slider.pack(fill="x", padx=4, pady=3)
        self.traffic_slider = ParameterSlider(scroll, "Traffic Effect", "🚗", 1, 5, 3,
                                               accent_color=COLORS["accent_red"])
        self.traffic_slider.pack(fill="x", padx=4, pady=3)

        traffic_card = ctk.CTkFrame(scroll, corner_radius=4, fg_color=COLORS["bg_card"],
                                    border_width=1, border_color=COLORS["border"])
        traffic_card.pack(fill="x", padx=4, pady=(3, 6))
        self.avoid_traffic_var = ctk.BooleanVar(value=True)
        switch_frame = ctk.CTkFrame(traffic_card, fg_color="transparent")
        switch_frame.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(switch_frame, text="🛣️", font=("Segoe UI Emoji", 12)).pack(side="left")
        ctk.CTkLabel(switch_frame, text="AVOID TRAFFIC", font=("Consolas", 10, "bold"),
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=(6, 0))
        ctk.CTkSwitch(switch_frame, text="", width=42, variable=self.avoid_traffic_var,
                      command=self.toggle_traffic, progress_color=COLORS["accent_green"],
                      button_color=COLORS["text_primary"],
                      fg_color=COLORS["border"]).pack(side="right")

        keys_card = ctk.CTkFrame(scroll, corner_radius=4, fg_color=COLORS["bg_card"],
                                  border_width=1, border_color=COLORS["border"])
        keys_card.pack(fill="x", padx=4, pady=(3, 6))
        ctk.CTkLabel(keys_card, text="// HOTKEYS", font=("Consolas", 10, "bold"),
                     text_color=COLORS["accent_cyan"]).pack(anchor="w", padx=10, pady=(8, 4))
        for key, action in [("SPACE", "Start / Pause"), ("S", "Setup"),
                            ("1-5", "Speed 1x-25x")]:
            row = ctk.CTkFrame(keys_card, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=1)
            ctk.CTkLabel(row, text=f"[{key}]", font=("Consolas", 9, "bold"),
                         text_color=COLORS["accent_yellow"], width=55,
                         anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=action, font=("Consolas", 9),
                         text_color=COLORS["text_muted"]).pack(side="left")
        ctk.CTkFrame(keys_card, fg_color="transparent", height=6).pack()

    def _build_center_panel(self):
        center_panel = ctk.CTkFrame(self, corner_radius=4, fg_color=COLORS["bg_panel"],
                                    border_width=1, border_color=COLORS["border"])
        center_panel.grid(row=0, column=1, padx=4, pady=8, sticky="nsew")
        center_panel.grid_rowconfigure(2, weight=1)
        center_panel.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkFrame(center_panel, fg_color=COLORS["accent_cyan"], height=2,
                      corner_radius=0).grid(row=0, column=0, columnspan=4,
                                            sticky="new", padx=0)

        stats_frame = ctk.CTkFrame(center_panel, fg_color="transparent")
        stats_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=10, pady=(10, 4))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.stat_delivered = StatCard(stats_frame, "Delivered", "0", "📬",
                                       accent_color=COLORS["accent_green"])
        self.stat_delivered.grid(row=0, column=0, padx=3, sticky="ew")
        self.stat_wait = StatCard(stats_frame, "Avg Wait", "0.00", "⏱️",
                                  accent_color=COLORS["accent_yellow"])
        self.stat_wait.grid(row=0, column=1, padx=3, sticky="ew")
        self.stat_active = StatCard(stats_frame, "Active Orders", "0", "📋",
                                    accent_color=COLORS["accent_cyan"])
        self.stat_active.grid(row=0, column=2, padx=3, sticky="ew")
        self.stat_efficiency = StatCard(stats_frame, "Efficiency", "0.00", "⚡",
                                        accent_color=COLORS["accent_purple"])
        self.stat_efficiency.grid(row=0, column=3, padx=3, sticky="ew")

        charts_frame = ctk.CTkFrame(center_panel, fg_color="transparent")
        charts_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=6, pady=3)
        charts_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.fig1, self.ax1 = self._create_styled_figure(size=(2.6, 1.6))
        self.fig2, self.ax2 = self._create_styled_figure(size=(2.6, 1.6))
        self.fig3, self.ax3 = self._create_styled_figure(size=(2.6, 1.6))
        self.fig4, self.ax4 = self._create_styled_figure(size=(2.6, 1.6))

        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=charts_frame)
        self.canvas1.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=2, pady=3)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=charts_frame)
        self.canvas2.get_tk_widget().grid(row=0, column=1, sticky="nsew", padx=2, pady=3)
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=charts_frame)
        self.canvas3.get_tk_widget().grid(row=0, column=2, sticky="nsew", padx=2, pady=3)
        self.canvas4 = FigureCanvasTkAgg(self.fig4, master=charts_frame)
        self.canvas4.get_tk_widget().grid(row=0, column=3, sticky="nsew", padx=2, pady=3)

        canvas_container = ctk.CTkFrame(center_panel, corner_radius=4,
                                         fg_color=COLORS["canvas_bg"],
                                         border_width=1, border_color=COLORS["border"])
        canvas_container.grid(row=2, column=0, columnspan=4, sticky="nsew",
                              padx=10, pady=(3, 10))
        canvas_container.grid_rowconfigure(1, weight=1)
        canvas_container.grid_columnconfigure(0, weight=1)

        canvas_header = ctk.CTkFrame(canvas_container, fg_color="transparent")
        canvas_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 0))
        ctk.CTkLabel(canvas_header, text="// WORLD_VIEW",
                     font=("Consolas", 12, "bold"),
                     text_color=COLORS["accent_cyan"]).pack(side="left")

        self.heatmap_btn = ctk.CTkButton(
            canvas_header, text="◈ HEATMAP", width=90, height=22,
            corner_radius=2, font=("Consolas", 9, "bold"),
            fg_color=COLORS["bg_card"], hover_color=COLORS["border"],
            border_width=1, border_color=COLORS["border"],
            text_color=COLORS["text_muted"], command=self._toggle_heatmap
        )
        self.heatmap_btn.pack(side="left", padx=(10, 0))

        legend_frame = ctk.CTkFrame(canvas_header, fg_color="transparent")
        legend_frame.pack(side="right")
        for dot, label, color in [
            ("■", "WH", "#fcee09"), ("●", "COUR", "#00f0ff"),
            ("●", "CUST", "#ff2a6d"), ("□", "ORD", "#ffffff"),
            ("◆", "CTR", "#00d4ff"), ("◆", "IND", "#ff6a00"),
            ("◆", "RES", "#39ff14")
        ]:
            ctk.CTkLabel(legend_frame, text=f"{dot}{label}",
                         font=("Consolas", 8),
                         text_color=color).pack(side="left", padx=(5, 0))

        self.canvas = ctk.CTkCanvas(canvas_container, bg=COLORS["canvas_bg"],
                                     highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        self.canvas.bind("<Motion>", self._on_canvas_hover)
        self.canvas.bind("<Leave>", self._on_canvas_leave)

    def _create_styled_figure(self, size=(3.2, 1.8)):
        fig, ax = plt.subplots(figsize=size)
        fig.patch.set_facecolor(COLORS["chart_bg"])
        ax.set_facecolor(COLORS["chart_bg"])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(COLORS["chart_grid"])
        ax.spines['bottom'].set_color(COLORS["chart_grid"])
        ax.tick_params(colors=COLORS["text_muted"], labelsize=7)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=5))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
        ax.grid(True, alpha=0.15, color=COLORS["text_muted"], linestyle=':')
        fig.tight_layout(pad=1.5)
        return fig, ax

    def _build_right_panel(self):
        right_panel = ctk.CTkFrame(self, corner_radius=4, fg_color=COLORS["bg_panel"],
                                   border_width=1, border_color=COLORS["border"])
        right_panel.grid(row=0, column=2, padx=(4, 8), pady=8, sticky="nsew")

        ctk.CTkFrame(right_panel, fg_color=COLORS["accent_red"], height=2,
                      corner_radius=0).pack(fill="x")

        header = ctk.CTkFrame(right_panel, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(12, 10))
        ctk.CTkLabel(header, text="// CONTROL", font=("Consolas", 14, "bold"),
                     text_color=COLORS["accent_red"]).pack(anchor="w")

        for text, color, cmd in [
            ("► SETUP", COLORS["accent_cyan"], self.setup_model),
            ("▶ START", COLORS["accent_green"], self.start_simulation),
            ("❚❚ PAUSE", COLORS["accent_yellow"], self.pause_simulation),
        ]:
            ctk.CTkButton(
                right_panel, text=text, fg_color=COLORS["bg_card"],
                hover_color=color, command=cmd,
                font=("Consolas", 12, "bold"), height=36, corner_radius=2,
                text_color=color,
                border_width=1, border_color=color
            ).pack(pady=3, fill="x", padx=14)

        ctk.CTkFrame(right_panel, fg_color=COLORS["border"], height=1).pack(
            fill="x", padx=18, pady=8)

        info_row = ctk.CTkFrame(right_panel, fg_color="transparent")
        info_row.pack(fill="x", padx=14, pady=(0, 4))
        info_row.grid_columnconfigure((0, 1), weight=1)

        sc = ctk.CTkFrame(info_row, corner_radius=4, fg_color=COLORS["bg_card"],
                          border_width=1, border_color=COLORS["border"])
        sc.grid(row=0, column=0, padx=(0, 3), sticky="ew")
        si = ctk.CTkFrame(sc, fg_color="transparent")
        si.pack(fill="x", padx=8, pady=5)
        ctk.CTkLabel(si, text="STATUS", font=("Consolas", 8),
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        self.status_label = ctk.CTkLabel(si, text="■ IDLE",
                                         font=("Consolas", 10, "bold"),
                                         text_color=COLORS["text_secondary"])
        self.status_label.pack(anchor="w")

        tc = ctk.CTkFrame(info_row, corner_radius=4, fg_color=COLORS["bg_card"],
                           border_width=1, border_color=COLORS["border"])
        tc.grid(row=0, column=1, padx=(3, 0), sticky="ew")
        ti = ctk.CTkFrame(tc, fg_color="transparent")
        ti.pack(fill="x", padx=8, pady=5)
        ctk.CTkLabel(ti, text="TICK", font=("Consolas", 8),
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        tick_row = ctk.CTkFrame(ti, fg_color="transparent")
        tick_row.pack(fill="x")
        self.tick_label = ctk.CTkLabel(tick_row, text="0000",
                                       font=("Consolas", 16, "bold"),
                                       text_color=COLORS["accent_cyan"])
        self.tick_label.pack(side="left")
        self.tps_label = ctk.CTkLabel(tick_row, text="0 t/s",
                                       font=("Consolas", 8),
                                       text_color=COLORS["text_muted"])
        self.tps_label.pack(side="right", anchor="s", pady=(0, 2))

        spc = ctk.CTkFrame(right_panel, corner_radius=4, fg_color=COLORS["bg_card"],
                            border_width=1, border_color=COLORS["border"])
        spc.pack(fill="x", padx=14, pady=(4, 4))
        spi = ctk.CTkFrame(spc, fg_color="transparent")
        spi.pack(fill="x", padx=8, pady=5)
        sph = ctk.CTkFrame(spi, fg_color="transparent")
        sph.pack(fill="x")
        ctk.CTkLabel(sph, text="SPEED", font=("Consolas", 10, "bold"),
                     text_color=COLORS["text_secondary"]).pack(side="left")
        self.speed_value_label = ctk.CTkLabel(sph, text="01x",
                                               font=("Consolas", 10, "bold"),
                                               text_color=COLORS["accent_yellow"])
        self.speed_value_label.pack(side="right")
        self.simulation_speed_slider = ctk.CTkSlider(
            spi, from_=1, to=25, command=self._on_speed_change,
            button_color=COLORS["accent_yellow"],
            button_hover_color=COLORS["accent_yellow"],
            progress_color=COLORS["accent_yellow"],
            fg_color=COLORS["border"], height=10,
        )
        self.simulation_speed_slider.set(1)
        self.simulation_speed_slider.pack(fill="x", pady=(4, 0))

        ctk.CTkFrame(right_panel, fg_color=COLORS["border"], height=1).pack(
            fill="x", padx=18, pady=5)

        ctk.CTkButton(
            right_panel, text="◈ EXPORT CSV",
            fg_color=COLORS["bg_card"], hover_color=COLORS["border"],
            border_width=1, border_color=COLORS["accent_cyan"],
            text_color=COLORS["accent_cyan"], font=("Consolas", 10, "bold"),
            height=30, corner_radius=2, command=self._export_csv
        ).pack(fill="x", padx=14, pady=(3, 3))

        ctk.CTkFrame(right_panel, fg_color=COLORS["border"], height=1).pack(
            fill="x", padx=18, pady=5)

        self.event_log = EventLog(right_panel)
        self.event_log.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _on_speed_change(self, val):
        speed = int(float(val))
        self.speed_value_label.configure(text=f"{speed:02d}x")

    @staticmethod
    def _lighten(hex_color, factor):
        h = hex_color.lstrip('#')
        r, g, b = int(h[:2], 16), int(h[2:4], 16), int(h[4:], 16)
        return (f"#{min(255,int(r+(255-r)*factor)):02x}"
                f"{min(255,int(g+(255-g)*factor)):02x}"
                f"{min(255,int(b+(255-b)*factor)):02x}")

    def _toggle_run(self):
        if self.running:
            self.pause_simulation()
        else:
            self.start_simulation()

    def _set_speed(self, value):
        self.simulation_speed_slider.set(value)
        self.speed_value_label.configure(text=f"{value:02d}x")

    def _export_csv(self):
        if not self.time_data:
            return
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"ncds_export_{self.tick}ticks.csv"
        )
        if not filepath:
            return
        with open(filepath, "w") as f:
            f.write("tick,delivered,avg_wait,active_orders,efficiency\n")
            for i in range(len(self.time_data)):
                eff = self.efficiency_data[i] if i < len(self.efficiency_data) else 0
                f.write(f"{self.time_data[i]},{self.delivered_data[i]},"
                        f"{self.wait_data[i]:.2f},{self.queue_data[i]},{eff:.4f}\n")
        self.event_log.add_event("system",
                                 f"Exported {len(self.time_data)} rows", self.tick)
        self.event_log.force_flush(self.tick)

    def _on_close(self):
        if self.running:
            self.running = False

        dialog = ctk.CTkToplevel(self)
        dialog.title("")
        dialog.resizable(False, False)
        dialog.configure(fg_color=COLORS["bg_panel"])
        dialog.grab_set()
        dialog.focus_force()

        dw, dh = 400, 200
        dialog.geometry(f"{dw}x{dh}")
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dw) // 2
        y = self.winfo_y() + (self.winfo_height() - dh) // 2
        dialog.geometry(f"{dw}x{dh}+{x}+{y}")

        ctk.CTkFrame(dialog, fg_color=COLORS["accent_red"], height=2,
                      corner_radius=0).pack(fill="x")

        ctk.CTkLabel(dialog, text="// SYSTEM EXIT",
                     font=("Consolas", 16, "bold"),
                     text_color=COLORS["accent_red"]).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="Disconnect from Night City systems?",
                     font=("Consolas", 11),
                     text_color=COLORS["text_secondary"]).pack(pady=(0, 5))
        ctk.CTkLabel(dialog, text="All unsaved data will be lost.",
                     font=("Consolas", 9),
                     text_color=COLORS["text_muted"]).pack(pady=(0, 15))

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(0, 20))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        def do_exit():
            dialog.destroy()
            self._force_shutdown()

        def do_cancel():
            dialog.destroy()

        ctk.CTkButton(
            btn_frame, text="CANCEL", height=34, corner_radius=2,
            fg_color=COLORS["bg_card"], hover_color=COLORS["border"],
            border_width=1, border_color=COLORS["accent_cyan"],
            text_color=COLORS["accent_cyan"], font=("Consolas", 11, "bold"),
            command=do_cancel
        ).grid(row=0, column=0, padx=(0, 5), sticky="ew")

        ctk.CTkButton(
            btn_frame, text="DISCONNECT", height=34, corner_radius=2,
            fg_color=COLORS["accent_red"], hover_color="#cc0030",
            text_color="#ffffff", font=("Consolas", 11, "bold"),
            command=do_exit
        ).grid(row=0, column=1, padx=(5, 0), sticky="ew")

        dialog.bind("<Escape>", lambda e: do_cancel())
        dialog.bind("<Return>", lambda e: do_exit())

    def _force_shutdown(self):
        try:
            self.running = False
        except Exception:
            pass
        try:
            plt.close('all')
        except Exception:
            pass
        try:
            if hasattr(self, 'model') and hasattr(self.model, 'netlogo'):
                self.model.netlogo.kill_workspace()
        except Exception:
            pass
        try:
            self.quit()
            self.destroy()
        except Exception:
            pass
        import os
        os._exit(0)

    def _toggle_heatmap(self):
        self.heatmap_enabled = not self.heatmap_enabled
        if self.heatmap_enabled:
            self.heatmap_btn.configure(fg_color=COLORS["accent_red"],
                                       text_color="#ffffff",
                                       border_color=COLORS["accent_red"])
        else:
            self.heatmap_btn.configure(fg_color=COLORS["bg_card"],
                                       text_color=COLORS["text_muted"],
                                       border_color=COLORS["border"])

    def _record_heatmap(self, couriers, customers, orders):
        gs = self.heatmap_grid_size
        courier_statuses = self.model.get_couriers_status()
        for cx, cy, state in courier_statuses:
            gx = int(round(cx / gs) * gs)
            gy = int(round(cy / gs) * gs)
            key = (gx, gy)
            if state in ("to-warehouse", "delivering", "returning"):
                self.heatmap_data[key] = self.heatmap_data.get(key, 0) + 2
            else:
                self.heatmap_data[key] = self.heatmap_data.get(key, 0) + 0.2
        if not courier_statuses:
            for item in couriers:
                try:
                    x, y = float(item[0]), float(item[1])
                    gx = int(round(x / gs) * gs)
                    gy = int(round(y / gs) * gs)
                    key = (gx, gy)
                    self.heatmap_data[key] = self.heatmap_data.get(key, 0) + 1
                except Exception:
                    continue
        for item in customers:
            try:
                x, y = float(item[0]), float(item[1])
                gx = int(round(x / gs) * gs)
                gy = int(round(y / gs) * gs)
                key = (gx, gy)
                self.heatmap_data[key] = self.heatmap_data.get(key, 0) + 0.3
            except Exception:
                continue
        for (dx, dy) in self._recent_delivery_points:
            gx = int(round(dx / gs) * gs)
            gy = int(round(dy / gs) * gs)
            key = (gx, gy)
            self.heatmap_data[key] = self.heatmap_data.get(key, 0) + 8

    def _draw_heatmap(self):
        if not self.heatmap_data:
            return
        decay_factor = 0.995
        keys_to_remove = []
        for key in self.heatmap_data:
            self.heatmap_data[key] *= decay_factor
            if self.heatmap_data[key] < 0.1:
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del self.heatmap_data[key]
        if not self.heatmap_data:
            return
        max_count = max(self.heatmap_data.values())
        if max_count == 0:
            return
        gs = self.heatmap_grid_size
        for (gx, gy), count in self.heatmap_data.items():
            intensity = count / max_count
            if intensity < 0.05:
                continue
            if intensity < 0.25:
                t = intensity / 0.25
                r = int(10 + 10 * t)
                g = int(20 + 100 * t)
                b = int(120 + 135 * t)
            elif intensity < 0.5:
                t = (intensity - 0.25) / 0.25
                r = int(20 + 230 * t)
                g = int(120 + 120 * t)
                b = int(255 - 200 * t)
            elif intensity < 0.75:
                t = (intensity - 0.5) / 0.25
                r = int(250 + 5 * t)
                g = int(240 - 100 * t)
                b = int(55 - 50 * t)
            else:
                t = (intensity - 0.75) / 0.25
                r = 255
                g = int(140 - 140 * t)
                b = int(5 + 55 * t)
            alpha = 0.35 + intensity * 0.50
            bg_r, bg_g, bg_b = 8, 7, 15
            fr = int(bg_r + (r - bg_r) * alpha)
            fg = int(bg_g + (g - bg_g) * alpha)
            fb = int(bg_b + (b - bg_b) * alpha)
            fr = max(0, min(255, fr))
            fg = max(0, min(255, fg))
            fb = max(0, min(255, fb))
            color = f"#{fr:02x}{fg:02x}{fb:02x}"
            cx1, cy1 = self.world_to_canvas(gx - gs / 2, gy + gs / 2)
            cx2, cy2 = self.world_to_canvas(gx + gs / 2, gy - gs / 2)
            self.canvas.create_rectangle(cx1, cy1, cx2, cy2, fill=color, outline="")

        w = self.canvas.winfo_width()
        bar_x = w - 25
        bar_y1 = 30
        bar_h = 80
        steps = 20
        for i in range(steps):
            t = i / (steps - 1)
            if t < 0.25:
                t2 = t / 0.25
                r = int(10 + 10 * t2)
                g = int(20 + 100 * t2)
                b = int(120 + 135 * t2)
            elif t < 0.5:
                t2 = (t - 0.25) / 0.25
                r = int(20 + 230 * t2)
                g = int(120 + 120 * t2)
                b = int(255 - 200 * t2)
            elif t < 0.75:
                t2 = (t - 0.5) / 0.25
                r = int(250 + 5 * t2)
                g = int(240 - 100 * t2)
                b = int(55 - 50 * t2)
            else:
                t2 = (t - 0.75) / 0.25
                r = 255
                g = int(140 - 140 * t2)
                b = int(5 + 55 * t2)
            y1 = bar_y1 + (1 - t) * bar_h
            y2 = y1 + bar_h / steps + 1
            self.canvas.create_rectangle(bar_x - 6, y1, bar_x + 6, y2,
                                         fill=f"#{r:02x}{g:02x}{b:02x}", outline="")
        self.canvas.create_text(bar_x, bar_y1 - 8, text="MAX",
                                fill=COLORS["accent_red"], font=("Consolas", 6, "bold"))
        self.canvas.create_text(bar_x, bar_y1 + bar_h + 10, text="MIN",
                                fill=COLORS["accent_cyan"], font=("Consolas", 6, "bold"))

    def toggle_traffic(self):
        self.model.set_avoid_traffic(bool(self.avoid_traffic_var.get()))

    def _on_canvas_hover(self, event):
        mx, my = event.x, event.y
        courier_statuses = self.model.get_couriers_status()
        if not courier_statuses:
            self._hide_tooltip()
            return
        closest = None
        closest_dist = float('inf')
        for cx, cy, state in courier_statuses:
            sx, sy = self.world_to_canvas(cx, cy)
            dist = math.sqrt((mx - sx) ** 2 + (my - sy) ** 2)
            if dist < closest_dist:
                closest_dist = dist
                closest = (cx, cy, state, sx, sy)
        if closest and closest_dist <= 15:
            wx, wy, state, sx, sy = closest
            self._show_tooltip(sx, sy, wx, wy, state)
        else:
            self._hide_tooltip()

    def _on_canvas_leave(self, event):
        self._hide_tooltip()

    def _show_tooltip(self, screen_x, screen_y, world_x, world_y, state):
        self._hide_tooltip()
        state_info = {
            "idle":         {"icon": "■", "label": "IDLE",
                             "color": COLORS["accent_red"],
                             "desc": "AWAITING ASSIGNMENT"},
            "to-warehouse": {"icon": "►", "label": "TO_WAREHOUSE",
                             "color": COLORS["accent_orange"],
                             "desc": "PICKING UP ORDER"},
            "delivering":   {"icon": "▶", "label": "DELIVERING",
                             "color": COLORS["accent_green"],
                             "desc": "EN ROUTE TO CLIENT"},
            "returning":    {"icon": "◄", "label": "RETURNING",
                             "color": COLORS["accent_cyan"],
                             "desc": "HEADING BACK"},
        }
        info = state_info.get(state, {"icon": "?", "label": state,
                                       "color": "#7b8cad", "desc": ""})

        line1 = f"{info['icon']} {info['label']}"
        line2 = info['desc']
        line3 = f"LOC [{world_x:.1f}, {world_y:.1f}]"

        pad_x, pad_y = 8, 5
        line_h = 15
        tooltip_w = 170
        tooltip_h = pad_y * 2 + line_h * 3 + 4

        tx = screen_x + 18
        ty = screen_y - tooltip_h - 5
        canvas_w = self.canvas.winfo_width()
        if tx + tooltip_w > canvas_w - 5:
            tx = screen_x - tooltip_w - 18
        if ty < 5:
            ty = screen_y + 18

        bg = self.canvas.create_rectangle(
            tx, ty, tx + tooltip_w, ty + tooltip_h,
            fill="#0c0b18", outline=info['color'], width=1
        )
        self._tooltip_items.append(bg)

        neon = self.canvas.create_rectangle(
            tx + 1, ty + 1, tx + tooltip_w - 1, ty + 3,
            fill=info['color'], outline=""
        )
        self._tooltip_items.append(neon)

        t1 = self.canvas.create_text(
            tx + pad_x, ty + pad_y + 5,
            text=line1, anchor="nw",
            fill=info['color'], font=("Consolas", 9, "bold")
        )
        self._tooltip_items.append(t1)

        t2 = self.canvas.create_text(
            tx + pad_x, ty + pad_y + 5 + line_h,
            text=line2, anchor="nw",
            fill=COLORS["text_secondary"], font=("Consolas", 8)
        )
        self._tooltip_items.append(t2)

        t3 = self.canvas.create_text(
            tx + pad_x, ty + pad_y + 5 + line_h * 2,
            text=line3, anchor="nw",
            fill=COLORS["text_muted"], font=("Consolas", 8)
        )
        self._tooltip_items.append(t3)

    def _hide_tooltip(self):
        for item_id in self._tooltip_items:
            try:
                self.canvas.delete(item_id)
            except Exception:
                pass
        self._tooltip_items.clear()

    def setup_model(self):
        self.is_setup = True
        self.status_label.configure(text="◆ INIT...",
                                     text_color=COLORS["accent_cyan"])
        self.update()

        self.model.setup(
            int(self.couriers_slider.get()),
            int(self.customers_slider.get()),
            int(self.order_rate_slider.get()),
            int(self.warehouse_slider.get()),
            self.speed_slider.get(),
            self.traffic_slider.get()
        )

        self.tick = 0
        self.time_data.clear()
        self.delivered_data.clear()
        self.wait_data.clear()
        self.queue_data.clear()
        self.efficiency_data.clear()
        self.pulse_effects.clear()
        self.delivery_particles.clear()
        self.prev_orders.clear()
        self.prev_delivered = 0
        self.prev_order_count = 0
        self.order_counter = 0
        self.delivery_counter = 0
        self.heatmap_data.clear()
        self._recent_delivery_points = []
        self.tps_last_time = time.time()
        self.tps_last_tick = 0

        self.event_log.clear_log()
        self.event_log.add_event("system",
            f"SYS_INIT: {int(self.couriers_slider.get())} couriers, "
            f"{int(self.customers_slider.get())} clients", 0)
        self.event_log.force_flush(0)

        self.update_all()
        self.status_label.configure(text="● READY",
                                     text_color=COLORS["accent_green"])

    def start_simulation(self):
        if not self.is_setup:
            return
        self.running = True
        self.status_label.configure(text="▶ RUNNING",
                                     text_color=COLORS["accent_green"])
        self.event_log.add_event("system", "SIMULATION ONLINE", self.tick)
        self.event_log.force_flush(self.tick)
        self.run_loop()

    def pause_simulation(self):
        self.running = False
        self.status_label.configure(text="❚❚ PAUSED",
                                     text_color=COLORS["accent_yellow"])
        self.event_log.add_event("system",
                                 f"HALTED @ tick {self.tick}", self.tick)
        self.event_log.force_flush(self.tick)

    def run_loop(self):
        if not self.running:
            return

        steps_per_frame = int(self.simulation_speed_slider.get())

        for _ in range(steps_per_frame):
            self.model.step()
            self.tick += 1

            stats = self.model.get_stats()
            try:
                delivered = int(stats['delivered'])
            except (ValueError, TypeError):
                delivered = 0
            try:
                avg_wait = float(stats['avg_wait'])
            except (ValueError, TypeError):
                avg_wait = 0.0
            try:
                active = int(stats['active'])
            except (ValueError, TypeError):
                active = 0

            self.time_data.append(self.tick)
            self.delivered_data.append(delivered)
            self.wait_data.append(avg_wait)
            self.queue_data.append(active)

            num_couriers = max(1, int(self.couriers_slider.get()))
            if self.tick > 0:
                efficiency = delivered / num_couriers / self.tick * 100
            else:
                efficiency = 0.0
            self.efficiency_data.append(efficiency)

            new_orders = active - self.prev_order_count + (delivered - self.prev_delivered)
            if new_orders > 0:
                for _ in range(new_orders):
                    self.order_counter += 1
                    self.event_log.add_event("new_order",
                        f"ORD#{self.order_counter:04d} created", self.tick)

            new_deliveries = delivered - self.prev_delivered
            if new_deliveries > 0:
                for _ in range(new_deliveries):
                    self.delivery_counter += 1
                    self.event_log.add_event("delivery",
                        f"DELIVERED #{self.delivery_counter:04d}", self.tick)

            self.prev_order_count = active
            self.prev_delivered = delivered

        self.stat_delivered.update_data(delivered)
        self.stat_wait.update_data(avg_wait)
        self.stat_active.update_data(active)
        self.stat_efficiency.update_data(round(efficiency, 2))
        self.tick_label.configure(text=f"{self.tick:04d}")
        self.event_log.force_flush(self.tick)

        now = time.time()
        elapsed = now - self.tps_last_time
        if elapsed >= 1.0:
            self.tps_value = int((self.tick - self.tps_last_tick) / elapsed)
            self.tps_last_time = now
            self.tps_last_tick = self.tick
            self.tps_label.configure(text=f"{self.tps_value} t/s")

        self.update_canvas()
        if self.tick % 5 == 0:
            self.update_plot()

        self.after(16, self.run_loop)

    def update_all(self):
        stats = self.model.get_stats()
        try:
            delivered = int(stats['delivered'])
        except (ValueError, TypeError):
            delivered = 0
        try:
            avg_wait = float(stats['avg_wait'])
        except (ValueError, TypeError):
            avg_wait = 0.0
        try:
            active = int(stats['active'])
        except (ValueError, TypeError):
            active = 0

        self.stat_delivered.update_data(delivered)
        self.stat_wait.update_data(avg_wait)
        self.stat_active.update_data(active)
        self.tick_label.configure(text=f"{self.tick:04d}")

        self.time_data.append(self.tick)
        self.delivered_data.append(delivered)
        self.wait_data.append(avg_wait)
        self.queue_data.append(active)

        num_couriers = max(1, int(self.couriers_slider.get()))
        if self.tick > 0:
            efficiency = delivered / num_couriers / self.tick * 100
        else:
            efficiency = 0.0
        self.efficiency_data.append(efficiency)
        self.stat_efficiency.update_data(round(efficiency, 2))

        self.update_canvas()
        self.update_plot()

    def update_canvas(self):
        if self.canvas.winfo_width() < 10:
            self.after(50, self.update_canvas)
            return

        self.canvas.delete("all")
        current_time = time.time()
        self._scanline_offset = (self._scanline_offset + 1) % 4

        data = self.model.get_agents()
        roads = data.get("roads", [])
        warehouses = data.get("warehouses", [])
        couriers = data.get("couriers", [])
        customers = data.get("customers", [])
        orders = data.get("orders", [])

        self._draw_districts()

        for item in roads:
            try:
                x, y, load = float(item[0]), float(item[1]), float(item[2])
                cx, cy = self.world_to_canvas(x, y)
                intensity = min(load / 5, 1)
                if intensity > 0.3:
                    r = int(255 * intensity)
                    g = int(60 * (1 - intensity))
                    b = int(30 * (1 - intensity))
                else:
                    r = int(30 + 40 * intensity)
                    g = int(30 + 20 * intensity)
                    b = int(50 + 30 * intensity)
                self.canvas.create_rectangle(cx - 1, cy - 1, cx + 1, cy + 1,
                                             fill=f"#{r:02x}{g:02x}{b:02x}", outline="")
            except Exception:
                continue

        self._draw_district_borders()
        self._draw_scanlines()

        current_orders = set()
        for item in orders:
            try:
                x, y = float(item[0]), float(item[1])
                order_key = (round(x, 2), round(y, 2))
                current_orders.add(order_key)
            except Exception:
                continue

        try:
            cur_delivered = int(self.model.get_stats().get("delivered", 0))
        except (ValueError, TypeError):
            cur_delivered = 0

        self._recent_delivery_points = []
        if cur_delivered > self.prev_delivered:
            courier_statuses = self.model.get_couriers_status()
            for cx, cy, state in courier_statuses:
                if state == "returning":
                    self._recent_delivery_points.append((cx, cy))

        self._record_heatmap(couriers, customers, orders)
        if self.heatmap_enabled:
            self._draw_heatmap()

        for item in warehouses:
            try:
                x, y = float(item[0]), float(item[1])
                cx, cy = self.world_to_canvas(x, y)
                glow_pulse = math.sin(current_time * 3) * 0.3 + 0.7

                for i in range(3, 0, -1):
                    gr = 6 + i * 4
                    gc = blend_color("#fcee09", glow_pulse * 0.25 / i)
                    self.canvas.create_oval(cx - gr, cy - gr, cx + gr, cy + gr,
                                            fill="", outline=gc, width=1)

                pts = [(cx, cy - 8), (cx + 8, cy), (cx, cy + 8), (cx - 8, cy)]
                self.canvas.create_polygon(pts, fill="#fcee09", outline="#ffd700",
                                           width=1)
                self.canvas.create_text(cx, cy, text="W", fill="#0a0a12",
                                        font=("Consolas", 7, "bold"))
            except Exception:
                continue

        for item in customers:
            try:
                x, y = float(item[0]), float(item[1])
                cx, cy = self.world_to_canvas(x, y)
                self.canvas.create_rectangle(cx - 2, cy - 2, cx + 2, cy + 2,
                                             fill="#ff2a6d", outline="")
            except Exception:
                continue

        for item in orders:
            try:
                x, y = float(item[0]), float(item[1])
                order_key = (round(x, 2), round(y, 2))
                cx, cy = self.world_to_canvas(x, y)
                if order_key not in self.prev_orders:
                    self.pulse_effects.append((x, y, current_time, "new_order"))

                blink = math.sin(current_time * 5 + hash(order_key)) * 0.3 + 0.7
                color = blend_color("#ffffff", blink)
                self.canvas.create_rectangle(cx - 3, cy - 3, cx + 3, cy + 3,
                                             fill=color, outline="#7b8cad", width=1)
            except Exception:
                continue

        if cur_delivered > self.prev_delivered:
            disappeared = self.prev_orders - current_orders
            for ox, oy in disappeared:
                cx, cy = self.world_to_canvas(ox, oy)
                self._spawn_delivery_particles(cx, cy)
                self.pulse_effects.append((ox, oy, current_time, "delivered"))

        self.prev_orders = current_orders

        for item in couriers:
            try:
                x, y = float(item[0]), float(item[1])
                cx, cy = self.world_to_canvas(x, y)

                glow_color = blend_color("#00f0ff", 0.15)
                self.canvas.create_oval(cx - 9, cy - 9, cx + 9, cy + 9,
                                        fill="", outline=glow_color, width=1)
                self.canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                                        fill="#00f0ff", outline="#0099aa", width=1)
                self.canvas.create_oval(cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5,
                                        fill="#ffffff", outline="")
            except Exception:
                continue

        self._draw_pulse_effects(current_time)
        self._update_and_draw_particles()
        self._draw_hud_overlay()

    def _draw_scanlines(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        scanline_color = blend_color("#ffffff", 0.02)
        for y in range(self._scanline_offset, h, 4):
            self.canvas.create_line(0, y, w, y, fill=scanline_color, width=1)

    def _draw_hud_overlay(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        c = COLORS["accent_cyan"]
        blen = 20
        self.canvas.create_line(5, 5, 5 + blen, 5, fill=c, width=1)
        self.canvas.create_line(5, 5, 5, 5 + blen, fill=c, width=1)
        self.canvas.create_line(w - 5, 5, w - 5 - blen, 5, fill=c, width=1)
        self.canvas.create_line(w - 5, 5, w - 5, 5 + blen, fill=c, width=1)
        self.canvas.create_line(5, h - 5, 5 + blen, h - 5, fill=c, width=1)
        self.canvas.create_line(5, h - 5, 5, h - 5 - blen, fill=c, width=1)
        self.canvas.create_line(w - 5, h - 5, w - 5 - blen, h - 5, fill=c, width=1)
        self.canvas.create_line(w - 5, h - 5, w - 5, h - 5 - blen, fill=c, width=1)

        self.canvas.create_text(10, h - 10, text=f"T:{self.tick:06d}",
                                anchor="sw", fill=COLORS["text_muted"],
                                font=("Consolas", 7))
        if self.running:
            self.canvas.create_text(w - 10, h - 10, text="● LIVE",
                                    anchor="se", fill=COLORS["accent_green"],
                                    font=("Consolas", 7, "bold"))
        else:
            self.canvas.create_text(w - 10, h - 10, text="■ OFFLINE",
                                    anchor="se", fill=COLORS["accent_red"],
                                    font=("Consolas", 7, "bold"))

    def _draw_districts(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        res_color = blend_color(DISTRICTS["residential"]["color"],
                                DISTRICTS["residential"]["alpha"])
        self.canvas.create_rectangle(0, 0, w, h, fill=res_color, outline="")
        ind_x1, ind_y1 = self.world_to_canvas(-33, 33)
        ind_x2, ind_y2 = self.world_to_canvas(-10, -33)
        ind_color = blend_color(DISTRICTS["industrial"]["color"],
                                DISTRICTS["industrial"]["alpha"])
        self.canvas.create_rectangle(ind_x1, ind_y1, ind_x2, ind_y2,
                                     fill=ind_color, outline="")
        cen_x1, cen_y1 = self.world_to_canvas(-5, 5)
        cen_x2, cen_y2 = self.world_to_canvas(5, -5)
        cen_color = blend_color(DISTRICTS["center"]["color"],
                                DISTRICTS["center"]["alpha"])
        self.canvas.create_rectangle(cen_x1, cen_y1, cen_x2, cen_y2,
                                     fill=cen_color, outline="")

    def _draw_district_borders(self):
        bx1, by1 = self.world_to_canvas(-10, 33)
        bx2, by2 = self.world_to_canvas(-10, -33)
        border_color = blend_color(DISTRICTS["industrial"]["color"], 0.25)
        self.canvas.create_line(bx1, by1, bx2, by2, fill=border_color,
                                width=1, dash=(6, 3))

        cx1, cy1 = self.world_to_canvas(-5, 5)
        cx2, cy2 = self.world_to_canvas(5, -5)
        center_border = blend_color(DISTRICTS["center"]["color"], 0.3)
        self.canvas.create_rectangle(cx1, cy1, cx2, cy2, fill="",
                                     outline=center_border, width=1, dash=(6, 3))

        lx, ly = self.world_to_canvas(-22, 28)
        self.canvas.create_text(lx, ly, text="// INDUSTRIAL",
                                fill=blend_color(DISTRICTS["industrial"]["color"], 0.4),
                                font=("Consolas", 8, "bold"))
        cx, cy = self.world_to_canvas(0, 8)
        self.canvas.create_text(cx, cy, text="// CENTER",
                                fill=blend_color(DISTRICTS["center"]["color"], 0.4),
                                font=("Consolas", 8, "bold"))
        rx, ry = self.world_to_canvas(18, 28)
        self.canvas.create_text(rx, ry, text="// RESIDENTIAL",
                                fill=blend_color(DISTRICTS["residential"]["color"], 0.4),
                                font=("Consolas", 8, "bold"))

    def _draw_pulse_effects(self, current_time):
        alive = []
        for wx, wy, start_time, etype in self.pulse_effects:
            elapsed = current_time - start_time
            cx, cy = self.world_to_canvas(wx, wy)
            if etype == "new_order":
                if elapsed > 1.0:
                    continue
                progress = elapsed / 1.0
                radius = 5 + 20 * progress
                alpha = 1 - progress
                self.canvas.create_oval(cx - radius, cy - radius,
                    cx + radius, cy + radius,
                    outline=blend_color("#00d4ff", alpha),
                    width=max(1, int(2 * alpha)))
                alive.append((wx, wy, start_time, etype))
            elif etype == "delivered":
                if elapsed > 0.8:
                    continue
                progress = elapsed / 0.8
                radius = 3 + 25 * progress
                alpha = 1 - progress
                self.canvas.create_oval(cx - radius, cy - radius,
                    cx + radius, cy + radius,
                    outline=blend_color("#39ff14", alpha),
                    width=max(1, int(3 * alpha)))
                if elapsed < 0.5:
                    self.canvas.create_text(cx, cy - radius - 5, text="✓",
                        fill="#39ff14",
                        font=("Consolas", max(8, int(12 * (1 - progress))),
                              "bold"))
                alive.append((wx, wy, start_time, etype))
        self.pulse_effects = alive

    def _spawn_delivery_particles(self, cx, cy):
        colors = ["#39ff14", "#00f0ff", "#fcee09", "#ffffff", "#bd00ff"]
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            self.delivery_particles.append({
                "x": cx, "y": cy,
                "dx": math.cos(angle) * speed,
                "dy": math.sin(angle) * speed,
                "life": 1.0, "decay": random.uniform(0.02, 0.05),
                "size": random.uniform(1.5, 3.5),
                "color": random.choice(colors),
            })

    def _update_and_draw_particles(self):
        alive = []
        for p in self.delivery_particles:
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            p["dy"] += 0.1
            p["life"] -= p["decay"]
            if p["life"] <= 0:
                continue
            size = p["size"] * p["life"]
            self.canvas.create_oval(p["x"] - size, p["y"] - size,
                p["x"] + size, p["y"] + size,
                fill=blend_color(p["color"], p["life"]), outline="")
            alive.append(p)
        self.delivery_particles = alive

    def update_plot(self):
        for ax, fig, cw, ydata, color, title in [
            (self.ax1, self.fig1, self.canvas1, self.delivered_data,
             COLORS["chart_line_1"], "// DELIVERED"),
            (self.ax2, self.fig2, self.canvas2, self.wait_data,
             COLORS["chart_line_2"], "// AVG_WAIT"),
            (self.ax3, self.fig3, self.canvas3, self.queue_data,
             COLORS["chart_line_3"], "// QUEUE"),
            (self.ax4, self.fig4, self.canvas4, self.efficiency_data,
             COLORS["chart_line_4"], "// EFFICIENCY"),
        ]:
            ax.clear()
            if self.time_data:
                ax.plot(self.time_data, ydata, color=color, linewidth=5,
                        alpha=0.15)
                ax.plot(self.time_data, ydata, color=color, linewidth=2,
                        alpha=0.9)
                ax.fill_between(self.time_data, ydata, alpha=0.08, color=color)
            ax.set_title(title, fontsize=9, color=color,
                        pad=6, loc='left', fontweight='bold',
                        fontfamily='Consolas')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(COLORS["chart_grid"])
            ax.spines['bottom'].set_color(COLORS["chart_grid"])
            ax.tick_params(colors=COLORS["text_muted"], labelsize=7)
            ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=5))
            ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
            ax.grid(True, alpha=0.1, color=COLORS["text_muted"], linestyle=':')
            ax.set_facecolor(COLORS["chart_bg"])
            fig.patch.set_facecolor(COLORS["chart_bg"])
            fig.tight_layout(pad=1.5)
            cw.draw()

    def world_to_canvas(self, x, y):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        scale = min(w, h) / 60
        return w / 2 + x * scale, h / 2 - y * scale