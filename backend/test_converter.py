"""Test content converter service."""
import base64
from services.content_converter_service import ContentConverterService


def test_text_items():
    converter = ContentConverterService()
    
    items = [
        {'type': 'text', 'content': 'Hello world'}
    ]
    
    result = converter.convert_items_to_text(items)
    
    assert len(result) == 1
    assert result[0]['content'] == 'Hello world'
    assert result[0]['source_type'] == 'text'
    print("✓ Text items test passed")


def test_file_conversion():
    converter = ContentConverterService()
    
    # Simple text file as base64
    text_content = b"This is a test file\nWith multiple lines"
    b64_content = base64.b64encode(text_content).decode('utf-8')
    
    items = [
        {'type': 'file', 'content': b64_content}
    ]
    
    result = converter.convert_items_to_text(items)
    
    assert len(result) == 1
    assert result[0]['source_type'] == 'file'
    assert '# Source: File' in result[0]['content']
    print("✓ File conversion test passed")


def test_url_conversion():
    converter = ContentConverterService()
    
    items = [
        {'type': 'link', 'content': 'https://example.com'}
    ]
    
    result = converter.convert_items_to_text(items)
    
    assert len(result) == 1
    assert result[0]['source_type'] == 'link'
    assert '# Source: https://example.com' in result[0]['content']
    print("✓ URL conversion test passed")


def test_mixed_items():
    converter = ContentConverterService()
    
    text_content = b"Test file"
    b64_content = base64.b64encode(text_content).decode('utf-8')
    
    items = [
        {'type': 'text', 'content': 'Plain text'},
        {'type': 'file', 'content': b64_content},
        {'type': 'link', 'content': 'https://example.com'}
    ]
    
    result = converter.convert_items_to_text(items)
    
    assert len(result) == 3
    assert all('content' in item for item in result)
    print("✓ Mixed items test passed")


if __name__ == '__main__':
    print("Testing ContentConverterService...")
    test_text_items()
    test_file_conversion()
    test_url_conversion()
    test_mixed_items()
    print("\nAll tests passed! ✓")
