import os
import re
import PyPDF2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import subprocess
import platform
import sys
import tempfile

# Sprawdzenie dostępności bibliotek OCR
try:
    import pytesseract
    from PIL import Image
    import fitz  # PyMuPDF

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# Sprawdzenie dostępności OpenCV dla preprocessing
try:
    import cv2
    import numpy as np

    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


# Konfiguracja Tesseract - automatyczne wykrywanie i konfiguracja
def configure_tesseract():
    """Automatycznie konfiguruje Tesseract OCR"""
    if not TESSERACT_AVAILABLE:
        return False

    # NAJPIERW sprawdź lokalny folder projektu
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_tesseract = os.path.join(script_dir, "Tesseract-OCR", "tesseract.exe")

    if os.path.exists(local_tesseract):
        print(f"✓ Znaleziono lokalny Tesseract: {local_tesseract}")
        pytesseract.pytesseract.tesseract_cmd = local_tesseract

        # Ustaw TESSDATA_PREFIX na lokalny folder tessdata
        tessdata_path = os.path.join(script_dir, "Tesseract-OCR", "tessdata")
        if os.path.exists(tessdata_path):
            os.environ['TESSDATA_PREFIX'] = tessdata_path
            print(f"✓ Ustawiono TESSDATA_PREFIX: {tessdata_path}")

        try:
            version = pytesseract.get_tesseract_version()
            print(f"✓ Lokalny Tesseract skonfigurowany, wersja: {version}")
            return True
        except Exception as e:
            print(f"❌ Błąd konfiguracji lokalnego Tesseract: {e}")

    # FALLBACK - sprawdź czy tesseract jest w PATH (bez ustawiania błędnej ścieżki)
    print("⚠ Lokalny Tesseract nie znaleziony, sprawdzam PATH...")

    try:
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        print("✓ Tesseract w PATH:", result.stdout.split('\n')[0])
        return True
    except:
        print("⚠ Tesseract nie jest w PATH")

    # Sprawdź inne możliwe lokalizacje (tylko jeśli istnieją)
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.join(os.path.expanduser("~"), "AppData", "Local", "Tesseract-OCR", "tesseract.exe")
    ]

    for path in possible_paths:
        if os.path.exists(path):
            print(f"✓ Znaleziono systemowy Tesseract: {path}")
            pytesseract.pytesseract.tesseract_cmd = path

            # Ustaw TESSDATA_PREFIX dla znalezionej instalacji
            tessdata_system = os.path.join(os.path.dirname(path), "tessdata")
            if os.path.exists(tessdata_system):
                os.environ['TESSDATA_PREFIX'] = tessdata_system
                print(f"✓ Ustawiono systemowy TESSDATA_PREFIX: {tessdata_system}")

            try:
                version = pytesseract.get_tesseract_version()
                print(f"✓ Systemowy Tesseract skonfigurowany, wersja: {version}")
                return True
            except Exception as e:
                print(f"❌ Błąd konfiguracji systemowego Tesseract: {e}")
                continue

    print("❌ Nie znaleziono działającego Tesseract")
    return False


# Skonfiguruj Tesseract przy starcie
TESSERACT_CONFIGURED = configure_tesseract() if TESSERACT_AVAILABLE else False


def natural_sort_key(filename):
    """Klucz do naturalnego sortowania plików (95.pdf < 100.pdf)"""
    parts = re.split(r'(\d+)', filename)
    return [int(part) if part.isdigit() else part.lower() for part in parts]


class UchwalomatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UchwałoMat - Generator tytułów uchwał, zarządzeń i raportów")
        self.root.geometry("700x650")
        self.folder_path = ""
        self.ocr_enabled = True  # Zawsze włączone
        self.tesseract_configured = TESSERACT_CONFIGURED

        self.setup_ui()

    def setup_ui(self):
        # Nagłówek
        title_label = tk.Label(self.root, text="UchwałoMat.pdf", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        subtitle_label = tk.Label(self.root,
                                  text="Generator tytułów uchwał, zarządzeń i raportów - made by Jakub Budzich",
                                  font=("Arial", 10))
        subtitle_label.pack(pady=5)

        # Status bibliotek
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=5)

        # Status PyPDF2
        pypdf2_status = "✓ PyPDF2 dostępne (ekstrakcja tekstu z PDF)"
        pypdf2_label = tk.Label(status_frame, text=pypdf2_status, font=("Arial", 9), fg="green")
        pypdf2_label.pack()

        # Status OCR
        self.setup_ocr_status(status_frame)

        # Wybór folderu
        folder_frame = tk.Frame(self.root)
        folder_frame.pack(pady=20, padx=20, fill="x")

        tk.Label(folder_frame, text="Wybierz folder z plikami PDF:").pack(anchor="w")

        path_frame = tk.Frame(folder_frame)
        path_frame.pack(fill="x", pady=5)

        self.path_var = tk.StringVar()
        self.path_entry = tk.Entry(path_frame, textvariable=self.path_var, state="readonly")
        self.path_entry.pack(side="left", fill="x", expand=True)

        browse_btn = tk.Button(path_frame, text="Przeglądaj", command=self.browse_folder)
        browse_btn.pack(side="right", padx=(5, 0))

        # Przycisk generowania
        generate_btn = tk.Button(self.root, text="Generuj raport", command=self.generate_report,
                                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        generate_btn.pack(pady=20)

        # Obszar statusu
        self.status_text = tk.Text(self.root, height=12, width=80)
        self.status_text.pack(pady=10, padx=20, fill="both", expand=True)

        # Scrollbar dla statusu
        scrollbar = tk.Scrollbar(self.status_text)
        scrollbar.pack(side="right", fill="y")
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)

    def setup_ocr_status(self, parent):
        """Konfiguruje wyświetlanie statusu OCR"""
        if not TESSERACT_AVAILABLE:
            ocr_status = "❌ Biblioteki OCR niedostępne (pytesseract, PIL, PyMuPDF)"
            ocr_label = tk.Label(parent, text=ocr_status, font=("Arial", 9), fg="red")
            ocr_label.pack()

            install_frame = tk.Frame(parent)
            install_frame.pack(pady=2)

            install_btn = tk.Button(install_frame, text="Zainstaluj biblioteki OCR",
                                    command=self.install_ocr_libraries, bg="#2196F3", fg="white")
            install_btn.pack()

        elif not self.tesseract_configured:
            ocr_status = "⚠️ Biblioteki OCR dostępne, ale Tesseract nie jest skonfigurowany"
            ocr_label = tk.Label(parent, text=ocr_status, font=("Arial", 9), fg="orange")
            ocr_label.pack()

            tesseract_frame = tk.Frame(parent)
            tesseract_frame.pack(pady=2)

            configure_btn = tk.Button(tesseract_frame, text="Skonfiguruj ścieżkę Tesseract",
                                      command=self.configure_tesseract_path, bg="#607D8B", fg="white")
            configure_btn.pack()

        else:
            ocr_status = "✓ OCR dostępne (Tesseract + biblioteki Python) - zawsze włączone"
            ocr_label = tk.Label(parent, text=ocr_status, font=("Arial", 9), fg="green")
            ocr_label.pack()

    def install_ocr_libraries(self):
        """Instaluje biblioteki OCR"""
        try:
            self.log_status("Instalowanie bibliotek OCR...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "pytesseract", "pillow", "pymupdf", "opencv-python"])
            messagebox.showinfo("Sukces", "Biblioteki OCR zostały zainstalowane. Uruchom aplikację ponownie.")
            self.log_status("✓ Biblioteki OCR zainstalowane")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zainstalować bibliotek: {str(e)}")
            self.log_status(f"❌ Błąd instalacji: {str(e)}")

    def configure_tesseract_path(self):
        """Pozwala użytkownikowi wybrać ścieżkę do tesseract.exe"""
        tesseract_path = filedialog.askopenfilename(
            title="Wybierz tesseract.exe",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )

        if tesseract_path:
            try:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                version = pytesseract.get_tesseract_version()
                self.tesseract_configured = True
                messagebox.showinfo("Sukces", f"Tesseract został skonfigurowany pomyślnie!\nWersja: {version}")
                self.log_status(f"✓ Tesseract skonfigurowany: {tesseract_path}")

                # Odśwież GUI
                self.root.destroy()
                root = tk.Tk()
                app = UchwalomatGUI(root)
                root.mainloop()
            except Exception as e:
                messagebox.showerror("Błąd", f"Nieprawidłowa ścieżka do Tesseract: {str(e)}")

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Wybierz folder z plikami PDF")
        if folder:
            self.folder_path = folder
            self.path_var.set(folder)
            self.log_status(f"Wybrano folder: {folder}")

    def log_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update()

    def open_file(self, filepath):
        """Otwiera plik w domyślnym programie systemu"""
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', filepath))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(filepath)
            else:  # Linux
                subprocess.call(('xdg-open', filepath))
            self.log_status(f"Otwarto plik: {filepath}")
        except Exception as e:
            self.log_status(f"Nie udało się otworzyć pliku: {str(e)}")

    def generate_report(self):
        if not self.folder_path:
            messagebox.showerror("Błąd", "Proszę wybrać folder z plikami PDF")
            return

        try:
            self.status_text.delete(1.0, tk.END)
            self.log_status("Rozpoczynanie generowania raportu...")

            processor = DocumentProcessor(self.log_status)
            result = processor.extract_titles_from_folder(self.folder_path, self.log_status)

            if result:
                self.log_status("✓ Raport wygenerowany pomyślnie!")
                self.log_status("Otwieranie pliku wyników...")
                self.open_file(result)
                messagebox.showinfo("Sukces",
                                    f"Raport zapisany w pliku:\n{result}\n\nPlik został automatycznie otwarty.")
            else:
                self.log_status("✗ Wystąpił błąd podczas generowania raportu")
                messagebox.showerror("Błąd", "Nie udało się wygenerować raportu")

        except Exception as e:
            self.log_status(f"✗ Błąd: {str(e)}")
            messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}")


class DocumentProcessor:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.pypdf2_used_count = 0
        self.ocr_used_count = 0
        self.use_ocr = TESSERACT_AVAILABLE and TESSERACT_CONFIGURED
        self.temp_dir = None

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)

    def setup_tesseract_temp(self):
        """Konfiguruje bezpieczny katalog tymczasowy dla Tesseract"""
        try:
            user_temp = os.path.join(os.path.expanduser("~"), "UchwaloMat_temp")
            os.makedirs(user_temp, exist_ok=True)
            self.temp_dir = tempfile.mkdtemp(dir=user_temp, prefix="ocr_")
            self.log(f"🗂️ Katalog tymczasowy OCR: {self.temp_dir}")
            return self.temp_dir
        except Exception as e:
            self.log(f"⚠️ Nie udało się skonfigurować katalogu tymczasowego: {str(e)}")
            self.temp_dir = tempfile.gettempdir()
            return self.temp_dir

    def cleanup_temp(self):
        """Czyści katalog tymczasowy"""
        if self.temp_dir and os.path.exists(self.temp_dir) and "UchwaloMat_temp" in self.temp_dir:
            try:
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                self.log("🧹 Wyczyszczono katalog tymczasowy")
            except Exception as e:
                self.log(f"⚠️ Nie udało się wyczyścić katalogu tymczasowego: {str(e)}")

    def preprocess_image_for_ocr(self, img):
        """Minimalny preprocessing obrazu dla OCR"""
        if not OPENCV_AVAILABLE:
            return img

        try:
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            return Image.fromarray(binary)
        except Exception as e:
            self.log(f"⚠️ Błąd preprocessing obrazu: {e}")
            return img

    def fix_common_ocr_errors(self, text):
        """Rozszerzona funkcja poprawek OCR"""
        corrections = {
            # Nowe poprawki z twoich wyników
            'ZARZĄDZENIK': 'ZARZĄDZENIE',
            'Nmr': 'Nr',
            'Gni Girarta': 'Gminy Gruta',
            'Gni': 'Gminy',
            'Girarta': 'Gruta',
            'wisprawie': 'w sprawie',
            'czerwęa': 'czerwca',
            'czerweń': 'czerwca',
            'Wiójia': 'Wójta',
            'Giniiny': 'Gminy',
            'Gir': 'Gruta',
            'Podstawówej': 'Podstawowej',
            'saińórządzie': 'samorządzie',
            'marea': 'marca',
            'giudnia': 'grudnia',
            'oświatówe': 'oświatowe',
            'Saińóiządowego': 'Samorządowego',
            'dńień': 'dniem',
            'pełnieni': 'pełnienia',
            'z:dnia': 'z dnia',
            'ź dnia': 'z dnia',
            'um,': 'im.',
            'pełnieniaa': 'pełnienia',
            '2035': '2025',
            '0.0': 'o.o',

            # Istniejące poprawki
            'czerwea': 'czerwca', 'ezerwea': 'czerwca', 'czerwiec': 'czerwca', 'ezerwiec': 'czerwca',
            'obowiazké6w': 'obowiązków', 'obowiazkéw': 'obowiązków', 'wniosk6éw': 'wniosków',
            'wtasnosé': 'własność', 'wlasnosé': 'własność', 'stanowigcych': 'stanowiących',
            'Lesifiskiego': 'Lesińskiego', 'Pawta': 'Pawła', 'uchwalte': 'uchwałę',
            'przediuzenia': 'przedłużenia', 'pelnienia': 'pełnienia', 'powolania': 'powołania',
            'zlozonych': 'złożonych', 'ZARZDZENIENR': 'ZARZĄDZENIE NR',
            'WOJTAGMINYGRUTA': 'WOJTA GMINY GRUTA', 'Napodstawie': 'Na podstawie',
            'zdnia': 'z dnia', 'wsprawie': 'w sprawie'
        }

        for error, correction in corrections.items():
            text = text.replace(error, correction)

        # Poprawki regex
        text = re.sub(r'(\d+)(\d{4})', r'\1/\2', text)  # 502025 → 50/2025
        text = re.sub(r'obowiązk(\d+)w', r'obowiązków', text)
        text = re.sub(r'wniosk(\d+)w', r'wniosków', text)
        text = re.sub(r'własno(\d+)', r'własność', text)

        return text

    def improve_text_spacing(self, text):
        """Poprawia spacje w tekście OCR"""
        # Dodaj spacje przed dużymi literami (nowe słowa)
        text = re.sub(r'([a-ząćęłńóśźż])([A-ZĄĆĘŁŃÓŚŹŻ])', r'\1 \2', text)

        # Popraw spacje wokół interpunkcji
        text = re.sub(r'([a-ząćęłńóśźż])([.,;:])', r'\1\2', text)
        text = re.sub(r'([.,;:])([A-ZĄĆĘŁŃÓŚŹŻ])', r'\1 \2', text)

        # Popraw spacje wokół dat
        text = re.sub(r'(\d+)([a-ząćęłńóśźż])', r'\1 \2', text)
        text = re.sub(r'([a-ząćęłńóśźż])(\d+)', r'\1 \2', text)

        # Usuń wielokrotne spacje
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def normalize_text_to_single_line(self, text):
        """Konwertuje tekst na jedną linię"""
        if not text:
            return ""

        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line:
                lines.append(line)

        single_line = ' '.join(lines)
        single_line = re.sub(r'\s+', ' ', single_line)
        return single_line.strip()

    def extract_text_with_pypdf2(self, pdf_path):
        """Ekstrakcja tekstu używając PyPDF2"""
        try:
            self.log("📄 Próbuję PyPDF2...")
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                if len(reader.pages) > 0:
                    text = reader.pages[0].extract_text()

                    if text and len(text.strip()) > 10:
                        text = self.normalize_text_to_single_line(text)
                        self.log(f"✅ PyPDF2 SUKCES: {len(text)} znaków")
                        self.pypdf2_used_count += 1
                        return text
                    else:
                        self.log("❌ PyPDF2 nie znalazł tekstu")
        except Exception as e:
            self.log(f"❌ Błąd PyPDF2: {str(e)}")

        return ""

    def extract_text_with_ocr(self, pdf_path):
        """Ekstrakcja tekstu używając OCR - preferuj język polski"""
        if not self.use_ocr:
            return ""

        try:
            self.log("🔍 Próbuję OCR (Tesseract)...")

            if not self.temp_dir:
                self.setup_tesseract_temp()

            doc = fitz.open(pdf_path)
            page = doc[0]
            pix = page.get_pixmap(dpi=400)  # Zachowujemy 400 DPI
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            img = self.preprocess_image_for_ocr(img)

            # Sprawdź dostępne języki
            try:
                available_langs = pytesseract.get_languages()
                self.log(f"📋 Dostępne języki: {available_langs}")

                # Preferuj polski, fallback na angielski
                if 'pol' in available_langs:
                    lang = 'pol'
                    self.log("🇵🇱 Używam języka polskiego")
                elif 'eng' in available_langs:
                    lang = 'eng'
                    self.log("🇬🇧 Używam języka angielskiego (fallback)")
                else:
                    lang = available_langs[0] if available_langs else 'eng'
                    self.log(f"🌐 Używam języka: {lang}")

            except Exception as e:
                self.log(f"⚠️ Nie można sprawdzić języków, używam 'eng': {e}")
                lang = 'eng'

            # Uproszczona konfiguracja OCR
            custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'

            text = pytesseract.image_to_string(img, lang=lang, config=custom_config)
            doc.close()

            if text and len(text.strip()) > 10:
                # ZINTEGROWANE POPRAWKI
                # 1. Podstawowe poprawki OCR
                text = self.fix_common_ocr_errors(text)

                # 2. Popraw spacje
                text = self.improve_text_spacing(text)

                # 3. Normalizuj do jednej linii
                text = self.normalize_text_to_single_line(text)

                self.log(f"✅ OCR SUKCES ({lang}): {len(text)} znaków")
                self.log(f"📝 Tekst po poprawkach: '{text[:100]}...'")
                self.ocr_used_count += 1
                return text
            else:
                self.log("❌ OCR nie znalazł tekstu")

        except Exception as e:
            self.log(f"❌ Błąd OCR: {str(e)}")

        return ""

    def extract_text_from_pdf(self, pdf_path):
        """Główna metoda ekstrakcji tekstu"""
        text = self.extract_text_with_pypdf2(pdf_path)
        if not text and self.use_ocr:
            text = self.extract_text_with_ocr(pdf_path)
        return text

    def detect_document_type_from_text(self, text):
        """Rozpoznaje typ dokumentu na podstawie tekstu"""
        if not text:
            return 'dokument'

        text_upper = text.upper()
        if 'ZARZĄDZENIE' in text_upper or 'ZARZADZENIE' in text_upper:
            return 'zarządzenie'
        elif 'UCHWAŁA' in text_upper or 'UCHWALA' in text_upper:
            return 'uchwała'
        else:
            return 'dokument'

    def extract_title_until_phrase(self, text, stop_phrase="na podstawie"):
        """Ekstraktowanie tytułu do frazy stop (ignoruje wielkość liter)"""
        if not text:
            return ""

        text_lower = text.lower()
        stop_phrase_lower = stop_phrase.lower()

        idx = text_lower.find(stop_phrase_lower)
        if idx != -1:
            result = text[:idx].strip()
            return result
        else:
            return text.strip()

    def extract_session_number_from_last_page(self, text):
        """Wyciąga numer sesji z tekstu"""
        match = re.search(r'Uchwała\s+Nr\s+([IVXLCDM]+)', text, re.IGNORECASE)
        if match:
            return match.group(1)
        match = re.search(r'\b([IVXLCDM]+)\b', text, re.IGNORECASE)
        if match:
            return match.group(1)
        return "?"

    def extract_date_from_text(self, text):
        """Wyciąga datę z tekstu"""
        match = re.search(r'(\d{1,2})\s+([a-ząćęłńóśźż]+)\s+(\d{4})\s*r?\.?', text, re.IGNORECASE)
        if match:
            day, month, year = match.groups()
            months = {
                'stycznia': 'stycznia', 'lutego': 'lutego', 'marca': 'marca', 'kwietnia': 'kwietnia', 'maja': 'maja',
                'czerwca': 'czerwca', 'lipca': 'lipca', 'sierpnia': 'sierpnia', 'września': 'września',
                'października': 'października', 'listopada': 'listopada', 'grudnia': 'grudnia'
            }
            month_name = months.get(month.lower(), month)
            return f"{int(day)} {month_name} {year} roku"
        return "?"

    def generate_report_title(self, text):
        """Generuje tytuł dla raportów na podstawie tekstu"""
        if not text:
            return "Raport głosowania – nie udało się odczytać zawartości."

        date = self.extract_date_from_text(text)
        session_number = self.extract_session_number_from_last_page(text)

        if session_number != "?" and date != "?":
            return f"Raport głosowania dla wszystkich uchwał procedowanych w trakcie {session_number} Sesji Rady Gminy Gruta w dniu {date}."
        else:
            return "Raport głosowania – nie udało się odczytać numeru sesji lub daty."

    def transform_title_for_report(self, title):
        """Transformuje tytuł zgodnie z wymaganiami formatowania"""
        if not title:
            return title

        # Szukamy pierwszego wystąpienia 'z dnia' lub 'dnia' (ignorując wielkość liter)
        match = re.search(r'\b(z dnia|dnia)\b', title, re.IGNORECASE)
        if match:
            pos = match.start()
            # Sprawdź czy 'zarządzenie' jest w tytule (ignorując wielkość liter)
            if re.search(r'zarządzenie', title, re.IGNORECASE):
                # Zamień na wielkie litery od początku do pierwszego wystąpienia 'z dnia' lub 'dnia'
                before = title[:pos].upper()
                after = title[pos:]
                transformed = before + after
            else:
                transformed = title
        else:
            transformed = title

        # Upewnij się, że tytuł zaczyna się od nowej linii
        transformed = '\n' + transformed.strip()
        return transformed

    def extract_titles_from_folder(self, folder_path, log_callback, stop_phrase="Na podstawie"):
        """ZOPTYMALIZOWANA FUNKCJA: Jedno wywołanie OCR na plik"""
        pdf_files = []
        self.pypdf2_used_count = 0
        self.ocr_used_count = 0

        if self.use_ocr:
            self.setup_tesseract_temp()

        log_callback("🔍 Skanowanie plików PDF...")

        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.pdf'):
                pdf_files.append(filename)

        log_callback(f"📁 Znaleziono {len(pdf_files)} plików PDF")

        # NATURALNE SORTOWANIE
        pdf_files.sort(key=natural_sort_key)

        results = []
        stats = {'uchwała': 0, 'zarządzenie': 0, 'raport': 0, 'dokument': 0}

        try:
            for filename in pdf_files:
                log_callback(f"\n{'=' * 60}")
                log_callback(f"🔄 PRZETWARZANIE: {filename}")
                log_callback(f"{'=' * 60}")

                pdf_path = os.path.join(folder_path, filename)

                # JEDNO WYWOŁANIE EKSTRAKCJI TEKSTU
                text = self.extract_text_from_pdf(pdf_path)

                if re.search(r'raport', filename, re.IGNORECASE):
                    title = self.generate_report_title(text)
                    doc_type = "raport"
                    log_callback(f"📊 Rozpoznano jako raport na podstawie nazwy")
                else:
                    # ROZPOZNAJ TYP NA PODSTAWIE WYEKSTRAKTOWANEGO TEKSTU
                    doc_type = self.detect_document_type_from_text(text)

                    # WYCIĄGNIJ TYTUŁ DO FRAZY "NA PODSTAWIE"
                    title = self.extract_title_until_phrase(text, stop_phrase)

                    log_callback(f"🏷️ Typ dokumentu: {doc_type}")
                    log_callback(f"📏 Długość tytułu: {len(title) if title else 0}")
                    if title:
                        display_title = title[:200] + "..." if len(title) > 200 else title
                        log_callback(f"📝 Tytuł: '{display_title}'")
                    else:
                        log_callback(f"❌ TYTUŁ JEST PUSTY!")

                stats[doc_type] += 1

                if title and title.strip():
                    # Zastosuj transformację tytułu
                    formatted_title = self.transform_title_for_report(title)
                    results.append(f'{filename} ({doc_type}): {formatted_title}')
                    log_callback(f"✅ ZAPISANO TYTUŁ dla {filename}")
                else:
                    results.append(f'{filename} ({doc_type}): [Brak tytułu]')
                    log_callback(f"❌ BRAK TYTUŁU dla {filename}")

        finally:
            if self.use_ocr:
                self.cleanup_temp()

        # Dodaj statystyki użycia
        stats_text = f"\n\nStatystyki przetwarzania:\n"
        stats_text += f"PyPDF2 użyte: {self.pypdf2_used_count} razy\n"
        if self.use_ocr:
            stats_text += f"OCR użyte: {self.ocr_used_count} razy\n"

        version_text = "UchwałoMat.pdf v2.1"
        if self.use_ocr:
            version_text += " (wersja z OCR - PyPDF2 + Tesseract -- odczyt plikow pdf zapisanych jako skan a nie tekst)"
        else:
            version_text += " (wersja podstawowa - tylko PyPDF2)"

        results.append(f"{stats_text}\n\nWygenerowano przy pomocy {version_text}, \n 2025 Jakub Budzich")

        output_file = os.path.join(folder_path, 'wyniki.txt')
        with open(output_file, 'w', encoding='utf-8') as out:
            for line in results:
                out.write(line + '\n\n')

        log_callback(f"💾 Raport zapisany: {output_file}")
        return output_file


if __name__ == "__main__":
    root = tk.Tk()
    app = UchwalomatGUI(root)
    root.mainloop()
