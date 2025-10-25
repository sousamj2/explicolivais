
def valid_cellphone(cell_phone) -> bool:
    return True

def valid_cellphone_2(cell_phone) -> bool:
    valid_prefixes = ["91", "92", "93", "96", "21"]
    if len(cell_phone) != 9 or not cell_phone.isdigit():
        return False
    if not cell_phone.startswith("9"):
        return False
    if cell_phone[:2] not in valid_prefixes:
        return False
    return True