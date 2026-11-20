from django.db import migrations


DESCRIPCIONES = {
    "alicate-pelacable-automatico-kamasa-7": (
        "Alicate pelacable automático KAMASA Professional de 7 pulgadas "
        "(180 mm), modelo KM-027."
    ),
    "disco-corte-stanley-4-1-2-115mm": (
        "Disco Stanley tipo 41 para corte de metal y acero inoxidable. "
        "Diámetro de 115 mm, espesor de 1,0 mm y eje de 22 mm."
    ),
    "grapas-curvas-cable-toolmak": (
        "Grapas curvas TOOLMAK para fijación de cables, disponibles en "
        "medidas de 6, 7, 8 y 10 mm."
    ),
    "diferencial-magnetotermico-chint-nb2le-1pn": (
        "Interruptor diferencial magnetotérmico CHINT NB2LE de 1P+N, "
        "230/240 V, sensibilidad de 30 mA y poder de corte de 6 kA. "
        "Disponible en calibres de 10, 16, 20, 25, 32 y 40 A."
    ),
    "temporizador-digital-lexo-ahc-24h": (
        "Temporizador digital LEXO con rango de programación de 0 a 24 h, "
        "corriente nominal de 16 A, alimentación de 220 V y reserva de marcha."
    ),
    "temporizador-horario-lexo-sul-181h": (
        "Temporizador horario analógico LEXO SUL 181H, con reserva de marcha, "
        "corriente nominal de 16 A y alimentación de 220 V."
    ),
    "luminaria-solar-logic-100w": (
        "Luminaria pública solar LED de 100 W con panel solar, control remoto "
        "y protección IP65."
    ),
    "luminaria-solar-logic-150w": (
        "Luminaria pública solar LED de 150 W con panel solar, control remoto "
        "y protección IP65."
    ),
    "luminaria-solar-logic-200w": (
        "Luminaria pública solar LED de 200 W con panel solar, control remoto "
        "y protección IP65."
    ),
    "sensor-movimiento-vkb-ke09-180": (
        "Sensor infrarrojo VKB KE09 para montaje en muro o cielo, con cobertura "
        "de 180° y alimentación de 220 V, 50 Hz."
    ),
    "sensor-movimiento-vkb-ip44-12m": (
        "Sensor de movimiento infrarrojo VKB blanco, con alcance de 12 m, "
        "cobertura ajustable de 180° a 360° y protección IP44."
    ),
    "sensor-movimiento-vkb-techo-360-ip20": (
        "Sensor infrarrojo VKB para montaje en cielo, con cobertura de 360°, "
        "alcance de 12 m, protección IP20 y acabado blanco."
    ),
    "detector-humo-fotoelectrico-bekam": (
        "Detector fotoeléctrico BEKAM para detección de humo."
    ),
    "fotocelda-vkb-1800w-200-240v": (
        "Fotocelda VKB con disipador, capacidad de 1800 W y alimentación de "
        "200–240 V CA."
    ),
    "medidor-digital-chint-pd666-3s3": (
        "Medidor digital multifunción CHINT PD666-3S3, tensión de 450 V, "
        "corriente de 5 A, pantalla LCD de 96 × 96 mm y comunicación Modbus RS485."
    ),
    "disparador-shunt-chint-sht-x1": (
        "Bobina de disparo CHINT SHT-X1 para control remoto, con tensión de "
        "control de 230/400 V CA."
    ),
    "kalop-interruptor-doble": (
        "Interruptor unipolar doble KALOP Tekna blanco, 10 A, 250 V. "
        "Referencia KS39651."
    ),
    "kalop-pulsador": (
        "Pulsador unipolar KALOP Tekna blanco, 10 A, 250 V. Referencia KS39657."
    ),
    "kalop-interruptor-con-toma": (
        "Combinación KALOP blanca de interruptor unipolar y tomacorriente "
        "2P+T, 10 A y 250 V. Referencia KS39674."
    ),
    "kalop-tapon-ciego": (
        "Tapón ciego KALOP blanco para módulo eléctrico, 250 V. Referencia KL40570."
    ),
    "kalop-interruptor-16a": (
        "Interruptor unipolar modular KALOP blanco, 16 A y 250 V. Referencia KL40100."
    ),
    "kalop-tomacorriente-10a": (
        "Tomacorriente KALOP Tekna blanco, formato 2P+T, 10 A y 250 V. "
        "Referencia KS39672."
    ),
    "kalop-tomacorriente-bipolar": (
        "Tomacorriente bipolar KALOP blanco con tierra central, 10 A y 250 V. "
        "Referencia KL40230."
    ),
    "kalop-tomacorriente-10-16a": (
        "Tomacorriente KALOP blanco 2P+T con tierra central, de 10–16 A y "
        "250 V. Referencia KL40260."
    ),
    "kalop-tomacorriente-triple": (
        "Tomacorriente triple KALOP Tekna blanco, formato 2P+T, 10 A y 250 V. "
        "Referencia KS39673."
    ),
    "panel-led-embutido-avc-6500k": (
        "Panel LED redondo AVC para montaje embutido. Versiones disponibles: "
        "3 W/3000 K, 6 W/3000 K, 6 W/6500 K, 12 W/6500 K, 18 W/3000 K y 18 W/6500 K."
    ),
    "panel-led-sobrepuesto-avc-6500k": (
        "Panel LED redondo AVC para montaje sobrepuesto. Versiones disponibles: "
        "6 W/3000 K, 12 W/6500 K, 18 W/3000 K y 18 W/6500 K."
    ),
}


CARACTERISTICAS = {
    "alicate-pelacable-automatico-kamasa-7": {
        2: "Largo: 7 pulgadas (180 mm).",
    },
    "disco-corte-stanley-4-1-2-115mm": {
        1: "Corte de metal y acero inoxidable.",
    },
    "cinta-aislante-pvc-fsl-negra-19mm-16m": {
        2: "Retardante a la llama.",
    },
    "ampolleta-led-fsl-gu10-6w": {
        1: "Base GU10 y flujo luminoso de 510 lm.",
    },
    "sensor-movimiento-vkb-ip44-12m": {
        1: "Alcance: 12 m.",
        3: "Cobertura ajustable de 180° a 360°.",
    },
    "sensor-movimiento-vkb-techo-360-ip20": {
        2: "Cobertura de 360° y alcance de 12 m.",
    },
    "medidor-digital-chint-pd666-3s3": {
        3: "Comunicación Modbus RS485.",
    },
}


def redactar_catalogo(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    for slug, descripcion in DESCRIPCIONES.items():
        Producto.objects.using(alias).filter(slug=slug).update(descripcion=descripcion)

    for slug, caracteristicas in CARACTERISTICAS.items():
        for orden, texto in caracteristicas.items():
            Caracteristica.objects.using(alias).filter(
                producto__slug=slug,
                orden=orden,
            ).update(texto=texto)


class Migration(migrations.Migration):
    dependencies = [("core", "0111_agregar_tarugos_y_grapas")]

    operations = [migrations.RunPython(redactar_catalogo, migrations.RunPython.noop)]
