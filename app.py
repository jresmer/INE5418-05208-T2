
from client import Node
from time import sleep


class Client:
    def __init__(self, ID: str, name: str, age: int):
        self.ID = ID
        self.name = name
        self.age = self.age

class Book:
    def __init__(self, ID: str, title: str, author: str, year: str, publisher: str):
        self.ID = ID
        self.title = title
        self.author = author
        self.year = year
        self.publisher = publisher
    
    def get_tuple(self) -> tuple:
        return (self.ID, self.title, self.author, self.year, self.publisher)

class Loan:
    def __init__(self, book: Book, client: Client):
        self.book = book
        self.client = client


class LibraryManager:
    def __init__(self):
        self.book_node = Node()
        self.clients: dict[str, Client] = {}
        self.loans: dict[tuple, Loan] = {}
    
    def get_client(self, ID: str) -> Client:
        try:
            return self.clients[ID]
        except KeyError:
            print("ERROR: Client not found")

    def add_client(self, ID: str, name: str, age: int):
        if ID not in self.clients:
            self.clients[ID] = Client(ID, name, age)
        else:
            print("ERROR: Client already registered")

    def remove_client(self, ID):
        try:
            del self.clients[ID]
        except KeyError:
            print("ERROR: Client not found")

    def loan_book(self, client_id: str, book_info: tuple):
        t = Node.get(book_info)
        book = Book(*t)
        client = self.get_client(client_id)
        self.loans[(client.ID, book.ID)] = Loan(book, client)

    def return_book(self, client_id: str, book_id: str):
        try:
            loan = self.loans[(client_id, book_id)]
        except KeyError:
            print("ERROR: Loan not found")
        
        book = loan.book
        client = loan.client

        t = book.get_tuple()
        self.node.write(t)
        try:
            del self.loans[(client_id, book_id)]
        except KeyError:
            print("ERROR: Couldn't delete loan")
    
    def add_book(self, ID: str, title: str, author: str, year: str, publisher: str):
        book = Book(ID, title, author, year, publisher)
        t = book.get_tuple()
        self.node.write(t)

if __name__ == "__main__":
    
    lib_manager = LibraryManager()

    lib_manager.add_client('c1', "Tiago", 21)
    lib_manager.add_book('b1', "Dune", "Frank Herbert", 1965, "Chilton Books")
    lib_manager.add_book('b2', "Witcher", "Andrzej Sapkowski", 1986, "Fantastyka")
    lib_manager.loan_book('c1', 'b1')
    sleep(3)
    lib_manager.return_book('c1', 'b1')