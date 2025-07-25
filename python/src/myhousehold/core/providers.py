from typing import AsyncGenerator, Iterable

from dishka import Provider, Scope, provide
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import Session


class ConfigPostgres(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str
    test_database: str | None = None
    use_test_by_default: bool = False
    pool_size: int = 5
    pool_max_overflow: int = 10

    def get_sqlalchemy_url(
        self,
        driver: str,
        *,
        is_test_database: bool | None = None,
    ):
        if is_test_database is None:
            is_test_database = self.use_test_by_default

        database = self.database
        if is_test_database:
            if self.test_database is None:
                raise ValueError("Test database not specified")
            database = self.test_database

        return "postgresql+{}://{}:{}@{}:{}/{}".format(
            driver,
            self.user,
            self.password,
            self.host,
            self.port,
            database,
        )


class ConfigMyHousehold(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        env_prefix="MYHOUSEHOLD__",
    )

    postgres: ConfigPostgres


class ProviderConfig(Provider):
    @provide(scope=Scope.APP)
    def get_config_myhousehold(self) -> ConfigMyHousehold:
        return ConfigMyHousehold()  # type: ignore

    @provide(scope=Scope.APP)
    def get_config_postgres(
        self,
        config: ConfigMyHousehold,
    ) -> ConfigPostgres:
        return config.postgres


class ProviderDatabase(Provider):
    @provide(scope=Scope.APP)
    def get_database_engine(
        self,
        config: ConfigPostgres,
    ) -> AsyncEngine:
        return create_async_engine(
            config.get_sqlalchemy_url("psycopg"),
        )

    @provide(scope=Scope.SESSION)
    async def get_database_session(
        self,
        engine: AsyncEngine,
    ) -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSession(
                engine,
                expire_on_commit=False,
        ) as session:
            yield session


class ProviderTestDatabase(Provider):
    def get_database_engine(
            self,
            config: ConfigPostgres,
    ) -> Engine:
        return create_engine(
            config.get_sqlalchemy_url("psycopg"),
        )

    def get_database_session(
            self,
            engine: Engine,
    ) -> Iterable[Session]:
        with Session(engine) as session:
            yield session
