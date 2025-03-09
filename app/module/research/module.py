from firecrawl import FirecrawlApp
from app.module.Base import BaseNode
from app.module.state import ChatState
from app.core.config import settings


class ResearchNode(BaseNode):
    def __init__(self, verbose=False, **kwargs):
        super().__init__(verbose=verbose, **kwargs)
        self.app = FirecrawlApp(api_key=settings.FIRECRAWL_API_KEY,api_url=settings.FIRECRAWL_URL)

    def execute(self, state: ChatState) -> ChatState:
        query = state.get("queue")
        research = self._research(query)
        state["research_results"] = research
        return state

    def _research(self, query: str) -> dict:
        try:
            response = self.app.search(
                query=query,
                params={"timeout": 15000, "limit": 20, "scrapeOptions": {"formats": ["markdown"]}}
            )
            
            # 검색 결과가 있는지 확인
            if 'data' in response and response['data'] and len(response['data']) > 0:
                return {
                    "title": response['data'][0]['title'], 
                    "description": response['data'][0]['description'], 
                    "url": response['data'][0]['url']
                }
            else:
                # 검색 결과가 없는 경우 기본 응답
                self.log(f"'{query}' 검색에 대한 결과가 없습니다.")
                return {
                    "title": "검색 결과 없음", 
                    "description": f"'{query}'에 대한 검색 결과가 없습니다.", 
                    "url": ""
                }
        except Exception as e:
            # 오류 발생 시 기본 응답
            self.log(f"검색 중 오류 발생: {str(e)}")
            return {
                "title": "검색 오류", 
                "description": f"검색 중 오류가 발생했습니다: {str(e)}", 
                "url": ""
            }


# app = FirecrawlApp(api_key=settings.FIRECRAWL_API_KEY,api_url=settings.FIRECRAWL_URL)

# response = app.search(
#             query="한국 영화의 문제점",
#             params={"timeout": 15000, "limit": 20, "scrapeOptions": {"formats": ["markdown"]}}
#         )

# print(response, len(response))
# print(response.keys())
# print(response['data'][0].keys())
# print(response['data'][0]['title'])
# print(response['data'][0]['description'])
# print(response['data'][0]['metadata'])
# print(response['data'][0]['url'])

