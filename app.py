
from collections import UserDict
from collections import defaultdict
import datetime as dt
import re
import pickle
from abc import abstractmethod, ABCMeta


#********************************************
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value) 

class Name(Field):
   
    # реалізація класу
     def __init__(self, value):
        super().__init__(value)
	
class Phone(Field):
    # реалізація класу
    def __init__(self,value ):
        self.__value=None
        self.value=value
    @property
    def value(self):
        return self.__value
    @value.setter
    def value(self, value):
            
        if re.fullmatch(r"\d{10}", value):
           self.__value=value
        else:
           raise ValueError('Невалідний телефон!')
	
    
class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = dt.datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phone =''
        self.birthday = None
    
    def add_phone(self, phone):  
        self.phone= Phone(phone)
    
    
    def find_phone(self,name):
        if self.name.value==name:
            mess=f"{self.name}s phone is {self.phone}"
        else:
            mess=f"Phone {name}s not found!"
        return mess
        

    def remove_phone(self):
        self.phone=''

    def edit_phone(self, phone_new):
        if self.phone:
            self.phone.value =phone_new
            print(f"Номер {self.name.value} змінено!")
           
    
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
        mess = f"{self.name.value}'s birthday added!"
        return mess
    

    def __str__(self):
        return f"Contact name: {self.name.value}, phone: { self.phone.value}"

class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value]=record


    def find(self,name):
        for n in self.data:
            if n==name:
                return self.data.get(n)
            elif n != name:
                continue
            else:
                return "No such contact."
    
  
  
    def delete(self,name):
        if name in self.data: 
            self.data.pop(name)
            print("Зап ис видалено")
        else: 
            print("Запис не знайдено")
    
    def get_upcoming_birthdays(self):  
        days=7
        today=dt.datetime.today().date()
        upcoming_birthdays=[]
     
        for user in self.data:
            if self.data:
                if self.data[user].birthday is not None:
                    birthday=dt.datetime.strptime(self.data[user].birthday.value, "%d.%m.%Y").date()
                    birthday_this_year=birthday.replace(year=today.year)
                    if birthday_this_year <  today:
                        birthday_this_year=birthday_this_year.replace(year=today.year+1)
                    if 0 <= (birthday_this_year -  today).days < days:
                        if birthday_this_year.weekday() >=5:
                            days_ahead=0-birthday_this_year.weekday()
                            days_ahead +=7
                            birthday_this_year=birthday_this_year+ dt.timedelta(days=days_ahead)
                        congratulation_date_str=birthday_this_year.strftime("%d.%m.%Y")
                        upcoming_birthdays.append({"name":user, "birthday":congratulation_date_str})

        return upcoming_birthdays

class MyOutputABC(metaclass=ABCMeta):
    @abstractmethod
    def add_contact(self,args, book: AddressBook):
        pass
    @abstractmethod
    def change_contact(self, args, book: AddressBook):
        pass
    @abstractmethod
    def show_phone(self,args, book: AddressBook):
        pass

    @abstractmethod
    def add_birthday(self,args,book:AddressBook):
        pass
    @abstractmethod
    def show_all(self,book:AddressBook):
        pass
    @abstractmethod
    def show_birthday(self,args, book: AddressBook):
        pass
    
    @abstractmethod
    def birthdays(self,book: AddressBook):
        pass
    
  

class MyOutputTerminal(MyOutputABC):
    def __init__(self, book: AddressBook):
        self.book=book
    
    def add_contact(self, args, book: AddressBook):
        name, phone, *_ = args
        record = book.find(name)
        mess = "Contact updated." 
        if record is None:
            record= Record(name)
            book.add_record(record)
            mess="Contact added."
        if phone:
            record.add_phone(phone)  
        print(record)
        return mess


    def change_contact(self,args, book: AddressBook):
        name, phone,*_ = args 
        record = book.find(name)
        if record:
            record.edit_phone(phone)
            mess="Contact updated."
        else:
            mess="Contact not found"
        return mess
    

    def show_phone(self,args, book: AddressBook):
        name, *_ = args
        record = book.find(name)
        if record:
            return str(record.find_phone(name))
        else:
            return "Contact not found."


        
   
    def add_birthday(self,args,book:AddressBook):
        name, birthday, *_ = args
        record = book.find(name)
        if record:
            print("Birthday added")
            return str(record.add_birthday(birthday))
        else:
            return "Contact not found."
        
   
    def show_all(self,book:AddressBook):
        print("AddressBook:") 
        for record_name, record in book.items():
            print(f"Name: {record_name}")
            print(f"Phone: {record.phone.value}")
            if record.birthday:
                print(f"Birthday: {record.birthday.value}")
            print("-" * 20)
        

    def show_birthday(self,args, book: AddressBook):
        name,*_ = args
        record = book.find(name)
        if record:
            if record.birthday.value!= None:
                print(f"{record.name}s Birthday: {str(record.birthday.value)}")
            else:
                print(f"I dont know {record.name}s birthday date :(")

        else:print("Contact not found.")
   
    def birthdays(self,book: AddressBook):
        upcoming_birthdays = book.get_upcoming_birthdays()
        if upcoming_birthdays:
            print(f"Список іменинників: {upcoming_birthdays}")
        else:
            print("No upcoming birthdays.")        


   #********************************************



def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args





def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

  
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook() 

# Створення нової адресної книги
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return  "KeyError"
        except IndexError:
            return  "IndexError"
        except AttributeError:
            return "AttributeError"

    return inner
 
def output_concel():
    book = load_data()
    output_terminal = MyOutputTerminal(book)
    print("-" * 20)
    print("Welcome to the AddressBooks assistant bot!")
    print("-" * 20)
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            print("-" * 20)
            break
        elif command in ["hello", "hi"]:
            print("How can I help you?")
            print("I have comands: [add]/[change] /[phone]/[show all]/[add-birthday]/[show-birthday/birthdays])))")
            print("-" * 20)
        elif command == "add":
            print(output_terminal.add_contact(args, book))
        elif command == "change":
            print(output_terminal.change_contact(args, book))
        elif command == "phone":
            print(output_terminal.show_phone(args, book))
        elif command == "show":
        
            output_terminal.show_all(book)
        elif command == "add-birthday":
            
            output_terminal.add_birthday(args, book)
        elif command == "show-birthday":
           
            output_terminal.show_birthday(args, book)
        elif command == "birthdays":
           
            output_terminal.birthdays(book)
        else:
            print("Invalid command.")
            print("-" * 20)
#==============================================

def main():
    output_concel() 

if __name__ == "__main__":
    main()
    