import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import engine, Base

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest.mark.asyncio
async def test_health_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"

        ready_res = await ac.get("/health/ready")
        assert ready_res.status_code == 200
        ready_data = ready_res.json()
        assert ready_data["ready"] is True
        assert ready_data["database"] == "connected"

@pytest.mark.asyncio
async def test_session_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Create session
        create_res = await ac.post("/api/sessions", json={"title": "Test PM Research"})
        assert create_res.status_code == 201
        session_data = create_res.json()
        session_id = session_data["id"]
        assert session_data["title"] == "Test PM Research"

        # 2. Get session
        get_res = await ac.get(f"/api/sessions/{session_id}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == session_id

        # 3. List sessions
        list_res = await ac.get("/api/sessions")
        assert list_res.status_code == 200
        assert any(s["id"] == session_id for s in list_res.json())

        # 4. Delete session
        del_res = await ac.delete(f"/api/sessions/{session_id}")
        assert del_res.status_code == 204

        # 5. Verify 404 after deletion
        missing_res = await ac.get(f"/api/sessions/{session_id}")
        assert missing_res.status_code == 404

@pytest.mark.asyncio
async def test_grounded_chat_and_citations():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create session
        sess = (await ac.post("/api/sessions", json={"title": "Elena Verna Q&A"})).json()
        sid = sess["id"]

        # Ask grounded growth question
        chat_res = await ac.post("/api/chat", json={
            "session_id": sid,
            "message": "What is Elena Verna's advice on growth loops and innovation at Lovable?",
            "provider": "mock"
        })
        assert chat_res.status_code == 200
        data = chat_res.json()
        assert data["session_id"] == sid
        assert len(data["sources"]) > 0
        assert any("Elena Verna" in s["title"] or "Elena" in (s.get("guest") or "") for s in data["sources"])

@pytest.mark.asyncio
async def test_insufficient_evidence_acknowledgment():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        sess = (await ac.post("/api/sessions", json={"title": "Out of domain test"})).json()
        sid = sess["id"]

        chat_res = await ac.post("/api/chat", json={
            "session_id": sid,
            "message": "How do I bake sourdough bread with wild yeast?",
            "provider": "mock"
        })
        assert chat_res.status_code == 200
        data = chat_res.json()
        assert "insufficient evidence" in data["content"].lower()

@pytest.mark.asyncio
async def test_ship30_skill_generation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        sess = (await ac.post("/api/sessions", json={"title": "Ship 30 Test"})).json()
        sid = sess["id"]

        res = await ac.post("/api/skills/ship30", json={
            "session_id": sid,
            "topic": "The 95% Innovation Rule in AI Startups",
            "target_word_count": 1250,
            "provider": "mock"
        })
        assert res.status_code == 200
        data = res.json()
        assert "artifact_id" in data
        assert len(data["sources"]) > 0
        assert "Source References" in data["content"] or "Elena Verna" in data["content"]

@pytest.mark.asyncio
async def test_models_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/models")
        assert res.status_code == 200
        data = res.json()
        assert "active_provider" in data
        assert len(data["models"]) >= 4
