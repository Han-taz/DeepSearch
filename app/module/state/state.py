from typing import TypedDict, Annotated, List, Dict
from langchain_core.messages import BaseMessage


class ChatState(TypedDict):

    messages: Annotated[List[BaseMessage], "대화 기록"]

    feedback: Annotated[List[str], "질문 피드백"]