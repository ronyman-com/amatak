"""
Amatak ORM Python Implementation
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
import warnings

M = TypeVar('M', bound='Model')

@dataclass
class Field:
    """Base field type for model attributes"""
    name: str = None
    primary_key: bool = False
    nullable: bool = False
    default: Any = None
    unique: bool = False
    index: bool = False

    def __post_init__(self):
        if callable(self.default):
            self.default = self.default()

@dataclass
class IntegerField(Field):
    """Integer field type"""
    min_value: Optional[int] = None
    max_value: Optional[int] = None

@dataclass
class StringField(Field):
    """String field type"""
    max_length: Optional[int] = None

@dataclass
class BooleanField(Field):
    """Boolean field type"""
    pass

@dataclass
class FloatField(Field):
    """Floating point field type"""
    precision: int = 2

@dataclass
class DateTimeField(Field):
    """DateTime field type"""
    auto_now: bool = False
    auto_now_add: bool = False

@dataclass
class ForeignKey(Field):
    """Foreign key relationship"""
    related_model: Type['Model']
    related_field: str = 'id'
    on_delete: str = 'CASCADE'  # CASCADE, SET_NULL, PROTECT

class ModelMeta(type):
    """Metaclass for Model that collects field definitions"""
    def __new__(cls, name, bases, namespace):
        # Collect fields from class attributes
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                value.name = key
                fields[key] = value
        
        # Store fields in _meta
        namespace['_meta'] = {
            'fields': fields,
            'table_name': namespace.get('__tablename__', name.lower()),
            'primary_key': next((f for f in fields.values() if f.primary_key), None)
        }
        
        return super().__new__(cls, name, bases, namespace)

class Model(metaclass=ModelMeta):
    """Base model class for ORM"""
    
    def __init__(self, **kwargs):
        for field_name, field_def in self._meta['fields'].items():
            value = kwargs.get(field_name, field_def.default)
            setattr(self, field_name, value)
    
    @classmethod
    def create_table(cls, driver):
        """Create table for this model in the database"""
        if not hasattr(driver, 'execute'):
            warnings.warn("Driver doesn't support execute method", RuntimeWarning)
            return False
        
        fields = []
        for name, field in cls._meta['fields'].items():
            field_sql = f"{name} {cls._get_sql_type(field)}"
            
            if field.primary_key:
                field_sql += " PRIMARY KEY"
            if not field.nullable:
                field_sql += " NOT NULL"
            if field.unique:
                field_sql += " UNIQUE"
            if field.default is not None and not callable(field.default):
                field_sql += f" DEFAULT {field.default}"
            
            fields.append(field_sql)
        
        sql = f"CREATE TABLE IF NOT EXISTS {cls._meta['table_name']} ({', '.join(fields)})"
        try:
            driver.execute(sql)
            return True
        except Exception as e:
            warnings.warn(f"Failed to create table: {e}", RuntimeWarning)
            return False
    
    @classmethod
    def _get_sql_type(cls, field: Field) -> str:
        """Map field types to SQL types"""
        if isinstance(field, IntegerField):
            return "INTEGER"
        elif isinstance(field, StringField):
            return f"VARCHAR({field.max_length})" if field.max_length else "TEXT"
        elif isinstance(field, BooleanField):
            return "BOOLEAN"
        elif isinstance(field, FloatField):
            return "REAL"
        elif isinstance(field, DateTimeField):
            return "TIMESTAMP"
        elif isinstance(field, ForeignKey):
            return "INTEGER"  # Foreign keys are integers by default
        return "TEXT"  # Default type
    
    def save(self, driver):
        """Save instance to database"""
        if not hasattr(driver, 'execute'):
            warnings.warn("Driver doesn't support execute method", RuntimeWarning)
            return False
        
        fields = []
        values = []
        placeholders = []
        
        for name, field_def in self._meta['fields'].items():
            value = getattr(self, name, None)
            if value is None and not field_def.nullable:
                warnings.warn(f"Field {name} cannot be null", RuntimeWarning)
                return False
            
            fields.append(name)
            values.append(value)
            placeholders.append("?")
        
        if self._meta['primary_key'] and getattr(self, self._meta['primary_key'].name) is None:
            # Insert new record
            sql = f"""INSERT INTO {self._meta['table_name']} 
                      ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"""
        else:
            # Update existing record
            pk_name = self._meta['primary_key'].name
            pk_value = getattr(self, pk_name)
            set_clause = ', '.join(f"{f} = ?" for f in fields)
            sql = f"""UPDATE {self._meta['table_name']} 
                      SET {set_clause} WHERE {pk_name} = ?"""
            values.append(pk_value)
        
        try:
            driver.execute(sql, values)
            if self._meta['primary_key'] and getattr(self, self._meta['primary_key'].name) is None:
                # Get the last inserted ID
                if hasattr(driver, 'lastrowid'):
                    setattr(self, self._meta['primary_key'].name, driver.lastrowid)
            return True
        except Exception as e:
            warnings.warn(f"Failed to save record: {e}", RuntimeWarning)
            return False
    
    @classmethod
    def objects(cls, driver) -> 'QuerySet':
        """Return a QuerySet for this model"""
        return QuerySet(cls, driver)

class QuerySet:
    """QuerySet implementation for building queries"""
    
    def __init__(self, model: Type[Model], driver):
        self.model = model
        self.driver = driver
        self._where = []
        self._params = []
        self._limit = None
        self._offset = None
        self._order_by = []
    
    def filter(self, **kwargs) -> 'QuerySet':
        """Add filter conditions to the query"""
        for key, value in kwargs.items():
            self._where.append(f"{key} = ?")
            self._params.append(value)
        return self
    
    def limit(self, count: int) -> 'QuerySet':
        """Limit the number of results"""
        self._limit = count
        return self
    
    def offset(self, count: int) -> 'QuerySet':
        """Offset the results"""
        self._offset = count
        return self
    
    def order_by(self, *fields: str) -> 'QuerySet':
        """Order the results by fields"""
        self._order_by.extend(fields)
        return self
    
    def all(self) -> List[Model]:
        """Execute the query and return all results"""
        sql = f"SELECT * FROM {self.model._meta['table_name']}"
        
        if self._where:
            sql += " WHERE " + " AND ".join(self._where)
        
        if self._order_by:
            sql += " ORDER BY " + ", ".join(self._order_by)
        
        if self._limit is not None:
            sql += f" LIMIT {self._limit}"
            if self._offset is not None:
                sql += f" OFFSET {self._offset}"
        
        try:
            results = self.driver.execute(sql, self._params)
            return [self.model(**dict(row)) for row in results]
        except Exception as e:
            warnings.warn(f"Query failed: {e}", RuntimeWarning)
            return []
    
    def first(self) -> Optional[Model]:
        """Return the first matching result"""
        results = self.limit(1).all()
        return results[0] if results else None
    
    def count(self) -> int:
        """Return the count of matching records"""
        sql = f"SELECT COUNT(*) FROM {self.model._meta['table_name']}"
        if self._where:
            sql += " WHERE " + " AND ".join(self._where)
        
        try:
            result = self.driver.execute(sql, self._params)
            return result[0][0] if result else 0
        except Exception as e:
            warnings.warn(f"Count failed: {e}", RuntimeWarning)
            return 0


# Public API
__all__ = [
    'Model',
    'Field',
    'IntegerField',
    'StringField', 
    'BooleanField',
    'FloatField',
    'DateTimeField',
    'ForeignKey'
]