from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse

from app.brain import Brain
from app.channel import Channel
from app.guardrails import Guardrails
from app.models import Message, OutboundMessage
from app.session import SessionStore

PRIVACY_POLICY = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Privacy Policy</title></head><body>
<h1>Privacy Policy</h1>
<p>This application is a Claude-powered messaging assistant. When you send it a
message on a connected channel (such as Instagram or WhatsApp), we process the
message text and your channel-provided conversation identifier solely to
generate and deliver a reply.</p>
<p>Conversation history is stored only to maintain context within a conversation
and is not sold or shared with third parties beyond the messaging platform and
the language-model provider used to produce replies.</p>
<p>To request access to or deletion of your data, see our
<a href="/data-deletion">data deletion instructions</a>.</p>
</body></html>"""

DATA_DELETION = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Data Deletion</title></head><body>
<h1>Data Deletion Instructions</h1>
<p>To delete the conversation data associated with your account, send a message
containing the word "delete" on the same channel you used to contact this
assistant, or contact the operator of this application. Your stored conversation
history will be removed.</p>
</body></html>"""


def create_app(
    channel: Channel,
    brain: Brain,
    store: SessionStore,
    guardrails: Guardrails,
) -> FastAPI:
    app = FastAPI()

    @app.get("/privacy", response_class=HTMLResponse)
    async def privacy() -> str:
        return PRIVACY_POLICY

    @app.get("/data-deletion", response_class=HTMLResponse)
    async def data_deletion() -> str:
        return DATA_DELETION

    @app.get("/webhook")
    async def verify(request: Request) -> Response:
        challenge = channel.verify(dict(request.query_params))
        if challenge is None:
            return Response(status_code=403)
        return Response(content=challenge, media_type="text/plain")

    @app.post("/webhook")
    async def receive(request: Request) -> Response:
        raw = await request.body()
        if not channel.verify_signature(raw, request.headers):
            return Response(status_code=403)
        inbound = channel.parse(raw)
        if inbound is None:
            return Response(status_code=200)

        guard_in = guardrails.screen_input(inbound.text)
        if not guard_in.allowed:
            await channel.send(
                OutboundMessage(conversation_id=inbound.conversation_id, text=guard_in.text)
            )
            return Response(status_code=200)

        history = await store.get_history(inbound.conversation_id)
        reply = await brain.respond(history, guard_in.text)
        guard_out = guardrails.screen_output(reply)

        await store.append(inbound.conversation_id, Message(role="user", text=inbound.text))
        await store.append(
            inbound.conversation_id, Message(role="assistant", text=guard_out.text)
        )
        await channel.send(
            OutboundMessage(conversation_id=inbound.conversation_id, text=guard_out.text)
        )
        return Response(status_code=200)

    return app
