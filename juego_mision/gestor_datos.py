import json
import os
from tkinter import filedialog, Tk

class GestorDatos:
    """Clase responsable de la carga y validación de datos del juego"""
    
    def __init__(self):
        self.datos_nivel = None
        self.total_agujeros_negros = 0
        self.total_agujeros_gusano = 0
    
    def cargar_nivel_desde_archivo(self):
        """Permite al usuario seleccionar y cargar un archivo JSON de nivel"""
        root = Tk()
        root.withdraw()
        
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de nivel",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
            initialdir="data"
        )
        
        if archivo:
            return self.cargar_nivel(archivo)
        else:
            return False, "No se seleccionó ningún archivo"
    
    def cargar_nivel(self, ruta_archivo):
        """Carga un nivel desde un archivo específico"""
        try:
            with open(ruta_archivo, 'r') as f:
                datos_temp = json.load(f)
            
            # Validar el nivel antes de asignarlo
            es_valido, mensaje = self.validar_nivel(datos_temp)
            
            if es_valido:
                self.datos_nivel = datos_temp
                self.total_agujeros_negros = len(self.datos_nivel['agujerosNegros'])
                self.total_agujeros_gusano = len(self.datos_nivel['agujerosGusano'])
                
                filas = self.datos_nivel['matriz']['filas']
                columnas = self.datos_nivel['matriz']['columnas']
                energia_inicial = self.datos_nivel['cargaInicial']
                
                mensaje_exito = f"Nivel cargado exitosamente. Matriz: {filas}x{columnas}. Energía inicial: {energia_inicial}"
                return True, mensaje_exito
            else:
                return False, f"Error en el nivel: {mensaje}"
                
        except Exception as e:
            return False, f"Error al cargar el archivo: {str(e)}"
    
    def validar_nivel(self, datos):
        """Valida que el nivel tenga una estructura correcta"""
        try:
            # Validar dimensiones mínimas de la matriz
            filas = datos['matriz']['filas']
            columnas = datos['matriz']['columnas']
            
            if filas < 30 or columnas < 30:
                return False, f"La matriz debe ser al menos de 30x30. Tamaño actual: {filas}x{columnas}"
            
            # Validar que la matriz inicial tenga las dimensiones correctas
            if len(datos['matrizInicial']) != filas:
                return False, f"La matriz inicial no tiene el número correcto de filas. Esperado: {filas}, Actual: {len(datos['matrizInicial'])}"
            
            for i, fila in enumerate(datos['matrizInicial']):
                if len(fila) != columnas:
                    return False, f"La fila {i} de la matriz inicial no tiene el número correcto de columnas. Esperado: {columnas}, Actual: {len(fila)}"
            
            # Validar mínimo de estrellas gigantes
            if len(datos['estrellasGigantes']) < 5:
                return False, "El nivel debe tener al menos 5 estrellas gigantes"
            
            # Validar valores de energía
            for fila in datos['matrizInicial']:
                for valor in fila:
                    if valor < 1 or valor > 10:
                        return False, f"Los valores de energía deben estar entre 1 y 10. Encontrado: {valor}"
            
            # Validar que el origen y destino estén dentro de los límites
            origen = datos['origen']
            destino = datos['destino']
            
            if not (0 <= origen[0] < filas and 0 <= origen[1] < columnas):
                return False, f"El punto de origen {origen} está fuera de los límites de la matriz"
            
            if not (0 <= destino[0] < filas and 0 <= destino[1] < columnas):
                return False, f"El punto de destino {destino} está fuera de los límites de la matriz"
            
            # Validar que todos los elementos estén dentro de los límites
            elementos_a_validar = [
                ('agujerosNegros', datos.get('agujerosNegros', [])),
                ('estrellasGigantes', datos.get('estrellasGigantes', [])),
            ]
            
            for nombre, lista in elementos_a_validar:
                for elemento in lista:
                    if not (0 <= elemento[0] < filas and 0 <= elemento[1] < columnas):
                        return False, f"Elemento en {nombre} fuera de límites: {elemento}"
            
            # Validar agujeros de gusano
            for gusano in datos.get('agujerosGusano', []):
                entrada = gusano['entrada']
                salida = gusano['salida']
                
                if not (0 <= entrada[0] < filas and 0 <= entrada[1] < columnas):
                    return False, f"Entrada de agujero de gusano fuera de límites: {entrada}"
                
                if not (0 <= salida[0] < filas and 0 <= salida[1] < columnas):
                    return False, f"Salida de agujero de gusano fuera de límites: {salida}"
            
            # Validar zonas de recarga
            for recarga in datos.get('zonasRecarga', []):
                if len(recarga) >= 2:
                    if not (0 <= recarga[0] < filas and 0 <= recarga[1] < columnas):
                        return False, f"Zona de recarga fuera de límites: {recarga[:2]}"
                
                if len(recarga) >= 3:
                    if recarga[2] <= 1:
                        return False, f"Multiplicador de recarga debe ser mayor a 1: {recarga[2]}"
            
            return True, "Nivel válido"
            
        except KeyError as e:
            return False, f"Clave faltante en el nivel: {str(e)}"
        except Exception as e:
            return False, f"Error de validación: {str(e)}"
    
    def obtener_datos_nivel(self):
        """Retorna los datos del nivel actual"""
        return self.datos_nivel
    
    def obtener_configuracion_inicial(self):
        """Retorna la configuración inicial del nivel"""
        if not self.datos_nivel:
            return None
        
        return {
            'origen': self.datos_nivel['origen'],
            'destino': self.datos_nivel['destino'],
            'energia_inicial': self.datos_nivel['cargaInicial'],
            'filas': self.datos_nivel['matriz']['filas'],
            'columnas': self.datos_nivel['matriz']['columnas']
        }
    
    def obtener_estadisticas(self):
        """Retorna estadísticas del nivel"""
        if not self.datos_nivel:
            return None
        
        return {
            'agujeros_negros_total': self.total_agujeros_negros,
            'agujeros_negros_actuales': len(self.datos_nivel['agujerosNegros']),
            'agujeros_gusano_total': self.total_agujeros_gusano,
            'agujeros_gusano_actuales': len(self.datos_nivel['agujerosGusano']),
            'estrellas_gigantes': len(self.datos_nivel['estrellasGigantes']),
            'zonas_recarga': len(self.datos_nivel['zonasRecarga'])
        }
    
    def reiniciar_nivel(self):
        """Reinicia el nivel a su estado original"""
        if self.datos_nivel:
            # Aquí podrías recargar el nivel desde el archivo original
            # Por ahora, simplemente limpiamos las referencias
            pass
    
    def nivel_esta_cargado(self):
        """Verifica si hay un nivel cargado"""
        return self.datos_nivel is not None
    
    def obtener_energia_inicial(self):
        """Retorna la energía inicial del nivel"""
        if self.datos_nivel:
            return self.datos_nivel['cargaInicial']
        return 0
    
    def obtener_origen_destino(self):
        """Retorna el origen y destino del nivel"""
        if self.datos_nivel:
            return self.datos_nivel['origen'], self.datos_nivel['destino']
        return None, None
    
    def verificar_posicion_valida(self, x, y):
        """Verifica si una posición está dentro de los límites del nivel"""
        if not self.datos_nivel:
            return False
        
        filas = self.datos_nivel['matriz']['filas']
        columnas = self.datos_nivel['matriz']['columnas']
        
        return 0 <= x < filas and 0 <= y < columnas
    
    def obtener_costo_energia(self, x, y):
        """Obtiene el costo de energía de una posición específica"""
        if not self.verificar_posicion_valida(x, y):
            return None
        
        return self.datos_nivel['matrizInicial'][x][y] 