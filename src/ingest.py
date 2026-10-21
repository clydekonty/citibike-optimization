import requests
import sqlite3

url_static = "https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_information.json"
url_live = "https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_status.json"
data_path = "data/"


def initialization():
    conn = sqlite3.connect(data_path + "station_data.db")
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS station_data (
            station_id TEXT PRIMARY KEY,
            name TEXT,
            lat REAL,
            lon REAL,
            capacity INTEGER
        )"""
    )

    conn.commit()
    conn.close()

    new_conn = sqlite3.connect(data_path + "station_status.db")
    curr = new_conn.cursor()
    curr.execute(
        """CREATE TABLE IF NOT EXISTS station_status (
        station_id TEXT,
        timestamp INTEGER,
        bikes_available INTEGER,
        e_bikes_available INTEGER,
        docks_available INTEGER,

        PRIMARY KEY(station_id, timestamp)
        )
        """
    )

    new_conn.commit()
    new_conn.close()


def grab_static(url):

    req = requests.get(url)
    if (req.status_code != 200):
        print("error status != 200")
        return None

    data = req.json()

    conn = sqlite3.connect(data_path + "station_data.db")
    cur = conn.cursor()

    for item in data["data"]["stations"]:
        cur.execute(
            "INSERT INTO station_data (station_id, name, lat, lon, capacity) VALUES (?, ?, ?, ?, ?)",
            (item["station_id"], item["name"], item["lat"], item["lon"], item["capacity"])
        )

    conn.commit()
    conn.close()

    print("Static data ingested successfully.")

def grab_live(url):

    req = requests.get(url)
    if (not req):
            print("error status != 200")
            return None

    data = req.json()

    conn = sqlite3.connect(data_path + "station_status.db")
    cur = conn.cursor()

    for item in data["data"]["stations"]:
        if (item["is_installed"] == 0 or item["is_renting"] == 0 or item["is_returning"] == 0):
            continue
        cur.execute(
            "INSERT INTO station_status (station_id, timestamp, bikes_available, e_bikes_available, dock_available) VALUES (?, ?, ?, ?, ?)",
            (item["station_id"], data["last_updated"], item["num_bikes_available"], item["num_ebikes_available"], item["num_docks_available"])
        )

    conn.commit()
    conn.close()


grab_live(url_live)
    

    

