class Logger:
    def __enter__(self):
        print("Start sekcji logowania")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Koniec sekcji logowania")
        return False


with Logger():
    print("Wykonuję kod wewnątrz bloku with")