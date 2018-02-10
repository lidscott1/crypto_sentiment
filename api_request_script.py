import sys
import requests
import datetime
import re
import pickle
from math import ceil


class ApiCall(object):
    
    
    def __init__(self, query, start_date, end_date, api_key, page = None):
        
        self.query = query
        self.start_date = start_date
        self.end_date = end_date
        self.api_key = api_key
        self.page = page        
        
        self.getRequest = 'https://newsapi.org/v2/everything?q=({query})\
        &from={start_date}&to={end_date}&language=en&sortBy=popularity\
        &apiKey={api_key}&page={page}'

    def __make_request__(self):


        self.request = requests.get(self.getRequest.format(query = self.query,
                                                      start_date = self.start_date,
                                                      end_date = self.end_date,
                                                      api_key = self.api_key,
                                                      page = self.page))

        
        if self.request.status_code == 200:
                        
            self.news_data = self.request.json()

        else:
            
            raise Exception("Bad response: {bad_status}\n".format(self.request.status_code))
            
            

    def __process_data__(self):


        for article in self.news_data['articles']:
                #don't care about author or image url
                del article['author'] 
                del article['urlToImage']
                #convert publishing data/time to be by day
                time = datetime.datetime.strptime(article['publishedAt'], "%Y-%m-%dT%H:%M:%S%fZ")
                next_time = time.replace(hour=0, minute=0, second=0, microsecond=0)
                article['publishedAt'] = str(next_time)
                #collect only the name of the source, not id
                article['source'] = article['source']['name']        
        
    
    def get_data(self, start_page = None, end_page = None):
        
        all_pages = False

        if (start_page is not None) and (end_page is not None): 
            
            assert start_page <= end_page, "start page cannot be greater than end page"        

        elif (start_page is None) and (end_page is None):
            
            print("No values specified grabbing up to 1000 pages")            
            
            all_pages = True
            
            start_page = 1
            
        elif (start_page is not None) and end_page is None:
            
            end_page = start_page

        else:
            print("start page not defined, setting to 1")
            
            start_page = 1
            
       
        keepGoing = True
        
        page_counter = start_page
                
        self.page_list = []        
        
        while keepGoing:
                        
                        
                        
            self.page = page_counter
            
            self.__make_request__()
  
            self.__process_data__()
            
            self.page_list.append(self.news_data)            
            
            if all_pages is True:
                
                end_page = min(ceil(self.news_data["totalResults"]/20), 1000)
            

            if page_counter >= end_page:
                
                keepGoing = False

            print(page_counter)            
            
            page_counter += 1





test = ApiCall("BTC OR bitcoin", "2018-01-01", 
               "2018-01-02", "54826b7dfe0845f5bcda79a02538c1db")


##expecting 10 results
test.get_data()

##expecting 5
test.get_data(1, 5)

##expecting 1
test.get_data(5)

##expecting 5
test.get_data(None, 5)

##expecting assert error
test.get_data(5, 4)


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