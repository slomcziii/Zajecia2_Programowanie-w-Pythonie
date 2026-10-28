class FileWriter:
    def __init__(self, sciezka):
        self.sciezka = sciezka

    def __enter__(self):
        self.plik = open(self.sciezka, "w", encoding="utf-8")
        return self.plik

    def __exit__(self, exc_type, exc_value, traceback):
        self.plik.close()
        return False


with FileWriter("notatka.txt") as plik:
    plik.write("Pierwsza linia tekstu.\n")
    plik.write("Uczę się programowania w Pythonie.\n")

print("Zapisano: notatka.txt")
print("Czy plik jest zamknięty?", plik.closed)