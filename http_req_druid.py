import requests, json, time

url = "http://35.225.91.126:8888/druid/v2/sql"
headers = {"Content-Type": "application/json"}
param = {'query': """SELECT agent
                        ,count(*) as calls
                    FROM "realtime_topic"
                    GROUP BY agent
                    ORDER BY 2 ASC"""}

def refresh_period(sec=10):
    for i in range(sec, -2, -1):
        time.sleep(1)
        print("\r", str(i), end="")

try:
    while True:
        refresh_period(3)
        r = requests.post(url, data=json.dumps(param), headers=headers)
        if r.status_code != 200:
            print("Status Code: " + str(r.status_code))
            print(r.text)
            break
        else:
            data = r.json()
            for d in data:
                print(d["agent"], ":" , d["calls"])
except KeyboardInterrupt:
    print("Uygulama kapatıldı...")
    pass
