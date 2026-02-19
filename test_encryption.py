"""Basic tests for Smart-Encrypt"""
import pytest
import tempfile
import os
from encryption import EncryptionManager
from storage import StorageManager

def test_encryption_basic():
    """Test basic encryption/decryption"""
    enc = EncryptionManager()
    enc.initialize("test_password")
    
    original = "This is a test message"
    encrypted = enc.encrypt(original)
    decrypted = enc.decrypt(encrypted)
    
    assert decrypted == original
    assert encrypted != original.encode()

def test_password_verification():
    """Test password hashing and verification"""
    enc = EncryptionManager()
    password = "secure_password_123"
    
    hash_val = enc.hash_password(password)
    assert enc.verify_password(password, hash_val)
    assert not enc.verify_password("wrong_password", hash_val)

def test_storage_basic():
    """Test basic storage operations"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = StorageManager(temp_dir)
        
        # Set master password
        storage.set_master_password("test_password")
        
        # Verify password
        assert storage.verify_master_password("test_password")
        assert not storage.verify_master_password("wrong_password")
        
        # Add category
        cat_id = storage.add_category("Test Category")
        assert cat_id > 0
        
        # Add entry
        entry_id = storage.add_entry(cat_id, "Test Title", "Test Content")
        assert entry_id > 0
        
        # Get entries
        entries = storage.get_entries(cat_id)
        assert len(entries) == 1
        assert entries[0]['title'] == "Test Title"
        assert entries[0]['content'] == "Test Content"

def test_search():
    """Test search functionality"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = StorageManager(temp_dir)
        storage.set_master_password("test_password")
        
        cat_id = storage.add_category("Test")
        storage.add_entry(cat_id, "Important Note", "This contains secret information")
        storage.add_entry(cat_id, "Shopping List", "Buy milk and bread")
        
        # Search for "secret"
        results = storage.search_entries("secret")
        assert len(results) == 1
        assert results[0]['title'] == "Important Note"
        
        # Search for "milk"
        results = storage.search_entries("milk")
        assert len(results) == 1
        assert results[0]['title'] == "Shopping List"

if __name__ == "__main__":
    pytest.main([__file__])