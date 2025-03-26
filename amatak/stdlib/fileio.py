# Amatak File I/O Standard Library
# Secure file system operations with sandboxing support

import os
import io
import hashlib
from pathlib import Path
from amatak.error_handling import ErrorHandler
from amatak.security.middleware import SecurityMiddleware

class FileIO:
    """Secure file system operations with sandboxing"""
    
    def __init__(self, sandbox_path=None):
        self.sandbox = self._init_sandbox(sandbox_path)
        self.security = SecurityMiddleware()
        self.error_handler = ErrorHandler()
        
    def _init_sandbox(self, path):
        """Initialize sandbox directory"""
        if path is None:
            return None
            
        sandbox = Path(path).absolute()
        sandbox.mkdir(exist_ok=True, parents=True)
        return sandbox
        
    def _resolve_path(self, path):
        """Resolve path within sandbox if enabled"""
        path = Path(path)
        if self.sandbox:
            path = (self.sandbox / path).resolve()
            if not str(path).startswith(str(self.sandbox)):
                raise PermissionError("Attempt to access outside sandbox")
        return path
        
    @security.check_permission('file_read')
    def read_file(self, path, mode='r', encoding='utf-8'):
        """Read file contents with security checks"""
        path = self._resolve_path(path)
        self.security.validate_path(path)
        
        try:
            with open(path, mode, encoding=encoding) as f:
                return f.read()
        except Exception as e:
            self.error_handler.log(e, f"Failed to read file {path}")
            raise
            
    @security.check_permission('file_write')
    def write_file(self, path, content, mode='w', encoding='utf-8'):
        """Write to file with security checks"""
        path = self._resolve_path(path)
        self.security.validate_path(path)
        
        try:
            with open(path, mode, encoding=encoding) as f:
                f.write(content)
        except Exception as e:
            self.error_handler.log(e, f"Failed to write file {path}")
            raise
            
    @security.check_permission('file_ops')
    def list_dir(self, path='.'):
        """List directory contents"""
        path = self._resolve_path(path)
        return [str(p) for p in Path(path).iterdir()]
        
    @security.check_permission('file_ops')
    def file_exists(self, path):
        """Check if file exists"""
        path = self._resolve_path(path)
        return Path(path).exists()
        
    @security.check_permission('file_meta')
    def get_stats(self, path):
        """Get file statistics"""
        path = self._resolve_path(path)
        stat = path.stat()
        return {
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'created': stat.st_ctime
        }
        
    @security.check_permission('file_hash')
    def file_hash(self, path, algorithm='sha256'):
        """Calculate file hash"""
        path = self._resolve_path(path)
        hasher = hashlib.new(algorithm)
        
        with open(path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
                
        return hasher.hexdigest()
        
    @security.check_permission('file_ops')
    def safe_join(self, base, *paths):
        """Safely join paths within sandbox"""
        try:
            full_path = self._resolve_path(Path(base).joinpath(*paths))
            return str(full_path)
        except Exception as e:
            self.error_handler.log(e, "Path join violation")
            raise
            
    def temp_file(self, content=None, suffix=None):
        """Create secure temporary file"""
        import tempfile
        mode = 'w' if isinstance(content, str) else 'wb'
        
        with tempfile.NamedTemporaryFile(
            mode=mode,
            suffix=suffix,
            dir=str(self.sandbox) if self.sandbox else None,
            delete=False
        ) as tmp:
            if content:
                tmp.write(content)
            return tmp.name

# Export default fileio instance
fileio = FileIO()