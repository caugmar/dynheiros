digitos = {
    0: "zero", 1: "um", 2: "dois", 3: "três", 4: "quatro",
    5: "cinco", 6: "seis", 7: "sete", 8: "oito", 9: "nove"
}

excessoes = {
    10: "dez", 11: "onze", 12: "doze", 13: "treze", 14: "quatorze", 15: "quinze",
    16: "dezesseis", 17: "dezessete", 18: "dezoito", 19: "dezenove"
}

dezenas = {
    20: "vinte", 30: "trinta", 40: "quarenta", 50: "cinquenta",
    60: "sessenta", 70: "setenta", 80: "oitenta", 90: "noventa"
}

centenas = {
    100: "cento", 200: "duzentos", 300: "trezentos", 400: "quatrocentos", 500: "quinhentos",
    600: "seiscentos", 700: "setecentos", 800: "oitocentos", 900: "novecentos"
}

def dezena(numero):
    """
    Converts a number (0-99) into its Portuguese word representation for tens.
    """
    if numero < 10:
        return digitos[numero]
    elif 10 <= numero < 20:
        return excessoes[numero]
    elif numero >= 20:
        if numero % 10 == 0:
            return dezenas[numero]
        else:
            return f"{dezenas[numero - (numero % 10)]} e {digitos[numero % 10]}"

def centena(numero):
    """
    Converts a number (0-999) into its Portuguese word representation for hundreds.
    """
    if numero < 100:
        return dezena(numero)
    else:
        if numero % 100 == 0:
            return "cem" if numero == 100 else centenas[numero]
        else:
            return f"{centenas[numero - (numero % 100)]} e {dezena(numero % 100)}"

def milhar(numero):
    """
    Converts a number (0-999999) into its Portuguese word representation for thousands.
    """
    if numero < 1000:
        return centena(numero)
    else:
        if numero % 1000 == 0:
            return f"{centena(numero // 1000)} mil"
        else:
            return f"{centena(numero // 1000)} mil e {centena(numero % 1000)}"

def separar(numero):
    """
    Separates a float number into its integer and decimal parts.
    The decimal part is padded with a leading zero if it's a single digit.
    """
    inteiros, decimais = str(numero).split('.')
    # Ensure decimals always have two digits, padding with '0' if necessary
    decimal_preenchido = decimais.ljust(2, '0')[:2]
    return [int(inteiros), int(decimal_preenchido)]

def em_reais(numero):
    """
    Converts a numeric value into its Portuguese monetary representation (reais and centavos).
    """
    # Using float() to handle potential exact->inexact conversion from Racket
    numero_real = float(numero)
    inteiros, centavos = separar(numero_real)

    if inteiros == 0 and centavos == 0:
        return ""
    elif inteiros == 0 and centavos == 1:
        return "um centavo"
    elif inteiros == 0:
        return f"{dezena(centavos)} centavos"
    elif inteiros != 0 and centavos == 0:
        # Handles "um real" and "reais" for other integer values
        if inteiros == 1:
            return "um real"
        return f"{milhar(inteiros)} reais"
    elif inteiros != 0 and centavos == 1:
        # Handles "um real e um centavo"
        if inteiros == 1:
            return "um real e um centavo"
        return f"{milhar(inteiros)} reais e um centavo"
    else:
        # Handles "reais e centavos" for other integer and decimal values
        if inteiros == 1:
            return f"um real e {dezena(centavos)} centavos"
        return f"{milhar(inteiros)} reais e {dezena(centavos)} centavos"

