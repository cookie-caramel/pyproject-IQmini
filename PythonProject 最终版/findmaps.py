import json
import os
import autosolution

SAVE_FILE = os.path.join( "testmaps.json")
maps={}

key=0
for _ in range(200):    
    goodmap , map=autosolution.test()
    if goodmap:
        maps[key]=map
        key+=1
print(key)    
with open(SAVE_FILE, 'w') as f:
    json.dump(maps, f, indent=4)