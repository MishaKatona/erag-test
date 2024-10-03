from src.llm.api_wrappers import OpenaiAPI, ClaudeAPI, LLMResponse
from src.llm.json_system_prompts import load_text_file
from src.llm.tools import ABCTool, BalanceSheetToolFlat, ContentsPageTool, UselessInfoTool
from config import AI_MODEL

_llm_apis = {
    "OpenAI": OpenaiAPI(temperature=0.2, model_name="gpt-4o-mini"),
    "Claude": ClaudeAPI
}
_llm_api = _llm_apis[AI_MODEL]


def extract_balance_sheet_as_json(table_str: str) -> LLMResponse:
    lower_case = table_str.lower()

    if not ("statement of financial position" in lower_case
            or "balance sheet" in lower_case):
        return {"table": False}

    system_prompt_v2 = load_text_file("json_system_prompts_v2.txt")

    return _llm_api.get_json_response(table_str, system_prompt_v2)


def extract_single_tool(table_str: str) -> LLMResponse:
    lower_case = table_str.lower()

    system_prompt = ("Given information choose the most appropriate tool to "
                     "extract information from it")

    tools = [
        BalanceSheetToolFlat,
        ContentsPageTool,
        UselessInfoTool
    ]

    return _llm_api.get_tool_response(lower_case, system_prompt, tools)


def extract_multiple_tool(tables_str: list[str]) -> list[LLMResponse]:
    lower_case_tables = [table.lower() for table in tables_str]

    system_prompt = ""

    tools = [
        BalanceSheetToolFlat,
        ContentsPageTool,
        UselessInfoTool
    ]

    responses = _llm_api.get_async_tool_response(lower_case_tables,
                                                 system_prompt,
                                                 tools)
    return responses






if __name__ == "__main__":
    text = "This does not contain anything interesting"
    responses = extract_multiple_tool([text])
    print(responses[0])
