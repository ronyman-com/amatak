"""
JSON compatibility layer with Amatak types support
"""

import json
from typing import Any, Dict, List, Union

class AmatakJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for Amatak types"""
    
    def default(self, obj: Any) -> Any:
        """Handle Amatak-specific types"""
        from amatak.runtime.types.core import AmatakType
        if isinstance(obj, AmatakType):
            return obj.to_json()
        return super().default(obj)

def loads(json_str: str) -> Union[Dict, List]:
    """Safe JSON parsing"""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {str(e)}")

def dumps(obj: Any, **kwargs: Any) -> str:
    """JSON serialization with Amatak support"""
    kwargs.setdefault('cls', AmatakJSONEncoder)
    kwargs.setdefault('indent', 2)
    return json.dumps(obj, **kwargs)