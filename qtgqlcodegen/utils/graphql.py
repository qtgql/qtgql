import re
from typing import Optional


def get_operation_name(query: str) -> Optional[str]:
    if match := re.search(r"(subscription|mutation|query)(.*?({|\())", query):
        return match.group(2).replace(" ", "").strip("{").strip("(")
