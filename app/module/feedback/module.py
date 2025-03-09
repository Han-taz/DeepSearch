from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from app.module.Base import BaseNode
from app.core.llms import LLMManager
from app.prompt.load_prompt import load_prompt_from_yaml
from app.module.state import ChatState
from langgraph.types import interrupt
from typing import Dict, List, Optional

class Feedback(BaseModel):
    feedbacks: list[str] = Field(description="피드백 질문")

class SearchQuery(BaseModel):
    """검색 질문"""
    search_queries: list[str] = Field(description="검색 질문")

class FeedbackNode(BaseNode):
    def __init__(self, verbose=False, **kwargs):
        super().__init__(verbose=verbose, **kwargs)
        raw_prompt = load_prompt_from_yaml("feedback")
        self.parser = PydanticOutputParser(pydantic_object=Feedback)
        self.prompt = raw_prompt.partial(format=self.parser.get_format_instructions())
        self.llm = LLMManager.get_llm("gpt-4o-mini")
        self.chain = self.prompt | self.llm | self.parser

    def execute(self, state: ChatState) -> ChatState:
        query = state.get("messages")
        max_feedbacks = state.get("max_feedbacks")
        feedbacks = self._get_feedback(query, max_feedbacks)
        state["feedbacks"] = feedbacks
        return state

    def _get_feedback(self, query: str, max_feedbacks: int = 3) -> list[str]:
        return self.chain.invoke({"query": query, "max_feedbacks": max_feedbacks})


class AskHumanNode(BaseNode):
    def __init__(self, verbose=False, **kwargs):
        super().__init__(verbose=verbose, **kwargs)
    
    def execute(self, state: ChatState) -> ChatState:
        # 현재 질문 가져오기
        question = state.get("queue")
        
        # 질문이 완료 표시이거나 없으면 처리하지 않음
        if not question or question == "<<FINISHED>>":
            return state
        
        # 로깅
        self.log(f"사용자에게 질문: {question}")
        
        # interrupt를 사용하여 사용자 입력 요청
        # 이렇게 하면 그래프 실행이 중단되고 외부에서 입력을 받을 수 있음
        # 이 부분은 컴파일 시 interrupt_before=['ask_human_node']와 함께 작동


        # feedback_qa 리스트 초기화 (없는 경우)
        qa_list = state.get("feedback_qa", [])
        
        # 새 QA 쌍 추가
        feedback_qa = {
            "question": question,
            "answer": None
        }
        qa_list.append(feedback_qa)
        
        
        # 상태 업데이트 및 반환
        return {"feedback_qa": qa_list}

class CreateSearchQueryNode(BaseNode):
    def __init__(self, verbose=False, **kwargs):
        super().__init__(verbose=verbose, **kwargs)
        prompt = load_prompt_from_yaml("create_search_query")
        self.parser = PydanticOutputParser(pydantic_object=Feedback)
        self.prompt = prompt.partial(format=self.parser.get_format_instructions())
        self.llm = LLMManager.get_llm("gpt-4o-mini")
        self.chain = self.prompt | self.llm | self.parser
    def execute(self, state: ChatState) -> ChatState:
        # 현재 질문 가져오기
        question = state.get("feedback_qa")[-1]['question']
        
        # 질문이 완료 표시이거나 없으면 처리하지 않음
        if not question:
            self.log("질문이 없습니다.")
            return state
 

        query_info = {
            "original_query": state.get("messages"),
            "follow_up_question": question,
            "follow_up_answer": state.get("feedback_qa")[-1]['answer'],
        }

        search_query = self._get_question(query_info)
        
        # 상태 업데이트 및 반환
        return {"search_query": search_query}

    def _get_question(self, query_info: Dict, max_queries: int = 5) -> list[str]:
        return self.chain.invoke({"original_query": query_info["original_query"], "follow_up_question": query_info["follow_up_question"], "follow_up_answer": query_info["follow_up_answer"], "max_queries": max_queries})
class WorkingQueueNode(BaseNode):
    def __init__(self, verbose=False, **kwargs):
        super().__init__(verbose=verbose, **kwargs)

    def execute(self, state: ChatState):
        # 이미 완료된 경우
        if state.get("queue") == "<<FINISHED>>":
            return {"queue": "<<FINISHED>>"}
            
        # feedbacks 리스트 가져오기
        if "feedbacks" in state and hasattr(state["feedbacks"], "feedbacks"):
            feedbacks_list = state["feedbacks"].feedbacks
            
            # 인덱스 관리
            current_index = state.get("queue_index", 0)
            
            # 모든 피드백을 처리했는지 확인
            if not feedbacks_list or current_index >= len(feedbacks_list):
                self.log("모든 피드백을 처리했습니다.")
                return {"queue": "<<FINISHED>>"}
            
            # 현재 인덱스의 피드백 가져오기
            current_feedback = feedbacks_list[current_index]
            self.log(f"처리 중인 피드백 ({current_index+1}/{len(feedbacks_list)}): {current_feedback}")
            
            # 다음 인덱스 설정
            next_index = current_index + 1
            
            # 피드백 객체를 변경하지 않고 상태만 업데이트
            return {
                "queue": current_feedback,
                "queue_index": next_index
            }
        
        # feedbacks가 없는 경우
        return {"queue": "<<FINISHED>>"}


def continue_parse(state: ChatState):
    """
    큐에 더 처리할 피드백이 있는지 확인합니다.
    
    Returns:
        bool: 계속 처리할 피드백이 있으면 True, 없으면 False
    """
    return state["queue"] != "<<FINISHED>>"
