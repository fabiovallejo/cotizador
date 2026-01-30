# app/services/tipo_cambio_service.py

import httpx
import json
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class TipoCambioService:
    """
    Servicio para obtener TC de SUNAT.
    """
    
    # Cache en memoria
    _cache = {}
    
    SUNAT_TOKEN = "koai6z623bdhh902ymj3c8lrxzwxivtk22e484my51d7eud23g7z"
    SUNAT_API_URL = "https://e-consulta.sunat.gob.pe/cl-at-ittipcam/tcS01Alias/listarTipoCambio"
    
    @classmethod
    async def obtener_tc_del_dia(
        cls,
        fecha: Optional[datetime] = None
    ) -> Dict[str, str]:
        """
        Obtiene TC oficial de SUNAT para un día específico.
        
        Args:
            fecha: datetime para obtener TC. Si None, usa hoy.
        
        Returns:
            {
                "fecha": "29/01/2026",
                "compra": "3.358",
                "venta": "3.368"
            }
        """
        
        # Si no hay fecha, usar hoy
        if not fecha:
            fecha = datetime.now()
        
        # Verificar cache (por día)
        cache_key = fecha.strftime("%d/%m/%Y")
        if cache_key in cls._cache:
            logger.info(f"TC del {cache_key} obtenido del cache")
            return cls._cache[cache_key]
        
        try:
            # Mes en SUNAT: 0=Enero, 1=Febrero, ..., 11=Diciembre
            payload = {
                "anio": fecha.year,
                "mes": fecha.month - 1,  # Convertir de 1-12 a 0-11
                "token": cls.SUNAT_TOKEN
            }
            
            logger.info(f"Obteniendo TC de SUNAT para {cache_key}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    cls.SUNAT_API_URL,
                    json=payload,
                    timeout=10.0
                )
                
                response.raise_for_status()
                
                datos = response.json()
                
                if not datos:
                    logger.warning(f"SUNAT retornó array vacío")
                    return cls._obtener_tc_default(fecha)
                
                tc_compra = None
                tc_venta = None
                
                for item in datos:
                    fec = item.get("fecPublica")  # Ej: "29/01/2026"
                    cod = item.get("codTipo")     # "C" o "V"
                    val = item.get("valTipo")     # Ej: "3.368"
                    
                    # Comparar fecha
                    if fec == cache_key:
                        if cod == "C":
                            tc_compra = val
                        elif cod == "V":
                            tc_venta = val
                
                # Si no encontramos el día, usar el más reciente del mes
                if not tc_compra or not tc_venta:
                    logger.warning(f"TC no disponible para {cache_key}, buscando más reciente del mes")
                    # Buscar último disponible (datos están ordenados)
                    for item in reversed(datos):
                        cod = item.get("codTipo")
                        if cod == "C" and not tc_compra:
                            tc_compra = item.get("valTipo")
                        if cod == "V" and not tc_venta:
                            tc_venta = item.get("valTipo")
                        if tc_compra and tc_venta:
                            break
                
                # Si aún no hay, usar default
                if not tc_compra or not tc_venta:
                    logger.error(f"No se pudo obtener TC para {cache_key}")
                    return cls._obtener_tc_default(fecha)
                
                result = {
                    "fecha": cache_key,
                    "compra": tc_compra,
                    "venta": tc_venta
                }
                
                # Guardar en cache
                cls._cache[cache_key] = result
                
                logger.info(f"TC obtenido de SUNAT: {result}")
                
                return result
        
        except httpx.HTTPError as e:
            logger.error(f"Error HTTP: {e}")
            return cls._obtener_tc_default(fecha)
        
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return cls._obtener_tc_default(fecha)
    
    @classmethod
    async def obtener_tc_venta_decimal(
        cls,
        fecha: Optional[datetime] = None
    ) -> Decimal:
        """
        Obtiene SOLO el TC de venta como Decimal.
        
        Returns:
            Decimal: TC venta (ej: Decimal("3.368"))
        """
        data = await cls.obtener_tc_del_dia(fecha)
        return Decimal(data["venta"])
    
    @classmethod
    async def obtener_tc_compra_decimal(
        cls,
        fecha: Optional[datetime] = None
    ) -> Decimal:
        """
        Obtiene SOLO el TC de compra como Decimal.
        
        Returns:
            Decimal: TC compra (ej: Decimal("3.358"))
        """
        data = await cls.obtener_tc_del_dia(fecha)
        return Decimal(data["compra"])
    
    @classmethod
    def _obtener_tc_default(cls, fecha: datetime) -> Dict[str, str]:
        """
        TC por defecto si API falla.
        Actualiza estos valores manualmente si lo necesitas.
        """
        logger.warning(f"Usando TC por defecto para {fecha.strftime('%d/%m/%Y')}")
        return {
            "fecha": fecha.strftime("%d/%m/%Y"),
            "compra": "3.45",
            "venta": "3.46"
        }


tipo_cambio_service = TipoCambioService()