import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.models.database import Analysis, AnalysisPage, Base, User
from backend.services.cleanup import cleanup_ephemeral_screenshots


def _run_async(coro):
    return asyncio.run(coro)


class _FakeStorage:
    def __init__(self) -> None:
        self.deleted: list[str] = []

    async def delete_object(self, key: str) -> bool:
        self.deleted.append(key)
        return True


def test_cleanup_prunes_free_analysis_screenshots():
    async def scenario():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        Session = async_sessionmaker(engine, expire_on_commit=False)

        async with Session() as session:
            now = datetime.now(timezone.utc)

            user = User(email="demo@funnelanalyzer.pro", plan="free", status="active", is_active=1)
            session.add(user)
            await session.flush()

            analysis = Analysis(
                user_id=user.id,
                urls=["https://example.com"],
                scores={"clarity": 50, "value": 50, "proof": 50, "design": 50, "flow": 50},
                overall_score=50,
                summary="summary",
                detailed_feedback=[
                    {
                        "url": "https://example.com",
                        "scores": {
                            "clarity": 50,
                            "value": 50,
                            "proof": 50,
                            "design": 50,
                            "flow": 50,
                        },
                        "feedback": "feedback",
                        "screenshot_url": "https://bucket/screenshots/test.png",
                        "screenshot_storage_key": "screenshots/test.png",
                    }
                ],
                analysis_duration_seconds=10,
                created_at=now - timedelta(days=10),
            )
            session.add(analysis)
            await session.flush()

            page = AnalysisPage(
                analysis_id=analysis.id,
                url="https://example.com",
                page_scores={"clarity": 50, "value": 50, "proof": 50, "design": 50, "flow": 50},
                page_feedback="feedback",
                screenshot_url="https://bucket/screenshots/test.png",
                screenshot_storage_key="screenshots/test.png",
            )
            session.add(page)
            await session.commit()

            storage = _FakeStorage()
            with patch("backend.services.cleanup.get_storage_service", return_value=storage):
                stats = await cleanup_ephemeral_screenshots(
                    session,
                    retention_days=7,
                    dry_run=False,
                    now=now,
                )

            assert stats["deleted"] == 1
            assert storage.deleted == ["screenshots/test.png"]

            refreshed_page = await session.get(AnalysisPage, page.id)
            assert refreshed_page is not None
            assert refreshed_page.screenshot_storage_key is None
            assert refreshed_page.screenshot_url is None

            refreshed_analysis = await session.get(Analysis, analysis.id)
            assert isinstance(refreshed_analysis.detailed_feedback, list)
            assert refreshed_analysis.detailed_feedback[0]["screenshot_storage_key"] is None
            assert refreshed_analysis.detailed_feedback[0]["screenshot_url"] is None

        await engine.dispose()

    _run_async(scenario())