from langgraph.graph import StateGraph, START, END
from app.module.state import ChatState
from app.module.feedback.module import FeedbackModule, FeedbackAnswerModule
from langgraph.checkpoint.memory import MemorySaver

# 그래프 생성
def create_feedback_graph():
    # 그래프 초기화
    graph = StateGraph(ChatState)
    
    # 노드 추가
    feedback_module = FeedbackModule()
    feedback_answer_module = FeedbackAnswerModule()
    
    graph.add_node("generate_feedback", lambda state: feedback_module.execute(state))
    graph.add_node("collect_answers", lambda state: feedback_answer_module.execute(state))
    
    # 엣지 설정 (실행 흐름)
    graph.add_edge(START, "generate_feedback")
    graph.add_edge("generate_feedback", "collect_answers")
    graph.add_edge("collect_answers", END)
    
    # 컴파일
    return graph.compile(checkpointer=MemorySaver())

# 사용 예시
def run_feedback_process(query: str, max_feedbacks: int = 3):
    # 그래프 생성
    graph = create_feedback_graph()
    
    # 초기 상태 설정
    initial_state = {"query": query, "max_feedbacks": max_feedbacks}
    
    # 스레드 생성 (상태 유지를 위함)
    thread = {"thread_id": "feedback_thread"}
    
    # 그래프 실행 (stream 모드로 실행하여 중단점에서 멈춤)
    print("피드백 질문 생성 중...")
    for event in graph.stream(initial_state, thread, stream_mode="values"):
        if "feedbacks" in event:
            print("\n생성된 질문들:")
            for i, question in enumerate(event["feedbacks"], 1):
                print(f"{i}. {question}")
    
    # 사용자 입력 처리
    print("\n각 질문에 대한 답변을 입력해주세요:")
    answers = {}
    for i, question in enumerate(event["feedbacks"], 1):
        answer = input(f"{i}. {question}\n답변: ")
        answers[question] = answer
    
    # 사용자 입력으로 그래프 실행 계속
    # 실제 구현에서는 interrupt로부터 받은 입력을 어떻게 처리할지 정의해야 함
    for event in graph.stream(None, thread, stream_mode="values"):
        if "feedback_qa" in event:
            print("\n피드백 질문-답변 결과:")
            for question, answer in event["feedback_qa"].items():
                print(f"Q: {question}")
                print(f"A: {answer}")
                print()
    
    return event


if __name__ == "__main__":
    import sys
    user_input = input("질문을 입력해주세요: ").encode(sys.stdin.encoding or "utf-8").decode("utf-8", errors="ignore")
    run_feedback_process(str(user_input))
