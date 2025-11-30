import re
from django.core.exceptions import ValidationError


def validar_rut(rut_string):
    """Valida formato y dígito verificador de un RUT chileno."""
    if not rut_string:
        return

    rut_normalizado = re.sub(r'[^0-9kK]', '', rut_string)
    if len(rut_normalizado) < 8 or len(rut_normalizado) > 9:
        raise ValidationError("El RUT debe tener entre 7 y 8 dígitos más dígito verificador.")

    cuerpo = rut_normalizado[:-1]
    dv = rut_normalizado[-1].upper()
    rut_formateado = f"{cuerpo}-{dv}"

    patron_formato = r'^\d{7,8}-[\dkK]$'
    if not re.match(patron_formato, rut_formateado):
        raise ValidationError("El formato del RUT no es válido (Ej: 12345678-K).")

    suma = 0
    multiplo = 2
    for c in reversed(cuerpo):
        suma += int(c) * multiplo
        multiplo += 1
        if multiplo == 8:
            multiplo = 2

    res = 11 - (suma % 11)
    dvr = '0' if res == 11 else 'K' if res == 10 else str(res)

    if dvr != dv:
        raise ValidationError("RUT inválido. El dígito verificador no corresponde.")


def validar_password_compleja(password):
    """Regex: Al menos 8 caracteres, 1 minúscula, 1 mayúscula y 1 número."""
    patron = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
    if not re.match(patron, password):
        raise ValidationError(
            "La contraseña debe tener mínimo 8 caracteres e incluir una mayúscula, una minúscula y un número."
        )
