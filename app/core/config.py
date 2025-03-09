import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 프로젝트 루트 디렉토리 설정
ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class LLMSettings(BaseSettings):
    """
    LLM(Large Language Model) 관련 설정 클래스
    
    LLM API 키 및 기본 설정을 관리합니다.
    """
    # API 키
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # 기본 모델 설정
    default_model: str = "gpt-4o-mini"
    default_temperature: float = 0.7
    streaming: bool = True
    timeout: int = 20
    max_retries: int = 3
    
    class Config:
        """Pydantic 설정 클래스"""
        extra = "ignore"


class SearchSettings(BaseSettings):
    """
    검색 관련 설정 클래스
    
    검색 API 키 및 관련 설정을 관리합니다.
    """
    firecrawl_api_key: str = os.getenv("FIRECRAWL_API_KEY", "")
    firecrawl_url: str = os.getenv("FIRECRAWL_URL", "")
    
    class Config:
        """Pydantic 설정 클래스"""
        extra = "ignore"


class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스
    
    환경 변수에서 설정을 로드하고 애플리케이션 전체에서 사용할 수 있는 설정을 제공합니다.
    """
    # 기본 API 설정
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "DeepSearch"
    PROJECT_DESCRIPTION: str = "심층적인 AI 리서치 에이전트 API"
    VERSION: str = "1.0.0"
    
    # 중첩 설정 객체
    llm: LLMSettings = LLMSettings()
    search: SearchSettings = SearchSettings()
    
    # 디렉토리 설정
    OUTPUT_DIR: Path = ROOT_DIR / "data" / "output"
    TEMP_DIR: Path = ROOT_DIR / "data" / "temp"
    
    # 리서치 설정
    MAX_RESEARCH_DEPTH: int = 3
    MAX_RESEARCH_WIDTH: int = 3
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Streamlit 관련 설정
    STREAMLIT_PORT: int = 8501
    
    # Firecrawl 설정
    FIRECRAWL_API_KEY: str = os.getenv("FIRECRAWL_API_KEY", "")
    FIRECRAWL_URL: str = os.getenv("FIRECRAWL_URL", "")
    
    # FastAPI 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        """Pydantic 설정 클래스"""
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # 추가 필드 무시

    def dict_with_flat_values(self) -> Dict[str, Any]:
        """
        설정 값들을 평면화된 딕셔너리로 반환
        
        경로 객체 등을 문자열로 변환하여 JSON 직렬화 가능한 형태로 반환
        """
        config_dict = self.dict()
        for key, value in config_dict.items():
            if isinstance(value, Path):
                config_dict[key] = str(value)
        return config_dict


# 설정 인스턴스 생성
settings = Settings()

# 디렉토리 존재 확인 및 생성
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)
