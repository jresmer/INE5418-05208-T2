
from client import Node
from time import sleep
import keyboard


class Client:
    def __init__(self, ID: str, name: str, age: int):
        self.ID = ID
        self.name = name
        self.age = age
    
    def get_info(self) -> tuple:
        return (self.ID, self.name, self.age)

class Book:
    def __init__(self, ID: str, title: str, author: str, year: str, publisher: str):
        self.ID = ID
        self.title = title
        self.author = author
        self.year = year
        self.publisher = publisher
    
    def get_info(self) -> tuple:
        return (self.ID, self.title, self.author, self.year, self.publisher)

class Loan:
    def __init__(self, book: Book, client: Client):
        self.book = book
        self.client = client


class LibraryManager:
    def __init__(self):
        # self.book_node = Node(1)
        self.clients: dict[str, Client] = {}
        self.loans: dict[tuple, Loan] = {}
    
    def search_client(self, ID: str) -> Client:
        try:
            return self.clients[ID].get_info()
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
        t = self.book_node.get(book_info)
        book = Book(*t)
        client = self.clients[client_id]
        self.loans[(client.ID, book.ID)] = Loan(book, client)

    def return_book(self, client_id: str, book_id: str):
        try:
            loan = self.loans[(client_id, book_id)]
        except KeyError:
            print("ERROR: Loan not found")
        
        book = loan.book
        client = loan.client

        t = book.get_info()
        self.book_node.write(t)
        try:
            del self.loans[(client_id, book_id)]
        except KeyError:
            print("ERROR: Couldn't delete loan")
    
    def add_book(self, ID: str, title: str, author: str, year: str, publisher: str):
        book = Book(ID, title, author, year, publisher)
        t = book.get_info()
        print(t)
        self.book_node.write(t)

    def search_book(self, ID: str, title: str, author: str, year: str, publisher:str):
        book = Book(ID, title, author, year, publisher)
        t = book.get_info()
        t = self.book_node.read(t)
        return t

if __name__ == "__main__":
    
    

    # lib_manager.add_client('c1', "Tiago", 21)
    # lib_manager.add_book('b1', "Dune", "Frank Herbert", "1965", "Chilton Books")
    # sleep(3)
    # a = lib_manager.search_book('b1', "Dune", "_", "_", "_")
    # print(a)
    # sleep(3)
    # lib_manager.add_book('b2', "Witcher", "Andrzej Sapkowski", "1986", "Fantastyka")
    # sleep(3)
    # lib_manager.loan_book('c1', 'b1')
    # lib_manager.return_book('c1', 'b1')

    '''
    INSTRUCTIONS:
        addbk -i id -t title -a author -y year -p publisher  # ADD BOOK
        addcli -i id -n name -a age                              # ADD CLIENT
        getcli -i id                                                 # GET CLIENT INFO BY ID
        getbk -i id -t title -a author -y year -p publisher  # GET BOOK INFO
        rmvcli -i id                                                 # REMOVE CLIENT BY ID
        mkloan -c clientID -b bookid -t title -a author -y year -p publisher
        rmloan -c clientID -b bookid
    '''

    lib_manager = LibraryManager()
    run = True
    while run:
        request = input()
        items = [x.split(" ") for x in request.split(" -")]
        # print(items)
        cmd = items[0][0]
        args = {item[0]: item[1] for item in items[1:]}
        # print(args)

        if cmd == "addbk":
            id = args.get('i', '_')
            title = args.get('t', '_')
            author = args.get('a', '_')
            year = args.get('y', '_')
            publisher = args.get('p', '_')

            lib_manager.add_book(id, title, author, year, publisher)
        elif cmd == "addcli":
            id = args.get('i', '_')
            name = args.get('n', '_')
            age = args.get('a', '_')
            
            lib_manager.add_client(id, name, age)
        elif cmd == "getcli":
            id = args.get('i', '_')
            t = lib_manager.search_client(id)
            info = " ".join(t)
            print(f"Client: {info}")
        elif cmd == "getbk":
            id = args.get('i', '_')
            title = args.get('t', '_')
            author = args.get('a', '_')
            year = args.get('y', '_')
            publisher = args.get('p', '_')

            t = lib_manager.search_book(id, title, author, year, publisher)
            info = " ".join(t)
            print(f"Book: {info}")
        elif cmd == "rmvcli":
            id = args.get('i', '_')

            lib_manager.remove_client(id)
        elif cmd == "mkloan":
            client_id = args.get('c', '_')
            book_id = args.get('b', '_')
            title = args.get('t', '_')
            author = args.get('a', '_')
            year = args.get('y', '_')
            publisher = args.get('p', '_')

            lib_manager.loan_book(client_id, book_id, title, author, year, publisher)
        elif cmd == "rmloan":
            client_id = args.get('c', '_')
            book_id = args.get('b', '_')
            
            lib_manager.return_book(client_id, book_id)
        elif cmd == "quit":
            run = False
            print("Goodbye")