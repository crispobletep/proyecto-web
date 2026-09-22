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
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "placeholder": "+56 9 1234 5678",
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "maxlength": 30,
                }
            ),
            "mensaje": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": (
                        "Indica cantidades, plazos y otros antecedentes "
                        "relevantes."
                    ),
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

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"].strip()
        digitos = re.sub(r"\D", "", telefono)
        if not 8 <= len(digitos) <= 15:
            raise forms.ValidationError(
                "Ingresa un teléfono válido, incluyendo el código de área."
            )
        return telefono
