import uuid

def create_unique_name(name_attempt: str, existing_names: set[str]):
    lower_names = {name.casefold() for name in existing_names}

    if _is_name_free(name_attempt=name_attempt, existing_names=lower_names):
        return name_attempt

    for i in range(1, 1000):
        name_attempt_with_num = name_attempt + str(i)
        if _is_name_free(name_attempt=name_attempt_with_num, existing_names=lower_names):
            return name_attempt_with_num

    # Failsafe - return a random UUID
    return str(uuid.uuid4())

def _is_name_free(name_attempt: str, existing_names: set[str]) -> bool:
    '''
    Check if the proposed name is free
    Check only casefolded version of display names since all search names are identical anyway
    '''
    return name_attempt.casefold() not in existing_names

def create_search_name(display_name: str) -> str:
    return display_name.casefold()    