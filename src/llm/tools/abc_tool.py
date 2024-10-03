from abc import ABC, abstractmethod


class ABCTool(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def name(self) -> str:
        """Name of the tool, this will also be returned with the response"""
        pass

    @abstractmethod
    def description(self) -> str:
        """
        From calude AI documentation, but should be applicable for all tools:
    Provide extremely detailed descriptions. This is by far the most important
    factor in tool performance. Your descriptions should explain every detail
    about the tool, including:
        What the tool does
        When it should be used (and when it shouldn’t)
        What each parameter means and how it affects the tool’s behavior
        Any important caveats or limitations, such as what information the
            tool does not return if the tool name is unclear. The more context
            you can give Claude about your tools, the better it will be at deciding
            when and how to use them. Aim for at least 3-4 sentences per tool
            description, more if the tool is complex.
    Prioritize descriptions over examples. While you can include examples of
    how to use a tool in its description or in the accompanying prompt, this is
    less important than having a clear and comprehensive explanation of the
    tool’s purpose and parameters. Only add examples after you’ve fully fleshed
    out the description.
        """
        pass

    @abstractmethod
    def parameters(self) -> (dict, list[str] or None):
        """
        Parameters for the tool to extract from the prompt, schema for this is
        as follows:
        schema = {
            "type": str = type of the parameter, one of
                ["string", "boolean", "integer", "number", "array", "object"],
            "description": str = description of the parameter,
            "enum": list[str] = list of possible STRING values for the parameter,
            "items": schema = schema for ARRAY items
            "properties": schema = schema for OBJECT key value pairs
            "required": list[str] = list of required keys for OBJECT
        }
        This method must return a dictionary with the values being like the
        schema above. Only the type is a required field in a schema.
        """
        pass

    @abstractmethod
    def required_parameters(self) -> list[str] or None:
        """
        List of required parameters for the tool, Only for the top level object
        If None, no parameters are required.
        """
        pass
