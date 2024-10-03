from openai import OpenAI, AsyncOpenAI
from src.llm.api_wrappers.abc_api_wrapper import LLMWrapper
from src.llm.api_wrappers.llm_response import LLMResponse
from src.llm.tools import ABCTool
from config import OPENAI_API_KEY


class OpenaiAPI(LLMWrapper):
    api_key = OPENAI_API_KEY

    def __init__(self,
                 model_name: str = "gpt-3.5-turbo-1106",
                 api_key: str or None = None,
                 max_tokens: int = 512,
                 temperature: float = 1):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature

        self.api_key = self.api_key if api_key is None else api_key
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.client = OpenAI(api_key=self.api_key)

    def _format_request_arguments(self,
                                  prompt: str or list[str],
                                  system_prompt: str,
                                  tools: list[dict] = None,
                                  return_json: bool = True
                                  ) -> dict or list[dict]:
        def insert_prompt(user_prompt: str):
            arguments = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
            if tools:
                arguments["tools"] = tools
            if return_json:
                arguments["response_format"] = {"type": "json_object"}

            return arguments

        if isinstance(prompt, str):
            return insert_prompt(prompt)
        else:
            return [insert_prompt(p) for p in prompt]

    def _format_tool_definitions(self, tools: list[ABCTool]) -> list[any]:

        def format_tool(tool_cls: ABCTool):
            tool = tool_cls()
            definitions = {
                "type": "function",
                "function": {
                    "name": tool.name(),
                    "description": tool.description(),
                    "parameters": {
                        "type": "object",
                        "properties": tool.parameters(),
                    }
                }
            }

            if tool.required_parameters() is not None:
                definitions["function"]["parameters"]["required"] = tool.required_parameters()

            return definitions

        return [format_tool(tool) for tool in tools]

    def _get_async_response_method(self) -> callable:
        return self.async_client.chat.completions.create

    def _get_response_method(self) -> callable:
        return self.client.chat.completions.create

    def _process_response(self, response, time_taken):
        in_tokens = response.usage.prompt_tokens
        out_tokens = response.usage.completion_tokens
        text_response = response.choices[0].message.content

        called_function_name = None
        if response.choices[0].message.tool_calls is not None:
            func = response.choices[0].message.tool_calls[0].function
            text_response = func.arguments
            called_function_name = func.name

        return LLMResponse(str_response=text_response,
                           time_taken=time_taken,
                           called_function_name=called_function_name,
                           model_name=self.model_name,
                           in_tokens=in_tokens,
                           out_tokens=out_tokens)


if __name__ == "__main__":
    from time import perf_counter
    from src.llm.tools import ContentsPageTool
    from src.llm.tools import BalanceSheetToolYears

    api = OpenaiAPI(temperature=0.2)
    prompt_ = "What is the capital city of France?"
    system_prompt_ = ("Respond to questions with a concise poem where the first"
                      " letters of each line spell out the answer.")
    system_prompt_ += "Respond in json format with your answer having the key 'poem'"
    print("------- Text response -------")
    s = perf_counter()
    response = api.get_json_response(prompt_, system_prompt_)
    print(f"Time taken: {perf_counter() - s:.2f}s")
    print(response.get_as_str())
    response.print_cost()
    print()

    prompt_ = """
        CONSOLIDATED STATEMENT OF FINANCIAL POSITION
    AS AT 31 DECEMBER 2023
    As restated  2023 2022
    Note £ £
    Fixed assets  1,139,705 657,702
    Tangible assets 12 1,039,716 657,702
    Investments 13 99,989 0
    Current assets  52,427,405 46,770,501
    Debtors: amounts falling due within one year 14 31,422,714 27,879,596
    Cash at bank and in hand 21,004,691 18,890,905
    Creditors: amounts falling due within one year 15 (38,803,171) (36,249,859)
    Net current assets 13,624,234 10,520,642
    Total assets less current liabilities 14,763,939 11,178,344
    Provisions for liabilities  (140,000) (140,000)
    Other provisions 17 (140,000) (140,000)
    Net assets 14,623,939 11,038,344
    Capital and reserves  14,623,939 11,038,344
    Called up share capital 18 344,564 344,564
    Capital redemption reserve 19 210,389 210,389
    Profit and loss account 19 14,068,986 10,483,391
    Equity attributable to owners of the parent Company 14,623,939 11,038,344
    The financial statements were approved and authorised for issue by the board and were signed on its behalf by :
    T.J. Benzecry T. Diossi"""

    prompts = [prompt_ for _ in range(1)]
    responses = api.get_async_tool_response(
        prompts,
        "Given a table extract the information with one of the functions",
        tools=[BalanceSheetToolYears(years=[2023, 2022]),
               ContentsPageTool()],
    )

    for response in responses:
        response.print_as_dict()
        print()

    # prompts = [prompt_ for _ in range(10)]
    # print("------- Async Text response -------")
    # s = perf_counter()
    # responses = api.get_async_json_response(prompts, system_prompt_)
    # e = perf_counter()
    # print(f"Time taken: {(e - s):.2f}s")
    # for response in responses:
    #     print(response.get_response_str())
    #     print()
