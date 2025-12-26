from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    URL_RATE_API: str

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    abstract_api_key: str = ('your-abstract-api-key')

    SECRET_KEY: str = 'your_secret_key' # ключ для соз
    # дания JWT токенов
    ALGORITHM: str # алгоритм для создания JWT токенов

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str

    DS_API_KEY: str


    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


    @property
    def rabbitmq_url(self) -> str:
        return (
            f'amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@'
            f'{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}'
        )


    @property
    def redis_url(self) -> str:
        return (
            f'redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:'
            f'{self.REDIS_PORT}/{self.REDIS_DB}'
        )


    @property
    def abstract_key(self) -> str:
        return self.abstract_api_key


    @property
    def secret_key(self) -> str:
        return self.SECRET_KEY


    @property
    def algorithm(self) -> str:
        return self.ALGORITHM


settings = Settings()
