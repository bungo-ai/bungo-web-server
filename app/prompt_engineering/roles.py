from data_classes.requests.openairequest import OpenAIRequest
from prompt_engineering.system_info import SystemInfo


class SystemRole:

    SHELL_ROLE = """You are a shell generator.
    Provide only {shell} commands for {platform} without any description.
    If there is a lack of details, provide most logical solution.
    Ensure the output is a valid shell command.
    If multiple steps required try to combine them together using &&.
    Provide only plain text without Markdown formatting.
    Do not provide markdown formatting such as ```.
    """

    DESCRIBE_SHELL_ROLE = """You are a shell describer.
    Provide a terse, single sentence description of the given shell command.
    Describe each argument and option of the command.
    Provide short responses in about 80 words.
    APPLY MARKDOWN formatting when possible."""
    # Note that output for all roles containing "APPLY MARKDOWN" will be formatted as Markdown.

    CODE_ROLE = """You are a code generator.
    Provide only code as output without any description.
    Provide only code in plain text format without Markdown formatting.
    Do not include symbols such as ``` or ```python.
    If there is a lack of details, provide most logical solution.
    You are not allowed to ask for more details.
    For example if the prompt is "Hello world Python", you should return "print('Hello world')"."""

    OS_ROLE = """You are programming and system administration assistant.
    You are managing {platform} operating system with {shell} shell.
    Provide short responses in about 100 words, unless you are specifically asked for more details.
    If you need to store any data, assume it will be stored in the conversation.
    APPLY MARKDOWN formatting when possible."""
    # Note that output for all roles containing "APPLY MARKDOWN" will be formatted as Markdown.

    DEFAULT_ROLE = """You are a helpful assistant wit programming and system administration background.
    Provide short responses in about 100 words, unless you are specifically asked for more details
    """

    ROLE_TEMPLATE = "You are {name}\n{role}"

    string_to_role_map = {
        "0": DEFAULT_ROLE,
        "1": OS_ROLE,
        "2": SHELL_ROLE,
        "3": DESCRIBE_SHELL_ROLE,
        "4": CODE_ROLE,
    }

    @classmethod
    def __role_lookup__(cls, role_id: str, shell: str, platform: str) -> str:
        role = SystemRole.string_to_role_map.get(str(role_id), "0")
        if platform and shell:
            role_instance = role.format(platform=platform, shell=shell)
        else:
            role_instance = role
        return role_instance

    @classmethod
    def __get_role_id___(cls, openai_request: OpenAIRequest) -> str:
        role_type_key = "role_key"
        if openai_request.request_context is not None:
            return openai_request.request_context.get(role_type_key, "0")
        else:
            return "0"

    @classmethod
    def get_role(cls, openai_request: OpenAIRequest) -> str:
        role_id_to_access = SystemRole.__get_role_id___(openai_request)
        sys_info = SystemInfo.get_sys_info(openai_request)
        if sys_info and "shell" in sys_info.keys() and "platform" in sys_info.keys():
            role = SystemRole.__role_lookup__(
                role_id_to_access, str(sys_info["shell"]), str(sys_info["platform"])
            )
        else:
            return SystemRole.DEFAULT_ROLE
        return role
