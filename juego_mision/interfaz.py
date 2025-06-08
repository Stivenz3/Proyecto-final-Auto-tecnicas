import pygame
import os

class InterfazJuego:
    """Clase responsable del manejo de la interfaz gráfica"""
    
    def __init__(self, ancho=1280, alto=720):
        pygame.init()
        
        # Dimensiones de la ventana
        self.ANCHO = ancho
        self.ALTO = alto
        self.ANCHO_BARRA_LATERAL = 300
        
        # Crear ventana
        self.pantalla = pygame.display.set_mode(
            (self.ANCHO, self.ALTO), 
            pygame.RESIZABLE | pygame.SHOWN
        )
        pygame.display.set_caption("Misión Interestelar")
        
        # Definir áreas de la interfaz
        self.AREA_MATRIZ = pygame.Rect(
            0, 0,
            self.ANCHO - self.ANCHO_BARRA_LATERAL,
            self.ALTO
        )
        
        self.AREA_INFO = pygame.Rect(
            self.ANCHO - self.ANCHO_BARRA_LATERAL, 0,
            self.ANCHO_BARRA_LATERAL,
            self.ALTO
        )
        
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
        
        # Variables de renderizado
        self.tamaño_celda = 0
        self.superficie_matriz = None
        
        # Cargar iconos
        self.iconos = self._cargar_iconos()
        
        # Crear botones
        self._crear_botones()
        
        # Leyenda
        self.leyenda = [
            ("Nave", 'nave'),
            ("Meta", 'meta'),
            ("Agujero Negro", 'agujero_negro'),
            ("Estrella Gigante", 'estrella'),
            ("Agujero de Gusano", 'gusano'),
            ("Zona de Recarga", 'recarga')
        ]
    
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
            iconos['recarga'] = pygame.image.load(os.path.join(iconos_path, "space-station.png"))
            iconos['meta'] = pygame.image.load(os.path.join(iconos_path, "goal.png"))
            
            # Redimensionar iconos
            for key in iconos:
                iconos[key] = pygame.transform.scale(iconos[key], (50, 50))
                
        except Exception as e:
            print(f"Error al cargar iconos: {str(e)}")
            # Crear círculos de colores como respaldo
            for key in ['nave', 'estrella', 'agujero_negro', 'gusano', 'recarga', 'meta']:
                superficie = pygame.Surface((48, 48), pygame.SRCALPHA)
                color = {
                    'nave': (255, 0, 0, 255),
                    'estrella': (255, 255, 0, 255),
                    'agujero_negro': (0, 0, 0, 255),
                    'gusano': (128, 0, 128, 255),
                    'recarga': (0, 255, 0, 255),
                    'meta': (255, 165, 0, 255)
                }.get(key, (255, 255, 255, 255))
                pygame.draw.circle(superficie, color, (24, 24), 20)
                iconos[key] = superficie
        
        return iconos
    
    def _crear_botones(self):
        """Crea los botones de la interfaz"""
        ancho_boton = self.ANCHO_BARRA_LATERAL - 40
        alto_boton = 50
        espacio_botones = 20
        x_botones = self.ANCHO - self.ANCHO_BARRA_LATERAL + 20
        y_botones = self.ALTO - (alto_boton + espacio_botones) * 3 - 20
        
        self.botones = [
            {
                'rect': pygame.Rect(x_botones, y_botones, ancho_boton, alto_boton),
                'texto': "Cargar Nivel",
                'color': self.VERDE,
                'color_hover': (100, 255, 100),
                'color_actual': self.VERDE,
                'accion': 'cargar_nivel'
            },
            {
                'rect': pygame.Rect(x_botones, y_botones + alto_boton + espacio_botones, ancho_boton, alto_boton),
                'texto': "Buscar Ruta",
                'color': self.AZUL,
                'color_hover': (100, 100, 255),
                'color_actual': self.AZUL,
                'accion': 'buscar_ruta'
            },
            {
                'rect': pygame.Rect(x_botones, y_botones + (alto_boton + espacio_botones) * 2, ancho_boton, alto_boton),
                'texto': "Salir",
                'color': self.ROJO,
                'color_hover': (255, 100, 100),
                'color_actual': self.ROJO,
                'accion': 'salir'
            }
        ]
    
    def dibujar_matriz(self, datos_nivel, scroll_x=0, scroll_y=0, rastro=None):
        """Dibuja la matriz del juego"""
        if not datos_nivel:
            return
            
        # Calcular tamaño de cada celda
        celda_ancho = self.AREA_MATRIZ.width // datos_nivel['matriz']['columnas']
        celda_alto = self.AREA_MATRIZ.height // datos_nivel['matriz']['filas']
        self.tamaño_celda = min(celda_ancho, celda_alto)
        
        # Centrar la matriz
        offset_x = (self.AREA_MATRIZ.width - (self.tamaño_celda * datos_nivel['matriz']['columnas'])) // 2
        offset_y = (self.AREA_MATRIZ.height - (self.tamaño_celda * datos_nivel['matriz']['filas'])) // 2
        
        # Crear superficie para la matriz si no existe
        if self.superficie_matriz is None:
            ancho_matriz = datos_nivel['matriz']['columnas'] * self.tamaño_celda
            alto_matriz = datos_nivel['matriz']['filas'] * self.tamaño_celda
            self.superficie_matriz = pygame.Surface((ancho_matriz, alto_matriz))
            
            # Dibujar celdas
            self.superficie_matriz.fill(self.NEGRO)
            for i in range(datos_nivel['matriz']['filas']):
                for j in range(datos_nivel['matriz']['columnas']):
                    x = j * self.tamaño_celda
                    y = i * self.tamaño_celda
                    rect = pygame.Rect(x, y, self.tamaño_celda - 1, self.tamaño_celda - 1)
                    
                    # Dibujar celda
                    pygame.draw.rect(self.superficie_matriz, self.GRIS_CLARO, rect, 1)
                    
                    # Dibujar valor de energía
                    valor = datos_nivel['matrizInicial'][i][j]
                    fuente = pygame.font.Font(None, int(self.tamaño_celda * 0.8))
                    texto = fuente.render(str(valor), True, self.BLANCO)
                    rect_texto = texto.get_rect(center=(x + self.tamaño_celda//2, y + self.tamaño_celda//2))
                    self.superficie_matriz.blit(texto, rect_texto)
                    
                    # Dibujar icono si corresponde
                    tipo = self._obtener_tipo_celda(i, j, datos_nivel)
                    if tipo:
                        icono = pygame.transform.scale(
                            self.iconos[tipo], 
                            (int(self.tamaño_celda * 0.8), int(self.tamaño_celda * 0.8))
                        )
                        rect_icono = icono.get_rect(center=(x + self.tamaño_celda//2, y + self.tamaño_celda//2))
                        self.superficie_matriz.blit(icono, rect_icono)
        
        # Dibujar la matriz centrada
        pos_x = self.AREA_MATRIZ.left + offset_x + scroll_x
        pos_y = self.AREA_MATRIZ.top + offset_y + scroll_y
        self.pantalla.blit(self.superficie_matriz, (pos_x, pos_y))
        
        # Dibujar borde del área de la matriz
        pygame.draw.rect(self.pantalla, self.BLANCO, self.AREA_MATRIZ, 2)
        
        # Dibujar rastro si existe
        if rastro:
            self._dibujar_rastro(rastro, offset_x, offset_y, scroll_x, scroll_y, datos_nivel)
    
    def _dibujar_rastro(self, rastro, offset_x, offset_y, scroll_x, scroll_y, datos_nivel):
        """Dibuja el rastro de la nave"""
        for j in range(len(rastro) - 1):
            p1 = rastro[j]
            p2 = rastro[j + 1]
            
            # Calcular coordenadas en pantalla
            x1 = self.AREA_MATRIZ.left + offset_x + p1[1] * self.tamaño_celda + self.tamaño_celda // 2
            y1 = self.AREA_MATRIZ.top + offset_y + p1[0] * self.tamaño_celda + self.tamaño_celda // 2
            x2 = self.AREA_MATRIZ.left + offset_x + p2[1] * self.tamaño_celda + self.tamaño_celda // 2
            y2 = self.AREA_MATRIZ.top + offset_y + p2[0] * self.tamaño_celda + self.tamaño_celda // 2
            
            # Dibujar línea continua
            pygame.draw.line(self.pantalla, self.VERDE, (x1, y1), (x2, y2), 3)
            
            # Verificar si es un teletransporte
            for gusano in datos_nivel['agujerosGusano']:
                if p1 == gusano['entrada'] and p2 == gusano['salida']:
                    # Efectos de teletransporte
                    radio = self.tamaño_celda // 2
                    pygame.draw.circle(self.pantalla, self.MORADO, (x1, y1), radio + 4, 2)
                    pygame.draw.circle(self.pantalla, self.MORADO, (x2, y2), radio + 4, 2)
    
    def _obtener_tipo_celda(self, x, y, datos_nivel):
        """Determina el tipo de celda en las coordenadas dadas"""
        if [x, y] == datos_nivel['origen']:
            return 'nave'
        if [x, y] == datos_nivel['destino']:
            return 'meta'
        if [x, y] in datos_nivel['agujerosNegros']:
            return 'agujero_negro'
        if [x, y] in datos_nivel['estrellasGigantes']:
            return 'estrella'
        for gusano in datos_nivel['agujerosGusano']:
            if [x, y] in [gusano['entrada'], gusano['salida']]:
                return 'gusano'
        for recarga in datos_nivel['zonasRecarga']:
            if [x, y] == recarga[:2]:
                return 'recarga'
        return None
    
    def dibujar_barra_lateral(self, datos_juego, mensaje="", mensaje_color=None):
        """Dibuja la barra lateral con información"""
        if mensaje_color is None:
            mensaje_color = self.BLANCO
            
        # Dibujar fondo de la barra lateral
        pygame.draw.rect(self.pantalla, (40, 40, 40), self.AREA_INFO)
        pygame.draw.rect(self.pantalla, self.BLANCO, self.AREA_INFO, 2)
        
        # Posición inicial para la información
        x = self.AREA_INFO.left + 20
        y = 20
        espaciado = 40
        
        # Mostrar información del juego
        if datos_juego:
            self._dibujar_texto(f"Energía: {datos_juego.get('energia', 0)}", x, y)
            y += espaciado
            
            self._dibujar_texto(f"Pasos: {datos_juego.get('pasos', 0)}", x, y)
            y += espaciado
            
            # Mostrar mensaje
            if mensaje:
                self._dibujar_texto_multilinea(mensaje, x, y, mensaje_color, 24)
                y += 100
        
        # Dibujar leyenda
        self._dibujar_leyenda(x, y)
        
        # Dibujar botones
        for boton in self.botones:
            self._dibujar_boton(boton)
    
    def _dibujar_texto(self, texto, x, y, color=None, tamaño=36):
        """Dibuja texto en la pantalla"""
        if color is None:
            color = self.BLANCO
        fuente = pygame.font.Font(None, tamaño)
        superficie = fuente.render(texto, True, color)
        self.pantalla.blit(superficie, (x, y))
    
    def _dibujar_texto_multilinea(self, texto, x, y, color, tamaño):
        """Dibuja texto en múltiples líneas"""
        palabras = texto.split()
        lineas = []
        linea_actual = []
        ancho_max = self.ANCHO_BARRA_LATERAL - 40
        
        for palabra in palabras:
            linea_actual.append(palabra)
            texto_prueba = ' '.join(linea_actual)
            fuente = pygame.font.Font(None, tamaño)
            if fuente.size(texto_prueba)[0] > ancho_max:
                linea_actual.pop()
                lineas.append(' '.join(linea_actual))
                linea_actual = [palabra]
        
        if linea_actual:
            lineas.append(' '.join(linea_actual))
        
        for linea in lineas:
            self._dibujar_texto(linea, x, y, color, tamaño)
            y += 30
    
    def _dibujar_leyenda(self, x, y):
        """Dibuja la leyenda del juego"""
        self._dibujar_texto("Leyenda:", x, y, self.BLANCO, 28)
        y += 35
        
        for nombre, clave in self.leyenda:
            icono = pygame.transform.scale(self.iconos[clave], (24, 24))
            rect_icono = icono.get_rect(topleft=(x, y))
            self.pantalla.blit(icono, rect_icono)
            self._dibujar_texto(nombre, x + 35, y + 5, self.BLANCO, 24)
            y += 35
    
    def _dibujar_boton(self, boton):
        """Dibuja un botón en la pantalla"""
        pygame.draw.rect(self.pantalla, boton['color_actual'], boton['rect'])
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
    
    def verificar_click_boton(self, pos_mouse):
        """Verifica si se hizo click en algún botón y retorna la acción"""
        for boton in self.botones:
            if boton['rect'].collidepoint(pos_mouse):
                return boton['accion']
        return None
    
    def limpiar_pantalla(self):
        """Limpia la pantalla"""
        self.pantalla.fill((30, 30, 30))
    
    def actualizar_pantalla(self):
        """Actualiza la pantalla"""
        pygame.display.flip()
    
    def resetear_matriz(self):
        """Resetea la superficie de la matriz para forzar redibujado"""
        self.superficie_matriz = None 