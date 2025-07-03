# Uchwalomat.PDF

**Prosty program do automatycznej analizy plików PDF z uchwałami i raportami – bez ręcznego szukania tytułów!**

## Opis

**Uchwalomat.PDF** to narzędzie, które automatycznie odczytuje tytuły uchwał oraz generuje tytuły raportów z plików PDF znajdujących się w wybranym folderze. Program jest przeznaczony dla urzędników, pracowników biur rady oraz wszystkich, którzy muszą szybko zebrać tytuły wielu dokumentów bez żmudnego otwierania każdego pliku.

- Obsługuje zarówno uchwały ktore są oznaczone numer.pdf (np. `100.pdf`, `101.pdf`), jak i raporty zawierajace w nazwie slowo `raport` (np. `raport_14_sesja.pdf`).
- Wyniki są zapisywane w czytelnym pliku tekstowym.
- Program posiada prosty interfejs graficzny (GUI) – nie wymaga znajomości programowania.
- Program w oparciu o pisma ustaw urzędu gmina https://www.bip.gruta.akcessnet.net/index.php?idg=3&id=15&x=60 BRAK GWARANCJI DZIAŁANIA NA INNYCH DOKUMENTACH NIŻ URZĘDU GRUTA

## Szybki start

### 1. Pobierz i uruchom

- Przejdź do folderu `dist`.
- Uruchom plik `Uchwalomat.PDF.exe` (nie wymaga instalacji Pythona ani bibliotek).

### 2. Jak używać?

1. **Uruchom program** – dwuklik na pliku `.exe`.
2. **Wybierz folder** z plikami PDF (przycisk „Przeglądaj”).
3. **Kliknij „Generuj raport”**.
4. Po chwili plik `wyniki.txt` pojawi się w wybranym folderze i otworzy się automatycznie.

## Funkcje

- **Automatyczne rozpoznawanie tytułów uchwał** – wydobywa tytuł do frazy „Na podstawie”.
- **Inteligentne generowanie tytułów raportów** – numer sesji pobierany z ostatniej strony PDF, data z pierwszej.
- **Sortowanie wyników** – uchwały według numerów, raporty na końcu.
- **Przyjazny interfejs** – obsługa przez okno, bez linii poleceń.
- **Podpis i branding** – na końcu pliku wynikowego automatyczny podpis projektu.

## Wymagania

- System Windows 7/8/10/11
- Pliki PDF muszą być tekstowe (nie skany/obrazy)

## Pliki w projekcie

| Plik/Folder         | Opis                                      |
|---------------------|-------------------------------------------|
| `dist/Uchwalomat.PDF.exe` | Gotowy program do uruchomienia         |
| `uchwalomatgui.py`  | Kod źródłowy programu (Python)            |
| `icon.ico`          | Ikona programu                            |
| `README.md`         | Ten plik z instrukcją                     |

## Autor

Wygenerowano przy pomocy **UchwałoMat.PDF**, projekt – Jakub Budzich

## Skrót (TL;DR)

- Uruchom `Uchwalomat.PDF.exe` z folderu `dist`
- Wskaż folder z PDF-ami
- Kliknij „Generuj raport”
- Otworzy się plik `wyniki.txt` z tytułami wszystkich uchwał i raportów

**Masz pytania lub chcesz zgłosić sugestię? Skontaktuj się przez GitHub lub bezpośrednio z autorem!**
