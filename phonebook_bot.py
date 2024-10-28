from collections import UserDict
from datetime import datetime
import re
from datetime import datetime, timedelta
from colorama import Fore

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    

class Name(Field):
		pass


class Phone(Field):
    def __init__(self, value):
        if re.match(r'^\d{10}$', value):
            super().__init__(value)
        else:
            raise ValueError("Invalid phone number. The number must consist of 10 digits.")
        
        


class Birthday(Field):
    def __init__(self, value):

        if re.match(r'^\d{2}\.\d{2}\.\d{4}$', value):
            try:
                birthday = datetime.strptime(value, '%d.%m.%Y').date()
            except:
                raise ValueError("Invalid date format. Ensure it exist.")
            
            super().__init__(birthday)

        else:
            raise ValueError("Invalid date format. Use the 'DD.MM.YYYY' format.")
        

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        return f"contact name: {self.name}, phones: {'; '.join(str(p) for p in self.phones)}"

    def add_phone(self, phone: Phone):
            self.phones.append(phone)
            return (f"Phone {phone} added to contact {self.name}")
        
    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p == phone]
        return (f"Phone {phone} deleted")
    
    def edit_phone(self, old_phone, new_phone):
        for index, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[index] = Phone(new_phone)
                return f"Phone {old_phone} changed to {new_phone}"
        return f"Phone {old_phone} not found"

    def find_phone(self, phone):
        for p in self.phones:
            if p == phone:
                return p
            elif p not in self.phones:
                return (f"Phone {phone} not found")

    def add_birthday(self, birthday: Birthday):
        self.birthday = birthday
        return (f"Birthday {birthday} added")


       

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[str(record.name)] = record
        return (f"Contact {record.name} added to address book")

    def find(self, name):
        return self.data.get(name, None)


    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return (f"Contact {name} deleted")
        else:
            return (f"Contact {name} not found")
    
    def get_upcoming_birthdays(self):
        congrats_list = []
        today = datetime.now().date()
    
        for contact in self.data.values():
            birthday = contact.birthday
            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday.replace(year=today.year + 1)
            
            days_until_birthday = (birthday_this_year - today).days

            if 0 <= days_until_birthday <= 7:

                if birthday_this_year.weekday() == 5:
                    birthday_this_year += timedelta(days=2)
                elif birthday_this_year.weekday() == 6:
                    birthday_this_year += timedelta(days=1)

                congrats_list.append({ contact.name: birthday_this_year.strftime("%d.%m.%Y") })

        return congrats_list





def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return e
        except ValueError as e:
            return e
        except IndexError as e:
            return e
        except Exception as e:
            return f'An unexpected error occurred: {e}. Please try again.'
    return inner

def parse_input(user_input):
    if not user_input.strip():
        return None, []
    
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def colored_output(phrase):
    return Fore.GREEN + phrase + Fore.RESET

def colored_error(phrase):
    return Fore.RED + phrase + Fore.RESET

def colored_info(phrase):
    return Fore.YELLOW + phrase + Fore.RESET





@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = colored_output(f"Contact {record.name} added to address book.")
    else:
        message = colored_output(f"Contact {record.name} updated.")

    if phone:
        record.add_phone(Phone(phone))

    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)

    if record is None:
        raise IndexError(colored_error(f"Contact '{name}' not found. Use 'add' to create it."))
    
    result = record.edit_phone(old_phone, new_phone)

    return colored_output(result)

@input_error
def show_phone(args, book: AddressBook):
    if not args:
        raise ValueError(colored_error("No contact name provided."))
    
    name = args[0]
    record = book.find(name)
    if record:
        phones = '; '.join(str(phone) for phone in record.phones)
        return colored_output(f"Contact '{name}' phones: {phones}")
    else:
        raise IndexError(colored_error(f"Contact '{name}' not found."))
    
@input_error
def show_all(book: AddressBook):
    if not book.data:
        raise ValueError(colored_error("No contacts available."))
    
    result = [f"{record}" for _, record in book.data.items()]
    return colored_output('\n'.join(result))

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if not record:
        raise IndexError(colored_error(f"Contact '{name}' not found. Use 'add' to create it."))
    
    result = record.add_birthday(birthday)
    return colored_output(result)

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if not record:
        raise IndexError(colored_error(f"Contact '{name}' not found. Use 'add' to create it."))
    
    result = f"{record.name} has Birthday on {record.birthday}"
    return colored_output(result)
    
@input_error
def show_all_birthdays(book: AddressBook):
    if not book.data:
        raise ValueError(colored_error("No contacts available."))
    
    result = book.get_upcoming_birthdays()
    return colored_output('\n'.join(result))
    
    


# ?? @input_error
def show_info():
    result = [
        colored_output('add <name> <phone>') + ': adds a new contact (e.g., add John 123456789)',
        colored_output('change <name> <phone>') + ': changes the phone number of an existing contact (e.g., change John 987654321)',
        colored_output('phone <name>') + ': shows the phone number of the specified contact (e.g., phone John)',
        colored_output('all') + ': shows all contacts in your phonebook',
        colored_output('info') + ': displays the list of available commands',
        colored_output('close or exit') + ': exits the application'
    ]
    return colored_info("Available commands:\n" + '\n'.join(result))




def main():
    book = AddressBook()
    print(("Welcome to the assistant bot!"))
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print(colored_info("Good bye!" + Fore.RESET))
            break

        elif command == "hello":
            print(colored_info("How can I help you?" + Fore.RESET)) #works

        elif command == "add":
            print(add_contact(args, book)) #works

        elif command == "change":
            print(change_contact(args, book)) #works

        elif command == "phone":
            print(show_phone(args, book)) #works

        elif command == "all":
            print(show_all(book)) #works

        elif command == "add-birthday":
            print(add_birthday(args, book)) #works

        elif command == "show-birthday":
            print(show_birthday(args, book)) #works

        elif command == "birthdays":
            print(show_all_birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()