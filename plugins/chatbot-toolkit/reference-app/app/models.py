from dataclasses import dataclass


@dataclass(frozen=True)
class InboundMessage:
    conversation_id: str
    text: str


@dataclass(frozen=True)
class OutboundMessage:
    conversation_id: str
    text: str


@dataclass(frozen=True)
class Message:
    role: str  # "user" or "assistant"
    text: str
