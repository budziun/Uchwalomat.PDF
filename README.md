# UchwałoMat.pdf

**UchwałoMat.pdf** to narzędzie desktopowe dla Windows, które automatycznie generuje czytelne tytuły uchwał, zarządzeń i raportów z plików PDF urzędowych. Umożliwia szybkie przetwarzanie dokumentów, zarówno tekstowych, jak i skanowanych, z wykorzystaniem technologii OCR.

**Pobierz najnowszą wersję przez [GitHub Releases](https://github.com/budziun/Uchwalomat.PDF/releases) i korzystaj bez instalacji!**

---

## Najważniejsze funkcje

- **Automatyczne rozpoznawanie typu dokumentu** (uchwała, zarządzenie, raport)
- **Ekstrakcja tytułów** z plików PDF, nawet jeśli są to skany (dzięki OCR)
- **Poprawne formatowanie tytułów** – np. dla zarządzeń fragment do „z dnia” jest zawsze WIELKIMI LITERAMI, tytuł zaczyna się od nowej linii
- **Obsługa wielu plików jednocześnie** – wystarczy wskazać folder z dokumentami
- **Przyjazny interfejs graficzny** (GUI) oparty o Tkinter
- **Statystyki przetwarzania** (ile plików, ile użyto OCR, ile PyPDF2)

---

## Jak działa?

1. **Wybierz folder z plikami PDF** (uchwały, zarządzenia, raporty)
2. Program rozpoznaje typ każdego dokumentu oraz wyciąga i formatuje tytuł
3. Wynik zapisuje się do pliku `wyniki.txt` w wybranym katalogu
4. Jeśli plik PDF jest skanem (obrazem), program używa OCR (Tesseract) do rozpoznania tekstu

---

## Pobieranie aplikacji

**Zalecane pobieranie przez [GitHub Releases](https://github.com/budziun/Uchwalomat.PDF/releases)** – znajdziesz tam najnowszą wersję programu, gotową do uruchomienia na Windows (plik `.exe`).

---

## OCR – co to jest i po co?

**OCR (Optical Character Recognition)** umożliwia rozpoznawanie tekstu ze skanów i plików PDF, które nie zawierają warstwy tekstowej (np. zeskanowane uchwały). Dzięki temu UchwałoMat.pdf potrafi przetwarzać zarówno dokumenty tekstowe, jak i obrazy.

- **Wersja z OCR** (dostępna w najnowszych release) działa „out of the box” – nie wymaga instalacji Tesseract osobno, bo jest dołączony w folderze projektu.
- **Wersja bez OCR** (w katalogu `dist`) działa tylko z PDF-ami tekstowymi, nie obsługuje skanów.

---

## Struktura projektu

Uchwalomat.PDF/
├── main.py # Główny plik programu
├── Tesseract-OCR/ # Folder z dołączonym Tesseract (dla OCR)
├── dist/ # Stara wersja bez OCR
├── requirements.txt # Minimalne zależności
└── ...


---

## Minimalne wymagania

- **Windows 10/11**
- **Python 3.8+** (tylko dla wersji źródłowej)
- Dla wersji .exe – nie są wymagane żadne instalacje ani uprawnienia administratora

---

## Instalacja i uruchomienie

### Gotowy plik .exe

1. Pobierz najnowszą wersję z zakładki **Releases**
2. Rozpakuj archiwum ZIP
3. Uruchom `UchwaloMat.exe`
4. Wskaż folder z plikami PDF i kliknij „Generuj raport”

### Wersja źródłowa

1. Sklonuj repozytorium
2. Zainstaluj zależności:
    ```
    pip install -r requirements.txt
    ```
3. Uruchom:
    ```
    python main.py
    ```

---

## FAQ

**Czy muszę instalować Tesseract?**  
Nie – program zawiera własną kopię Tesseract w folderze `Tesseract-OCR`.

**Czy obsługiwane są skany PDF?**  
Tak, wersja z OCR automatycznie rozpoznaje tekst ze skanów.

**Co znajduje się w katalogu `dist`?**  
Stara wersja programu, która nie obsługuje OCR – działa tylko z PDF-ami tekstowymi.

---

## Autor

Projekt: **Jakub Budzich**  
Repozytorium: [github.com/budziun/Uchwalomat.PDF](https://github.com/budziun/Uchwalomat.PDF)


