"""Database connection management."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as aioredis
from elasticsearch import AsyncElasticsearch
from config.settings import settings


# PostgreSQL Connection
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    poolclass=NullPool if settings.environment == "test" else None,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# MongoDB Connection
mongo_client = AsyncIOMotorClient(settings.mongodb_url)
mongo_db = mongo_client[settings.mongo_db]


async def get_mongo_db():
    """Get MongoDB database."""
    return mongo_db


# Redis Connection
redis_client = None


async def get_redis():
    """Get Redis client."""
    global redis_client
    if redis_client is None:
        redis_client = await aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )
    return redis_client


# Elasticsearch Connection
es_client = AsyncElasticsearch([settings.elasticsearch_url])


async def get_elasticsearch():
    """Get Elasticsearch client."""
    return es_client


async def close_connections():
    """Close all database connections."""
    global redis_client

    # Close PostgreSQL
    await engine.dispose()

    # Close MongoDB
    mongo_client.close()

    # Close Redis
    if redis_client:
        await redis_client.close()

    # Close Elasticsearch
    await es_client.close()
