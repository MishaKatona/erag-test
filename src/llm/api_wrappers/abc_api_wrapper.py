from abc import ABC, abstractmethod
import asyncio
from time import perf_counter
from src.llm.api_wrappers.llm_response import LLMResponse
from src.llm.tools import ABCTool


class LLMWrapper(ABC):

    @abstractmethod
    def __init__(self,
                 model_name: str,
                 api_key: str or None = None,
                 max_tokens: int = 512,
                 temperature: float = 1):
        pass

    def _run_single(self,
                    prompt: str,
                    system_prompt: str,
                    tools: list[dict] = None,
                    return_json: bool = False) -> (object, float):
        method = self._get_response_method()
        arguments = self._format_request_arguments(
            prompt=prompt,
            system_prompt=system_prompt,
            tools=tools,
            return_json=return_json
        )

        start = perf_counter()
        response = method(**arguments)
        time_taken = perf_counter() - start

        return response, round(time_taken, 2)

    def _run_async(self,
                   prompts: list[str],
                   system_prompt: str,
                   tools: list[dict] = None,
                   return_json: bool = False) -> (object, float):
        method = self._get_async_response_method()
        arguments = self._format_request_arguments(
            prompt=prompts,
            system_prompt=system_prompt,
            tools=tools,
            return_json=return_json
        )

        async def gather_responses():
            return await asyncio.gather(
                *[method(**argument) for argument in arguments]
            )

        start = perf_counter()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        responses = loop.run_until_complete(gather_responses())
        loop.close()
        time_taken = perf_counter() - start

        return responses, round(time_taken, 2)

    def get_text_response(self,
                          prompt: str,
                          system_prompt: str) -> LLMResponse:
        raw_response, time_taken = self._run_single(prompt, system_prompt)

        return self._process_response(raw_response,
                                      time_taken)

    def get_async_text_response(self,
                                prompts: list[str],
                                system_prompt: str
                                ) -> list[LLMResponse]:
        raw_responses, time_taken = self._run_async(prompts, system_prompt)

        return [self._process_response(response,
                                       time_taken)
                for response in raw_responses]

    def get_json_response(self,
                          prompt: str,
                          system_prompt: str) -> LLMResponse:
        raw_response, time_taken = self._run_single(prompt,
                                                    system_prompt,
                                                    return_json=True)

        return self._process_response(raw_response,
                                      time_taken)

    def get_async_json_response(self,
                                prompts: list[str],
                                system_prompt: str) -> list[LLMResponse]:
        raw_responses, time_taken = self._run_async(prompts,
                                                    system_prompt,
                                                    return_json=True)

        return [self._process_response(response,
                                       time_taken)
                for response in raw_responses]

    def get_tool_response(self,
                          prompt: str,
                          system_prompt: str,
                          tools: list[ABCTool]) -> LLMResponse:
        tools = self._format_tool_definitions(tools)
        raw_response, time_taken = self._run_single(prompt,
                                                    system_prompt,
                                                    tools)

        return self._process_response(raw_response, time_taken)

    def get_async_tool_response(self,
                                prompts: list[str],
                                system_prompt: str,
                                tools: list[ABCTool]) -> list[LLMResponse]:
        tools = self._format_tool_definitions(tools)
        raw_responses, time_taken = self._run_async(prompts,
                                                    system_prompt,
                                                    tools)

        return [self._process_response(response, time_taken)
                for response in raw_responses]

    @abstractmethod
    def _format_request_arguments(self,
                                  prompt: str or list[str],
                                  system_prompt: str,
                                  tools: list[dict] = None,
                                  return_json: bool = True
                                  ) -> dict or list[dict]:
        pass

    @abstractmethod
    def _format_tool_definitions(self, tools: list[ABCTool]) -> list[any]:
        pass

    @abstractmethod
    def _get_response_method(self) -> callable:
        pass

    @abstractmethod
    def _get_async_response_method(self) -> callable:
        pass

    @abstractmethod
    def _process_response(self,
                          response,
                          time_taken: float) -> LLMResponse:
        pass

