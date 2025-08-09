import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Proje dizininin tam yolu (bu .py dosyasının bulunduğu klasör)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Ayarları config.json’dan yükle
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as cfg:
        SETTINGS = json.load(cfg)
except (FileNotFoundError, json.JSONDecodeError):
    # Eğer config.json dosyası yoksa veya bozuksa varsayılan ayarları kullan
    SETTINGS = {"theme": "light"}


class TurkceKodIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Turkce Kod IDE")
        self.geometry("800x600")
        self.filepath = None
        self._create_widgets()
        self.set_theme(SETTINGS.get("theme", "light"))

    def _create_widgets(self):
        # Menü çubuğu
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Yeni", command=self.new_file)
        file_menu.add_command(label="Aç", command=self.open_file)
        file_menu.add_command(label="Kaydet", command=self.save_file)
        menubar.add_cascade(label="Dosya", menu=file_menu)

        # Tema menüsü
        theme_menu = tk.Menu(menubar, tearoff=0)
        theme_menu.add_command(label="Aydınlık", command=lambda: self.set_theme("light"))
        theme_menu.add_command(label="Koyu",    command=lambda: self.set_theme("dark"))
        menubar.add_cascade(label="Tema", menu=theme_menu)

        # Kod editörüm
        self.editor = scrolledtext.ScrolledText(self, wrap=tk.NONE, undo=True)
        self.editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Konsol çıktısı
        self.console = scrolledtext.ScrolledText(self, height=10, bg="#222", fg="#fff")
        self.console.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

        # Çalıştır düğmesi
        run_btn = tk.Button(self, text="Çalıştır ▶️", command=self.run_code)
        run_btn.pack(pady=(0, 5))

        # Footer etiketi: "Efe Aydın Turkce Kod"
        self.footer = tk.Label(self, text="Efe Aydın Turkce Kod", font=("Segoe UI", 9))
        self.footer.pack(side=tk.BOTTOM, pady=(0, 5))

    def set_theme(self, theme: str):
        # Tema renk paletleri
        bg_colors = {
            "dark":  {"editor_bg": "#252526", "editor_fg": "#d4d4d4", "console_bg": "#1e1e1e", "console_fg": "#d4d4d4"},
            "light": {"editor_bg": "#f3f3f3", "editor_fg": "#000000", "console_bg": "#ffffff", "console_fg": "#000000"},
        }
        colors = bg_colors.get(theme, bg_colors["light"])

        # Editör ve konsol renklerini ayarlama
        self.editor.config(background=colors["editor_bg"],
                           fg=colors["editor_fg"],
                           insertbackground=colors["editor_fg"])
        self.console.config(background=colors["console_bg"],
                            fg=colors["console_fg"])
        self.configure(background=colors["console_bg"])

        # Footer metin rengini zıt renge ayarlama
        footer_fg = "#ffffff" if theme == "dark" else "#000000"
        self.footer.config(background=colors["console_bg"],
                            fg=footer_fg)

    def new_file(self):
        if self._prompt_save():
            self.editor.delete("1.0", tk.END)
            self.filepath = None
            self.title("Turkce Kod IDE – Yeni")

    def open_file(self):
        if not self._prompt_save():
            return
        # Uzantı .turkcekod olarak güncellendi
        file_path = filedialog.askopenfilename(
            defaultextension=".turkcekod",
            filetypes=[("Turkce Kod Dosyaları", "*.turkcekod")]
        )
        if not file_path:
            return
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", content)
        self.filepath = file_path
        self.title(f"Turkce Kod IDE – {os.path.basename(file_path)}")

    def save_file(self) -> bool:
        if not self.filepath:
            # Uzantı .turkcekod olarak güncellendi
            self.filepath = filedialog.asksaveasfilename(
                defaultextension=".turkcekod",
                filetypes=[("Turkce Kod Dosyaları", "*.turkcekod")]
            )
        if not self.filepath:
            return False
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(self.editor.get("1.0", tk.END))
        self.title(f"Turkce Kod IDE – {os.path.basename(self.filepath)}")
        return True

    def _prompt_save(self) -> bool:
        # Metinde değişiklik olup olmadığını kontrol eder
        if self.editor.edit_modified():
            ans = messagebox.askyesnocancel("Değişiklikler Kaydedilsin mi?",
                                             "Değişiklikleri kaydetmek ister misiniz?")
            if ans is None:   # İptal
                return False
            if ans:           # Evet
                return self.save_file()
        return True

    def run_code(self):
        # 1) Geçici Turkce Kod dosyasını oluştur
        # Dosya uzantısı .turkcekod olarak güncellendi
        tmp_filename = os.path.join(SCRIPT_DIR, "tmp_run.turkcekod")
        code = self.editor.get("1.0", tk.END)
        with open(tmp_filename, "w", encoding="utf-8") as f:
            f.write(code)

        # 2) Yorumlayıcının tam yolunu oluştur
        yorumlayici_path = os.path.join(SCRIPT_DIR, "yorumlayici.py")

        # 3) Alt süreçte yorumlayıcıyı çalıştır
        try:
            proc = subprocess.run(
                [sys.executable, yorumlayici_path, tmp_filename],
                text=True,
                capture_output=True,
                check=True,
                encoding="utf-8"
            )
            output = proc.stdout
        except FileNotFoundError:
            output = f"HATA: 'yorumlayici.py' dosyası bulunamadı. Lütfen aynı klasörde olduğundan emin olun."
        except subprocess.CalledProcessError as e:
            output = e.stderr

        # 4) Konsola yazdır
        self.console.delete("1.0", tk.END)
        self.console.insert(tk.END, output)

        # 5) Düzenlenme işaretini temizle
        self.editor.edit_modified(False)


if __name__ == "__main__":
    app = TurkceKodIDE()
    app.mainloop()
