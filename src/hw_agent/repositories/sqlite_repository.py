# src/hw_agent/repositories/sqlite_repository.py

import sqlite3
import os
from typing import Optional
from hw_agent.core.orchestrator_type import OrchestratorType
from hw_agent.repositories.base_repository import BaseRepository
from hw_agent.repositories.repository_factory import RepositoryFactory
from hw_agent.services.settings_service import SettingsService
from hw_agent.models.connection_config_models import ConnectionConfigCreate, ConnectionConfigRead
from threading import Lock
import json

@RepositoryFactory.register('sqlite')
class SQLiteRepository(BaseRepository):
    _lock = Lock()

    def __init__(self):
        settings = SettingsService()
        db_file = settings.get('sqlite_db_file', 'data/configurations.db')
        self.db_file = os.path.abspath(db_file)
        # Ensure the configs directory exists
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        self.connection = sqlite3.connect(self.db_file, check_same_thread=False)
        self._initialize_db()

    def _initialize_db(self):
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configurations (
                    config_id TEXT PRIMARY KEY,
                    connection_info TEXT
                )
            ''')
            self.connection.commit()

    def save_configuration(self, config_id, connection_info: ConnectionConfigCreate) -> None:
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO configurations (config_id, connection_info)
                VALUES (?, ?)
            ''', (config_id, json.dumps(connection_info.model_dump(mode="json"))))
            self.connection.commit()

    def get_configuration(self, config_id) -> Optional[ConnectionConfigRead]:
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT connection_info FROM configurations WHERE config_id = ?
            ''', (config_id,))
            row = cursor.fetchone()
            if row:
                connection_info_json = row[0]
                connection_info_data = json.loads(connection_info_json)
                # Add the config_id to the data
                connection_info_data['config_id'] = config_id
                
                # Instantiate ConnectionConfigRead using automatic mapping
                return ConnectionConfigRead(**connection_info_data)           
            else:
                return None
    def get_configurations(self):
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute('SELECT config_id, connection_info FROM configurations')
            rows = cursor.fetchall()
            return {config_id: json.loads(connection_info) for config_id, connection_info in rows}
        
    def clear_all_configurations(self):
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM configurations')
            self.connection.commit()    
        
    def delete_configuration(self, config_id):
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM configurations WHERE config_id = ?', (config_id,))
            self.connection.commit()
            
            return True