def test_app_imports() -> None:
    from backend.main import app

    assert app.title == "ResearchForge OS API"
