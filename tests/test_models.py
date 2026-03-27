from app.models.logs import list_chatrooms, parse_log_file


def test_list_chatrooms_empty():
    """Test listing chatrooms when none exist"""
    result = list_chatrooms('/nonexistent/path')
    assert result == []
