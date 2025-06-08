import time
import heapq
from collections import deque

class Nave:
    """Clase para representar el estado de la nave durante la búsqueda"""
    def __init__(self, posicion_inicial, carga_inicial=200):
        self.posicion = posicion_inicial
        self.carga = carga_inicial
        self.ruta = [posicion_inicial]
        self.estrellas_usadas = set()
        self.portales_usados = set()
        
    def mover(self, nueva_posicion, gasto_energia):
        """Mueve la nave a una nueva posición y actualiza su carga"""
        if self.carga >= gasto_energia:
            self.posicion = nueva_posicion
            self.carga -= gasto_energia
            self.ruta.append(nueva_posicion)
            return True
        return False
        
    def recargar(self, multiplicador):
        """Recarga la energía de la nave"""
        self.carga *= multiplicador
        
    def usar_estrella(self, posicion_estrella):
        """Marca una estrella como usada"""
        self.estrellas_usadas.add(tuple(posicion_estrella))
        
    def usar_portal(self, portal):
        """Marca un portal como usado"""
        self.portales_usados.add(tuple(portal))
        
    def retroceder(self):
        """Retrocede un paso en la ruta"""
        if len(self.ruta) > 1:
            self.ruta.pop()
            self.posicion = self.ruta[-1]
            return True
        return False

def encontrar_ruta(datos_nivel, x_inicial, y_inicial, x_final, y_final, energia_inicial):
    """Encuentra la ruta óptima maximizando energía final"""
    filas = datos_nivel['matriz']['filas']
    columnas = datos_nivel['matriz']['columnas']
    
    def distancia_manhattan(x1, y1, x2, y2):
        return abs(x2 - x1) + abs(y2 - y1)
    
    def es_valido(x, y, agujeros_destruidos=None):
        if agujeros_destruidos is None:
            agujeros_destruidos = set()
        return (0 <= x < filas and 
                0 <= y < columnas and 
                ((x, y) not in {tuple(agujero) for agujero in datos_nivel['agujerosNegros']} or 
                 (x, y) in agujeros_destruidos))
    
    def calcular_energia_minima_necesaria(x, y):
        """Calcula energía mínima aproximada para llegar al destino"""
        distancia = distancia_manhattan(x, y, x_final, y_final)
        if distancia == 0:
            return 0
        
        min_costo = float('inf')
        for fila in datos_nivel['matrizInicial']:
            for costo in fila:
                if costo < min_costo:
                    min_costo = costo
        
        return distancia * min_costo
    
    def necesita_recarga(x, y, energia_actual):
        """Determina si realmente necesita recarga para llegar al destino"""
        energia_necesaria = calcular_energia_minima_necesaria(x, y)
        return energia_actual < energia_necesaria * 1.2
    
    def evaluar_estado(x, y, energia, pasos):
        """Evaluación simple: MAXIMIZAR energía final, luego minimizar pasos"""
        dist_a_meta = distancia_manhattan(x, y, x_final, y_final)
        
        # PRIORIDAD ABSOLUTA: Maximizar energía final
        prioridad_energia = -energia * 1000  # Volver al peso original
        
        # PRIORIDAD SECUNDARIA: Minimizar pasos
        prioridad_pasos = pasos * 100
        
        # PRIORIDAD TERCIARIA: Distancia a la meta
        prioridad_distancia = dist_a_meta * 50
        
        return prioridad_energia + prioridad_pasos + prioridad_distancia

    # Cola de prioridad simple - volver al original
    cola = []
    evaluacion_inicial = evaluar_estado(x_inicial, y_inicial, energia_inicial, 0)
    
    # Inicializar tracking de poder y agujeros
    agujeros_destruidos_inicial = set()
    estrellas_usadas_inicial = set()
    poder_inicial = False
    
    # Verificar si el origen está sobre una estrella gigante
    if [x_inicial, y_inicial] in datos_nivel['estrellasGigantes']:
        poder_inicial = True
        estrellas_usadas_inicial.add((x_inicial, y_inicial))
    
    heapq.heappush(cola, (evaluacion_inicial, 0, x_inicial, y_inicial, energia_inicial, 
                         [[x_inicial, y_inicial]], poder_inicial, agujeros_destruidos_inicial, estrellas_usadas_inicial))
    
    # Control de visitados simple pero efectivo
    visitados = set()
    visitados.add((x_inicial, y_inicial))
    
    soluciones_encontradas = []
    MAX_SOLUCIONES = 3  # Volver al original
    
    iteraciones = 0
    MAX_ITERACIONES = 50000  # Volver al original
    
    while cola and iteraciones < MAX_ITERACIONES:
        iteraciones += 1
        
        evaluacion_actual, pasos, x, y, energia, ruta, poder_disponible, agujeros_destruidos, estrellas_usadas = heapq.heappop(cola)
        
        # Si llegamos al destino
        if x == x_final and y == y_final:
            if energia > 0:
                soluciones_encontradas.append((energia, pasos, ruta))
                
                if len(soluciones_encontradas) >= MAX_SOLUCIONES:
                    break
            continue
        
        # JAMÁS permitir energía negativa o cero
        if energia <= 0:
            continue
            
        opciones_movimiento = []
        
        # NUEVA FUNCIONALIDAD: DESTRUIR AGUJERO NEGRO (si tiene poder)
        if poder_disponible:
            direcciones = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            agujeros_adyacentes = []
            
            for dx, dy in direcciones:
                adj_x, adj_y = x + dx, y + dy
                if (0 <= adj_x < filas and 0 <= adj_y < columnas and 
                    [adj_x, adj_y] in datos_nivel['agujerosNegros'] and
                    (adj_x, adj_y) not in agujeros_destruidos):
                    agujeros_adyacentes.append((adj_x, adj_y))
            
            if agujeros_adyacentes:
                # Elegir el agujero más cerca del destino
                mejor_agujero = None
                menor_distancia = float('inf')
                
                for agujero in agujeros_adyacentes:
                    dist = distancia_manhattan(agujero[0], agujero[1], x_final, y_final)
                    if dist < menor_distancia:
                        menor_distancia = dist
                        mejor_agujero = agujero
                
                if mejor_agujero:
                    agujero_x, agujero_y = mejor_agujero[0], mejor_agujero[1]
                    costo_movimiento = datos_nivel['matrizInicial'][agujero_x][agujero_y]
                    nueva_energia = energia - costo_movimiento
                    
                    if nueva_energia > 0:
                        nuevos_agujeros_destruidos = agujeros_destruidos.copy()
                        nuevos_agujeros_destruidos.add(mejor_agujero)
                        
                        evaluacion = evaluar_estado(agujero_x, agujero_y, nueva_energia, pasos + 1)
                        opciones_movimiento.append((evaluacion, pasos + 1, agujero_x, agujero_y, nueva_energia, 
                                                   False, nuevos_agujeros_destruidos, estrellas_usadas))
        
        # PRIORIDAD 1: VERIFICAR AGUJEROS DE GUSANO
        for gusano in datos_nivel['agujerosGusano']:
            entrada = gusano['entrada']
            salida = gusano['salida']
            
            if [x, y] == entrada and tuple(salida) not in visitados:
                if es_valido(salida[0], salida[1], agujeros_destruidos):
                    costo_salida = datos_nivel['matrizInicial'][salida[0]][salida[1]]
                    nueva_energia = energia - costo_salida
                    
                    if nueva_energia > 0:
                        evaluacion = evaluar_estado(salida[0], salida[1], nueva_energia, pasos + 1)
                        opciones_movimiento.append((evaluacion, pasos + 1, salida[0], salida[1], nueva_energia, 
                                                   poder_disponible, agujeros_destruidos, estrellas_usadas))
        
        # PRIORIDAD 2: MOVIMIENTOS NORMALES
        direcciones = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dx, dy in direcciones:
            nuevo_x, nuevo_y = x + dx, y + dy
            
            # Permitir revisitar SOLO si es una estrella gigante no usada (necesaria para obtener poder)
            es_estrella_no_usada = ([nuevo_x, nuevo_y] in datos_nivel['estrellasGigantes'] and 
                                   (nuevo_x, nuevo_y) not in estrellas_usadas)
            
            if (es_valido(nuevo_x, nuevo_y, agujeros_destruidos) and 
                ((nuevo_x, nuevo_y) not in visitados or es_estrella_no_usada)):
                
                costo_movimiento = datos_nivel['matrizInicial'][nuevo_x][nuevo_y]
                nueva_energia = energia - costo_movimiento
                
                if nueva_energia > 0:
                    energia_final = nueva_energia
                    
                    # Verificar recarga si es necesaria
                    for recarga in datos_nivel['zonasRecarga']:
                        if [nuevo_x, nuevo_y] == recarga[:2]:
                            if necesita_recarga(nuevo_x, nuevo_y, nueva_energia):
                                energia_final = nueva_energia * recarga[2]
                            break
                    
                    # NUEVA FUNCIONALIDAD: Verificar si obtiene poder en nueva posición
                    nuevo_poder_disponible = poder_disponible
                    nuevas_estrellas_usadas = estrellas_usadas.copy()
                    
                    if es_estrella_no_usada:
                        nuevo_poder_disponible = True
                        nuevas_estrellas_usadas.add((nuevo_x, nuevo_y))
                    
                    evaluacion = evaluar_estado(nuevo_x, nuevo_y, energia_final, pasos + 1)
                    opciones_movimiento.append((evaluacion, pasos + 1, nuevo_x, nuevo_y, energia_final, 
                                               nuevo_poder_disponible, agujeros_destruidos, nuevas_estrellas_usadas))
        
        # Agregar TODAS las opciones válidas a la cola
        for evaluacion, nuevo_pasos, nuevo_x, nuevo_y, nueva_energia, nuevo_poder, nuevos_agujeros, nuevas_estrellas in opciones_movimiento:
            heapq.heappush(cola, (evaluacion, nuevo_pasos, nuevo_x, nuevo_y, nueva_energia, 
                                 ruta + [[nuevo_x, nuevo_y]], nuevo_poder, nuevos_agujeros, nuevas_estrellas))
            visitados.add((nuevo_x, nuevo_y))
    
    if soluciones_encontradas:
        soluciones_encontradas.sort(key=lambda x: (-x[0], x[1]))
        mejor_energia, mejor_pasos, mejor_ruta = soluciones_encontradas[0]
        return mejor_ruta
    
    return None

class Backtracking:
    def __init__(self):
        self.mejor_ruta = None
        self.mejor_energia_final = float('-inf')
        self.mejor_pasos = float('inf')
        self.tiempo_inicio = 0
        self.TIEMPO_MAXIMO = 20
    
    def distancia_manhattan(self, pos1, pos2):
        return abs(pos2[0] - pos1[0]) + abs(pos2[1] - pos1[1])
    
    def es_valido(self, x, y, datos_nivel, agujeros_destruidos=None):
        if agujeros_destruidos is None:
            agujeros_destruidos = set()
        return (0 <= x < datos_nivel['matriz']['filas'] and 
                0 <= y < datos_nivel['matriz']['columnas'] and 
                ((x, y) not in {tuple(agujero) for agujero in datos_nivel['agujerosNegros']} or 
                 (x, y) in agujeros_destruidos))
    
    def calcular_energia_minima_para_destino(self, x, y, destino_x, destino_y, datos_nivel):
        distancia = self.distancia_manhattan([x, y], [destino_x, destino_y])
        if distancia == 0:
            return 0
        
        min_costo = float('inf')
        for fila in datos_nivel['matrizInicial']:
            for costo in fila:
                if costo < min_costo:
                    min_costo = costo
        
        return distancia * min_costo
    
    def necesita_usar_recarga(self, x, y, energia_actual, destino_x, destino_y, datos_nivel):
        energia_necesaria = self.calcular_energia_minima_para_destino(x, y, destino_x, destino_y, datos_nivel)
        return energia_actual < energia_necesaria * 1.3
    
    def buscar_ruta_backtracking(self, datos_nivel, x, y, destino_x, destino_y, energia, visitados, ruta_actual, poder_disponible, agujeros_destruidos, estrellas_usadas):
        if time.time() - self.tiempo_inicio > self.TIEMPO_MAXIMO:
            return False
        
        if energia <= 0:
            return False
        
        if x == destino_x and y == destino_y:
            pasos_actuales = len(ruta_actual) - 1
            
            if (self.mejor_ruta is None or 
                energia > self.mejor_energia_final or
                (energia == self.mejor_energia_final and pasos_actuales < self.mejor_pasos)):
                
                self.mejor_ruta = ruta_actual.copy()
                self.mejor_energia_final = energia
                self.mejor_pasos = pasos_actuales
            
            return True
        
        solucion_encontrada = False
        opciones = []
        
        # OPCIÓN ESPECIAL: Destruir agujero negro
        if poder_disponible:
            direcciones = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            for dx, dy in direcciones:
                adj_x, adj_y = x + dx, y + dy
                if (0 <= adj_x < datos_nivel['matriz']['filas'] and 
                    0 <= adj_y < datos_nivel['matriz']['columnas'] and 
                    [adj_x, adj_y] in datos_nivel['agujerosNegros'] and
                    (adj_x, adj_y) not in agujeros_destruidos):
                    
                    costo = datos_nivel['matrizInicial'][adj_x][adj_y]
                    nueva_energia = energia - costo
                    
                    if nueva_energia > 0:
                        nuevos_agujeros = agujeros_destruidos.copy()
                        nuevos_agujeros.add((adj_x, adj_y))
                        
                        dist_a_meta = self.distancia_manhattan([adj_x, adj_y], [destino_x, destino_y])
                        prioridad = -nueva_energia * 1000 + dist_a_meta - 1000  # Alto bonus por destruir
                        opciones.append((prioridad, 'destruir', adj_x, adj_y, nueva_energia, False, nuevos_agujeros, estrellas_usadas))
        
        # GUSANOS
        for gusano in datos_nivel['agujerosGusano']:
            entrada = gusano['entrada']
            salida = gusano['salida']
            
            if ([x, y] == entrada and 
                tuple(salida) not in visitados):
                
                if self.es_valido(salida[0], salida[1], datos_nivel, agujeros_destruidos):
                    costo = datos_nivel['matrizInicial'][salida[0]][salida[1]]
                    nueva_energia = energia - costo
                    
                    if nueva_energia > 0:
                        dist_a_meta = self.distancia_manhattan(salida, [destino_x, destino_y])
                        prioridad = -nueva_energia * 1000 + dist_a_meta - 500
                        opciones.append((prioridad, 'gusano', salida[0], salida[1], nueva_energia, poder_disponible, agujeros_destruidos, estrellas_usadas))
        
        # MOVIMIENTOS NORMALES
        direcciones = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dx, dy in direcciones:
            nuevo_x, nuevo_y = x + dx, y + dy
            
            if (self.es_valido(nuevo_x, nuevo_y, datos_nivel, agujeros_destruidos) and 
                (nuevo_x, nuevo_y) not in visitados):
                
                costo = datos_nivel['matrizInicial'][nuevo_x][nuevo_y]
                energia_despues_movimiento = energia - costo
                
                if energia_despues_movimiento > 0:
                    energia_final = energia_despues_movimiento
                    
                    # Verificar recarga
                    for recarga in datos_nivel['zonasRecarga']:
                        if [nuevo_x, nuevo_y] == recarga[:2]:
                            if self.necesita_usar_recarga(nuevo_x, nuevo_y, energia_despues_movimiento, destino_x, destino_y, datos_nivel):
                                energia_final = energia_despues_movimiento * recarga[2]
                            break
                    
                    # Verificar nuevo poder
                    nuevo_poder = poder_disponible
                    nuevas_estrellas = estrellas_usadas.copy()
                    
                    if ([nuevo_x, nuevo_y] in datos_nivel['estrellasGigantes'] and 
                        (nuevo_x, nuevo_y) not in estrellas_usadas):
                        nuevo_poder = True
                        nuevas_estrellas.add((nuevo_x, nuevo_y))
                    
                    dist_a_meta = self.distancia_manhattan([nuevo_x, nuevo_y], [destino_x, destino_y])
                    prioridad = -energia_final * 1000 + dist_a_meta
                    
                    opciones.append((prioridad, 'movimiento', nuevo_x, nuevo_y, energia_final, nuevo_poder, agujeros_destruidos, nuevas_estrellas))
        
        # Explorar opciones ordenadas
        opciones.sort()
        
        for prioridad, tipo, nuevo_x, nuevo_y, nueva_energia, nuevo_poder, nuevos_agujeros, nuevas_estrellas in opciones:
            visitados.add((nuevo_x, nuevo_y))
            
            if self.buscar_ruta_backtracking(datos_nivel, nuevo_x, nuevo_y, 
                                           destino_x, destino_y, nueva_energia,
                                           visitados, ruta_actual + [[nuevo_x, nuevo_y]], 
                                           nuevo_poder, nuevos_agujeros, nuevas_estrellas):
                solucion_encontrada = True
            
            visitados.remove((nuevo_x, nuevo_y))
        
        return solucion_encontrada
    
    def iniciar_busqueda(self, datos_nivel, origen, destino, energia_inicial):
        # Intentar A* primero
        ruta_astar = encontrar_ruta(datos_nivel, origen[0], origen[1], 
                                   destino[0], destino[1], energia_inicial)
        
        if ruta_astar:
            return ruta_astar
        
        # Backtracking como respaldo
        self.tiempo_inicio = time.time()
        self.mejor_ruta = None
        self.mejor_energia_final = float('-inf')
        self.mejor_pasos = float('inf')
        
        poder_inicial = [origen[0], origen[1]] in datos_nivel['estrellasGigantes']
        estrellas_iniciales = set()
        if poder_inicial:
            estrellas_iniciales.add((origen[0], origen[1]))
        
        visitados = {(origen[0], origen[1])}
        ruta_inicial = [origen]
        
        if self.buscar_ruta_backtracking(datos_nivel, origen[0], origen[1], 
                                       destino[0], destino[1], energia_inicial,
                                       visitados, ruta_inicial, poder_inicial, set(), estrellas_iniciales):
            return self.mejor_ruta
        else:
            return None
