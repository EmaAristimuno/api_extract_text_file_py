# app/services/comprobante_data_extractor.py
import re
from app.models.comprobante import Comprobante

class ComprobanteDataExtractor:
    @staticmethod
    def extract_comprobante_data(text_content: str) -> Comprobante:
        # Eliminar texto repetido producto de múltiples copias
        text_content = ComprobanteDataExtractor._remove_repeated_sections(text_content)

        # Definir patrones para extraer información
        punto_venta = re.search(r"Punto de Venta:\s*(\d+)", text_content)
        numero_comprobante = re.search(r"Comp\.? Nro:\s*(\d+)", text_content)
        fecha_emision = re.search(r"Fecha de Emisión:\s*(\d{2}/\d{2}/\d{4})", text_content)
        importe_total = re.search(r"Importe Total:\s*\$?\s*([\d.,]+)", text_content)
        periodo_facturado = re.search(r"Período Facturado Desde:\s*(\d{2}/\d{2}/\d{4})\s*Hasta:\s*(\d{2}/\d{2}/\d{4})", text_content)
        cuit_emisor = re.search(r"CUIT:\s*(\d{11})", text_content)
        
        # Patrones ajustados para el emisor
        razon_social_emisor = re.search(r"Razón Social:\s*(.+?)(?=\n|Fecha de Emisión)", text_content, re.DOTALL)
        domicilio_comercial_emisor = re.search(r"Domicilio Comercial:\s*(.+?)(?=\n|CUIT)", text_content, re.DOTALL)
        condicion_iva_emisor = re.search(r"Condición frente al IVA:\s*(.+?)(?=\n|Fecha de Inicio de Actividades)", text_content, re.DOTALL)

        # Patrones ajustados para el receptor
        cuit_receptor = re.search(r"CUIT:\s*(\d{11})\s*Apellido y Nombre / Razón Social:", text_content)
        razon_social_receptor = re.search(
            r"Apellido y Nombre / Razón Social:\s*(.+?)(?=\n|Condición frente al IVA)", 
            text_content, 
            re.DOTALL
        )
        domicilio_comercial_receptor = re.search(
            r"Apellido y Nombre / Razón Social:.+?Domicilio:\s*(.+?)(?=\n|$)", 
            text_content, 
            re.DOTALL
        )
        condicion_iva_receptor = re.search(
            r"Apellido y Nombre / Razón Social:.+?Condición frente al IVA:\s*(.+?)(?=\n|Domicilio)", 
            text_content, 
            re.DOTALL
        )

        # Campos adicionales
        subtotal = re.search(r"Subtotal:\s*\$?\s*([\d.,]+)", text_content)
        bonificacion_porcentaje = re.search(r"Bonif:\s*%(\d+)", text_content)
        bonificacion_importe = re.search(r"Importe Bonif:\s*\$?\s*([\d.,]+)", text_content)
        subtotal_con_bonificacion = re.search(r"Subtotal c/Bonif\.?:\s*\$?\s*([\d.,]+)", text_content)
        importe_otros_tributos = re.search(r"Importe Otros Tributos:\s*\$?\s*([\d.,]+)", text_content)
        profesion_oficio = re.search(r"\"(.+? - MP \d+)\"", text_content)
        cae_numero = re.search(r"CAE N°:\s*(\d+)", text_content)
        cae_fecha_vencimiento = re.search(r"Fecha de Vto\. de CAE:\s*(\d{2}/\d{2}/\d{4})", text_content)

        # Contar la cantidad de copias (ORIGINAL, DUPLICADO, TRIPLICADO)
        cantidad_copias = ComprobanteDataExtractor._count_copies(text_content)

        # Crear una instancia de Comprobante
        comprobante = Comprobante(
            filename="comprobante.pdf",  # Este valor se actualiza en el FileProcessor
            size=0,  # Este valor se actualiza en el FileProcessor
            content_type="application/pdf",  # Este valor se actualiza en el FileProcessor
            text_content=text_content,
            qr_content=None,  # Este valor se actualiza en el FileProcessor
            diagnostic_messages=[],
            es_comprobante_valido=False,  # Se valida después
            punto_venta=punto_venta.group(1) if punto_venta else None,
            numero_comprobante=numero_comprobante.group(1) if numero_comprobante else None,
            fecha_emision=fecha_emision.group(1) if fecha_emision else None,
            importe_total=importe_total.group(1) if importe_total else None,
            periodo_facturado_desde=periodo_facturado.group(1) if periodo_facturado else None,
            periodo_facturado_hasta=periodo_facturado.group(2) if periodo_facturado else None,
            cuit_emisor=cuit_emisor.group(1) if cuit_emisor else None,
            razon_social_emisor=razon_social_emisor.group(1).strip() if razon_social_emisor else None,
            domicilio_comercial_emisor=domicilio_comercial_emisor.group(1).strip() if domicilio_comercial_emisor else None,
            condicion_iva_emisor=condicion_iva_emisor.group(1).strip() if condicion_iva_emisor else None,
            cuit_receptor=cuit_receptor.group(1) if cuit_receptor else None,
            razon_social_receptor=razon_social_receptor.group(1).strip() if razon_social_receptor else None,
            domicilio_comercial_receptor=domicilio_comercial_receptor.group(1).strip() if domicilio_comercial_receptor else None,
            condicion_iva_receptor=condicion_iva_receptor.group(1).strip() if condicion_iva_receptor else None,
            subtotal=subtotal.group(1) if subtotal else None,
            bonificacion_porcentaje=bonificacion_porcentaje.group(1) if bonificacion_porcentaje else None,
            bonificacion_importe=bonificacion_importe.group(1) if bonificacion_importe else None,
            subtotal_con_bonificacion=subtotal_con_bonificacion.group(1) if subtotal_con_bonificacion else None,
            importe_otros_tributos=importe_otros_tributos.group(1) if importe_otros_tributos else None,
            profesion_oficio=profesion_oficio.group(1) if profesion_oficio else None,
            cae_numero=cae_numero.group(1) if cae_numero else None,
            cae_fecha_vencimiento=cae_fecha_vencimiento.group(1) if cae_fecha_vencimiento else None,
            cantidad_copias=cantidad_copias,
            otros_datos_no_formateados={},  # Inicialmente vacío
        )

        # Validar si el comprobante es válido
        comprobante.es_comprobante_valido = comprobante.es_valido()

        return comprobante

    @staticmethod
    def _remove_repeated_sections(text: str) -> str:
        """Elimina secciones repetidas en el texto, producto de múltiples copias."""
        blocks = text.split("\n\n")
        unique_blocks = []
        seen_blocks = set()

        for block in blocks:
            normalized_block = " ".join(block.split())
            if normalized_block not in seen_blocks:
                seen_blocks.add(normalized_block)
                unique_blocks.append(block)

        return "\n\n".join(unique_blocks)

    @staticmethod
    def _count_copies(text: str) -> int:
        """Cuenta la cantidad de copias (ORIGINAL, DUPLICADO, TRIPLICADO) en el texto."""
        count = 0
        for line in text.split("\n"):
            if line.strip() in ["ORIGINAL", "DUPLICADO", "TRIPLICADO"]:
                count += 1
        return count