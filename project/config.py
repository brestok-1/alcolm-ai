import os
import pathlib
from functools import lru_cache

import pandas as pd
from openai import AsyncOpenAI
from environs import Env
import faiss

env = Env()
env.read_env()


class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent
    OPENAI_CLIENT = AsyncOpenAI(api_key=env('OPENAI_API_KEY'))
    FAISS_INDEX = faiss.read_index(str(BASE_DIR / 'faiss.index'))
    SEARCH_RADIUS = 15


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    ORIGINS = ["http://127.0.0.1:8000",
               "http://localhost:8000",
               'https://alcolm.com/',
               'https://help.alcolm.com/'
               ]
    QA_PROMPT = """As the virtual assistant for Alcolm AI, a company renowned for its expertise in developing bespoke cloud solutions, your role encompasses providing comprehensive and structured responses based on previous interactions. Ensure your answers remain within the realm of Alcolm's specialization, avoiding references to external companies. For detailed information or further reading, incorporate links directing users to the appropriate page on our website. Your responses should precisely address the user's query, leveraging insights from earlier discussions to ensure relevance and accuracy."""

    def __init__(self):
        self.products_dataset = pd.read_csv(self.BASE_DIR / 'chunk.csv')


class TestConfig(BaseConfig):
    pass


@lru_cache()
def get_settings() -> DevelopmentConfig | ProductionConfig | TestConfig:
    config_cls_dict = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestConfig
    }
    config_name = env('FASTAPI_CONFIG', default='production')
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
