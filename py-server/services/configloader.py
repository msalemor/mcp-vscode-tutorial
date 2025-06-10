import json
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class SchemaConfig:
    """Class representing a schema configuration."""
    table: str
    cluster: str
    database: str
    schema: str = None
    schema_cmd: str = field(default="")
    description: str = ""

    def __post_init__(self):
        # Convert camelCase to snake_case for schema_cmd if provided as schemaCmd
        if not self.schema_cmd and hasattr(self, 'schemaCmd'):
            self.schema_cmd = getattr(self, 'schemaCmd')
            delattr(self, 'schemaCmd')


class SchemaConfigLoader:
    """Class to load and manage schema configurations."""

    def __init__(self, config_path: str = './kqlschemas.json'):
        self.configs: List[SchemaConfig] = []
        if config_path:
            self.load_from_file(config_path)

    def load_from_file(self, file_path: str) -> List[SchemaConfig]:
        """Load configurations from a JSON file."""
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                return self.load_from_data(data)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ValueError(f"Error loading configuration file: {e}")

    def load_from_data(self, data: List[dict]) -> List[SchemaConfig]:
        """Load configurations from a list of dictionaries."""
        self.configs = [SchemaConfigLoader._create_config(config_dict) for config_dict in data]
        return self.configs

    def load_from_json_string(self, json_str: str) -> List[SchemaConfig]:
        """Load configurations from a JSON string."""
        try:
            data = json.loads(json_str)
            return self.load_from_data(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON string: {e}")

    @staticmethod
    def _create_config(config_dict: dict) -> SchemaConfig:
        """Create a SchemaConfig instance from a dictionary."""
        # Handle field name differences between JSON and Python conventions
        if 'schemaCmd' in config_dict:
            config_dict['schema_cmd'] = config_dict.pop('schemaCmd')
        
        return SchemaConfig(**config_dict)

    def get_configs_by_name(self, name: str) -> SchemaConfig:
        """Get all configurations with the specified name."""
        try:
            return [config for config in self.configs if config.table == name][0]
        except IndexError:
            return None

    def get_all_configs(self) -> List[SchemaConfig]:
        """Get all loaded configurations."""
        return self.configs

# Singleton implementation for SchemaConfigLoader
class SchemaConfigsSingleton:
    """Singleton class for SchemaConfigLoader."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls, config_path: str = './kqlschemas.json') -> SchemaConfigLoader:
        """Get or create the singleton instance of SchemaConfigLoader."""
        if cls._instance is None:
            cls._instance = SchemaConfigLoader(config_path)
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (mainly for testing purposes)."""
        cls._instance = None
