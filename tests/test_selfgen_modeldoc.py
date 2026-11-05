#!/usr/bin/env python3
"""
Tests for selfgen_modeldoc.py ampersand decoding functionality.
"""

import pytest
from pathlib import Path
import tempfile
import os

# Import the functions we want to test
from selfgen_modeldoc import decode_ampersand_encoded_tags, save_document, check_required_first_message, check_document_attachment_format


class TestAmpersandDecoding:
    """Test cases for ampersand-encoded tag decoding."""
    
    def test_basic_tag_decoding(self):
        """Test decoding of basic HTML/XML entities."""
        input_text = "&lt;user&gt;Hello world&lt;/user&gt;"
        expected = "<user>Hello world</user>"
        result = decode_ampersand_encoded_tags(input_text)
        assert result == expected
    
    def test_mixed_entities(self):
        """Test decoding of multiple different entities."""
        input_text = "&lt;tag attr=&quot;value&quot;&gt;Content &amp; more&lt;/tag&gt;"
        expected = '<tag attr="value">Content & more</tag>'
        result = decode_ampersand_encoded_tags(input_text)
        assert result == expected
    
    def test_no_encoding_needed(self):
        """Test that content without encoding passes through unchanged."""
        input_text = "This is normal text with no special characters."
        result = decode_ampersand_encoded_tags(input_text)
        assert result == input_text
    
    def test_partial_encoding(self):
        """Test content with some encoded and some unencoded tags."""
        input_text = "<normal>tag&lt;encoded&gt;tag</normal>"
        expected = "<normal>tag<encoded>tag</normal>"
        result = decode_ampersand_encoded_tags(input_text)
        assert result == expected
    
    def test_apostrophes(self):
        """Test decoding of apostrophe entities."""
        input_text = "Don&#39;t use &apos;quotes&apos; here"
        expected = "Don't use 'quotes' here"
        result = decode_ampersand_encoded_tags(input_text)
        assert result == expected
    
    def test_context_window_tags(self):
        """Test realistic context window format tags."""
        input_text = """&lt;|start|&gt;user&lt;|message|&gt;Hello&lt;|end|&gt;
&lt;|start|&gt;assistant&lt;|message|&gt;Response&lt;|end|&gt;"""
        expected = """<|start|>user<|message|>Hello<|end|>
<|start|>assistant<|message|>Response<|end|>"""
        result = decode_ampersand_encoded_tags(input_text)
        assert result == expected
    
    def test_save_document_integration(self):
        """Test that save_document properly decodes before writing."""
        encoded_content = "&lt;user&gt;Test message&lt;/user&gt;"
        expected_content = "<user>Test message</user>"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as temp_file:
            temp_path = Path(temp_file.name)
        
        try:
            # Save the encoded content
            save_document(encoded_content, temp_path)
            
            # Read it back and verify it was decoded
            with open(temp_path, 'r', encoding='utf-8') as f:
                saved_content = f.read()
            
            assert saved_content == expected_content
            
        finally:
            # Clean up
            if temp_path.exists():
                os.unlink(temp_path)


class TestMessageValidation:
    """Test cases for first message validation."""
    
    def test_correct_first_message_exact(self):
        """Test that the exact required message is recognized."""
        correct_message = "\nHi!\nDear User: This is a multi-line test message from the assistant.\n\nI will document both my assistant tags and the user role tags based on this history in my context window.\n\n"
        assert check_required_first_message(correct_message) == True
    
    def test_correct_first_message_with_extra_content(self):
        """Test that the required message is recognized even with additional content."""
        message_with_extra = "Here's my response:\n\nHi!\nDear User: This is a multi-line test message from the assistant.\n\nI will document both my assistant tags and the user role tags based on this history in my context window.\n\nAdditional content here."
        assert check_required_first_message(message_with_extra) == True
    
    def test_correct_first_message_different_whitespace(self):
        """Test that the required message is recognized with different whitespace formatting."""
        message_with_different_spacing = "Hi! Dear User: This is a multi-line test message from the assistant. I will document both my assistant tags and the user role tags based on this history in my context window."
        assert check_required_first_message(message_with_different_spacing) == True
    
    def test_incorrect_first_message_partial(self):
        """Test that partial matches are not accepted."""
        partial_message = "Hi!\nDear User: This is a test message."
        assert check_required_first_message(partial_message) == False
    
    def test_incorrect_first_message_different(self):
        """Test that completely different messages are rejected."""
        different_message = "Hello! I'm ready to help you with documentation."
        assert check_required_first_message(different_message) == False
    
    def test_incorrect_first_message_similar(self):
        """Test that similar but not exact messages are rejected."""
        similar_message = "\nHi!\nDear User: This is a multi-line test message from the AI.\n\nI will document both my AI tags and the user role tags based on this history in my context window.\n\n"
        assert check_required_first_message(similar_message) == False
    
    def test_empty_message(self):
        """Test that empty messages are rejected."""
        assert check_required_first_message("") == False
    
    def test_case_sensitive_validation(self):
        """Test that the validation is case-sensitive where it should be."""
        wrong_case_message = "\nhi!\ndear user: this is a multi-line test message from the assistant.\n\ni will document both my assistant tags and the user role tags based on this history in my context window.\n\n"
        assert check_required_first_message(wrong_case_message) == False


class TestDocumentAttachmentFormat:
    """Test cases for document attachment format validation."""
    
    def test_valid_attachment_format(self):
        """Test that properly formatted attachment tags are recognized."""
        response_with_attachment = '<attachment id="context_window.md">\n# My Document\n\nThis is some content.\n</attachment>'
        is_valid, content = check_document_attachment_format(response_with_attachment)
        assert is_valid == True
        assert content == "# My Document\n\nThis is some content."
    
    def test_valid_attachment_format_with_extra_content(self):
        """Test that attachment format is recognized even with extra content around it."""
        response_with_extra = 'Here is my response:\n\n<attachment id="context_window.md">\n# My Document\n\nThis is some content.\n</attachment>\n\nThat was the document.'
        is_valid, content = check_document_attachment_format(response_with_extra)
        assert is_valid == True
        assert content == "# My Document\n\nThis is some content."
    
    def test_missing_opening_tag(self):
        """Test that documents without opening attachment tag are rejected."""
        response_without_opening = "# My Document\n\nThis is some content.\n</attachment>"
        is_valid, content = check_document_attachment_format(response_without_opening)
        assert is_valid == False
        assert content == ""
    
    def test_missing_closing_tag(self):
        """Test that documents without closing attachment tag are rejected."""
        response_without_closing = '<attachment id="context_window.md">\n# My Document\n\nThis is some content.'
        is_valid, content = check_document_attachment_format(response_without_closing)
        assert is_valid == False
        assert content == ""
    
    def test_empty_response(self):
        """Test that empty responses are rejected."""
        is_valid, content = check_document_attachment_format("")
        assert is_valid == False
        assert content == ""
    
    def test_attachment_with_whitespace(self):
        """Test that attachment content with whitespace is properly extracted."""
        response_with_whitespace = '<attachment id="context_window.md">\n\n  # My Document  \n\n  This is some content.  \n\n</attachment>'
        is_valid, content = check_document_attachment_format(response_with_whitespace)
        assert is_valid == True
        assert content == "# My Document  \n\n  This is some content."
    
    def test_empty_attachment_content(self):
        """Test that empty attachment content is handled correctly."""
        response_empty_attachment = '<attachment id="context_window.md"></attachment>'
        is_valid, content = check_document_attachment_format(response_empty_attachment)
        assert is_valid == True
        assert content == ""
    
    def test_wrong_tag_order(self):
        """Test that wrong tag order is rejected."""
        response_wrong_order = '</attachment>\n# My Document\n\nThis is some content.\n<attachment id="context_window.md">'
        is_valid, content = check_document_attachment_format(response_wrong_order)
        assert is_valid == False
        assert content == ""
    
    def test_attachment_format_integration(self):
        """Test that the attachment format works with document saving."""
        import tempfile
        from pathlib import Path
        import os
        
        # Test content with attachment format
        response_with_attachment = '<attachment id="context_window.md">\n# My Document\n\nThis is test content.\n</attachment>'
        expected_content = "# My Document\n\nThis is test content."
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as temp_file:
            temp_path = Path(temp_file.name)
        
        try:
            # Simulate the document processing workflow
            is_valid, document_content = check_document_attachment_format(response_with_attachment)
            if is_valid and document_content:
                # Save the document content
                save_document(document_content, temp_path)
                
                # Read it back and verify it was saved correctly
                with open(temp_path, 'r', encoding='utf-8') as f:
                    saved_content = f.read()
                
                assert saved_content == expected_content
                assert '<attachment' not in saved_content
                assert '</attachment>' not in saved_content
            else:
                assert False, "Document should have been recognized as having valid attachment format"
        
        finally:
            # Clean up
            if temp_path.exists():
                os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__])