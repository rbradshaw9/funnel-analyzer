"""CLI helper to prune stale screenshot assets from storage."""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime

from ..db.session import AsyncSessionFactory, init_db
from ..services.cleanup import cleanup_ephemeral_screenshots


async def main() -> None:
    parser = argparse.ArgumentParser(description="Remove stale screenshot uploads from S3")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute deletions. Without this flag the command runs in dry-run mode",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Retention window (days) for anonymous/free analyses",
    )
    args = parser.parse_args()

    await init_db()

    async with AsyncSessionFactory() as session:
        stats = await cleanup_ephemeral_screenshots(
            session,
            retention_days=max(1, args.days),
            dry_run=not args.apply,
        )

    print(json.dumps(stats, default=str, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
