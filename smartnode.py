import sys
import datetime
import sqlite3
import time
import xml.etree.ElementTree as ET
import lib.transmissionrpc
import getpass
import urllib
import re, os
import pandas as pd

managed_torrents_file = "managed_torrents.csv"
tohave_torrents_file = "tohave_torrents.csv"
collections_folder = "collections"
collections_urls = "collections_urls.txt"

# loop over all csv files to sync
with open(collections_urls, "r") as urls:
    for url in urls:
        url = url.strip()
        if (url != ""):
            print(url)
            filedata = urllib.request.urlopen(url)  
            datatowrite = filedata.read()

            # detect more errors here

            os.makedirs(collections_folder, exist_ok=True)
            with open(collections_folder + "/" + os.path.basename(url), 'wb') as f:  
                f.write(datatowrite)

tohave_torrents = pd.DataFrame(columns = ['INFOHASH'])
tohave_torrents.set_index("INFOHASH", inplace=True)

for f in os.listdir(collections_folder):
    a = pd.read_csv(collections_folder + "/" + f)
    a.set_index("INFOHASH", inplace=True)
    a["COLLECTION"] = f
    tohave_torrents = tohave_torrents.append(a, sort=False)
    
# take union
tohave_torrents = tohave_torrents.drop_duplicates()
print("Total torrents from all collections: ", len(tohave_torrents))

if not os.path.isfile(managed_torrents_file):
    managed_torrents.to_csv(managed_torrents_file)
    
managed_torrents = pd.read_csv(managed_torrents_file)
managed_torrents.set_index("INFOHASH", inplace=True)

toremove_torrents = set(managed_torrents.index) - set(tohave_torrents.index)



userannounce = None
def get_userannounce():
    global userannounce
    if userannounce is None:
        import requests
        key = config.get("AcademicTorrents","api_key")
        cookie_key = dict([k.split("=") for k in key.split(";")])
        resp = requests.get(url="https://academictorrents.com/apiv2/userannounce", cookies=cookie_key)
        userannounce = resp.json()["userannounce"] # Check the JSON Response Content documentation below
    return userannounce



import transmissionrpc
import configparser
config = configparser.RawConfigParser()
config.read('smartnode.properties')

client = transmissionrpc.Client(address = config.get("Transmission","address"), 
                                port=int(config.get("Transmission","port")),
                                user = config.get("Transmission","user"), 
                                password = config.get("Transmission","password"))



## TODO finish transmission interface part


torrents = client.list()
for torrentid in torrents:
    torrentobj = torrents[torrentid]
    
    # use the different between tohave_torrents and managed_torrents to remove torrents
    if torrentobj.hashString in toremove_torrents:
        print("Something to remove", torrentobj.hashString, torrentid, torrentobj.name)
        # do something to remove it
        
    if torrentobj.hashString in managed_torrents.index:
        print(torrentobj.hashString, torrentid, torrentobj.name)
        
        client.change_torrent(torrentid, trackerReplace=[0,get_userannounce()])
        
        

# filter tohave_torrents based on what we have with some sort of logic


# download everything in tohave_torrents




