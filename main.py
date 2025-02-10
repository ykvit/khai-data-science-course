from calculations import CALCULATIONS
import traceback


def get_input_values():

    try:
        return float(input("Введіть a: ")), float(input("Введіть b: "))
    except ValueError:
        print("Невірне числове значення!")
        return None, None

def main():

    try:
        variant = int(input(f"Виберіть варіант обчислення (1-{len(CALCULATIONS)}): "))
        if variant not in CALCULATIONS:
            print("Невірний варіант!")
            return

        calc = CALCULATIONS[variant]
        print(f"Формула: {calc['formula']}")

        a, b = get_input_values()
        if a is None or b is None:
            return

        try:
            result = calc['func'](a, b)
            print(f"Результат: {result}")
        except ZeroDivisionError:
            print("Помилка: ділення на нуль!")
        except Exception as e:
            print(f"Сталася помилка: {e}")
            traceback.print_exc()

    except ValueError:
        print("Невірне значення для варіанту!")

if __name__ == '__main__':
    main()
