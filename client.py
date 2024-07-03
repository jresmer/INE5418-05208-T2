import kazoo.client
from random import sample
from time import sleep, time
import threading


class Node:

    def __init__(self, node_id: int=None, f: int=1, server_ip: str="localhost") -> None:
        # initializing zookeeper client
        self.client = kazoo.client.KazooClient(f"{server_ip}:2181,{server_ip}:2182,{server_ip}:2183")
        self.client.start()
        # ensuring the existence of the root znode and recovering the f value
        if not self.client.exists("root"):
            self.client.create("root", value=bytes(f"{f}", "utf-8"))
        else:
            f = self.client.get("root")[0]
            f = f.decode("utf-8")
            f = int(f)
        # ensuring the existence of the znode corresponding to the node id
        self.znodes = [node for node in self.client.get_children("root", watch=self.update_znode_list) if node != f"{node_id}"]
        if node_id is None:
            max_id = max(self.znodes + ['0'])
            node_id = int(max_id) + 1
        self.n_replicas = f
        self.id = node_id
        self.path = f"root/{node_id}"
        self.client.ensure_path(self.path)
        self.client.get(self.path, watch=self.react_to_change)
        # initializing local tuple set
        self.tuples = set()
        # inizialize replica mapper
        self.replicas = dict()
        # initializting search control variables
        self.waiting_for_search = ()
        self.search_result = ()
        self.lock = threading.Lock()
    
    def get_tuples(self) -> set:

        return self.tuples

    def update_znode_list(self, *args) -> None:

        self.znodes = [node for node in self.client.get_children("root", watch=self.update_znode_list) if node != self.path[5:]]

    def remove(self, t: tuple):

        # removes tuple from space
        self.tuples.remove(t)
        for node in self.replicas[t]:

            value = bytes(f"remove:{t}", "utf-8")
            self.client.set(f"root/{node}", value=value)
        del self.replicas[t]

    def replicate(self, replicas: list, t: str) -> None:
        # sends a write request to all the replicas
        value = bytes(f"write:{replicas + [self.path[5:]]}:{t}", "utf-8")
        for node in replicas:

            self.client.set(f"root/{node}", value=value)
            if t not in self.replicas.keys():
                self.replicas[t] = {node}
            else:
                self.replicas[t].add(node)

    def __search(self, fields):
        # searches locally for a tuple
        selected = None
        for local_t in self.tuples:

            valid = True
            for field, value in enumerate(fields):

                if value in {"*", "_"} :
                    continue

                if value != local_t[field]:
                    valid = False
                    break

            if valid:
                selected = local_t
                break

        return selected

    def look_for_tuple(self, t: list) -> tuple:
        # controls local search
        path, t = t
        selected = None
        fields = eval(t)
        selected = self.__search(fields)

        if selected is not None:
            value = bytes(f"found:{selected}", "utf-8") 
            self.client.set(path, value=value)
        else:
            value = bytes(f"not found:{self.path}", "utf-8") 
            self.client.set(path, value=value)

        return selected


    def react_to_change(self, *args) -> None:
        # to provent other threads to react concorrently
        self.lock.acquire()
        # general callback/watcher function
        # reacts to changes to the nodes' corresponding znode
        value = self.client.get(self.path)[0]
        value = value.decode("utf-8")
        request, *t = value.split(":")
        print(f"{self.id} reacting to {request} type request")

        if request == "write":
            replicas, t = t
            replicas = eval(replicas)
            replicas.remove(self.path[5:])
            t = eval(t)
            if t in self.tuples:
                self.client.get(self.path, watch=self.react_to_change)
                self.lock.release()
                return
            self.tuples.add(t)
            self.replicate(replicas, t)
        elif request == "get":
            selected = self.look_for_tuple(t)
            if selected is None:
                self.client.get(self.path, watch=self.react_to_change)
                self.lock.release()
                return

            self.remove(selected)
        elif request == "read":
            selected = self.look_for_tuple(t)
        elif request == "found":
            if not self.waiting_for_search:
                self.client.get(self.path, watch=self.react_to_change)
                self.lock.release()
                return
            t = eval(t[0])
            self.waiting_for_search = set()
            self.search_result = t
        elif request == "not found":
            path = t[0]
            node = path[5:]
            self.waiting_for_search.remove(node)
        elif request == "remove":
            t = eval(t[0])
            if t in self.tuples:
                self.remove(t)

        self.client.get(self.path, watch=self.react_to_change)
        self.lock.release()

    def get(self, t: str) -> tuple:

        self.search_result = ()
        # waits for
        while len(self.search_result) == 0:

            # does local search first
            local_result = self.__search(t)
            if local_result is not None:
                self.remove(local_result)
                return local_result
            # searchs in other nodes
            self.waiting_for_search = set(self.znodes)
            for node in self.znodes:

                value = bytes(f"get:{self.path}:{t}", "utf-8")
                self.client.set(f"root/{node}", value=value)

            sleep(2)

        return self.search_result

    def read(self, t: str) -> tuple:

        self.waiting_for_search = set(self.znodes)
        self.search_result = ()

        local_result = self.__search(t)
        if local_result is not None:
            return local_result
        
        start = time()
        for node in self.znodes:

            value = bytes(f"read:{self.path}:{t}", "utf-8")
            self.client.set(f"root/{node}", value=value)
        
        sleep(0.2)
        while len(self.waiting_for_search) > 1:

            if time() - start >= 2:
                # delete inactive nodes from the vision
                # for node in self.waiting_for_search:
                #     path = f"root/{node}"
                #     if path == self.path:
                #         continue
                #     print(f"deleting: {path}")
                #     self.client.delete(path)
                break
        
        return self.search_result

    def write(self, t: str) -> None:
        # if tuple already exits in space aborts operation
        response = self.read(t)
        if len(response) != 0:
            print("already there")
            return
        # every replica multicasts in caise there's a fault mid loop
        self.tuples.add(t)
        me = self.path[5:]
        znodes = [node for node in self.znodes if node != me]
        replicas = sample(znodes, min(len(znodes), self.n_replicas))
        print(f"replicas={replicas}")
        self.replicate(replicas, t)
