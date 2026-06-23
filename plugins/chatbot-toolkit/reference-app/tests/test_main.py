from app.channel import InstagramChannel, WhatsAppChannel
from app.config import Settings
from app.main import build_channel


def make_settings(
    channel: str,
    instagram_graph_url: str = "https://graph.facebook.com/v21.0",
) -> Settings:
    return Settings(
        anthropic_api_key="k",
        anthropic_model="m",
        meta_app_secret="s",
        meta_verify_token="v",
        database_url="postgresql://x",
        channel=channel,
        whatsapp_access_token="wa-tok",
        whatsapp_phone_number_id="PNID",
        instagram_access_token="ig-tok",
        instagram_id="IGID",
        instagram_graph_url=instagram_graph_url,
    )


def test_build_channel_defaults_to_whatsapp():
    channel = build_channel(make_settings("whatsapp"))
    assert isinstance(channel, WhatsAppChannel)
    assert channel._phone_number_id == "PNID"


def test_build_channel_selects_instagram():
    channel = build_channel(make_settings("instagram"))
    assert isinstance(channel, InstagramChannel)
    assert channel._ig_id == "IGID"
    assert channel._graph_url == "https://graph.facebook.com/v21.0"


def test_build_channel_uses_configured_instagram_graph_url():
    channel = build_channel(
        make_settings("instagram", instagram_graph_url="https://graph.instagram.com/v21.0")
    )
    assert channel._graph_url == "https://graph.instagram.com/v21.0"
