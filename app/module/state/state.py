from typing import TypedDict, Annotated, List, Dict, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class ChatState(TypedDict):

    messages: Annotated[Optional[list[add_messages]], "대화 기록"]
    feedbacks: Annotated[Optional[List[str]], "질문 피드백"]
    feedback_qa: Annotated[Optional[Dict[str, str]], "질문 피드백 답변"]
    human_interrupt: Annotated[Optional[bool], "사용자 개입 답변"]
    queue: Annotated[Optional[str], "피드백 질문 큐"]
    queue_index: Annotated[Optional[int], "피드백 질문 큐 인덱스"]
    search_query: Annotated[Optional[List[str]], "검색 질문"]
    research_results: Annotated[Optional[List[Dict[str, str]]], "검색 결과"]
    ask_human: Annotated[Optional[bool], "사용자 개입 질문"]