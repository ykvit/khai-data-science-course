from calculations import CALCULATIONS
import traceback


def get_input_values():
    # Gets two float numbers from user input, returns (None, None) if invalid
    try:
        return float(input("Enter  a: ")), float(input("Enter  b: "))
    except ValueError:
        print("Incorrect numerical value!")
        return None, None

def main():
    # Handles user interaction flow and calculation execution
    try:
        variant = int(input(f"Select a calculation variant (1-{len(CALCULATIONS)}): "))
        if variant not in CALCULATIONS:
            print("Incorrect variant!")
            return

        calc = CALCULATIONS[variant]
        print(f"Formula: {calc['formula']}")

        a, b = get_input_values()
        if a is None or b is None:
            return

        try:
            result = calc['func'](a, b)
            print(f"Result: {result}")
        except ZeroDivisionError:
            print("Error: division by zero!")
        except Exception as e:
            print(f"An error has occurred: {e}")
            traceback.print_exc()

    except ValueError:
        print("Invalid value for a variant!")

if __name__ == '__main__':
    main()

