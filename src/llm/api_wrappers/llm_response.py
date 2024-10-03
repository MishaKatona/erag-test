import json


model_costs = {
    "gpt-3.5-turbo-1106":
        {"per_million_input": 0.5, "per_million_output": 1.5},
    "gpt-4o-mini":
        {"per_million_input": 0.15, "per_million_output": 0.6},
    "claude-3-haiku-20240307":
        {"per_million_input": 0.25, "per_million_output": 1.25},
    "gemini-1.5-flash":
        {"per_million_input": 0.35, "per_million_output": 1.05},
}


class LLMResponse:

    def __init__(self,
                 str_response: str,
                 dict_response: dict = None,
                 time_taken: float = None,
                 called_function_name: str = None,
                 model_name: str = None,
                 in_tokens: int = None,
                 out_tokens: int = None,):
        self.str_response = str_response
        
        if dict_response is None:
            try:
                self.dict_response = json.loads(str_response)
            except json.JSONDecodeError:
                self.dict_response = None
        else:
            self.dict_response = dict_response

        self.function_call_name = called_function_name
        self.model_name = model_name
        self.time_taken = time_taken
        self.in_tokens = in_tokens
        self.out_tokens = out_tokens

    def get_as_dict(self) -> dict or None:
        return self.dict_response

    def print_as_dict(self):
        print(json.dumps(self.dict_response, indent=4))

    def get_as_str(self) -> str or None:
        return self.str_response

    def get_function_call_name(self) -> str or None:
        return self.function_call_name

    def get_time_taken(self) -> float or None:
        return self.time_taken

    def get_cost(self) -> float or None:
        if self.in_tokens is None or self.out_tokens is None:
            print("Missing both or one of in_tokens and out_tokens")
            return None

        if self.model_name is None:
            print("Missing model_name")
            return None

        model_cost = model_costs.get(self.model_name)

        if model_cost is None:
            print("Model cost not found")
            return None

        in_token_cost_per_million = model_cost["per_million_input"]
        out_token_cost_per_million = model_cost["per_million_output"]

        cost = (self.in_tokens * in_token_cost_per_million +
                self.out_tokens * out_token_cost_per_million) / 1e6

        return cost

    def print_cost(self):
        cost = self.get_cost()
        if cost is not None:
            print(f"Cost: ${cost * 100:.4f} cents, for 1$ this would equal {1/cost:.0f} calls")

    def get_token_usage(self) -> dict:
        return {"in_tokens": self.in_tokens, "out_tokens": self.out_tokens}
