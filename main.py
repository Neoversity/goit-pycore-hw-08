import pickle
from datetime import datetime, timedelta
from collections import UserDict


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Phone number cannot be empty")
        try:
            self.validate(value)
        except ValueError as e:
            print(e)
        super().__init__(value)

    @staticmethod
    def validate(value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must be 10 digits and contain only digits")


class Birthday(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Birthday cannot be empty")
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

    @staticmethod
    def validate(value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        try:
            Phone.validate(phone)
            self.phones.append(Phone(phone))
        except ValueError as e:
            print(e)

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        try:
            Phone.validate(new_phone)
            for phone in self.phones:
                if str(phone) == old_phone:
                    phone.value = new_phone
                    return
            print(f"Phone number {old_phone} not found.")
        except ValueError as e:
            print(e)

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p
        return None

    def add_birthday(self, birthday):
        if self.birthday:
            raise ValueError("Birthday already exists for this record")
        self.birthday = Birthday(birthday)

    def __str__(self):
        birthday_str = str(self.birthday) if self.birthday else "None"
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}, birthday: {birthday_str}"


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Error: {e}"

    return wrapper


@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise ValueError("Usage: add-birthday [name] [DD.MM.YYYY]")

    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        return f"Contact '{name}' not found."


@input_error
def show_birthday(args, book):
    if len(args) != 1:
        raise ValueError("Usage: show-birthday [name]")

    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday.value}"
    elif record:
        return f"{name} doesn't have a birthday set."
    else:
        return f"Contact '{name}' not found."


@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join(str(record) for record in upcoming_birthdays)
    else:
        return "No upcoming birthdays in the next week."


@input_error
def change_phone(args, book):
    if len(args) != 2:
        raise ValueError("Usage: change [name] [new_phone]")

    name, new_phone = args
    record = book.find(name)
    if record:
        old_phone = str(
            record.phones[0]
        )  # Припускаємо, що у кожного контакту є лише один номер телефону
        record.edit_phone(old_phone, new_phone)
        return f"Phone number for {name} changed from {old_phone} to {new_phone}."
    else:
        return f"Contact '{name}' not found."


@input_error
def show_phone(args, book):
    if len(args) != 1:
        raise ValueError("Usage: phone [name]")

    name = args[0]
    record = book.find(name)
    if record and record.phones:
        return f"{name}'s phone number: {record.phones[0]}"
    elif record:
        return f"{name} doesn't have a phone number set."
    else:
        return f"Contact '{name}' not found."


@input_error
def show_all(book):
    if book:
        return "\n".join(str(record) for record in book.values())
    else:
        return "Address book is empty."


class AddressBook(UserDict):
    def add_record(self, record):
        if not isinstance(record, Record):
            raise ValueError("Only Record objects can be added to AddressBook")
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        next_week = today + timedelta(days=7)
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(
                    record.birthday.value, "%d.%m.%Y"
                ).date()
                birthday_this_year = birthday_date.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                if today <= birthday_this_year <= next_week:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

    def save_to_file(self, filename):
        with open(filename, "wb") as f:
            pickle.dump(self.data, f)

    @classmethod
    def load_from_file(cls, filename):
        with open(filename, "rb") as f:
            data = pickle.load(f)
        address_book = cls()
        address_book.data = data
        return address_book


def parse_input(user_input):
    parts = user_input.split()
    command = parts[0]
    args = parts[1:] if len(parts) > 1 else []  # Додано перевірку на довжину parts
    return command, args


def hello():
    return "Hello! How can I assist you today?"


def close():
    return "Goodbye!"


def main():
    filename = "address_book.pkl"  # Файл для збереження адресної книги

    try:
        book = AddressBook.load_from_file(filename)
    except FileNotFoundError:
        book = AddressBook()

    while True:
        print(
            "add",
            "change",
            "phone",
            "all",
            "add-birthday",
            "show-birthday",
            "birthdays",
            "hello",
            "close",
            "exit",
        )
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command == "add":
            if len(args) != 2:
                print("Usage: add [name] [phone]")
            else:
                name, phone = args
                record = book.find(name)
                if record:
                    record.add_phone(phone)
                    print(f"Phone number added to existing contact '{name}'.")
                else:
                    new_record = Record(name)
                    new_record.add_phone(phone)
                    book.add_record(new_record)  # Використовуємо метод add_record
                    print(f"New contact '{name}' added with phone number '{phone}'.")

        elif command == "change":
            if len(args) != 3:
                print("Usage: change [name] [old_phone] [new_phone]")
            else:
                name, old_phone, new_phone = args
                record = book.find(name)
                if record:
                    record.edit_phone(old_phone, new_phone)
                else:
                    print(f"Contact '{name}' not found.")

        elif command == "phone":
            if len(args) != 1:
                print("Usage: phone [name]")
            else:
                name = args[0]
                record = book.find(name)
                if record:
                    print(
                        f"{name}'s phone numbers: {', '.join(str(p) for p in record.phones)}"
                    )
                else:
                    print(f"Contact '{name}' not found.")

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            if len(args) != 2:
                print("Usage: add-birthday [name] [DD.MM.YYYY]")
            else:
                name, birthday = args
                print(add_birthday([name, birthday], book))

        elif command == "show-birthday":
            if len(args) != 1:
                print("Usage: show-birthday [name]")
            else:
                name = args[0]
                print(show_birthday([name], book))

        elif command == "birthdays":
            upcoming_birthdays = book.get_upcoming_birthdays()
            if upcoming_birthdays:
                print("\n".join(str(record) for record in upcoming_birthdays))
            else:
                print("No upcoming birthdays in the next week.")

        elif command == "hello":
            print(hello())

        elif command in ["close", "exit"]:
            book.save_to_file(filename)  # Зберігаємо адресну книгу при закритті
            print(close())
            break
        else:
            print("Invalid command. Please try again.")


if __name__ == "__main__":
    main()
