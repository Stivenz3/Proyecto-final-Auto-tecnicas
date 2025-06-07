import pygame
import json
import os
import sys
from tkinter import filedialog, Tk
from .nave import Nave
from .backtracking import Backtracking

class JuegoMision:
    def __init__(self):
        pygame.init()
        
        # Dimensiones iniciales de la ventana
        self.ANCHO = 1280
        self.ALTO = 720
        self.ANCHO_BARRA_LATERAL = 300  # Barra lateral más ancha
        self.tamaño_celda = 0  # Nueva variable para el tamaño de celda
        
        # Crear ventana
        self.pantalla = pygame.display.set_mode(
            (self.ANCHO, self.ALTO), 
            pygame.RESIZABLE | pygame.SHOWN
        )
        pygame.display.set_caption("Misión Interestelar")
        
        # Definir áreas de la interfaz
        self.AREA_MATRIZ = pygame.Rect(
            0, 0,  # Posición X,Y
            self.ANCHO - self.ANCHO_BARRA_LATERAL,  # Ancho
            self.ALTO  # Alto
        )
        
        self.AREA_INFO = pygame.Rect(
            self.ANCHO - self.ANCHO_BARRA_LATERAL, 0,  # Posición X,Y
            self.ANCHO_BARRA_LATERAL,  # Ancho
            self.ALTO  # Alto
        )
        
        self.corriendo = True
        self.buscando_solucion = False
        self.cancelar_busqueda = False
        
        # Colores
        self.NEGRO = (0, 0, 0)
        self.BLANCO = (255, 255, 255)
        self.AZUL = (0, 0, 255)
        self.ROJO = (255, 0, 0)
        self.VERDE = (0, 255, 0)
        self.GRIS = (50, 50, 50)
        self.GRIS_CLARO = (100, 100, 100)
        self.AMARILLO = (255, 255, 0)
        self.MORADO = (128, 0, 128)
        
        # Variables de posición inicial
        self.offset_inicial_x = 0
        self.offset_inicial_y = 0
        
        # Variables de scroll
        self.scroll_x = 0
        self.scroll_y = 0
        self.velocidad_scroll = 50
        
        # Variables de zoom y arrastre
        self.zoom = 1.0
        self.min_zoom = 0.3
        self.max_zoom = 3.0
        self.offset_x = 0
        self.offset_y = 0
        self.arrastrando = False
        self.pos_arrastre = None
        self.velocidad_zoom = 0.1
        self.suavizado_movimiento = 0.8
        self.offset_objetivo_x = 0
        self.offset_objetivo_y = 0
        self.zoom_objetivo = 1.0
        
        # Buffer de renderizado
        self.buffer_superficie = None
        self.ultima_actualizacion = 0
        self.tiempo_minimo_actualizacion = 1/120  # 120 FPS máximo
        
        # Cargar iconos
        self.iconos = self._cargar_iconos()
        
        # Estado del juego
        self.datos_nivel = None
        self.nave = None
        self.mensaje = "Seleccione un archivo de nivel (JSON)"
        self.mensaje_color = self.BLANCO
        self.ruta = None
        self.busqueda_iniciada = False
        self.carga_actual = 0
        self.pasos = 0
        self.superficie_matriz = None
        
        # Crear botones en la barra lateral
        ancho_boton = self.ANCHO_BARRA_LATERAL - 40  # 20 píxeles de margen a cada lado
        alto_boton = 50
        espacio_botones = 20
        x_botones = self.ANCHO - self.ANCHO_BARRA_LATERAL + 20  # 20 píxeles desde el borde izquierdo de la barra
        y_botones = self.ALTO - (alto_boton + espacio_botones) * 3 - 20  # 20 píxeles desde el borde inferior
        
        self.botones = [
            {
                'rect': pygame.Rect(x_botones, y_botones, ancho_boton, alto_boton),
                'texto': "Cargar Nivel",
                'color': self.VERDE,
                'color_hover': (100, 255, 100),
                'color_actual': self.VERDE,
                'accion': self.cargar_nivel
            },
            {
                'rect': pygame.Rect(x_botones, y_botones + alto_boton + espacio_botones, ancho_boton, alto_boton),
                'texto': "Buscar Ruta",
                'color': self.AZUL,
                'color_hover': (100, 100, 255),
                'color_actual': self.AZUL,
                'accion': self.buscar_ruta
            },
            {
                'rect': pygame.Rect(x_botones, y_botones + (alto_boton + espacio_botones) * 2, ancho_boton, alto_boton),
                'texto': "Salir",
                'color': self.ROJO,
                'color_hover': (255, 100, 100),
                'color_actual': self.ROJO,
                'accion': self.salir
            }
        ]
        
        # Leyenda
        self.leyenda = [
            ("Nave", 'nave'),
            ("Meta", 'meta'),
            ("Agujero Negro", 'agujero_negro'),
            ("Estrella Gigante", 'estrella'),
            ("Agujero de Gusano", 'gusano'),
            ("Zona de Recarga", 'recarga')
        ]
        
        # Cargar nivel
        self.cargar_nivel()
        
    def _cargar_iconos(self):
        """Carga los iconos del juego"""
        iconos = {}
        iconos_path = "assets/icons"
        try:
            # Mapeo de iconos disponibles
            iconos['nave'] = pygame.image.load(os.path.join(iconos_path, "rocket.png"))
            iconos['estrella'] = pygame.image.load(os.path.join(iconos_path, "star.png"))
            iconos['agujero_negro'] = pygame.image.load(os.path.join(iconos_path, "black-hole.png"))
            iconos['gusano'] = pygame.image.load(os.path.join(iconos_path, "teleport.png"))
            iconos['recarga'] = pygame.image.load(os.path.join(iconos_path, "process.png"))
            iconos['meta'] = pygame.image.load(os.path.join(iconos_path, "goal.png"))
            
            # Redimensionar iconos (se ajustará en tiempo de ejecución)
            for key in iconos:
                iconos[key] = pygame.transform.scale(iconos[key], (48, 48))
            
        except Exception as e:
            print(f"Error al cargar iconos: {str(e)}")
            # Crear círculos de colores como respaldo
            for key in ['nave', 'estrella', 'agujero_negro', 'gusano', 'recarga', 'meta']:
                superficie = pygame.Surface((48, 48), pygame.SRCALPHA)
                color = {
                    'nave': (255, 0, 0, 255),      # Rojo
                    'estrella': (255, 255, 0, 255), # Amarillo
                    'agujero_negro': (0, 0, 0, 255), # Negro
                    'gusano': (128, 0, 128, 255),   # Morado
                    'recarga': (0, 255, 0, 255),    # Verde
                    'meta': (255, 165, 0, 255)      # Naranja
                }.get(key, (255, 255, 255, 255))
                pygame.draw.circle(superficie, color, (24, 24), 20)
                iconos[key] = superficie
            
            print("Usando círculos de colores como iconos de respaldo")
        
        return iconos
        
    def crear_boton(self, texto, x, y, ancho, alto, color, color_hover=(150,150,150)):
        """Crea un botón rectangular con texto"""
        return {
            'rect': pygame.Rect(x, y, ancho, alto),
            'texto': texto,
            'color': color,
            'color_hover': color_hover,
            'color_actual': color
        }

    def dibujar_boton(self, boton):
        """Dibuja un botón en la pantalla"""
        # Dibujar el rectángulo del botón
        pygame.draw.rect(self.pantalla, boton['color_actual'], boton['rect'])
        
        # Dibujar el texto del botón
        fuente = pygame.font.Font(None, 36)
        texto = fuente.render(boton['texto'], True, self.NEGRO)
        rect_texto = texto.get_rect(center=boton['rect'].center)
        self.pantalla.blit(texto, rect_texto)

    def actualizar_botones(self, pos_mouse):
        """Actualiza el color de los botones según la posición del mouse"""
        for boton in self.botones:
            if boton['rect'].collidepoint(pos_mouse):
                boton['color_actual'] = boton['color_hover']
            else:
                boton['color_actual'] = boton['color']

    def dibujar_matriz(self):
        if not self.datos_nivel:
            return
            
        # Calcular tamaño de cada celda para aprovechar el espacio
        celda_ancho = self.AREA_MATRIZ.width // self.datos_nivel['matriz']['columnas']
        celda_alto = self.AREA_MATRIZ.height // self.datos_nivel['matriz']['filas']
        self.tamaño_celda = min(celda_ancho, celda_alto)
        
        # Centrar la matriz en el área disponible
        offset_x = (self.AREA_MATRIZ.width - (self.tamaño_celda * self.datos_nivel['matriz']['columnas'])) // 2
        offset_y = (self.AREA_MATRIZ.height - (self.tamaño_celda * self.datos_nivel['matriz']['filas'])) // 2
        
        # Crear superficie para la matriz si no existe
        if self.superficie_matriz is None:
            ancho_matriz = self.datos_nivel['matriz']['columnas'] * self.tamaño_celda
            alto_matriz = self.datos_nivel['matriz']['filas'] * self.tamaño_celda
            self.superficie_matriz = pygame.Surface((ancho_matriz, alto_matriz))
            
            # Dibujar celdas
            self.superficie_matriz.fill(self.NEGRO)
            for i in range(self.datos_nivel['matriz']['filas']):
                for j in range(self.datos_nivel['matriz']['columnas']):
                    x = j * self.tamaño_celda
                    y = i * self.tamaño_celda
                    rect = pygame.Rect(x, y, self.tamaño_celda - 1, self.tamaño_celda - 1)
                    
                    # Dibujar celda
                    pygame.draw.rect(self.superficie_matriz, self.GRIS_CLARO, rect, 1)
                    
                    # Dibujar valor de energía
                    valor = self.datos_nivel['matrizInicial'][i][j]
                    fuente = pygame.font.Font(None, int(self.tamaño_celda * 0.8))
                    texto = fuente.render(str(valor), True, self.BLANCO)
                    rect_texto = texto.get_rect(center=(x + self.tamaño_celda//2, y + self.tamaño_celda//2))
                    self.superficie_matriz.blit(texto, rect_texto)
                    
                    # Dibujar icono si corresponde
                    tipo = self.obtener_tipo_celda(i, j)
                    if tipo:
                        icono = pygame.transform.scale(
                            self.iconos[tipo], 
                            (int(self.tamaño_celda * 0.8), int(self.tamaño_celda * 0.8))
                        )
                        rect_icono = icono.get_rect(center=(x + self.tamaño_celda//2, y + self.tamaño_celda//2))
                        self.superficie_matriz.blit(icono, rect_icono)
        
        # Dibujar la matriz centrada
        pos_x = self.AREA_MATRIZ.left + offset_x + self.scroll_x
        pos_y = self.AREA_MATRIZ.top + offset_y + self.scroll_y
        self.pantalla.blit(self.superficie_matriz, (pos_x, pos_y))
        
        # Dibujar borde del área de la matriz
        pygame.draw.rect(self.pantalla, self.BLANCO, self.AREA_MATRIZ, 2)
        
        # Si hay un rastro, dibujarlo
        if hasattr(self, 'rastro') and self.rastro:
            for j in range(len(self.rastro) - 1):
                p1 = self.rastro[j]
                p2 = self.rastro[j + 1]
                
                # Calcular coordenadas en pantalla
                x1 = self.AREA_MATRIZ.left + offset_x + p1[1] * self.tamaño_celda + self.tamaño_celda // 2
                y1 = self.AREA_MATRIZ.top + offset_y + p1[0] * self.tamaño_celda + self.tamaño_celda // 2
                x2 = self.AREA_MATRIZ.left + offset_x + p2[1] * self.tamaño_celda + self.tamaño_celda // 2
                y2 = self.AREA_MATRIZ.top + offset_y + p2[0] * self.tamaño_celda + self.tamaño_celda // 2
                
                # Dibujar línea continua
                pygame.draw.line(self.pantalla, self.VERDE, (x1, y1), (x2, y2), 3)
                
                # Si es un punto de teletransporte, dibujar destello
                for gusano in self.datos_nivel['agujerosGusano']:
                    if p1 == gusano['entrada'] and p2 == gusano['salida']:
                        # Destello en entrada
                        radio = self.tamaño_celda // 2
                        pygame.draw.circle(self.pantalla, self.MORADO, (x1, y1), radio + 4, 2)
                        pygame.draw.circle(self.pantalla, self.MORADO, (x1, y1), radio + 8, 2)
                        # Destello en salida
                        pygame.draw.circle(self.pantalla, self.MORADO, (x2, y2), radio + 4, 2)
                        pygame.draw.circle(self.pantalla, self.MORADO, (x2, y2), radio + 8, 2)
        
        # Si hay una posición final, dibujar la nave allí
        if hasattr(self, 'posicion_final') and self.posicion_final:
            x = self.AREA_MATRIZ.left + offset_x + self.posicion_final[1] * self.tamaño_celda + self.tamaño_celda // 2
            y = self.AREA_MATRIZ.top + offset_y + self.posicion_final[0] * self.tamaño_celda + self.tamaño_celda // 2
            
            icono_nave = pygame.transform.scale(
                self.iconos['nave'],
                (int(self.tamaño_celda * 0.8), int(self.tamaño_celda * 0.8))
            )
            rect_nave = icono_nave.get_rect(center=(x, y))
            self.pantalla.blit(icono_nave, rect_nave)

    def dibujar_texto(self, texto, x, y, color=None, tamaño=36):
        """Dibuja texto en la pantalla"""
        if color is None:
            color = self.BLANCO
        fuente = pygame.font.Font(None, tamaño)
        superficie = fuente.render(texto, True, color)
        self.pantalla.blit(superficie, (x, y))

    def dibujar_barra_lateral(self):
        """Dibuja la barra lateral con información"""
        # Dibujar fondo de la barra lateral
        pygame.draw.rect(self.pantalla, (40, 40, 40), self.AREA_INFO)
        pygame.draw.rect(self.pantalla, self.BLANCO, self.AREA_INFO, 2)  # Borde
        
        # Posición inicial para la información
        x = self.AREA_INFO.left + 20
        y = 20
        espaciado = 40
        
        # Mostrar información del juego
        if self.datos_nivel:
            # Mostrar energía actual
            self.dibujar_texto(f"Energía: {self.carga_actual}", x, y)
            y += espaciado
            
            # Mostrar pasos
            if hasattr(self, 'pasos'):
                self.dibujar_texto(f"Pasos: {self.pasos}", x, y)
                y += espaciado
            
            # Mostrar estadísticas
            if hasattr(self, 'total_agujeros_negros'):
                agujeros_destruidos = self.total_agujeros_negros - len(self.datos_nivel['agujerosNegros'])
                self.dibujar_texto("Agujeros Negros", x, y)
                y += espaciado // 2
                self.dibujar_texto(f"Destruidos: {agujeros_destruidos}", x + 20, y)
                y += espaciado
            
            self.dibujar_texto("Agujeros de Gusano", x, y)
            y += espaciado // 2
            self.dibujar_texto(f"Disponibles: {len(self.datos_nivel['agujerosGusano'])}", x + 20, y)
            y += espaciado * 2  # Espacio extra antes del mensaje
        
        # Mostrar mensaje actual
        if hasattr(self, 'mensaje'):
            # Dividir el mensaje en líneas si es muy largo
            palabras = self.mensaje.split()
            lineas = []
            linea_actual = []
            ancho_max = self.ANCHO_BARRA_LATERAL - 40
            
            for palabra in palabras:
                linea_actual.append(palabra)
                texto_prueba = ' '.join(linea_actual)
                fuente = pygame.font.Font(None, 24)
                if fuente.size(texto_prueba)[0] > ancho_max:
                    linea_actual.pop()
                    lineas.append(' '.join(linea_actual))
                    linea_actual = [palabra]
            
            if linea_actual:
                lineas.append(' '.join(linea_actual))
            
            for linea in lineas:
                self.dibujar_texto(linea, x, y, self.mensaje_color, 24)
                y += 30
                
            y += espaciado  # Espacio adicional después del mensaje
        
        # Dibujar leyenda después del mensaje
        # Título de la leyenda
        self.dibujar_texto("Leyenda:", x, y, self.BLANCO, 28)
        y += 35
        
        # Dibujar cada elemento de la leyenda
        for nombre, clave in self.leyenda:
            # Escalar icono
            icono = pygame.transform.scale(self.iconos[clave], (24, 24))
            # Dibujar icono
            rect_icono = icono.get_rect(topleft=(x, y))
            self.pantalla.blit(icono, rect_icono)
            # Dibujar texto
            self.dibujar_texto(nombre, x + 35, y + 5, self.BLANCO, 24)
            y += 35
        
        # Dibujar botones al final
        for boton in self.botones:
            self.dibujar_boton(boton)

    def dibujar_interfaz(self):
        # Limpiar pantalla
        self.pantalla.fill((30, 30, 30))
        
        # Dibujar matriz primero
        self.dibujar_matriz()
        
        # Dibujar barra lateral después
        self.dibujar_barra_lateral()
        
        # Actualizar pantalla
        pygame.display.flip()

    def procesar_eventos(self):
        """Procesa los eventos de Pygame"""
        pos_mouse = pygame.mouse.get_pos()
        self.actualizar_botones(pos_mouse)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.salir()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                # Verificar si se hizo clic en algún botón
                for boton in self.botones:
                    if boton['rect'].collidepoint(pos_mouse):
                        boton['accion']()  # Llamar a la función asociada al botón
                        return
            elif evento.type == pygame.VIDEORESIZE:
                # Actualizar dimensiones cuando se redimensiona la ventana
                self.ANCHO = evento.w
                self.ALTO = evento.h
                self.pantalla = pygame.display.set_mode(
                    (self.ANCHO, self.ALTO),
                    pygame.RESIZABLE | pygame.SHOWN
                )
                # Actualizar áreas
                self.AREA_MATRIZ = pygame.Rect(0, 0, self.ANCHO - self.ANCHO_BARRA_LATERAL, self.ALTO)
                self.AREA_INFO = pygame.Rect(self.ANCHO - self.ANCHO_BARRA_LATERAL, 0, self.ANCHO_BARRA_LATERAL, self.ALTO)
                # Actualizar posición de los botones
                self._actualizar_posicion_botones()
                # Redibujar matriz
                self.superficie_matriz = None
                self.dibujar_interfaz()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.salir()
                # Scroll con teclas de flecha
                if evento.key == pygame.K_LEFT:
                    self.scroll_x = min(0, self.scroll_x + self.velocidad_scroll)
                elif evento.key == pygame.K_RIGHT:
                    min_scroll = min(0, -(self.datos_nivel['matriz']['columnas'] * self.tamaño_celda - 
                                       (self.ANCHO_BARRA_LATERAL)))
                    self.scroll_x = max(min_scroll, self.scroll_x - self.velocidad_scroll)
                elif evento.key == pygame.K_UP:
                    self.scroll_y = min(0, self.scroll_y + self.velocidad_scroll)
                elif evento.key == pygame.K_DOWN:
                    min_scroll = min(0, -(self.datos_nivel['matriz']['filas'] * self.tamaño_celda - self.ALTO))
                    self.scroll_y = max(min_scroll, self.scroll_y - self.velocidad_scroll)

    def _actualizar_posicion_botones(self):
        """Actualiza la posición de los botones cuando se redimensiona la ventana"""
        ancho_boton = self.ANCHO_BARRA_LATERAL - 40
        alto_boton = 50
        espacio_botones = 20
        x_botones = self.ANCHO - self.ANCHO_BARRA_LATERAL + 20
        y_botones = self.ALTO - (alto_boton + espacio_botones) * 3 - 20
        
        for i, boton in enumerate(self.botones):
            boton['rect'] = pygame.Rect(
                x_botones,
                y_botones + (alto_boton + espacio_botones) * i,
                ancho_boton,
                alto_boton
            )

    def animar_ruta(self):
        """Anima el movimiento de la nave por la ruta encontrada"""
        if not self.ruta:
            return
            
        # Crear una lista para almacenar el rastro
        self.rastro = []
        self.pasos = 0
        self.carga_actual = self.datos_nivel['cargaInicial']
        
        # Calcular offset para centrar la matriz
        offset_x = (self.AREA_MATRIZ.width - (self.tamaño_celda * self.datos_nivel['matriz']['columnas'])) // 2
        offset_y = (self.AREA_MATRIZ.height - (self.tamaño_celda * self.datos_nivel['matriz']['filas'])) // 2
        
        # Para cada punto en la ruta
        i = 0
        while i < len(self.ruta):
            # Procesar eventos para evitar que la aplicación se congele
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.salir()
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        return
            
            punto = self.ruta[i]
            # Actualizar pasos y energía
            self.pasos += 1
            self.carga_actual -= self.datos_nivel['matrizInicial'][punto[0]][punto[1]]
            
            # Verificar zonas de recarga
            for recarga in self.datos_nivel['zonasRecarga']:
                if punto == recarga[:2]:
                    self.carga_actual *= recarga[2]
                    self.mensaje = f"¡Recargando energía! Multiplicador: x{recarga[2]}"
                    self.mensaje_color = self.VERDE
            
            # Limpiar la pantalla y dibujar la interfaz completa
            self.pantalla.fill((30, 30, 30))
            self.dibujar_matriz()
            
            # Dibujar el rastro completo
            for j in range(len(self.rastro) - 1):
                p1 = self.rastro[j]
                p2 = self.rastro[j + 1]
                
                # Calcular coordenadas en pantalla
                x1 = self.AREA_MATRIZ.left + offset_x + p1[1] * self.tamaño_celda + self.tamaño_celda // 2
                y1 = self.AREA_MATRIZ.top + offset_y + p1[0] * self.tamaño_celda + self.tamaño_celda // 2
                x2 = self.AREA_MATRIZ.left + offset_x + p2[1] * self.tamaño_celda + self.tamaño_celda // 2
                y2 = self.AREA_MATRIZ.top + offset_y + p2[0] * self.tamaño_celda + self.tamaño_celda // 2
                
                # Dibujar línea continua
                pygame.draw.line(self.pantalla, self.VERDE, (x1, y1), (x2, y2), 3)
            
            # Verificar si es un agujero de gusano
            es_gusano = False
            for gusano in self.datos_nivel['agujerosGusano']:
                if punto == gusano['entrada']:
                    # Encontrar el siguiente punto después de la salida del gusano
                    salida = gusano['salida']
                    if i + 1 < len(self.ruta) and self.ruta[i + 1] == salida:
                        es_gusano = True
                        # Agregar punto actual al rastro
                        self.rastro.append(punto)
                        # Mostrar mensaje de teletransporte
                        self.mensaje = "¡Teletransportando nave!"
                        self.mensaje_color = self.MORADO
                        # Esperar antes de teletransportar
                        self.dibujar_barra_lateral()
                        pygame.display.flip()
                        pygame.time.wait(700)  # Pausa antes del teletransporte
                        # Agregar punto de salida al rastro
                        self.rastro.append(salida)
                        # Eliminar el agujero de gusano usado
                        self.datos_nivel['agujerosGusano'].remove(gusano)
                        i += 1  # Saltar el punto de salida ya que estamos teletransportando
                        break
            
            if not es_gusano:
                # Agregar punto actual al rastro
                self.rastro.append(punto)
            
            # Dibujar nave en la posición actual
            x = self.AREA_MATRIZ.left + offset_x + punto[1] * self.tamaño_celda + self.tamaño_celda // 2
            y = self.AREA_MATRIZ.top + offset_y + punto[0] * self.tamaño_celda + self.tamaño_celda // 2
            
            icono_nave = pygame.transform.scale(
                self.iconos['nave'],
                (int(self.tamaño_celda * 0.8), int(self.tamaño_celda * 0.8))
            )
            rect_nave = icono_nave.get_rect(center=(x, y))
            self.pantalla.blit(icono_nave, rect_nave)
            
            # Dibujar barra lateral
            self.dibujar_barra_lateral()
            
            # Actualizar pantalla
            pygame.display.flip()
            
            # Esperar un tiempo normal para movimientos regulares
            if not es_gusano:
                pygame.time.wait(400)
            
            i += 1
            
        # Actualizar mensaje final
        if self.carga_actual > 0:
            self.mensaje = f"¡Ruta completada! Energía restante: {int(self.carga_actual)}"
            self.mensaje_color = self.VERDE
        else:
            self.mensaje = "La nave se quedó sin energía"
            self.mensaje_color = self.ROJO
            
        # Guardar la posición final de la nave
        self.posicion_final = self.ruta[-1]
        
        # Dibujar estado final
        self.dibujar_interfaz()
        pygame.display.flip()

    def buscar_ruta(self):
        """Inicia la búsqueda de una ruta"""
        if not self.datos_nivel:
            self.mensaje = "Primero debe cargar un nivel"
            self.mensaje_color = self.ROJO
            return
        
        # Reiniciar estado
        self.ruta = None
        self.busqueda_iniciada = True
        self.mensaje = "Buscando ruta..."
        self.mensaje_color = self.AMARILLO
        
        # Obtener origen y destino
        origen = self.datos_nivel['origen']
        destino = self.datos_nivel['destino']
        energia_inicial = self.datos_nivel['cargaInicial']
        
        # Crear instancia de Backtracking y buscar ruta
        buscador = Backtracking()
        self.ruta = buscador.iniciar_busqueda(self.datos_nivel, origen, destino, energia_inicial)
        
        if self.ruta:
            self.mensaje = "¡Ruta encontrada! Iniciando animación..."
            self.mensaje_color = self.VERDE
            self.carga_actual = energia_inicial
            self.pasos = len(self.ruta)
            # Actualizar la interfaz antes de la animación
            self.dibujar_interfaz()
            pygame.display.flip()
            # Iniciar la animación
            self.animar_ruta()
        else:
            self.mensaje = "No se encontró una ruta válida"
            self.mensaje_color = self.ROJO
        
        self.busqueda_iniciada = False
        # Actualizar la interfaz una última vez
        self.dibujar_interfaz()
        pygame.display.flip()

    def _esta_en_obstaculo(self, x, y):
        """Verifica si una coordenada está en un obstáculo"""
        # Verificar agujeros negros
        if [x, y] in self.datos_nivel['agujerosNegros']:
            return True
            
        # Verificar estrellas gigantes
        if [x, y] in self.datos_nivel['estrellasGigantes']:
            return True
            
        return False

    def cargar_nivel(self):
        """Permite al usuario seleccionar y cargar un archivo JSON de nivel"""
        root = Tk()
        root.withdraw()
        
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de nivel",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
            initialdir="data"
        )
        
        if archivo:
            try:
                with open(archivo, 'r') as f:
                    datos_temp = json.load(f)
                
                # Validar el nivel antes de asignarlo
                try:
                    # Validar dimensiones mínimas de la matriz
                    filas = datos_temp['matriz']['filas']
                    columnas = datos_temp['matriz']['columnas']
                    
                    if filas < 30 or columnas < 30:
                        raise ValueError(f"La matriz debe ser al menos de 30x30. Tamaño actual: {filas}x{columnas}")
                    
                    # Validar que la matriz inicial tenga las dimensiones correctas
                    if len(datos_temp['matrizInicial']) != filas:
                        raise ValueError(f"La matriz inicial no tiene el número correcto de filas. Esperado: {filas}, Actual: {len(datos_temp['matrizInicial'])}")
                    
                    for i, fila in enumerate(datos_temp['matrizInicial']):
                        if len(fila) != columnas:
                            raise ValueError(f"La fila {i} de la matriz inicial no tiene el número correcto de columnas. Esperado: {columnas}, Actual: {len(fila)}")
                    
                    # Validar mínimo de estrellas gigantes
                    if len(datos_temp['estrellasGigantes']) < 5:
                        raise ValueError("El nivel debe tener al menos 5 estrellas gigantes")
                    
                    # Validar valores de energía
                    for fila in datos_temp['matrizInicial']:
                        for valor in fila:
                            if valor < 1 or valor > 10:
                                raise ValueError(f"Los valores de energía deben estar entre 1 y 10. Encontrado: {valor}")
                    
                    # Validar que el origen y destino estén dentro de los límites
                    origen = datos_temp['origen']
                    destino = datos_temp['destino']
                    
                    if not (0 <= origen[0] < filas and 0 <= origen[1] < columnas):
                        raise ValueError(f"El punto de origen {origen} está fuera de los límites de la matriz")
                    
                    if not (0 <= destino[0] < filas and 0 <= destino[1] < columnas):
                        raise ValueError(f"El punto de destino {destino} está fuera de los límites de la matriz")
                    
                    # Si pasa todas las validaciones, asignar los datos
                    self.datos_nivel = datos_temp
                    self.carga_actual = self.datos_nivel['cargaInicial']
                    # Guardar total inicial de agujeros negros y gusanos
                    self.total_agujeros_negros = len(self.datos_nivel['agujerosNegros'])
                    self.total_agujeros_gusano = len(self.datos_nivel['agujerosGusano'])
                    
                    # Ajustar el tamaño de celda para matrices grandes
                    area_matriz_ancho = self.ANCHO - self.ANCHO_BARRA_LATERAL
                    area_matriz_alto = self.ALTO
                    
                    celda_ancho = area_matriz_ancho // columnas
                    celda_alto = area_matriz_alto // filas
                    self.tamaño_celda = min(celda_ancho, celda_alto)
                    
                    # Asegurar un tamaño mínimo de celda
                    if self.tamaño_celda < 10:
                        self.tamaño_celda = 10
                    
                    # Limpiar estado anterior
                    self.rastro = []
                    self.ruta = None
                    self.posicion_final = None
                    self.superficie_matriz = None
                    self.busqueda_iniciada = False
                    self.pasos = 0  # Reiniciar contador de pasos
                    
                    self.mensaje = f"Nivel cargado. Matriz: {filas}x{columnas}. Energía inicial: {self.carga_actual}"
                    self.mensaje_color = self.VERDE
                    self.dibujar_interfaz()
                    return True
                    
                except ValueError as e:
                    self.mensaje = f"Error en el nivel: {str(e)}"
                    self.mensaje_color = self.ROJO
                    self.dibujar_interfaz()
                    return False
                    
            except Exception as e:
                self.mensaje = f"Error al cargar el archivo: {str(e)}"
                self.mensaje_color = self.ROJO
                print(f"Error detallado: {e}")  # Para depuración
                self.dibujar_interfaz()
                return False
        else:
            self.mensaje = "No se seleccionó ningún archivo"
            self.mensaje_color = self.ROJO
            self.dibujar_interfaz()
            return False

    def obtener_tipo_celda(self, x, y):
        """Determina el tipo de celda en las coordenadas dadas"""
        if self.ruta and self.ruta[0] == [x, y]:
            return None  # No mostrar la nave en la posición inicial durante la animación
        if [x, y] == self.datos_nivel['origen']:
            return 'nave'
        if [x, y] == self.datos_nivel['destino']:
            return 'meta'
        if [x, y] in self.datos_nivel['agujerosNegros']:
            return 'agujero_negro'
        if [x, y] in self.datos_nivel['estrellasGigantes']:
            return 'estrella'
        for gusano in self.datos_nivel['agujerosGusano']:
            if [x, y] in [gusano['entrada'], gusano['salida']]:
                return 'gusano'
        for recarga in self.datos_nivel['zonasRecarga']:
            if [x, y] == recarga[:2]:
                return 'recarga'
        return None
        
    def actualizar_zoom_y_posicion(self):
        """Actualiza suavemente el zoom y la posición"""
        # Actualizar zoom con suavizado
        if abs(self.zoom - self.zoom_objetivo) > 0.001:
            self.zoom += (self.zoom_objetivo - self.zoom) * 0.1
        
        # Actualizar posición con suavizado
        if not self.arrastrando:
            self.offset_x += (self.offset_objetivo_x - self.offset_x) * self.suavizado_movimiento
            self.offset_y += (self.offset_objetivo_y - self.offset_y) * self.suavizado_movimiento

    def dibujar_leyenda(self):
        """Dibuja la leyenda del juego"""
        # Dibujar leyenda en la parte inferior derecha
        fuente = pygame.font.Font(None, 24)
        y = self.ALTO - 50
        for nombre, clave in self.leyenda:
            icono = pygame.transform.scale(self.iconos[clave], (24, 24))
            rect = icono.get_rect(topleft=(self.ANCHO - 200, y))
            self.pantalla.blit(icono, rect)
            texto = fuente.render(nombre, True, self.BLANCO)
            rect_texto = texto.get_rect(topleft=(self.ANCHO - 170, y))
            self.pantalla.blit(texto, rect_texto)
            y += 30

    def salir(self):
        """Cierra el juego y fuerza la terminación"""
        try:
            pygame.display.quit()
            pygame.quit()
        except:
            pass
        finally:
            sys.exit(0)  # Usar sys.exit en lugar de os._exit para un cierre más limpio

    def ejecutar(self):
        """Ejecuta el bucle principal del juego"""
        reloj = pygame.time.Clock()
        self.corriendo = True
        
        # Mostrar la interfaz inicial
        self.dibujar_interfaz()
        
        try:
            while self.corriendo:
                self.procesar_eventos()
                self.dibujar_interfaz()
                reloj.tick(60)
        except Exception as e:
            print(f"Error en el bucle principal: {str(e)}")
        finally:
            self.salir()

    def animar_retroceso(self, punto_actual, punto_anterior):
        """Anima el retroceso del backtracking"""
        # Mostrar mensaje de retroceso
        self.mensaje = "Retrocediendo para buscar otro camino..."
        self.mensaje_color = self.AMARILLO
        
        # Calcular coordenadas en pantalla
        offset_x = (self.AREA_MATRIZ.width - (self.tamaño_celda * self.datos_nivel['matriz']['columnas'])) // 2
        offset_y = (self.AREA_MATRIZ.height - (self.tamaño_celda * self.datos_nivel['matriz']['filas'])) // 2
        
        x1 = self.AREA_MATRIZ.left + offset_x + punto_anterior[1] * self.tamaño_celda + self.tamaño_celda // 2
        y1 = self.AREA_MATRIZ.top + offset_y + punto_anterior[0] * self.tamaño_celda + self.tamaño_celda // 2
        x2 = self.AREA_MATRIZ.left + offset_x + punto_actual[1] * self.tamaño_celda + self.tamaño_celda // 2
        y2 = self.AREA_MATRIZ.top + offset_y + punto_actual[0] * self.tamaño_celda + self.tamaño_celda // 2
        
        # Animar el retroceso con una línea roja
        pygame.draw.line(self.pantalla, self.ROJO, (x1, y1), (x2, y2), 3)
        pygame.display.flip()
        pygame.time.wait(300)  # Pequeña pausa para visualizar el retroceso

    def mostrar_estadisticas(self):
        """Muestra estadísticas en la barra lateral"""
        x = self.AREA_INFO.left + 20
        y = 20
        espaciado = 40
        
        # Mostrar agujeros negros destruidos
        if hasattr(self, 'total_agujeros_negros'):
            agujeros_destruidos = self.total_agujeros_negros - len(self.datos_nivel['agujerosNegros'])
            self.dibujar_texto(f"Agujeros Negros Destruidos: {agujeros_destruidos}", x, y)
            y += espaciado
        
        # Mostrar agujeros de gusano disponibles
        self.dibujar_texto(f"Agujeros de Gusano: {len(self.datos_nivel['agujerosGusano'])}", x, y)
