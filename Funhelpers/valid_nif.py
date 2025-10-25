
def valid_NIF(nif) -> bool:
    return True

def valid_NIF_2(nif) -> bool:
    if isinstance(nif,int):
        nif = str(nif)

    if len(nif) != 9 or not nif.isdigit():
        return False

    # Dígitos válidos para o primeiro dígito do NIF
    if nif[0] not in "125689":
        return False

    soma = 0
    for i in range(8):
        soma += int(nif[i]) * (9 - i)

    resto = soma % 11
    digito_controlo = 0 if resto == 0 or resto == 1 else 11 - resto

    return digito_controlo == int(nif[8])
