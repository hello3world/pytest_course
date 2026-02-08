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
        
        
    def test_initial_editor_is_empty(self):
        # GIVEN: initial document editor right after initialization (with no operation applied)
        editor = DocumentEditor()
        # WHEN: checking if editor is empty
        is_editor_empty = editor.is_empty()
        # THEN: editor should be empty AND history should be empty
        assert is_editor_empty
        assert len(editor.history) == 0
        
    def test_clear_empty_editor_is_empty(self):
        # GIVEN: initial document editor right after initialization (with no operation applied)
        editor = DocumentEditor()
        # WHEN: clearing the editor
        editor.clear()
        # THEN: editor should be empty AND history should have one operation
        expected_number_of_operations = 1
        assert len(editor.history) == expected_number_of_operations
        assert editor.is_empty()
        assert len(editor.history) == expected_number_of_operations
        
    def test_written_content_is_correct(self):
        # GIVEN: initial document editor right after initialization (with no operation applied)
        editor = DocumentEditor()
        # WHEN: writing 'Text' to the editor
        editor.write('Text')
        editor.write('Text 2')
        # THEN: content should be 'TextText 2' AND editor should not be empty
        assert editor.content == 'TextText 2'
        assert not editor.is_empty()
        
# pytest document-editor\tests\test_main.py -vv