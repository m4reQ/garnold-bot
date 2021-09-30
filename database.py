from typing import Any, Dict, List
import pymongo
from pymongo import collection

# UNSAFE !!!
CONNECTION_STRING = 'mongodb+srv://discord-bot:ciCEhfZKDpPVXkKI@cluster0.izokc.mongodb.net/wymiar_bot?retryWrites=true&w=majority'
    
def get_server_info() -> Dict[str, Any]:
    with pymongo.MongoClient(CONNECTION_STRING) as client:
        collection = client['wymiar_bot']['server_info']

    return collection.find_one({})

def get_names() -> List[str]:
    with pymongo.MongoClient(CONNECTION_STRING) as client:
        collection = client['wymiar_bot']['names']

    names = [x['name'] for x in collection.find({})]
    
    print(f'Names list with {len(names)} entries retrieved from database.')

    return names

def add_names(names: List[str]) -> None:
    with pymongo.MongoClient(CONNECTION_STRING) as client:
        collection = client['wymiar_bot']['names']
        
        already_existing = [x['name'] for x in collection.find({})]
        for name in already_existing:
            if name in names:
                names.remove(name)

        update_dict = [{'name': x} for x in names]
        if not update_dict:
            print('No new updates found.')
            return
        
        result = collection.insert_many(update_dict)

    print(f'Succesfully updated names database with {len(result.inserted_ids)} entries.')

def update_names(filename: str) -> None:
    with open(filename, 'r', encoding='utf-8') as f:
        names = [x.replace('\n', '') for x in f.readlines()]
    
    add_names(names)