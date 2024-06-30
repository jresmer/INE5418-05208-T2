from client import Node
from time import sleep


n = Node(2)

l = 0
sleep(4)
print("getting")
while 1:
    print("vivo")
    r = n.read((3, "*", "*"))
    print(r)
    if len(r) > 0:
        break
    sleep(3)

print("saiu")
while 1:
    pass