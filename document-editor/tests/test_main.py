from errno import EISDIR
from src.main import DocumentEditor

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
        assert editor.get_last_content() == ''
        editor.write('Text 2')
        assert editor.get_last_content() == 'Text'
