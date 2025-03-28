# amatak/database/drivers/postgres.py
"""
PostgreSQL Database Driver (Python Implementation)
"""

import psycopg2
import psycopg2.extras
from typing import Dict, List, Any, Optional, Union

class PostgresDriver:
    """
    PostgreSQL database driver implementation
    
    Properties:
    - connection: The active database connection
    - cursor: The active cursor
    - connected: Boolean indicating connection status
    """
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connected = False
        self.connection_params: Dict[str, Any] = {}
        
    def connect(self, params: Dict[str, Any]) -> bool:
        """
        Connect to a PostgreSQL database
        
        Args:
            params: Dictionary with connection parameters:
                - host: Database host
                - port: Connection port
                - dbname: Database name
                - user: Username
                - password: Password
                - options: Additional connection options
        
        Returns:
            bool: True if connection succeeded, False otherwise
        """
        try:
            self.connection_params = params
            self.connection = psycopg2.connect(
                host=params.get('host', 'localhost'),
                port=params.get('port', 5432),
                dbname=params.get('dbname'),
                user=params.get('user'),
                password=params.get('password'),
                options=params.get('options', '')
            )
            self.cursor = self.connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor
            )
            self.connected = True
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
            
    def disconnect(self) -> bool:
        """Close the database connection"""
        if self.connected:
            try:
                self.cursor.close()
                self.connection.close()
                self.connected = False
                return True
            except Exception as e:
                print(f"Disconnection error: {e}")
        return False
        
    def execute(self, query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query
        
        Args:
            query: SQL query string
            params: Optional parameters for prepared statements
        
        Returns:
            List of result rows as dictionaries
        """
        if not self.connected:
            raise RuntimeError("Not connected to database")
            
        try:
            self.cursor.execute(query, params or [])
            
            if query.strip().upper().startswith("SELECT"):
                return [dict(row) for row in self.cursor.fetchall()]
            else:
                self.connection.commit()
                return []
        except Exception as e:
            self.connection.rollback()
            raise RuntimeError(f"PostgreSQL Error: {e}")
            
    def execute_many(self, query: str, params_list: List[List[Any]]) -> int:
        """
        Execute a query multiple times
        
        Args:
            query: SQL query string
            params_list: List of parameter lists
        
        Returns:
            Number of rows affected
        """
        if not self.connected:
            raise RuntimeError("Not connected to database")
            
        try:
            self.cursor.executemany(query, params_list)
            self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            raise RuntimeError(f"Bulk Execute Error: {e}")
            
    def call_procedure(self, proc_name: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Call a stored procedure
        
        Args:
            proc_name: Name of stored procedure
            params: Optional parameters
        
        Returns:
            List of result rows
        """
        return self.execute(f"CALL {proc_name}({','.join(['%s']*len(params))})", params)
        
    def table_exists(self, table_name: str, schema: str = 'public') -> bool:
        """
        Check if a table exists in the database
        
        Args:
            table_name: Name of table to check
            schema: Schema name (default: public)
        
        Returns:
            bool: True if table exists
        """
        query = """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
        )
        """
        result = self.execute(query, [schema, table_name])
        return result[0]['exists']
        
    def get_table_columns(self, table_name: str, schema: str = 'public') -> List[Dict[str, Any]]:
        """
        Get column information for a table
        
        Args:
            table_name: Name of table
            schema: Schema name (default: public)
        
        Returns:
            List of column information dictionaries
        """
        query = """
        SELECT 
            column_name, 
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
        """
        return self.execute(query, [schema, table_name])
        
    def begin_transaction(self, isolation_level: Optional[str] = None):
        """
        Begin a transaction
        
        Args:
            isolation_level: Optional isolation level:
                - READ UNCOMMITTED
                - READ COMMITTED
                - REPEATABLE READ
                - SERIALIZABLE
        """
        if isolation_level:
            self.execute(f"BEGIN TRANSACTION ISOLATION LEVEL {isolation_level}")
        else:
            self.execute("BEGIN TRANSACTION")
        
    def commit(self):
        """Commit current transaction"""
        self.execute("COMMIT")
        
    def rollback(self):
        """Rollback current transaction"""
        self.execute("ROLLBACK")
        
    def savepoint(self, name: str):
        """Create a savepoint"""
        self.execute(f"SAVEPOINT {name}")
        
    def rollback_to_savepoint(self, name: str):
        """Rollback to a savepoint"""
        self.execute(f"ROLLBACK TO SAVEPOINT {name}")
        
    def copy_from(self, file: Any, table: str, columns: Optional[List[str]] = None, sep: str = '\t'):
        """
        Perform bulk copy from file
        
        Args:
            file: File-like object or path
            table: Target table name
            columns: Optional list of column names
            sep: Field separator
        """
        try:
            self.cursor.copy_from(
                file=file,
                table=table,
                columns=columns if columns else None,
                sep=sep
            )
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise RuntimeError(f"COPY Error: {e}")
            
    def copy_to(self, file: Any, query: str, sep: str = '\t'):
        """
        Perform bulk copy to file
        
        Args:
            file: File-like object or path
            query: Query to export
            sep: Field separator
        """
        try:
            self.cursor.copy_expert(
                f"COPY ({query}) TO STDOUT WITH DELIMITER '{sep}'",
                file
            )
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise RuntimeError(f"COPY Error: {e}")

__all__ = ['PostgresDriver']