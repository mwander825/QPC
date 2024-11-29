from pathlib import Path

import datetime
import os
import time

data_fp = Path(__file__).parents[1] / "data"
file_name = "Expenses - Expense_Data.csv"
file_path = data_fp / file_name

type_dict = {'0': 'Savings',
             '1': 'Rent',
             '2': 'Utilities',
             '3': 'Grocery',
             '4': 'Food',
             '5': 'Shop',
             '6': 'RecEnt',
             '7': 'TransportationT',
             '8': 'HealthWell',
             '9': 'Other'}

today = datetime.datetime.today().date().strftime("%m/%d/%Y")


def insert_line(line: str, backup: bool = True):
    with open(file_path, "a") as file:
        file.write(line)


def backup():
    try:
        backup_file_name = f"{file_name}_{datetime.datetime.today().strftime('%Y%m%d%H%M%S')}.csv"
        backup_file_dir = data_fp / "backup"
        if not os.path.isdir(backup_file_dir):
            os.mkdir(backup_file_dir)
        with open(os.path.join(backup_file_dir, backup_file_name), "w") as file:
            with open(file_path, "r") as og_file:
                file.write(og_file.read())
                print("Data successfully backed up.\n")
                return True
    except Exception as e:
        print(str(e) + "\n")
        print("Data backup failed.\n")
        return False


def insert_term(insert_input):
    line_elements = []

    # name of expense
    if insert_input == 'q':
        return False
    line_elements.append(str(insert_input))

    # amount in USD (int or float)
    expense_input = input("\nExpense Amount? (int or float)\n")
    if expense_input == 'q':
        return False
    while not expense_input.replace(".", "").isnumeric():
        expense_input = input("\nExpense Amount? (int or float)\n")
    line_elements.append(str(float(expense_input)))

    # type / category input
    expense_input = input(f"""\nExpense Type?
{chr(10).join([f"{k}: {v}" for k, v in type_dict.items()])}\n""")
    if expense_input == 'q':
        return False
    while not expense_input.isnumeric() or expense_input not in type_dict.keys():
        expense_input = input(f"""\nExpense Type?
{chr(10).join([f"{k}: {v}" for k, v in type_dict.items()])}\n""")
    line_elements.append(type_dict[expense_input])

    # date of expense
    expense_input = input("\nExpense Date (mm/dd/yyyy)? (Input enter to default to today's date)\n")
    if expense_input == 'q':
        return False
    while expense_input != '' and (len(expense_input) != 10 or not expense_input.replace("/", "").isnumeric()):
        expense_input = input("\nExpense Date (mm/dd/yyyy)? (Input enter to default to today's date)\n")
    if expense_input == '':
        expense_input = today
    line_elements.append(expense_input)

    # confirming information to insert line into data .csv
    expense_input = input(f"""\nConfirm expense line (y/n):
Name: {line_elements[0]}
Amount: {line_elements[1]}
Type: {line_elements[2]}
Date: {line_elements[3]}\n""")
    if expense_input == 'q':
        return False
    if expense_input == 'y':
        insert_line(','.join(line_elements) + "\n")
        print("Data written.")
        time.sleep(0.5)
        return True
    elif expense_input == 'n':
        print("\nAborting insert.")
        time.sleep(0.5)
        return True


if __name__ == "__main__":
    result = True
    while result:
        main_input = input("Expense Name? (Input 'b' to backup data. Input 'q' at any time to quit.)\n")
        if main_input == 'q':
            result = False
        elif main_input == 'b':
            backup()
        else:
            result = insert_term(main_input)
        time.sleep(0.5)
        os.system("cls")
