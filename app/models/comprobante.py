# app/models/comprobante.py
from pydantic import BaseModel
from typing import Optional, Dict

class Comprobante(BaseModel):
    # Información general del archivo
    filename: str
    size: int
    content_type: str
    text_content: str
    qr_content: Optional[str]
    diagnostic_messages: list[str]
    es_comprobante_valido: bool

    # Campos comunes
    punto_venta: Optional[str]
    numero_comprobante: Optional[str]
    fecha_emision: Optional[str]
    importe_total: Optional[str]
    periodo_facturado_desde: Optional[str]
    periodo_facturado_hasta: Optional[str]
    cuit_emisor: Optional[str]
    razon_social_emisor: Optional[str]
    domicilio_comercial_emisor: Optional[str]
    condicion_iva_emisor: Optional[str]
    cuit_receptor: Optional[str]
    razon_social_receptor: Optional[str]
    domicilio_comercial_receptor: Optional[str]
    condicion_iva_receptor: Optional[str]

    # Campos específicos de facturas/recibos
    subtotal: Optional[str]
    bonificacion_porcentaje: Optional[str]
    bonificacion_importe: Optional[str]
    subtotal_con_bonificacion: Optional[str]
    importe_otros_tributos: Optional[str]
    profesion_oficio: Optional[str]
    cae_numero: Optional[str]
    cae_fecha_vencimiento: Optional[str]

    # Información adicional
    cantidad_copias: Optional[int]

    # Campos no definidos en el VO
    otros_datos_no_formateados: Optional[Dict[str, str]]

    def es_valido(self) -> bool:
        """Valida si el comprobante tiene los campos mínimos requeridos."""
        campos_requeridos = [
            self.punto_venta,
            self.numero_comprobante,
            self.fecha_emision,
            self.importe_total,
            self.cuit_emisor,
            self.razon_social_emisor,
        ]
        return all(campos_requeridos)