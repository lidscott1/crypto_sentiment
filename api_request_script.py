import sys
import requests
import datetime
import re
import pickle



class test(object):
    
    def __init__(self):
        
        print("dont overwrite the gd directory")




class Struct(object):

    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)): 
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value

class myclass(object):

    def get_raw_data(self,call):
        r = requests.get(call).json()
        
        for i in r['articles']:
            del i['author']
            del i['urlToImage']
            t = datetime.datetime.strptime(i['publishedAt'], "%Y-%m-%dT%H:%M:%S%fZ")
            nt = t.replace(hour=0, minute=0, second=0, microsecond=0)
            i['publishedAt'] = str(nt)
            i['source'] = i['source']['name']
        
        return r
    
    def __init__(self,call):
        self.call = call
        self.data = Struct(self.get_raw_data(call))
        self.data.n_pages = self.data.totalResults/20
        
    def paginate(self,n):
        fp = self.call.find('&page=')
        if fp > 0:
            l = [x for x, v in enumerate(self.call) if v == '&']
            l.append(len(self.call))
            nxt = l[next(x[0] for x in enumerate(l) if x[1] > fp)]
            base_call = self.call[:fp] + self.call[nxt:]
        else:
            base_call = self.call
         
        articles_list = []

        for i in range(1,n+1):
            new_call = base_call + "&page=" + str(i)
            d = Struct(self.get_raw_data(new_call))
            articles_list.extend(d.articles)
            
        return articles_list

n =  myclass(sys.argv[1])

if n.data.n_pages > 900:
    p = 900
else:
    p = int(n.data.n_pages)

l = n.paginate(p)

with open(sys.argv[2], "wb") as f:
    pickle.dump(l, f)