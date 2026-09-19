import os
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp

START_INDEX = 3
END_INDEX = 768

# ---- تحديد المسار الصحيح ----
def find_base_dir():
    candidates = [
        os.path.dirname(os.path.abspath(__file__)),
        os.getcwd(),
        "/storage/emulated/0/Download/EEGnosis",
        "/storage/emulated/0/Android/data/ru.iiec.pydroid3/files",
    ]
    for c in candidates:
        if os.path.exists(os.path.join(c, "main.py")):
            return c
    return os.path.dirname(os.path.abspath(__file__))

BASE = find_base_dir()
ASSETS = os.path.join(BASE, "assets")

print("=" * 50)
print("BASE DIR:", BASE)
print("ASSETS DIR:", ASSETS)
print("ASSETS EXISTS:", os.path.exists(ASSETS))
if os.path.exists(ASSETS):
    files = os.listdir(ASSETS)
    print(f"FILES COUNT: {len(files)}")
    print("SAMPLE:", files[:5])
print("=" * 50)

SECTIONS = [
    ("ALL", "All Sections"),
    ("Normal and Benign Variants", "1. Normal & Benign"),
    ("Artifacts", "2. Artifacts"),
    ("Newborn", "3. Newborn"),
    ("Focal Nonepileptiform Activity", "4. Focal Nonepileptiform"),
    ("Generalized Nonepileptiform Activity", "5. Generalized Nonepileptiform"),
    ("ICU", "6. ICU"),
    ("Epileptic Encephalopathy", "7. Epileptic Encephalopathy"),
    ("Generalized Epilepsy", "8. Generalized Epilepsy"),
    ("Focal Epilepsy", "9. Focal Epilepsy"),
]


class MainScreen(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", **kw)
        Window.clearcolor = (0.035, 0.05, 0.086, 1)

        self.all_data = self._build_data()
        self.filtered = list(self.all_data)
        self.index = 0
        self.caption_visible = False

        # شريط علوي
        top = BoxLayout(size_hint_y=None, height=dp(52), padding=dp(10), spacing=dp(10))
        top.add_widget(Label(text="EEGnosis Atlas", bold=True,
                             color=(0.95, 0.96, 0.97, 1), font_size=dp(16)))
        self.progress_lbl = Label(text="- / -", color=(0.55, 0.58, 0.62, 1),
                                  font_size=dp(13), size_hint_x=None, width=dp(90))
        top.add_widget(self.progress_lbl)
        self.add_widget(top)

        # الصورة
        self.img = Image(allow_stretch=True, keep_ratio=True)
        self.add_widget(self.img)

        # Spinner الأقسام
        spin_row = BoxLayout(size_hint_y=None, height=dp(46), padding=(dp(10), dp(4)))
        self.spinner = Spinner(
            text=SECTIONS[0][1], values=[s[1] for s in SECTIONS],
            background_color=(0.12, 0.16, 0.22, 1),
            color=(0.9, 0.91, 0.92, 1), font_size=dp(13),
        )
        self.spinner.bind(text=self._on_section)
        spin_row.add_widget(self.spinner)
        self.add_widget(spin_row)

        # صف الأزرار 1
        row1 = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(6), padding=(dp(6), 0))
        self.prev_btn = self._btn("Prev", (0.12, 0.16, 0.22, 1), lambda *_: self.navigate(-1))
        self.cap_btn = self._btn("Caption", (0.145, 0.388, 0.922, 1), lambda *_: self.toggle_caption())
        self.mark_btn = self._btn("Markings", (0.545, 0.361, 0.965, 1), lambda *_: self.toggle_markings())
        row1.add_widget(self.prev_btn)
        row1.add_widget(self.cap_btn)
        row1.add_widget(self.mark_btn)
        self.add_widget(row1)

        # صف الأزرار 2
        row2 = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(6), padding=(dp(6), 0))
        self.rec_btn = self._btn("Recognized", (0.086, 0.639, 0.29, 1), lambda *_: self.recognized())
        self.again_btn = self._btn("Again", (0.851, 0.467, 0.024, 1), lambda *_: self.again())
        self.next_btn = self._btn("Next", (0.12, 0.16, 0.22, 1), lambda *_: self.navigate(1))
        row2.add_widget(self.rec_btn)
        row2.add_widget(self.again_btn)
        row2.add_widget(self.next_btn)
        self.add_widget(row2)

        self.add_widget(BoxLayout(size_hint_y=None, height=dp(8)))
        self.render()

    def _btn(self, text, color, cb):
        b = Button(text=text, background_normal="", background_color=color,
                   font_size=dp(12), bold=True)
        b.bind(on_release=cb)
        return b

    def _build_data(self):
        data = []
        for i in range(START_INDEX, END_INDEX + 1):
            num = f"{i:03d}"
            jpg = os.path.join(ASSETS, f"figure_{num}.jpg")
            data.append({
                "id": i,
                "image": jpg,
                "txt": os.path.join(ASSETS, f"figure_{num}.txt"),
                "section": "General",
            })
        sec_file = os.path.join(ASSETS, "sections.json")
        try:
            with open(sec_file, "r", encoding="utf-8") as f:
                mapping = json.load(f)
            for d in data:
                key = f"figure_{d['id']:03d}"
                if key in mapping:
                    d["section"] = mapping[key]
        except Exception as e:
            print("sections.json not loaded:", e)
        return data

    def _on_section(self, spinner, text):
        code = next((s[0] for s in SECTIONS if s[1] == text), "ALL")
        self.filtered = ([*self.all_data] if code == "ALL"
                         else [d for d in self.all_data if d["section"] == code])
        self.index = 0
        self.render()

    def render(self):
        if not self.filtered:
            self.progress_lbl.text = "0 / 0"
            return
        item = self.filtered[self.index]

        exists = os.path.exists(item["image"])
        print(f"[{self.index+1}/{len(self.filtered)}] {os.path.basename(item['image'])} -> {exists}")

        self.img.source = item["image"]
        self.img.reload()
        self.caption_visible = False
        self.cap_btn.text = "Caption"
        self.progress_lbl.text = f"{self.index + 1} / {len(self.filtered)}"
        self.prev_btn.disabled = self.index == 0
        self.next_btn.disabled = self.index == len(self.filtered) - 1

    def toggle_caption(self):
        if not self.filtered:
            return
        item = self.filtered[self.index]
        if self.caption_visible:
            self.caption_visible = False
            self.cap_btn.text = "Caption"
            return
        try:
            with open(item["txt"], "r", encoding="utf-8") as f:
                text = f.read().strip()
        except Exception:
            text = "No caption file found."

        scroll = ScrollView()
        lbl = Label(text=text, size_hint_y=None, halign="left", valign="top",
                    color=(0.95, 0.96, 0.97, 1), font_size=dp(13),
                    padding=(dp(12), dp(12)))
        lbl.bind(width=lambda *_: setattr(lbl, "text_size", (lbl.width, None)),
                 texture_size=lambda *_: setattr(lbl, "height", lbl.texture_size[1]))
        scroll.add_widget(lbl)

        popup = Popup(title="Caption", content=scroll, size_hint=(0.92, 0.72),
                      background_color=(0.06, 0.09, 0.15, 0.98),
                      title_color=(0.9, 0.91, 0.92, 1),
                      separator_color=(0.16, 0.23, 0.35, 1))
        popup.open()
        self.caption_visible = True
        self.cap_btn.text = "Hide"

    def toggle_markings(self):
        # لا توجد ملفات _marked، لذا نُظهر رسالة
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        p = Popup(title="Markings",
                  content=Label(text="No marked version available\nfor this figure.",
                                color=(0.9, 0.91, 0.92, 1)),
                  size_hint=(0.7, 0.3),
                  background_color=(0.06, 0.09, 0.15, 0.98))
        p.open()

    def recognized(self):
        self.navigate(1)

    def again(self):
        self.navigate(1)

    def navigate(self, step):
        n = self.index + step
        if 0 <= n < len(self.filtered):
            self.index = n
            self.render()


class EEGnosisApp(App):
    def build(self):
        self.title = "EEGnosis Atlas"
        return MainScreen()


if __name__ == "__main__":
    EEGnosisApp().run()