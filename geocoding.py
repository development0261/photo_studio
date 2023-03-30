import requests, json 
lat="25.274399"
long="133.775131"
url ="https://api.mapbox.com/geocoding/v5/mapbox.places/"+lat+","+long+".json?types=poi&access_token=pk.eyJ1IjoiYXJhYmFwcCIsImEiOiJjbDh2YmtiODQwNXo4M29udTA0eWxldmIxIn0.tzc8bwS-5vvdE32_T0EY7A" 
# url ="https://api.mapbox.com/geocoding/v5/mapbox.places/72.831062,21.170240.json?types=poi&access_token=pk.eyJ1IjoiYXJhYmFwcCIsImEiOiJjbDh2YmtiODQwNXo4M29udTA0eWxldmIxIn0.tzc8bwS-5vvdE32_T0EY7A" 
resp = requests.get(url) 
data = json.loads(resp.content.decode()) 
print(data)
country=state=city=""
for i,j in data.items():
    if i=="features": 
        for k in j: 
            print(k['context'][1]['text'])
            country=k['context'][-1]['text']
            state=k['context'][-2]['text']
            city=k['context'][-3]['text']
print("="*50)
print("COUNTRY: ",country)
print("STATE: ",state)
print("CITY: ",city)