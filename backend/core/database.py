"""
Database connection management for PostgreSQL, MongoDB, Elasticsearch, and Redis.
"""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis
import logging

from config.settings import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

# Database engines and clients
postgres_engine = None
mongo_client: Optional[AsyncIOMotorClient] = None
elasticsearch_client: Optional[AsyncElasticsearch] = None
redis_client: Optional[Redis] = None

# Session makers
AsyncSessionLocal = None


async def init_postgres():
    """Initialize PostgreSQL connection."""
    global postgres_engine, AsyncSessionLocal

    try:
        postgres_engine = create_async_engine(
            settings.async_postgres_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )

        AsyncSessionLocal = async_sessionmaker(
            postgres_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        logger.info("PostgreSQL connection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL: {e}")
        raise


async def init_mongodb():
    """Initialize MongoDB connection."""
    global mongo_client

    try:
        mongo_client = AsyncIOMotorClient(
            settings.mongo_url,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000
        )

        # Test connection
        await mongo_client.admin.command('ping')
        logger.info("MongoDB connection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {e}")
        raise


async def init_elasticsearch():
    """Initialize Elasticsearch connection."""
    global elasticsearch_client

    try:
        elasticsearch_client = AsyncElasticsearch(
            [settings.elasticsearch_url],
            verify_certs=False,
            max_retries=3,
            retry_on_timeout=True
        )

        # Test connection
        info = await elasticsearch_client.info()
        logger.info(f"Elasticsearch connection initialized: {info['version']['number']}")
    except Exception as e:
        logger.error(f"Failed to initialize Elasticsearch: {e}")
        raise


async def init_redis():
    """Initialize Redis connection."""
    global redis_client

    try:
        redis_client = Redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50
        )

        # Test connection
        await redis_client.ping()
        logger.info("Redis connection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        raise


async def close_postgres():
    """Close PostgreSQL connection."""
    global postgres_engine
    if postgres_engine:
        await postgres_engine.dispose()
        logger.info("PostgreSQL connection closed")


async def close_mongodb():
    """Close MongoDB connection."""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")


async def close_elasticsearch():
    """Close Elasticsearch connection."""
    global elasticsearch_client
    if elasticsearch_client:
        await elasticsearch_client.close()
        logger.info("Elasticsearch connection closed")


async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_mongo_db():
    """Get MongoDB database instance."""
    if mongo_client is None:
        raise RuntimeError("MongoDB client not initialized")
    return mongo_client[settings.MONGO_DB]


def get_elasticsearch():
    """Get Elasticsearch client."""
    if elasticsearch_client is None:
        raise RuntimeError("Elasticsearch client not initialized")
    return elasticsearch_client


def get_redis():
    """Get Redis client."""
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client


# Database initialization function
async def init_databases():
    """Initialize all database connections."""
    logger.info("Initializing database connections...")
    await init_postgres()
    await init_mongodb()
    await init_elasticsearch()
    await init_redis()
    logger.info("All database connections initialized")


# Database cleanup function
async def close_databases():
    """Close all database connections."""
    logger.info("Closing database connections...")
    await close_postgres()
    await close_mongodb()
    await close_elasticsearch()
    await close_redis()
    logger.info("All database connections closed")
