from typing import Dict, Optional

SHELL_ROLE = """Provide only {shell} commands for {os} without any description.
If there is a lack of details, provide most logical solution.
Ensure the output is a valid shell command.
If multiple steps required try to combine them together using &&.
Provide only plain text without Markdown formatting.
Do not provide markdown formatting such as ```.
"""

DESCRIBE_SHELL_ROLE = """Provide a terse, single sentence description of the given shell command.
Describe each argument and option of the command.
Provide short responses in about 80 words.
APPLY MARKDOWN formatting when possible."""
# Note that output for all roles containing "APPLY MARKDOWN" will be formatted as Markdown.

CODE_ROLE = """Provide only code as output without any description.
Provide only code in plain text format without Markdown formatting.
Do not include symbols such as ``` or ```python.
If there is a lack of details, provide most logical solution.
You are not allowed to ask for more details.
For example if the prompt is "Hello world Python", you should return "print('Hello world')"."""

DEFAULT_ROLE = """You are programming and system administration assistant.
You are managing {os} operating system with {shell} shell.
Provide short responses in about 100 words, unless you are specifically asked for more details.
If you need to store any data, assume it will be stored in the conversation.
APPLY MARKDOWN formatting when possible."""
# Note that output for all roles containing "APPLY MARKDOWN" will be formatted as Markdown.


ROLE_TEMPLATE = "You are {name}\n{role}"


string_to_role_map = {
    "0": DEFAULT_ROLE,
    "1": SHELL_ROLE,
    "2": DESCRIBE_SHELL_ROLE,
    "3": CODE_ROLE,
}


class SystemRole:
    def __init__(
        self, name: str, role: str, sys_info: Optional[Dict[str, str]]
    ) -> None:
        self.name = name
        if sys_info:
            role = role.format(**sys_info)
        self.role = role

    @classmethod
    def generate_roles(
        cls, sys_info: Optional[Dict[str, str]]
    ) -> Dict[str, "SystemRole"]:
        roles = {}
        for role_id, role_content in string_to_role_map.items():
            role_name = f"Role_{role_id}"
            role_instance = cls(role_name, role_content, sys_info)
            roles[role_id] = role_instance
        return roles
