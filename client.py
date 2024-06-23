import kazoo.client
from random import sample
from time import sleep


class Node:

    def __init__(self, node_id: int) -> None:

        self.client = kazoo.client.KazooClient("localhost:2181,localhost:2182,localhost:2183")
        self.client.start()
        # get f
        f = self.client.get("root")[0]
        self.n_replicas = int(f)
        self.znodes = list(self.client.get_children("root", watch=self.update_znode_list))
        self.path = f"root/{node_id}"
        self.client.ensure_path(self.path)
        self.client.get(self.path, watch=self.react_to_change)
        self.tuples = set()
        self.replicas = dict()
    

        self.waiting_for_search = ()
        self.search_result = ()
        self.id = node_id
        # inizialize replica mapper
        for node in self.znodes:

            self.replicas[node] = set()

    def update_znode_list(self, *args) -> None:

        self.znodes = list(self.client.get_children("root"))

    def remove(self, t: tuple):

        # removes tuple from space
        self.tuples.remove(t)
        del self.replicas[t]

    def replicate(self, replicas: list, t: str) -> None:

        for node in replicas:

            value = bytes(f"write:{replicas}:{t}", "utf-8")
            self.client.set(f"root/{node}", value=value)
            if t not in self.replicas.keys():
                self.replicas[t] = {node}
            else:
                self.replicas[t].add(node)

    def look_for_tuple(self, t: list) -> tuple:

        path, t = t
        selected = None
        fields = eval(t)
        print(f"looking for {t} in {self.tuples}")
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
            value = bytes(f"found:{selected}", "utf-8") 
            self.client.set(path, value=value)
            print(f"answer: {value}")
        else:
            value = bytes(f"not found", "utf-8") 
            self.client.set(path, value=value)
            print(f"answer: {value}")

        return selected

    def react_to_change(self, *args) -> None:

        
        value = self.client.get(self.path)[0]
        value = value.decode("utf-8")
        request, *t = value.split(":")
        print(f"{self.id} reacting to {request} request ")

        if request == "write":
            replicas, t = t
            replicas = eval(replicas)
            self.tuples.add(t)
            self.replicate(replicas, t)
        elif request == "get":
            selected = self.look_for_tuple(t)
            for node in self.replicas[selected]:

                value = bytes(f"remove:{selected}", "utf-8")
                self.client.set(f"root/{node}", value=value)

            self.remove(selected)
        elif "read":
            selected = self.look_for_tuple(t)
        elif "found":
            if not self.waiting_for_search:
                return
            t = eval(t[0])
            self.waiting_for_search = set()
            self.search_result = t
        elif "not_found":
            node = args[0].path.split("/")
            node = node[1]
            self.waiting_for_search.remove(node)
        elif "remove":
            t = eval(t[0])
            self.remove(t)

    def get(self, t: str) -> tuple:

        self.search_result = ()

        while (self.search_result) == 0:

            self.waiting_for_search = set(self.znodes)
            for node in self.znodes:

                value = bytes(f"get:{self.path}:{t}", "utf-8")
                self.client.set(f"root/{node}", value=value)

            sleep(2)

        return self.search_result

    def read(self, t: str) -> tuple:

        self.waiting_for_search = set(self.znodes)
        self.search_result = ()

        print(self.znodes)
        
        for node in self.znodes:

            value = bytes(f"read:{self.path}:{t}", "utf-8")
            self.client.set(f"root/{node}", value=value)

        while len(self.waiting_for_search) > 1:
            pass
        
        return self.search_result


    def write(self, t: str) -> None:
        # every replica multicasts in caise there's a fault mid loop
        self.tuples.add(t)
        replicas = sample(self.znodes, self.n_replicas)
        self.replicate(replicas, t)

