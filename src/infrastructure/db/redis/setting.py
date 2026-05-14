from pydantic_settings import BaseSettings, SettingsConfigDict

class SettingsRedis(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str = ""
    
    @property
    def get_redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = SettingsRedis()
