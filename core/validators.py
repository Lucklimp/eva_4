import re
from django.core.exceptions import ValidationError


def validar_rut(rut_string):
    """Valida formato y dígito verificador de un RUT chileno."""
    if not rut_string:
        return

    patron_formato = r'^(\d{1,3}(?:\.?\d{3}){2}-?[\dkK])$'
    if not re.match(patron_formato, rut_string):
        raise ValidationError("El formato del RUT no es válido (Ej: 12.345.678-K).")

    rut_clean = re.sub(r'[\.-]', '', rut_string).upper()
    cuerpo = rut_clean[:-1]
    dv = rut_clean[-1]

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
    """Regex: Al menos 8 caracteres, 1 número, 1 letra."""
    patron = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$'
    if not re.match(patron, password):
        raise ValidationError("La contraseña debe tener al menos 8 caracteres, incluyendo letras y números.")
