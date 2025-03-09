from langchain_core.prompts import load_prompt, PromptTemplate
from pathlib import Path

def load_prompt_from_yaml(prompt: str, encoding: str = "utf-8") -> PromptTemplate:
    current_file = Path(__file__)
    project_root = next(
        (parent for parent in current_file.parents if (parent / "pyproject.toml").exists()),
        None
    )

    if project_root is None:
        raise RuntimeError("Could not find project root directory")
    if prompt is None:
        raise ValueError("Prompt is None")

    # prompt_path 설정
    if prompt == "feedback":
        prompt_path = project_root / "app" / "prompt" / "feedback" / "prompt.yml"
    elif prompt == "create_search_query":
        prompt_path = project_root / "app" / "prompt" / "feedback" / "create_question.yml"
 
    else:
        raise ValueError(f"Invalid prompt: {prompt}")  

    # YAML 프롬프트 로드
    loaded_prompt = load_prompt(str(prompt_path), encoding=encoding)
    return loaded_prompt
