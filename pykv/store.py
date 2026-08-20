class Store:
    def __init__(self):
        self.data={}

    def set(self ,key ,value):
        self.data[key]=value
    
    def get(self ,key):
        return self.data.get(key, None)
    
    def delete(self ,key):
        if key in self.data:
            del self.data[key]
            return True
        else:
            return False
    
    def keys(self):
        return list(self.data.keys())
    
    def size(self):
        return len(list(self.data.keys()))