# -*- coding: utf-8 -*-
"""
دوال بناء التبويبات (تُستورد داخل main.py وتُدمج في WellnessApp)
كل دالة تأخذ self لأنها تصبح method في الكلاس.
"""

from datetime import date, datetime, timedelta

from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox, MDSwitch
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar

# نستورد الأدوات المساعدة والألوان من main دون استيراد دائري وقت التحميل
import main as m


def today_str():
    return str(date.today())


# ============================================================
# 🏠 الرئيسية
# ============================================================
def build_home_tab(self):
    scroll = ScrollView()
    box = m.AutoHeightBox(padding=dp(14), spacing=dp(10))

    self.greeting_label = MDLabel(
        text=m.get_greeting(self.store), font_style="H6", bold=True,
        theme_text_color="Custom", text_color=m.TEXT,
        size_hint_y=None, height=dp(34),
    )
    box.add_widget(self.greeting_label)

    box.add_widget(MDLabel(
        text=date.today().strftime("%A, %B %d"),
        theme_text_color="Custom", text_color=m.SUBTEXT,
        size_hint_y=None, height=dp(22),
    ))

    self.home_cards = {}
    for key, icon, title in [
        ("water", "💧", "Water"), ("vitamins", "💊", "Vitamins"),
        ("routine", "🌙", "Routine"), ("mood", "📔", "Mood"),
        ("cycle", "🌸", "Cycle"),
    ]:
        card = m.make_card(height=dp(70), orientation="horizontal")
        card.add_widget(MDLabel(text=icon, font_style="H5", size_hint_x=None, width=dp(50)))
        inner = m.AutoHeightBox(spacing=dp(2))
        inner.add_widget(MDLabel(text=title, bold=True, theme_text_color="Custom",
                                  text_color=m.TEXT, size_hint_y=None, height=dp(20)))
        val_lbl = MDLabel(text="", theme_text_color="Custom", text_color=m.SUBTEXT,
                           size_hint_y=None, height=dp(20))
        inner.add_widget(val_lbl)
        card.add_widget(inner)
        box.add_widget(card)
        self.home_cards[key] = val_lbl

    self.tip_label = MDLabel(text="", theme_text_color="Custom", text_color=m.ACCENT,
                              size_hint_y=None, height=dp(50))
    tip_card = m.make_card(height=dp(60))
    tip_card.add_widget(self.tip_label)
    box.add_widget(tip_card)

    scroll.add_widget(box)
    self.home_content.add_widget(scroll)


def refresh_home(self):
    d = self.store.data
    today = today_str()
    self.greeting_label.text = m.get_greeting(self.store)

    water_count = d.get("water", {}).get(today, 0)
    self.home_cards["water"].text = f"{water_count} / 8 glasses"

    vit_list = d.get("custom_vitamins", [])
    vit_done = sum(1 for v in vit_list if d.get("vitamins", {}).get(today, {}).get(v, False))
    self.home_cards["vitamins"].text = f"{vit_done} / {len(vit_list)} taken"

    r_list = d.get("custom_morning", []) + d.get("custom_night", [])
    routine_done = sum(
        1 for step in r_list
        if d.get("routine", {}).get(today, {}).get(f"morning_{step}", False)
        or d.get("routine", {}).get(today, {}).get(f"night_{step}", False)
    )
    self.home_cards["routine"].text = f"{routine_done} steps done"

    self.home_cards["mood"].text = d.get("mood", {}).get(today, {}).get("emoji", "—")

    lp = d.get("cycle", {}).get("last_period")
    if lp:
        cl = d["cycle"].get("cycle_length", 28)
        days_left = (datetime.strptime(lp, "%Y-%m-%d") + timedelta(days=cl) - datetime.today()).days
        cycle_txt = f"Next period in {days_left} days" if days_left >= 0 else "Period may have started"
    else:
        cycle_txt = "Set your cycle date"
    self.home_cards["cycle"].text = cycle_txt

    hour = datetime.now().hour
    tip = ("💡 Don't forget your morning routine! ☀️" if hour < 12 else
           ("💡 Stay hydrated! 💧" if hour < 17 else "💡 Time for your night routine! 🌙"))
    self.tip_label.text = tip


# ============================================================
# 💧 المياه والفيتامينات
# ============================================================
def build_water_tab(self):
    scroll = ScrollView()
    self.water_box = m.AutoHeightBox(padding=dp(14), spacing=dp(10))
    scroll.add_widget(self.water_box)
    self.water_content.add_widget(scroll)
    refresh_water(self)


def refresh_water(self):
    self.water_box.clear_widgets()
    d = self.store.data
    today = today_str()
    d.setdefault("water", {}).setdefault(today, 0)
    d.setdefault("vitamins", {}).setdefault(today, {})

    self.water_box.add_widget(m.section_title("💧 Water Tracker"))

    w_card = m.make_card(height=dp(160))
    count = d["water"][today]
    self.water_count_label = MDLabel(text=f"{count} / 8", font_style="H4", bold=True,
                                      halign="center", theme_text_color="Custom", text_color=m.ACCENT,
                                      size_hint_y=None, height=dp(60))
    w_card.add_widget(self.water_count_label)
    self.water_icons_label = MDLabel(text="💧" * count + "○" * (8 - count), halign="center",
                                      font_style="H6", size_hint_y=None, height=dp(40))
    w_card.add_widget(self.water_icons_label)
    self.water_box.add_widget(w_card)

    btn_row = MDBoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
    btn_row.add_widget(m.green_button("+ Add Glass", lambda *_: add_glass(self)))
    remove_btn = MDFlatButton(text="− Remove", md_bg_color=m.SOFT, text_color=m.ACCENT)
    remove_btn.bind(on_release=lambda *_: remove_glass(self))
    btn_row.add_widget(remove_btn)
    self.water_box.add_widget(btn_row)

    self.water_box.add_widget(m.section_title("💊 Vitamins"))
    vit_card = m.make_card(height=dp(44) * max(1, len(d["custom_vitamins"])))
    self.vit_checks = {}
    for vit in d["custom_vitamins"]:
        row = MDBoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        chk = MDCheckbox(active=d["vitamins"][today].get(vit, False), size_hint_x=None, width=dp(40))
        chk.bind(active=lambda inst, val, name=vit: toggle_vitamin(self, name, val))
        row.add_widget(chk)
        row.add_widget(MDLabel(text=vit, theme_text_color="Custom", text_color=m.TEXT))
        del_btn = MDIconButton(icon="close", theme_text_color="Custom", text_color=(0.8, 0.2, 0.2, 1))
        del_btn.bind(on_release=lambda *_, name=vit: delete_vitamin(self, name))
        row.add_widget(del_btn)
        vit_card.add_widget(row)
    self.water_box.add_widget(vit_card)

    add_row = MDBoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
    self.new_vit_field = MDTextField(hint_text="New vitamin name...")
    add_row.add_widget(self.new_vit_field)
    add_row.add_widget(m.green_button("➕ Add", lambda *_: add_new_vitamin(self), width=dp(90)))
    self.water_box.add_widget(add_row)


def add_glass(self):
    d = self.store.data
    today = today_str()
    if d["water"][today] < 8:
        d["water"][today] += 1
        self.store.save()
        refresh_water(self)


def remove_glass(self):
    d = self.store.data
    today = today_str()
    if d["water"][today] > 0:
        d["water"][today] -= 1
        self.store.save()
        refresh_water(self)


def toggle_vitamin(self, name, value):
    today = today_str()
    self.store.data["vitamins"][today][name] = value
    self.store.save()


def add_new_vitamin(self):
    name = self.new_vit_field.text.strip()
    if name and name not in self.store.data["custom_vitamins"]:
        self.store.data["custom_vitamins"].append(name)
        self.store.save()
        self.new_vit_field.text = ""
        refresh_water(self)


def delete_vitamin(self, name):
    d = self.store.data
    if name in d["custom_vitamins"]:
        d["custom_vitamins"].remove(name)
        today = today_str()
        d.get("vitamins", {}).get(today, {}).pop(name, None)
        self.store.save()
        refresh_water(self)


# ============================================================
# 🌙 الروتين
# ============================================================
def build_routine_tab(self):
    scroll = ScrollView()
    self.routine_box = m.AutoHeightBox(padding=dp(14), spacing=dp(10))
    scroll.add_widget(self.routine_box)
    self.routine_content.add_widget(scroll)
    refresh_routine(self)


def _routine_section(self, container, title, prefix):
    d = self.store.data
    today = today_str()
    steps = d[f"custom_{prefix}"]
    container.add_widget(m.section_title(title))
    card = m.make_card(height=dp(44) * max(1, len(steps)))
    for step in steps:
        key = f"{prefix}_{step}"
        row = MDBoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        saved = d.get("routine", {}).get(today, {}).get(key, False)
        chk = MDCheckbox(active=saved, size_hint_x=None, width=dp(40))
        chk.bind(active=lambda inst, val, k=key: toggle_routine(self, k, val))
        row.add_widget(chk)
        row.add_widget(MDLabel(text=step, theme_text_color="Custom", text_color=m.TEXT))
        del_btn = MDIconButton(icon="close", theme_text_color="Custom", text_color=(0.8, 0.2, 0.2, 1))
        del_btn.bind(on_release=lambda *_, p=prefix, s=step: delete_routine_step(self, p, s))
        row.add_widget(del_btn)
        card.add_widget(row)
    container.add_widget(card)

    add_row = MDBoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
    field = MDTextField(hint_text=f"New step for {title}...")
    add_row.add_widget(field)
    add_row.add_widget(m.green_button("➕", lambda *_, f=field, p=prefix: add_routine_step(self, p, f), width=dp(60)))
    container.add_widget(add_row)


def refresh_routine(self):
    self.routine_box.clear_widgets()
    self.routine_box.add_widget(MDLabel(text="🌙 My Routine", font_style="H6", bold=True,
                                         theme_text_color="Custom", text_color=m.TEXT,
                                         size_hint_y=None, height=dp(34)))
    _routine_section(self, self.routine_box, "☀️ Morning Routine", "morning")
    _routine_section(self, self.routine_box, "🌙 Night Routine", "night")

    is_weekend = datetime.today().weekday() >= 5
    if is_weekend:
        self.routine_box.add_widget(m.section_title("🎉 Weekend Special"))
        card = m.make_card(height=dp(44) * 3)
        d = self.store.data
        today = today_str()
        for step in ["Face Mask 🌿", "Hair Mask 💆", "Deep Conditioning 🪮"]:
            key = f"weekend_{step}"
            row = MDBoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
            saved = d.get("routine", {}).get(today, {}).get(key, False)
            chk = MDCheckbox(active=saved, size_hint_x=None, width=dp(40))
            chk.bind(active=lambda inst, val, k=key: toggle_routine(self, k, val))
            row.add_widget(chk)
            row.add_widget(MDLabel(text=step, theme_text_color="Custom", text_color=m.TEXT))
            card.add_widget(row)
        self.routine_box.add_widget(card)
    else:
        self.routine_box.add_widget(MDLabel(
            text="🎉 Weekend Special unlocks on Saturday!",
            theme_text_color="Custom", text_color=m.SUBTEXT,
            size_hint_y=None, height=dp(30)))


def toggle_routine(self, key, value):
    d = self.store.data
    today = today_str()
    d.setdefault("routine", {}).setdefault(today, {})[key] = value
    self.store.save()


def add_routine_step(self, prefix, field):
    step = field.text.strip()
    if not step:
        return
    list_key = f"custom_{prefix}"
    if step not in self.store.data[list_key]:
        self.store.data[list_key].append(step)
        self.store.save()
        field.text = ""
        refresh_routine(self)


def delete_routine_step(self, prefix, step):
    d = self.store.data
    list_key = f"custom_{prefix}"
    if step in d[list_key]:
        d[list_key].remove(step)
        key = f"{prefix}_{step}"
        today = today_str()
        d.get("routine", {}).get(today, {}).pop(key, None)
        self.store.save()
        refresh_routine(self)


# ============================================================
# 🌸 الدورة الشهرية
# ============================================================
def build_cycle_tab(self):
    scroll = ScrollView()
    self.cycle_box = m.AutoHeightBox(padding=dp(14), spacing=dp(10))
    scroll.add_widget(self.cycle_box)
    self.cycle_content.add_widget(scroll)
    refresh_cycle(self)


def refresh_cycle(self):
    self.cycle_box.clear_widgets()
    d = self.store.data
    d.setdefault("cycle", {"last_period": None, "cycle_length": 28})

    self.cycle_box.add_widget(MDLabel(text="🌸 Cycle Tracker", font_style="H6", bold=True,
                                       theme_text_color="Custom", text_color=m.TEXT,
                                       size_hint_y=None, height=dp(34)))

    info_card = m.make_card(height=dp(150))
    lp = d["cycle"].get("last_period")
    cl = d["cycle"].get("cycle_length", 28)
    next_lbl = MDLabel(text="", halign="center", theme_text_color="Custom",
                        text_color=m.SUBTEXT, size_hint_y=None, height=dp(24))
    days_lbl = MDLabel(text="", halign="center", font_style="H4", bold=True,
                        theme_text_color="Custom", text_color=m.ACCENT,
                        size_hint_y=None, height=dp(50))
    phase_lbl = MDLabel(text="", halign="center", theme_text_color="Custom",
                         text_color=m.SUBTEXT, size_hint_y=None, height=dp(24))

    if lp:
        try:
            last = datetime.strptime(lp, "%Y-%m-%d")
            next_p = last + timedelta(days=cl)
            days_left = (next_p - datetime.today()).days
            if days_left < 0:
                next_lbl.text = "⚠️ Period may have started"
            elif days_left == 0:
                next_lbl.text = "🌸 Period expected today!"
            else:
                next_lbl.text = "Next period in"
                days_lbl.text = f"{days_left} days"
            days_since = (datetime.today() - last).days % cl
            phase = ("🩸 Menstrual — Rest" if days_since < 5 else
                     "🌱 Follicular — Energy rising!" if days_since < 13 else
                     "✨ Ovulation — Peak energy!" if days_since < 16 else
                     "🌙 Luteal — Take it slow")
            phase_lbl.text = phase
        except Exception:
            pass
    else:
        next_lbl.text = "Select your last period date 👇"

    info_card.add_widget(next_lbl)
    info_card.add_widget(days_lbl)
    info_card.add_widget(phase_lbl)
    self.cycle_box.add_widget(info_card)

    len_row = MDBoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
    len_row.add_widget(MDLabel(text="Cycle length:", theme_text_color="Custom",
                                text_color=m.SUBTEXT, size_hint_x=None, width=dp(110)))
    self.cycle_length_field = MDTextField(text=str(cl), input_filter="int", size_hint_x=None, width=dp(70))
    len_row.add_widget(self.cycle_length_field)
    len_row.add_widget(m.green_button("Save", lambda *_: save_cycle_length(self), width=dp(90)))
    self.cycle_box.add_widget(len_row)

    self.cycle_box.add_widget(MDLabel(text="📅 Last period start:", theme_text_color="Custom",
                                       text_color=m.SUBTEXT, size_hint_y=None, height=dp(24)))
    date_row = MDBoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
    current_date_txt = lp if lp else "Not set"
    self.cycle_date_label = MDLabel(text=current_date_txt, theme_text_color="Custom", text_color=m.TEXT)
    date_row.add_widget(self.cycle_date_label)
    date_row.add_widget(m.green_button("📅 Pick Date", lambda *_: open_date_picker(self), width=dp(130)))
    self.cycle_box.add_widget(date_row)


def open_date_picker(self):
    picker = MDDatePicker()
    picker.bind(on_save=on_date_selected)
    picker.open()
    self._active_picker_owner = self # مرجع مؤقت


def on_date_selected(instance, value, date_range):
    app = m.MDApp.get_running_app()
    app.store.data.setdefault("cycle", {})["last_period"] = value.strftime("%Y-%m-%d")
    app.store.save()
    refresh_cycle(app)
    refresh_home(app)


def save_cycle_length(self):
    try:
        val = int(self.cycle_length_field.text)
        if val > 0:
            self.store.data["cycle"]["cycle_length"] = val
            self.store.save()
            refresh_cycle(self)
    except (ValueError, TypeError):
        pass


# ============================================================
# 📔 المزاج
# ============================================================
def build_mood_tab(self):
    scroll = ScrollView()
    box = m.AutoHeightBox(padding=dp(14), spacing=dp(10))

    box.add_widget(MDLabel(text="📔 Mood Journal", font_style="H6", bold=True,
                            theme_text_color="Custom", text_color=m.TEXT,
                            size_hint_y=None, height=dp(34)))
    box.add_widget(MDLabel(text="How are you feeling today?", theme_text_color="Custom",
                            text_color=m.SUBTEXT, size_hint_y=None, height=dp(24)))

    d = self.store.data
    today = today_str()
    d.setdefault("mood", {}).setdefault(today, {"emoji": "", "note": ""})
    saved_emoji = d["mood"][today].get("emoji", "")

    self.mood_display = MDLabel(text=saved_emoji, halign="center", font_style="H3",
                                 size_hint_y=None, height=dp(70))
    box.add_widget(self.mood_display)
    saved_name = next((n for e, n in m.MOODS if e == saved_emoji), "")
    self.mood_name_label = MDLabel(text=saved_name, halign="center", bold=True,
                                    theme_text_color="Custom", text_color=m.ACCENT,
                                    size_hint_y=None, height=dp(24))
    box.add_widget(self.mood_name_label)

    grid = MDGridLayout(cols=4, spacing=dp(8), size_hint_y=None, height=dp(110))
    for emoji, name in m.MOODS:
        btn = MDFlatButton(text=emoji, md_bg_color=m.SOFT, font_size="22sp")
        btn.bind(on_release=lambda *_, e=emoji, n=name: select_mood(self, e, n))
        grid.add_widget(btn)
    box.add_widget(grid)

    box.add_widget(m.section_title("📝 Today's note"))
    self.note_field = MDTextField(multiline=True, text=d["mood"][today].get("note", ""),
                                   size_hint_y=None, height=dp(100))
    box.add_widget(self.note_field)

    box.add_widget(m.green_button("💾 Save Note", lambda *_: save_mood_note(self)))

    scroll.add_widget(box)
    self.mood_content.add_widget(scroll)


def select_mood(self, emoji, name):
    today = today_str()
    self.store.data["mood"][today]["emoji"] = emoji
    self.store.save()
    self.mood_display.text = emoji
    self.mood_name_label.text = name


def save_mood_note(self):
    today = today_str()
    self.store.data["mood"][today]["note"] = self.note_field.text.strip()
    self.store.save()
    Snackbar(text="✅ Saved!").open()


# ============================================================
# 📊 الإحصائيات (رسم بسيط بدون matplotlib لتسهيل بناء أندرويد)
# ============================================================
def build_stats_tab(self):
    scroll = ScrollView()
    self.stats_box = m.AutoHeightBox(padding=dp(14), spacing=dp(10))
    scroll.add_widget(self.stats_box)
    self.stats_content.add_widget(scroll)


def refresh_stats(self):
    self.stats_box.clear_widgets()
    d = self.store.data
    self.stats_box.add_widget(MDLabel(text="📊 My Stats", font_style="H6", bold=True,
                                       theme_text_color="Custom", text_color=m.TEXT,
                                       size_hint_y=None, height=dp(34)))

    mood_map = {"😊": 8, "🥰": 9, "⚡": 7, "😌": 6, "😴": 4, "😔": 3, "😰": 2, "😤": 2, "": 0}
    days_labels, mood_values, water_values = [], [], []
    for i in range(6, -1, -1):
        dd = str(date.today() - timedelta(days=i))
        day = (date.today() - timedelta(days=i)).strftime("%a")
        days_labels.append(day)
        mood_values.append(mood_map.get(d.get("mood", {}).get(dd, {}).get("emoji", ""), 0))
        water_values.append(d.get("water", {}).get(dd, 0))

    self.stats_box.add_widget(m.section_title("💧 Water This Week"))
    self.stats_box.add_widget(_simple_bar_chart(days_labels, water_values, 8, m.ACCENT2))

    self.stats_box.add_widget(m.section_title("📔 Mood This Week (0-10)"))
    self.stats_box.add_widget(_simple_bar_chart(days_labels, mood_values, 10, m.ACCENT))

    total = sum(water_values)
    summary = m.make_card(height=dp(110))
    for t in [f"💧 Total water: {total} glasses",
              f"📊 Daily average: {total / 7:.1f} glasses",
              f"🎯 Days goal reached: {sum(1 for v in water_values if v >= 8)} / 7"]:
        summary.add_widget(MDLabel(text=t, theme_text_color="Custom", text_color=m.TEXT,
                                    size_hint_y=None, height=dp(28)))
    self.stats_box.add_widget(m.section_title("🏆 Weekly Summary"))
    self.stats_box.add_widget(summary)


def _simple_bar_chart(labels, values, max_val, color):
    """رسم أعمدة بسيط باستخدام عناصر KivyMD (بدون matplotlib) - أخف للبناء على أندرويد."""
    row = MDBoxLayout(size_hint_y=None, height=dp(120), spacing=dp(6), padding=(dp(4), 0))
    for label, val in zip(labels, values):
        col = m.AutoHeightBox(size_hint_x=1, spacing=dp(2))
        bar_wrap = MDBoxLayout(size_hint_y=None, height=dp(80))
        filled_ratio = min(1.0, val / max_val) if max_val else 0
        filler = MDBoxLayout(size_hint_y=None)
        filler.height = dp(80) * filled_ratio
        bar = MDBoxLayout(md_bg_color=color, size_hint_y=None)
        bar.height = dp(80) * filled_ratio
        spacer_top = MDBoxLayout(size_hint_y=None, height=dp(80) * (1 - filled_ratio))
        bar_col = m.AutoHeightBox(height=dp(80))
        bar_col.add_widget(spacer_top)
        from kivymd.uix.card import MDCard
        bar_visual = MDCard(md_bg_color=color, size_hint_y=None,
                             height=max(dp(4), dp(80) * filled_ratio), radius=[4, 4, 0, 0])
        bar_col.add_widget(bar_visual)
        col.add_widget(bar_col)
        col.add_widget(MDLabel(text=str(val), halign="center", font_size="11sp",
                                size_hint_y=None, height=dp(16)))
        col.add_widget(MDLabel(text=label, halign="center", font_size="11sp",
                                theme_text_color="Custom", text_color=m.SUBTEXT,
                                size_hint_y=None, height=dp(16)))
        row.add_widget(col)
    return row


# ============================================================
# 🔔 التذكيرات
# ============================================================
def build_reminders_tab(self):
    scroll = ScrollView()
    box = m.AutoHeightBox(padding=dp(14), spacing=dp(10))
    box.add_widget(MDLabel(text="🔔 Reminders", font_style="H6", bold=True,
                            theme_text_color="Custom", text_color=m.TEXT,
                            size_hint_y=None, height=dp(34)))
    box.add_widget(MDLabel(
        text="Reminders trigger while the app is open. For background alerts "
             "after closing the app, extra Android setup is required.",
        theme_text_color="Custom", text_color=m.SUBTEXT,
        size_hint_y=None, height=dp(40)))

    self.reminder_time_fields = {}
    for name, default_time in m.REMINDERS_LIST:
        saved = self.store.data["reminders"][name]
        card = m.make_card(height=dp(90))
        top = MDBoxLayout(size_hint_y=None, height=dp(30))
        top.add_widget(MDLabel(text=name, bold=True, theme_text_color="Custom", text_color=m.TEXT))
        switch = MDSwitch(active=saved.get("enabled", True))
        switch.bind(active=lambda inst, val, n=name: toggle_reminder(self, n, val))
        top.add_widget(switch)
        card.add_widget(top)

        bot = MDBoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        t = saved.get("time", default_time).split(":")
        h_field = MDTextField(text=t[0], input_filter="int", size_hint_x=None, width=dp(50))
        m_field = MDTextField(text=t[1], input_filter="int", size_hint_x=None, width=dp(50))
        self.reminder_time_fields[name] = (h_field, m_field)
        bot.add_widget(h_field)
        bot.add_widget(MDLabel(text=":", size_hint_x=None, width=dp(10)))
        bot.add_widget(m_field)
        bot.add_widget(m.green_button("Save", lambda *_, n=name: save_reminder_time(self, n), width=dp(80)))
        card.add_widget(bot)
        box.add_widget(card)

    scroll.add_widget(box)
    self.reminders_content.add_widget(scroll)


def toggle_reminder(self, name, value):
    self.store.data["reminders"][name]["enabled"] = value
    self.store.save()


def save_reminder_time(self, name):
    h_field, m_field = self.reminder_time_fields[name]
    try:
        h = h_field.text.strip().zfill(2)
        mi = m_field.text.strip().zfill(2)
        if 0 <= int(h) <= 23 and 0 <= int(mi) <= 59:
            self.store.data["reminders"][name]["time"] = f"{h}:{mi}"
            self.store.save()
            Snackbar(text=f"✅ {name} time saved").open()
    except ValueError:
        pass


def check_reminders(self, dt):
    """يفحص كل 30 ثانية إذا حان وقت أحد التذكيرات (أثناء فتح التطبيق فقط)."""
    now = datetime.now().strftime("%H:%M")
    for name, info in self.store.data.get("reminders", {}).items():
        if info.get("enabled") and info.get("time") == now:
            last_fired = info.get("_last_fired")
            today = today_str()
            if last_fired != today:
                info["_last_fired"] = today
                self.store.save()
                if m.android_notification:
                    try:
                        m.android_notification.notify(title=f"🌿 {name}", message=f"Time for: {name}!", timeout=5)
                    except Exception:
                        pass
                Snackbar(text=f"🔔 {name}").open()

