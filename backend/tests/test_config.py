from app.core.config import settings


def test_public_config_does_not_expose_api_key():
    public_config = settings.public_config()

    assert "llm_api_key" not in public_config
    assert "api_key" not in public_config
