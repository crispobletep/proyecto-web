import re

from django import forms

from .models import Cotizacion


SERVICIOS = (
    ("", "Selecciona una opción"),
    ("Instalación eléctrica", "Instalación eléctrica"),
    ("Soluciones electrónicas", "Soluciones electrónicas"),
    ("Infraestructura", "Infraestructura"),
    ("Mantención", "Mantención"),
    ("Productos", "Productos"),
    ("Proyecto especial / Otro", "Proyecto especial / Otro"),
)


class CotizacionForm(forms.ModelForm):
    servicio = forms.ChoiceField(
        choices=SERVICIOS,
        label="Servicio a cotizar",
        error_messages={"required": "Selecciona el servicio que necesitas."},
    )

    class Meta:
        model = Cotizacion
        fields = (
            "nombre",
            "empresa",
            "email",
            "telefono",
            "servicio",
            "mensaje",
        )
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "placeholder": "Tu nombre",
                    "autocomplete": "name",
                    "minlength": 3,
                    "maxlength": 120,
                }
            ),
            "empresa": forms.TextInput(
                attrs={
                    "placeholder": "Nombre de la empresa",
                    "autocomplete": "organization",
                    "maxlength": 150,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "correo@empresa.cl",
                    "autocomplete": "email",
                    "maxlength": 254,
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "placeholder": "+56 9 1234 5678",
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "pattern": r"[+0-9\(\) \-]{9,18}",
                    "title": (
                        "Ingresa 9 dígitos chilenos o el número completo "
                        "con código +56."
                    ),
                    "maxlength": 18,
                    "aria-describedby": "telefono-ayuda",
                }
            ),
            "mensaje": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": (
                        "Indica cantidades, plazos y otros antecedentes "
                        "relevantes."
                    ),
                    "minlength": 20,
                    "maxlength": 2000,
                    "aria-describedby": "mensaje-ayuda",
                }
            ),
        }
        error_messages = {
            "nombre": {"required": "Ingresa tu nombre."},
            "email": {
                "required": "Ingresa un correo electrónico.",
                "invalid": "Ingresa un correo electrónico válido.",
            },
            "telefono": {"required": "Ingresa un teléfono de contacto."},
            "mensaje": {"required": "Describe brevemente lo que necesitas."},
        }

    def clean_nombre(self):
        nombre = " ".join(self.cleaned_data["nombre"].split())
        caracteres_permitidos = " .-'’"

        if len(nombre) < 3:
            raise forms.ValidationError(
                "Ingresa un nombre de al menos 3 caracteres."
            )

        if not any(caracter.isalpha() for caracter in nombre) or any(
            not caracter.isalpha() and caracter not in caracteres_permitidos
            for caracter in nombre
        ):
            raise forms.ValidationError(
                "El nombre solo puede contener letras, espacios, apóstrofes "
                "y guiones."
            )

        return nombre

    def clean_empresa(self):
        return " ".join(self.cleaned_data.get("empresa", "").split())

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"].strip()
        if not re.fullmatch(r"\+?[0-9() -]+", telefono):
            raise forms.ValidationError(
                "El teléfono solo puede contener cifras y signos de formato."
            )

        digitos = re.sub(r"\D", "", telefono)
        numero_nacional = digitos[2:] if len(digitos) == 11 and digitos.startswith("56") else digitos

        if len(numero_nacional) != 9 or numero_nacional[0] == "0":
            raise forms.ValidationError(
                "Ingresa un teléfono chileno válido: 9 dígitos o el número "
                "completo con código +56."
            )

        return f"+56{numero_nacional}"

    def clean_mensaje(self):
        mensaje = self.cleaned_data["mensaje"].strip()

        if len(mensaje) < 20:
            raise forms.ValidationError(
                "Describe tu solicitud con al menos 20 caracteres."
            )

        if len(mensaje) > 2000:
            raise forms.ValidationError(
                "La descripción no puede superar los 2000 caracteres."
            )

        return mensaje
