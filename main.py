# -*- coding: utf-8 -*-
"""
🌿 My Wellness - تطبيق جوال (Android)
مبني بـ Kivy + KivyMD
"""

import json
import os
from datetime import date, datetime, timedelta

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.scrollview import ScrollView

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDCheckbox, MDSwitch
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar

try:
    from plyer import notification as android_notification
except Exception:
    android_notification = None

# ================= الألوان =================
ACCENT = (74 / 255, 124 / 255, 89 / 255, 1) # #4a7c59
ACCENT2 = (106 / 255, 171 / 255, 125 / 255, 1) # #6aab7d
SOFT = (232 / 255, 245 / 255, 233 / 255, 1) # #e8f5e9
BG = (245 / 255, 245 / 255, 240 / 255, 1) # #f5f5f0
CARD = (1, 1, 1, 1)
TEXT = (45 / 255, 74 / 255, 53 / 255, 1)
SUBTEXT = (106 / 255, 143 / 255, 114 / 255, 1)

MOODS = [
    ("😊", "Happy"), ("😌", "Calm"), ("😔", "Sad"), ("😤", "Stressed"),
    ("😴", "Tired"), ("🥰", "Grateful"), ("😰", "Anxious"), ("⚡", "Energetic"),
]

REMINDERS_LIST = [
    ("☀️ Morning Routine", "08:00"),
    ("💊 Vitamins", "09:00"),
    ("💧 Water 1", "11:00"),
    ("💧 Water 2", "14:00"),
    ("💧 Water 3", "17:00"),
    ("🌙 Night Routine", "21:00"),
    ("📔 Mood Journal", "22:00"),
]


def today_str():
    return str(date.today())


# ================= إدارة البيانات =================
class Store:
    """يخزن كل بيانات المستخدم في ملف JSON داخل مجلد بيانات التطبيق."""

    def __init__(self, app_dir):
        self.data_file = os.path.join(app_dir, "wellness_data.json")
        self.user_file = os.path.join(app_dir, "user_data.json")
        self.data = self._load(self.data_file, {})
        self._ensure_defaults()

    def _load(self, path, default):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return default
        return default

    def save(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def _ensure_defaults(self):
        d = self.data
        d.setdefault("custom_vitamins", ["Vitamin D ☀️", "Magnesium 🪙"])
        d.setdefault("custom_morning", ["Cleanser 🧴", "Moisturizer ✨", "Sunscreen ☀️", "Face Massage 🤍"])
        d.setdefault("custom_night", ["Face Wash 🫧", "Serum 💎", "Night Cream 🌙", "Brush Hair 🪮", "Hair Oil 💆"])
        d.setdefault("water", {})
        d.setdefault("vitamins", {})
        d.setdefault("routine", {})
        d.setdefault("mood", {})
        d.setdefault("cycle", {"last_period": None, "cycle_length": 28})
        d.setdefault("reminders", {})
        for name, t in REMINDERS_LIST:
            d["reminders"].setdefault(name, {"enabled": True, "time": t})
        self.save()

    # ---------- اسم المستخدم ----------
    def get_user_name(self):
        info = self._load(self.user_file, {})
        return info.get("name")

    def save_user_name(self, name):
        with open(self.user_file, "w", encoding="utf-8") as f:
            json.dump({"name": name}, f, ensure_ascii=False)


def get_greeting(store):
    hour = datetime.now().hour
    name = store.get_user_name()
    display_name = f", {name}!" if name else "!"
    if hour < 12:
        return f"☀️ Good Morning{display_name}"
    elif 12 <= hour < 18:
        return f"🌤️ Good Afternoon{display_name}"
    else:
        return f"🌙 Good Evening{display_name}"


# ================= عناصر مساعدة =================
def make_card(**kwargs):
    return MDCard(
        orientation="vertical",
        padding=dp(12),
        spacing=dp(6),
        size_hint_y=None,
        radius=[14, 14, 14, 14],
        md_bg_color=CARD,
        line_color=(0.8, 0.9, 0.8, 1),
        **kwargs,
    )


def section_title(text):
    lbl = MDLabel(
        text=text, bold=True, theme_text_color="Custom",
        text_color=ACCENT, font_style="Subtitle1",
        size_hint_y=None, height=dp(30),
    )
    return lbl


def green_button(text, on_release, width=None):
    btn = MDRaisedButton(
        text=text, md_bg_color=ACCENT, text_color=(1, 1, 1, 1),
    )
    if width:
        btn.size_hint_x = None
        btn.width = width
    btn.bind(on_release=on_release)
    return btn


class AutoHeightBox(MDBoxLayout):
    """صندوق عمودي يضبط ارتفاعه تلقائيًا حسب المحتوى."""
    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("spacing", dp(8))
        super().__init__(**kwargs)
        self.bind(minimum_height=self.setter("height"))


# ================= التطبيق =================
class WellnessApp(MDApp):
    def build(self):
        self.title = "My Wellness"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        Window.clearcolor = BG

        self.store = Store(self.user_data_dir)

        self.sm = ScreenManager(transition=FadeTransition())
        self.welcome_screen = self.build_welcome_screen()
        self.main_screen = self.build_main_screen()
        self.sm.add_widget(self.welcome_screen)
        self.sm.add_widget(self.main_screen)

        if self.store.get_user_name():
            self.sm.current = "main"
            Clock.schedule_once(lambda dt: self.refresh_home(), 0.2)
        else:
            self.sm.current = "welcome"

        # فحص التذكيرات كل 30 ثانية أثناء فتح التطبيق
        Clock.schedule_interval(self.check_reminders, 30)
        return self.sm

    # ---------------- شاشة الترحيب ----------------
    def build_welcome_screen(self):
        screen = Screen(name="welcome")
        layout = MDBoxLayout(
            orientation="vertical", padding=dp(30), spacing=dp(14),
        )
        layout.add_widget(MDLabel(text="🌿", font_style="H2", halign="center",
                                   size_hint_y=None, height=dp(90)))
        layout.add_widget(MDLabel(text="Welcome to My Wellness", font_style="H5",
                                   halign="center", theme_text_color="Custom",
                                   text_color=TEXT, size_hint_y=None, height=dp(40)))
        layout.add_widget(MDLabel(text="Your personal health & self-care companion.",
                                   halign="center", theme_text_color="Custom",
                                   text_color=SUBTEXT, size_hint_y=None, height=dp(30)))

        spacer = MDBoxLayout(size_hint_y=1)
        layout.add_widget(spacer)

        self.name_field = MDTextField(hint_text="Enter your name...", size_hint_x=1)
        layout.add_widget(self.name_field)

        self.welcome_error = MDLabel(text="", theme_text_color="Custom",
                                      text_color=(0.8, 0.1, 0.1, 1),
                                      size_hint_y=None, height=dp(20), halign="center")
        layout.add_widget(self.welcome_error)

        start_btn = green_button("Get Started ✨", self.submit_name)
        layout.add_widget(start_btn)

        spacer2 = MDBoxLayout(size_hint_y=1)
        layout.add_widget(spacer2)

        screen.add_widget(layout)
        return screen

    def submit_name(self, *_):
        name = self.name_field.text.strip()
        if not name:
            self.welcome_error.text = "Please enter a valid name! ⚠️"
            return
        self.store.save_user_name(name)
        self.sm.current = "main"
        self.refresh_home()

    # ---------------- الشاشة الرئيسية (Bottom Navigation) ----------------
    def build_main_screen(self):
        screen = Screen(name="main")
        root = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(title="🌿 My Wellness", elevation=2,
                               md_bg_color=ACCENT, specific_text_color=(1, 1, 1, 1))
        root.add_widget(toolbar)

        nav = MDBottomNavigation()

        tab_home = MDBottomNavigationItem(name="home", text="Home", icon="home")
        self.home_content = MDBoxLayout(orientation="vertical")
        tab_home.add_widget(self.home_content)
        nav.add_widget(tab_home)

        tab_water = MDBottomNavigationItem(name="water", text="Water", icon="cup-water")
        self.water_content = MDBoxLayout(orientation="vertical")
        tab_water.add_widget(self.water_content)
        nav.add_widget(tab_water)

        tab_routine = MDBottomNavigationItem(name="routine", text="Routine", icon="weather-night")
        self.routine_content = MDBoxLayout(orientation="vertical")
        tab_routine.add_widget(self.routine_content)
        nav.add_widget(tab_routine)

        tab_cycle = MDBottomNavigationItem(name="cycle", text="Cycle", icon="flower")
        self.cycle_content = MDBoxLayout(orientation="vertical")
        tab_cycle.add_widget(self.cycle_content)
        nav.add_widget(tab_cycle)

        tab_mood = MDBottomNavigationItem(name="mood", text="Mood", icon="notebook")
        self.mood_content = MDBoxLayout(orientation="vertical")
        tab_mood.add_widget(self.mood_content)
        nav.add_widget(tab_mood)

        tab_stats = MDBottomNavigationItem(name="stats", text="Stats", icon="chart-bar")
        self.stats_content = MDBoxLayout(orientation="vertical")
        tab_stats.add_widget(self.stats_content)
        nav.add_widget(tab_stats)

        tab_rem = MDBottomNavigationItem(name="reminders", text="Alerts", icon="bell")
        self.reminders_content = MDBoxLayout(orientation="vertical")
        tab_rem.add_widget(self.reminders_content)
        nav.add_widget(tab_rem)

        self.nav = nav
        nav.bind(current=self.on_tab_switch)

        root.add_widget(nav)
        screen.add_widget(root)

        self.build_home_tab()
        self.build_water_tab()
        self.build_routine_tab()
        self.build_cycle_tab()
        self.build_mood_tab()
        self.build_stats_tab()
        self.build_reminders_tab()

        return screen

    def on_tab_switch(self, instance, value):
        if value == "home":
            self.refresh_home()
        elif value == "stats":
            self.refresh_stats()

    # يتم استكمال باقي دوال بناء التبويبات في ملف tabs.py ويتم دمجها هنا
    from tabs import (
        build_home_tab, refresh_home,
        build_water_tab, refresh_water,
        build_routine_tab, refresh_routine,
        build_cycle_tab, refresh_cycle, open_date_picker, on_date_selected, save_cycle_length,
        build_mood_tab, select_mood, save_mood_note,
        build_stats_tab, refresh_stats,
        build_reminders_tab, save_reminder_time,
        check_reminders,
    )


if __name__ == "__main__":
    WellnessApp().run()

