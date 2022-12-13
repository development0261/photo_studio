import requests, json 
lat="72.831062"
long="21.170240"
url ="https://api.mapbox.com/geocoding/v5/mapbox.places/"+lat+","+long+".json?types=poi&access_token=pk.eyJ1IjoiYXJhYmFwcCIsImEiOiJjbDh2YmtiODQwNXo4M29udTA0eWxldmIxIn0.tzc8bwS-5vvdE32_T0EY7A" 
resp = requests.get(url) 
data = json.loads(resp.content.decode()) 
for i,j in data.items():
    if i=="features": 
        for k in j: 
            print(k)
            country=k['context'][-1]['text']
            state=k['context'][-2]['text']
            city=k['context'][-3]['text']
print("="*50)
print("COUNTRY: ",country)
print("STATE: ",state)
print("CITY: ",city)