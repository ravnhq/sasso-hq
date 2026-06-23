import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str
    anthropic_model: str
    meta_app_secret: str
    meta_verify_token: str
    database_url: str
    channel: str
    whatsapp_access_token: str
    whatsapp_phone_number_id: str
    instagram_access_token: str
    instagram_id: str
    instagram_graph_url: str


def load_settings() -> Settings:
    return Settings(
        anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
        anthropic_model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        meta_app_secret=os.environ["META_APP_SECRET"],
        meta_verify_token=os.environ["META_VERIFY_TOKEN"],
        database_url=os.environ["DATABASE_URL"],
        channel=os.environ.get("CHANNEL", "whatsapp"),
        whatsapp_access_token=os.environ.get("WHATSAPP_ACCESS_TOKEN", ""),
        whatsapp_phone_number_id=os.environ.get("WHATSAPP_PHONE_NUMBER_ID", ""),
        instagram_access_token=os.environ.get("INSTAGRAM_ACCESS_TOKEN", ""),
        instagram_id=os.environ.get("INSTAGRAM_ID", ""),
        instagram_graph_url=os.environ.get(
            "INSTAGRAM_GRAPH_URL", "https://graph.facebook.com/v21.0"
        ),
    )
