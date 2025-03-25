import pytest
import os
import tempfile
from amatak.stdlib.fileio import FileIO

class TestFileIO:
    @pytest.fixture
    def fileio(self):
        return FileIO()

    @pytest.fixture
    def temp_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            f.flush()
            yield f.name
        os.unlink(f.name)

    def test_read_write_text(self, fileio, temp_file):
        # Test writing and reading text
        test_content = "Hello Amatak FileIO"
        
        # Write text
        fileio.write_text(temp_file, test_content)
        
        # Read text
        content = fileio.read_text(temp_file)
        assert content == test_content

    def test_read_write_binary(self, fileio, temp_file):
        # Test writing and reading binary
        test_content = b"\x00\x01\x02\x03"
        
        # Write binary
        fileio.write_binary(temp_file, test_content)
        
        # Read binary
        content = fileio.read_binary(temp_file)
        assert content == test_content

    def test_file_exists(self, fileio, temp_file):
        # Test file existence checks
        assert fileio.exists(temp_file)
        assert not fileio.exists("nonexistent_file.txt")

    def test_file_operations(self, fileio, temp_file):
        # Test file operations
        new_path = temp_file + ".copy"
        
        # Copy
        fileio.copy(temp_file, new_path)
        assert fileio.exists(new_path)
        
        # Move
        moved_path = temp_file + ".moved"
        fileio.move(new_path, moved_path)
        assert fileio.exists(moved_path)
        assert not fileio.exists(new_path)
        
        # Delete
        fileio.delete(moved_path)
        assert not fileio.exists(moved_path)

    def test_directory_operations(self, fileio):
        # Test directory operations
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "subdir")
            
            # Create directory
            fileio.create_directory(new_dir)
            assert fileio.is_directory(new_dir)
            
            # List directory
            test_file = os.path.join(new_dir, "test.txt")
            fileio.write_text(test_file, "test")
            contents = fileio.list_directory(new_dir)
            assert "test.txt" in contents
            
            # Delete directory
            fileio.delete_directory(new_dir)
            assert not fileio.exists(new_dir)

    def test_error_handling(self, fileio):
        # Test error cases
        with pytest.raises(FileNotFoundError):
            fileio.read_text("nonexistent_file.txt")
        
        with pytest.raises(IsADirectoryError):
            with tempfile.TemporaryDirectory() as temp_dir:
                fileio.read_text(temp_dir)