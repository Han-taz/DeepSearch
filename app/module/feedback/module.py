from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from app.module.Base import BaseNode
from app.core.llms import LLMManager
from app.prompt.load_prompt import load_prompt_from_yaml
from app.module.state import ChatState
class Feedback(BaseModel):
    feedbacks: list[str] = Field(description="피드백 질문")









class FeedbackModule(BaseNode):
    def __init__(self):
        raw_prompt = load_prompt_from_yaml("feedback")
        self.parser = PydanticOutputParser(pydantic_object=Feedback)
        self.prompt = raw_prompt.partial(format=self.parser.get_format_instructions())
        self.llm = LLMManager.get_llm("gpt-4o-mini")
        self.chain = self.prompt | self.llm | self.parser

    def execute(self, state: ChatState) -> ChatState:
        return self.chain.invoke({"query": state.get("query"), "max_feedbacks": state.get("max_feedbacks")})


if __name__ == "__main__":
    feedback_module = FeedbackModule()
    state = ChatState(query="여성의 성 상품화 추세", max_feedbacks=3)
    print(state)
    print(feedback_module(state))

