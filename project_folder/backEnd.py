import threading

class DeadlockDetector:
    def __init__(self):
        self.lock_graph = {}
        self.lock = threading.Lock()

    def detect_cycle(self):
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self.lock_graph.get(node, set()):
                if dfs(neighbor):
                    return True
            rec_stack.remove(node)
            return False
        
        return any(dfs(thread) for thread in self.lock_graph)

    def request_resource(self, thread_id, resource_id):
        with self.lock:
            if thread_id not in self.lock_graph:
                self.lock_graph[thread_id] = set()
            self.lock_graph[thread_id].add(resource_id)
            if self.detect_cycle():
                self.lock_graph[thread_id].remove(resource_id)
                return False
            return True

    def release_resource(self, thread_id, resource_id):
        with self.lock:
            if thread_id in self.lock_graph and resource_id in self.lock_graph[thread_id]:
                self.lock_graph[thread_id].remove(resource_id)
