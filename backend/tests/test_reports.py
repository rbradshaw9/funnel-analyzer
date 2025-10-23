import asyncio
from unittest.mock import patch

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.models.database import Analysis, AnalysisPage, Base, User
from backend.services.reports import delete_report


def _run_async(coro):
    return asyncio.run(coro)


class _FakeStorage:
    def __init__(self, succeed: bool = True) -> None:
        self.succeed = succeed
        self.deleted: list[str] = []

    async def delete_object(self, key: str) -> bool:
        self.deleted.append(key)
        return self.succeed


def test_delete_report_removes_assets_and_row():
    async def scenario() -> None:
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        Session = async_sessionmaker(engine, expire_on_commit=False)

        async with Session() as session:
            user = User(email="member@example.com", plan="pro", status="active", is_active=1)
            session.add(user)
            await session.flush()

            analysis = Analysis(
                user_id=user.id,
                urls=["https://example.com"],
                scores={"clarity": 80, "value": 82, "proof": 78, "design": 81, "flow": 79},
                overall_score=80,
                summary="summary",
                detailed_feedback=[
                    {
                        "url": "https://example.com",
                        "scores": {"clarity": 80, "value": 82, "proof": 78, "design": 81, "flow": 79},
                        "feedback": "feedback",
                        "screenshot_storage_key": "screenshots/key-a.png",
                    },
                    {
                        "url": "https://example.com/extra",
                        "scores": {"clarity": 70, "value": 72, "proof": 68, "design": 71, "flow": 69},
                        "feedback": "secondary",
                        "screenshot_storage_key": "screenshots/key-b.png",
                    },
                ],
                pipeline_metrics=None,
                analysis_duration_seconds=15,
            )
            session.add(analysis)
            await session.flush()

            page = AnalysisPage(
                analysis_id=analysis.id,
                url="https://example.com",
                page_scores={"clarity": 80, "value": 82, "proof": 78, "design": 81, "flow": 79},
                page_feedback="feedback",
                screenshot_storage_key="screenshots/key-a.png",
                screenshot_url="https://bucket/screenshots/key-a.png",
            )
            session.add(page)
            await session.commit()

            storage = _FakeStorage()
            with patch("backend.services.reports.get_storage_service", return_value=storage):
                stats = await delete_report(session=session, analysis_id=analysis.id, user_id=user.id)

            assert stats is not None
            assert stats["analysis_id"] == analysis.id
            assert stats["assets_total"] == 2
            assert stats["assets_deleted"] == 2
            assert stats["assets_failed"] == 0
            assert stats["assets_skipped"] == 0
            assert stats["storage_available"] is True
            assert storage.deleted == ["screenshots/key-a.png", "screenshots/key-b.png"]

            remaining = await session.get(Analysis, analysis.id)
            assert remaining is None

            page_exists = await session.get(AnalysisPage, page.id)
            assert page_exists is None

        await engine.dispose()

    _run_async(scenario())


def test_delete_report_skips_assets_when_storage_missing():
    async def scenario() -> None:
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        Session = async_sessionmaker(engine, expire_on_commit=False)

        async with Session() as session:
            user = User(email="member@example.com", plan="pro", status="active", is_active=1)
            session.add(user)
            await session.flush()

            analysis = Analysis(
                user_id=user.id,
                urls=["https://example.com"],
                scores={"clarity": 80, "value": 80, "proof": 80, "design": 80, "flow": 80},
                overall_score=80,
                summary="summary",
                detailed_feedback=[
                    {
                        "url": "https://example.com",
                        "scores": {"clarity": 80, "value": 80, "proof": 80, "design": 80, "flow": 80},
                        "feedback": "feedback",
                        "screenshot_storage_key": "screenshots/key-c.png",
                    }
                ],
                pipeline_metrics=None,
                analysis_duration_seconds=12,
            )
            session.add(analysis)
            await session.commit()

            with patch("backend.services.reports.get_storage_service", return_value=None):
                stats = await delete_report(session=session, analysis_id=analysis.id, user_id=user.id)

            assert stats is not None
            assert stats["assets_total"] == 1
            assert stats["assets_deleted"] == 0
            assert stats["assets_skipped"] == 1
            assert stats["storage_available"] is False

            missing = await session.get(Analysis, analysis.id)
            assert missing is None

        await engine.dispose()

    _run_async(scenario())


def test_delete_report_returns_none_when_not_found():
    async def scenario() -> None:
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        Session = async_sessionmaker(engine, expire_on_commit=False)

        async with Session() as session:
            result = await delete_report(session=session, analysis_id=9999, user_id=1)
            assert result is None

        await engine.dispose()

    _run_async(scenario())
