class SafeDivision:
    def __enter__(self):
        return self

    def divide(self, a, b):
        return a / b

    def __exit__(self, exc_type, exc_value, traceback):
        if isinstance(exc_value, ZeroDivisionError):
            print("Nie można dzielić przez zero")
            return True

        return False


with SafeDivision() as dzielenie:
    print("10 / 2 =", dzielenie.divide(10, 2))
    print("10 / 0 =", dzielenie.divide(10, 0))

print("Program działa dalej.")