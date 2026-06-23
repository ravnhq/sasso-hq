from fastapi import FastAPI

from app.brain import ClaudeBrain
from app.channel import Channel, InstagramChannel, WhatsAppChannel
from app.config import Settings, load_settings
from app.guardrails import HeuristicGuardrails
from app.session import PostgresSessionStore
from app.webhook import create_app


def build_channel(settings: Settings) -> Channel:
    if settings.channel == "instagram":
        return InstagramChannel(
            app_secret=settings.meta_app_secret,
            verify_token=settings.meta_verify_token,
            access_token=settings.instagram_access_token,
            ig_id=settings.instagram_id,
            graph_url=settings.instagram_graph_url,
        )
    return WhatsAppChannel(
        app_secret=settings.meta_app_secret,
        verify_token=settings.meta_verify_token,
        access_token=settings.whatsapp_access_token,
        phone_number_id=settings.whatsapp_phone_number_id,
    )


def create_default_app() -> FastAPI:
    settings = load_settings()
    brain = ClaudeBrain(
        model=settings.anthropic_model, api_key=settings.anthropic_api_key
    )
    return create_app(
        channel=build_channel(settings),
        brain=brain,
        store=PostgresSessionStore(settings.database_url),
        guardrails=HeuristicGuardrails(),
    )
