from errno import EISDIR
from src.main import DocumentEditor
import pytest

class TestDocumentEditor:
    def test_write(self):
        editor = DocumentEditor()
        editor.write('Text')
        assert editor.content == 'Text'

    def test_clear(self):
        editor = DocumentEditor()
        editor.write('Text')
        assert editor.content == 'Text'
        editor.clear()
        assert editor.content == ''
        assert editor.is_empty() 

    def test_get_last_content(self):
        editor = DocumentEditor()
        editor.write('Text')
        editor.clear()
        
        expected_last_content = editor.history[-1]
        
        last_content = editor.get_last_content()
        # last_content = 'text'
        
        error_msg = (f'Last content is expected to be '
                     f'the content before last operation. '
                     f'Actual editor history {editor.history} '
                     f'error: expected last content to be {expected_last_content} vs '
                     f'actual last content {last_content}')
        # assert last_content == expected_last_content, error_msg
        if last_content != expected_last_content:
            pytest.fail(error_msg)
            
    def test_raise_error_if_no_history(self):
        editor = DocumentEditor()
        # with pytest.raises(Exception, match="No history"):
        with pytest.raises(Exception) as exc_info:
            editor.get_last_content()
        assert str(exc_info.value).startswith('Content is empty')
        assert exc_info.type == ValueError
# pytest document-editor\tests\test_main.py -vv