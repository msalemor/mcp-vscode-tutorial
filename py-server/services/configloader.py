import json
import os
from threading import Lock
from dataclasses import dataclass
from typing import Optional, Any, List

@dataclass
class SchemaData:
    cluster: str
    database: str
    schema: Optional[Any]
    schemaCmd: str
    description: str

@dataclass
class QueryData:
    cluster: str
    database: str
    queryCmd: str
    description: str

@dataclass
class KQLSchema:
    type: str
    key: str
    data: SchemaData | QueryData

class ConfigLoader:
    _instance = None
    _lock = Lock()
    _data = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path='./kqlschemas.json'):
        if self._data is None:
            with open(config_path, 'r') as f:
                content = f.read()                
                raw_data = json.loads(content)
                self._data = [self._parse_item(item) for item in raw_data]

    def _parse_item(self, item):
        if item['type'] == 'schema':
            data = SchemaData(**item['data'])
        elif item['type'] == 'query':
            data = QueryData(**item['data'])
        else:
            data = item['data']
        return KQLSchema(type=item['type'], key=item['key'], data=data)

    def get_by_key(self, key)->SchemaData | None:
        try:
            return [item for item in self._data if item.key == key][0]
        except Exception as e:
            print(f"Error retrieving item by key '{key}': {e}")
            return None
        
    def get_by_type_key(self, type:str, key:str)->SchemaData | None:
        try:
            return [item for item in self._data if item.type==type and item.key == key][0]
        except Exception as e:
            print(f"Error retrieving item by key '{key}': {e}")
            return None


    def get_first_by_key(self, key):
        for item in self._data:
            if item.key == key:
                return item
        return None

_config_loader_instance = None

def get_config_loader(config_path=None):
    global _config_loader_instance
    if _config_loader_instance is None:
        _config_loader_instance = ConfigLoader(config_path)
    return _config_loader_instance

