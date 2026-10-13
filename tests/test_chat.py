import pytest

@pytest.mark.asyncio
async def test_chat_flow(client):
    sp = await client.post("/api/system-prompts", json={"name": "default", "body": "Be concise."})
    assert sp.status_code == 200
    sess = await client.post("/api/sessions", json={"title": "Demo", "system_inline": "Helpful bot"})
    assert sess.status_code == 200
    sid = sess.json()["id"]
    msg = await client.post(f"/api/sessions/{sid}/messages", json={"content": "Hello there"})
    assert msg.status_code == 200
    assert msg.json()["reply"]

@pytest.mark.asyncio
async def test_chat_stream(client):
    sess = await client.post("/api/sessions", json={"title": "Stream"})
    sid = sess.json()["id"]
    async with client.stream("POST", f"/api/sessions/{sid}/stream", json={"content": "ping"}) as resp:
        assert resp.status_code == 200
        lines = []
        async for line in resp.aiter_lines():
            if line.startswith("data: "):
                lines.append(line[6:])
    assert any(l != "[DONE]" for l in lines)
