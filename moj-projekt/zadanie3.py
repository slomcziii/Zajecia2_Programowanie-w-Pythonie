class FileWriter:
    def __init__(self, sciezka):
        self.sciezka = sciezka

    def __enter__(self):
        self.plik = open(self.sciezka, "w", encoding="utf-8")
        return self.plik

    def __exit__(self, exc_type, exc_value, traceback):
        self.plik.close()

        if exc_type is not None:
            print(f"Błąd podczas zapisu: {exc_value}")

        return False


with FileWriter("blad.txt") as plik:
    plik.write("Ten tekst został zapisany przed błędem.\n")
    raise ValueError("Testowy błąd")

print("Ten komunikat się nie wyświetli.")