import kazoo.client
from random import sample


class Node:

    def __init__(self) -> None:

        self.client = kazoo.client.KazooClient("localhost:2181,localhost:2182,localhost:2183")
        self.client.start()
        # get f
        f = self.client.get("root")
        self.n_replicas = int(f)
        self.znodes = list(self.client.get_children("root", watch=self.update_znode_list))
        self.path = self.client.create("root", makepath=True)
        self.client.get(self.path, watch=self.react_to_change)
        self.tuples = set()
        self.replicas = dict()
        self.tuple_queue = list()
        # inizialize replica mapper
        for node in self.znodes:

            self.replicas[node] = set()

    def update_znode_list(self) -> None:

        self.znodes = list(self.client.get_children("root"))

    def remove(self, t: tuple):

        # removes tuple from space
        self.tuples.remove(t)
        del self.replicas[t]

    def replicate(self, replicas: list, t: str) -> None:

        for node in replicas:

            t = eval(t)
            value = bytes(f"write:{replicas}:{t}", "utf-8")
            self.client.set(node, value=value)
            self.replicas[t].add(node)

    def look_for_tuple(self, t: list) -> tuple:

        path, t = t
        selected = None
        fields = eval(t)
        for local_t in self.tuples:

            valid = True
            for field, value in enumerate(fields):

                if value == "*":
                    continue

                if value != local_t[field]:
                    valid = False
                    break

            if valid:
                selected = local_t

        if selected is not None:
            value = bytes(f"found:{selected}") 
            self.client.set(path, value)

        return selected

    def react_to_change(self) -> None:

        value = self.client.get(self.path)
        value = str(value)
        request, *t = value.split(":")

        if request == "write":
            replicas, t = t
            replicas = replicas[1:-1].split(",")
            self.tuples.add(t)
            self.replicate(replicas, t)
        elif request == "get":
            t
            selected = self.look_for_tuple(t)
            for node in self.replicas[selected]:

                value = bytes(f"remove:{selected}", "utf-8")
                self.client.set(node, value=value)

            self.remove(selected)
        elif "read":
            selected = self.look_for_tuple(t)
        elif "found":
            t = eval(t[0])
            # store value somewhere
        elif "remove":
            t = eval(t[0])
            self.remove(t)

    def get(self, t: str) -> tuple:

        ...

    def read(self, t: str) -> tuple:

        ...

    def write(self, t: str) -> None:
        # every replica multicasts in caise there's a fault mid loop
        self.tuples.add(t)
        replicas = sample(self.znodes, self.n_replicas)
        self.replicate(replicas, t)
