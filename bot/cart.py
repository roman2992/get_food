from collections import defaultdict

class Cart:
    def __init__(self):
        self.data=defaultdict(dict)

    def add(self,uid,pizza_id,name,size,price,qty):
        key=f"{pizza_id}:{size}"
        item=self.data[uid].get(key)
        if item: item["quantity"]+=qty
        else: self.data[uid][key]={"key":key,"pizza_id":pizza_id,"name":name,"size":size,"unit_price":price,"quantity":qty}

    def items(self,uid): return list(self.data[uid].values())
    def total(self,uid): return sum(x["unit_price"]*x["quantity"] for x in self.data[uid].values())
    def inc(self,uid,key):
        if key in self.data[uid]: self.data[uid][key]["quantity"]+=1
    def dec(self,uid,key):
        if key in self.data[uid]:
            self.data[uid][key]["quantity"]-=1
            if self.data[uid][key]["quantity"]<=0: del self.data[uid][key]
    def clear(self,uid): self.data[uid].clear()
