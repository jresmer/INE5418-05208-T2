from client import Node
from time import sleep


n = Node(1)
for i in range(5):

    t = (1, i, i**2)
    print(t)
    n.write(t)
    sleep(1)

while 1:
    pass