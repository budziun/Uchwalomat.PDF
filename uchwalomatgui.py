import os
import re
import PyPDF2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import subprocess
import platform


class UchwalomatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UchwałoMat - Generator tytułów uchwał i raportów")
        self.root.geometry("600x400")
        self.folder_path = ""

        self.setup_ui()

    def setup_ui(self):
        # Nagłówek
        title_label = tk.Label(self.root, text="UchwałoMat.pdf", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        subtitle_label = tk.Label(self.root, text="Generator tytułów uchwał i raportów - made by Jakub Budzich",
                                  font=("Arial", 10))
        subtitle_label.pack(pady=5)

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
        self.status_text = tk.Text(self.root, height=10, width=70)
        self.status_text.pack(pady=10, padx=20, fill="both", expand=True)

        # Scrollbar dla statusu
        scrollbar = tk.Scrollbar(self.status_text)
        scrollbar.pack(side="right", fill="y")
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)

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

            processor = DocumentProcessor()
            result = processor.extract_titles_from_folder(self.folder_path, self.log_status)

            if result:
                self.log_status("✓ Raport wygenerowany pomyślnie!")
                self.log_status("Otwieranie pliku wyników...")

                # Automatyczne otwarcie pliku
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
    def extract_title_until_phrase(self, pdf_path, stop_phrase="Na podstawie"):
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            if len(reader.pages) > 0:
                first_page = reader.pages[0]
                text = first_page.extract_text()
                if text:
                    result = []
                    stop_phrase_lower = stop_phrase.lower()
                    for line in text.splitlines():
                        line_stripped = line.strip()
                        idx = line_stripped.lower().find(stop_phrase_lower)
                        if idx != -1:
                            if idx > 0:
                                result.append(line_stripped[:idx].strip())
                            break
                        result.append(line_stripped)
                    return ' '.join(result)
        return ''

    def extract_session_number_from_last_page(self, text):
        match = re.search(r'Uchwała\s+Nr\s+([IVXLCDM]+)', text, re.IGNORECASE)
        if match:
            return match.group(1)
        match = re.search(r'\b([IVXLCDM]+)\b', text, re.IGNORECASE)
        if match:
            return match.group(1)
        return "?"

    def extract_date_from_text(self, text):
        match = re.search(r'(\d{1,2})\s+([a-ząćęłńóśźż]+)\s+(\d{4})\s*r?\.?', text, re.IGNORECASE)
        if match:
            day, month, year = match.groups()
            months = {
                'stycznia': 'stycznia', 'lutego': 'lutego', 'marca': 'marca', 'kwietnia': 'kwietnia', 'maja': 'maja',
                'czerwca': 'czerwca',
                'lipca': 'lipca', 'sierpnia': 'sierpnia', 'września': 'września', 'października': 'października',
                'listopada': 'listopada', 'grudnia': 'grudnia'
            }
            month_name = months.get(month.lower(), month)
            return f"{int(day)} {month_name} {year} roku"
        return "?"

    def generate_report_title(self, pdf_path):
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            first_page_text = reader.pages[0].extract_text()
            date = self.extract_date_from_text(first_page_text if first_page_text else "")
            last_page_text = reader.pages[-1].extract_text()
            session_number = self.extract_session_number_from_last_page(last_page_text if last_page_text else "")
        if session_number != "?" and date != "?":
            return f"Raport głosowania dla wszystkich uchwał procedowanych w trakcie {session_number} Sesji Rady Gminy Gruta w dniu {date}."
        else:
            return "Raport głosowania – nie udało się odczytać numeru sesji lub daty."

    def extract_titles_from_folder(self, folder_path, log_callback, stop_phrase="Na podstawie"):
        numeric_files = []
        report_files = []
        other_files = []

        log_callback("Skanowanie plików PDF...")

        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.pdf'):
                if re.fullmatch(r'\d+\.pdf', filename):
                    numeric_files.append(filename)
                elif re.search(r'raport', filename, re.IGNORECASE):
                    report_files.append(filename)
                else:
                    other_files.append(filename)

        log_callback(f"Znaleziono {len(numeric_files)} uchwał i {len(report_files)} raportów")

        numeric_files.sort(key=lambda x: int(re.match(r'(\d+)', x).group(1)))
        report_files.sort()

        results = []

        # Przetwarzaj pliki liczbowe
        for filename in numeric_files:
            log_callback(f"Przetwarzanie: {filename}")
            pdf_path = os.path.join(folder_path, filename)
            title = self.extract_title_until_phrase(pdf_path, stop_phrase)
            if title:
                results.append(f'{filename}:\n{title}\n')
            else:
                results.append(f'{filename}: [Brak tytułu]\n')

        # Przetwarzaj pliki raportów
        for filename in report_files:
            log_callback(f"Przetwarzanie: {filename}")
            pdf_path = os.path.join(folder_path, filename)
            title = self.generate_report_title(pdf_path)
            results.append(f'{filename}:\n{title}\n')


        results.append("\n\n\n\n\nWygenerowano przy pomocy UchwałoMat.pdf, projekt - Jakub Budzich")

        output_file = os.path.join(folder_path, 'wyniki.txt')
        with open(output_file, 'w', encoding='utf-8') as out:
            for line in results:
                out.write(line + '\n')

        log_callback(f"Raport zapisany: {output_file}")
        return output_file


if __name__ == "__main__":
    root = tk.Tk()
    app = UchwalomatGUI(root)
    root.mainloop()
