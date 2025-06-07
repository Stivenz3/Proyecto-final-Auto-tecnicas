import time

def encontrar_ruta(datos_nivel, x_inicial, y_inicial, x_final, y_final, energia_inicial):
    """Encuentra una ruta desde el origen hasta el destino usando backtracking"""
    filas = datos_nivel['matriz']['filas']
    columnas = datos_nivel['matriz']['columnas']
    visitados = set()
    mejor_ruta = {'camino': None, 'energia': -float('inf'), 'pasos': float('inf')}
    
    def distancia_manhattan(x1, y1, x2, y2):
        """Calcula la distancia Manhattan entre dos puntos"""
        return abs(x2 - x1) + abs(y2 - y1)
    
    def encontrar_gusanos_utiles(x, y, energia):
        """Encuentra todos los agujeros de gusano que nos acercan al destino"""
        gusanos_utiles = []
        
        for gusano in datos_nivel['agujerosGusano']:
            entrada = gusano['entrada']
            salida = gusano['salida']
            
            # Solo considerar el gusano si nos acerca al destino
            dist_actual = distancia_manhattan(x, y, x_final, y_final)
            dist_desde_salida = distancia_manhattan(salida[0], salida[1], x_final, y_final)
            
            if dist_desde_salida < dist_actual:
                # Calcular costo energético solo de entrada y salida
                costo_entrada = datos_nivel['matrizInicial'][entrada[0]][entrada[1]]
                costo_salida = datos_nivel['matrizInicial'][salida[0]][salida[1]]
                costo_total = costo_entrada + costo_salida
                
                if costo_total < energia:
                    # Calcular beneficio basado en distancia ahorrada y energía conservada
                    distancia_ahorrada = dist_actual - dist_desde_salida
                    energia_conservada = energia - costo_total
                    beneficio = distancia_ahorrada * energia_conservada
                    
                    gusanos_utiles.append({
                        'gusano': gusano,
                        'beneficio': beneficio,
                        'energia_final': energia_conservada,
                        'distancia_meta': dist_desde_salida
                    })
        
        # Ordenar por beneficio (mayor beneficio primero)
        return sorted(gusanos_utiles, key=lambda g: (-g['beneficio'], g['distancia_meta']))
    
    def es_valido(x, y):
        """Verifica si una posición es válida"""
        return (0 <= x < filas and 
                0 <= y < columnas and 
                [x, y] not in datos_nivel['agujerosNegros'] and
                [x, y] not in datos_nivel['estrellasGigantes'])
    
    def backtrack(x, y, energia, ruta_actual):
        # Si ya encontramos una ruta con más energía y menos pasos, no seguimos
        if (len(ruta_actual) > mejor_ruta['pasos'] and 
            energia <= mejor_ruta['energia']):
            return
            
        # Verificar si llegamos al destino
        if x == x_final and y == y_final:
            # Actualizar mejor ruta si:
            # 1. Tiene más energía, o
            # 2. Tiene igual energía pero menos pasos
            if (energia > mejor_ruta['energia'] or 
                (energia == mejor_ruta['energia'] and 
                 len(ruta_actual) < mejor_ruta['pasos'])):
                mejor_ruta['camino'] = ruta_actual.copy()
                mejor_ruta['energia'] = energia
                mejor_ruta['pasos'] = len(ruta_actual)
            return
            
        # SIEMPRE intentar usar agujeros de gusano primero
        gusanos_utiles = encontrar_gusanos_utiles(x, y, energia)
        for gusano_util in gusanos_utiles:
            gusano = gusano_util['gusano']
            entrada = gusano['entrada']
            salida = gusano['salida']
            
            # Si la entrada del gusano está cerca, intentar usarlo
            if distancia_manhattan(x, y, entrada[0], entrada[1]) <= 2:
                costo_entrada = datos_nivel['matrizInicial'][entrada[0]][entrada[1]]
                costo_salida = datos_nivel['matrizInicial'][salida[0]][salida[1]]
                costo_total = costo_entrada + costo_salida
                
                nueva_energia = energia - costo_total
                
                # Verificar zonas de recarga
                for recarga in datos_nivel['zonasRecarga']:
                    if entrada[:2] == recarga[:2]:
                        nueva_energia *= recarga[2]
                    elif salida[:2] == recarga[:2]:
                        nueva_energia *= recarga[2]
                
                if tuple(salida) not in visitados:
                    visitados.add(tuple(salida))
                    backtrack(salida[0], salida[1], nueva_energia, ruta_actual + [entrada, salida])
                    visitados.remove(tuple(salida))
        
        # Si no podemos usar gusanos, movernos normalmente
        # Ordenar movimientos por cercanía a la meta y menor costo de energía
        movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        movimientos_valorados = []
        
        for dx, dy in movimientos:
            nuevo_x, nuevo_y = x + dx, y + dy
            
            if es_valido(nuevo_x, nuevo_y) and (nuevo_x, nuevo_y) not in visitados:
                dist_a_meta = distancia_manhattan(nuevo_x, nuevo_y, x_final, y_final)
                costo = datos_nivel['matrizInicial'][nuevo_x][nuevo_y]
                # Priorizar movimientos que conservan energía y acercan a la meta
                valor = dist_a_meta * costo
                movimientos_valorados.append((valor, dx, dy))
        
        # Ordenar movimientos (menor valor = mejor)
        for _, dx, dy in sorted(movimientos_valorados):
            nuevo_x, nuevo_y = x + dx, y + dy
            energia_gastada = datos_nivel['matrizInicial'][nuevo_x][nuevo_y]
            nueva_energia = energia - energia_gastada
            
            # Verificar zonas de recarga
            for recarga in datos_nivel['zonasRecarga']:
                if [nuevo_x, nuevo_y] == recarga[:2]:
                    nueva_energia *= recarga[2]
            
            if nueva_energia > 0:
                visitados.add((nuevo_x, nuevo_y))
                backtrack(nuevo_x, nuevo_y, nueva_energia, ruta_actual + [[nuevo_x, nuevo_y]])
                visitados.remove((nuevo_x, nuevo_y))
    
    # Iniciar búsqueda
    visitados.add((x_inicial, y_inicial))
    backtrack(x_inicial, y_inicial, energia_inicial, [[x_inicial, y_inicial]])
    
    return mejor_ruta['camino'] if mejor_ruta['camino'] else None

class Backtracking:
    def __init__(self):
        self.mejor_ruta = None
        self.mejor_energia = float('-inf')
        self.mejor_pasos = float('inf')
        self.iteraciones = 0
        self.MAX_ITERACIONES = 10000
        self.tiempo_inicio = 0
        self.TIEMPO_MAXIMO = 5
        self.UMBRAL_ENERGIA_ALTA = 30
        self.DISTANCIA_CERCANA_META = 5
        self.ruta_encontrada = False
    
    def distancia_manhattan(self, pos1, pos2):
        return abs(pos2[0] - pos1[0]) + abs(pos2[1] - pos1[1])
    
    def es_valido(self, x, y, datos_nivel):
        return (0 <= x < datos_nivel['matriz']['filas'] and 
                0 <= y < datos_nivel['matriz']['columnas'] and 
                [x, y] not in datos_nivel['agujerosNegros'] and
                [x, y] not in datos_nivel['estrellasGigantes'])
    
    def es_alto_costo(self, x, y, datos_nivel):
        return datos_nivel['matrizInicial'][x][y] > self.UMBRAL_ENERGIA_ALTA
    
    def calcular_costo_camino(self, origen, destino, datos_nivel):
        """Calcula el costo mínimo aproximado entre dos puntos"""
        x1, y1 = origen
        x2, y2 = destino
        dist = self.distancia_manhattan(origen, destino)
        
        # Encontrar las casillas de menor costo en el camino
        min_costo = float('inf')
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if self.es_valido(x, y, datos_nivel):
                    costo = datos_nivel['matrizInicial'][x][y]
                    min_costo = min(min_costo, costo)
        
        return dist * min_costo
    
    def encontrar_mejor_camino_directo(self, pos_actual, destino, energia, datos_nivel, visitados):
        x, y = pos_actual
        destino_x, destino_y = destino
        
        # Calcular dirección hacia el destino
        dx = 1 if destino_x > x else -1 if destino_x < x else 0
        dy = 1 if destino_y > y else -1 if destino_y < y else 0
        
        mejores_movimientos = []
        
        # Intentar movimientos en orden de preferencia
        movimientos = []
        if dx != 0 and dy != 0:
            movimientos.append((dx, dy))  # Diagonal (preferido si es posible)
        if dx != 0:
            movimientos.append((dx, 0))   # Horizontal
        if dy != 0:
            movimientos.append((0, dy))   # Vertical
            
        for mdx, mdy in movimientos:
            nuevo_x, nuevo_y = x + mdx, y + mdy
            if (self.es_valido(nuevo_x, nuevo_y, datos_nivel) and 
                (nuevo_x, nuevo_y) not in visitados):
                
                costo = datos_nivel['matrizInicial'][nuevo_x][nuevo_y]
                if costo <= energia * 0.3:  # Solo considerar si el costo es razonable
                    dist_actual = self.distancia_manhattan([x, y], destino)
                    dist_nueva = self.distancia_manhattan([nuevo_x, nuevo_y], destino)
                    
                    if dist_nueva < dist_actual:  # Solo movimientos que nos acerquen
                        valor = (-dist_nueva * 5 - costo * 2)  # Priorizar distancia y bajo costo
                        mejores_movimientos.append((valor, (nuevo_x, nuevo_y)))
        
        if mejores_movimientos:
            mejores_movimientos.sort()  # Ordenar por valor (menor es mejor)
            return mejores_movimientos[0][1]
        return None
    
    def encontrar_gusanos_cercanos(self, pos_actual, destino, energia, datos_nivel, visitados):
        gusanos_utiles = []
        dist_a_meta = self.distancia_manhattan(pos_actual, destino)
        
        if dist_a_meta <= self.DISTANCIA_CERCANA_META:
            return []
        
        for gusano in datos_nivel['agujerosGusano']:
            entrada = gusano['entrada']
            salida = gusano['salida']
            
            dist_a_entrada = self.distancia_manhattan(pos_actual, entrada)
            if dist_a_entrada <= 5 and tuple(salida) not in visitados:
                dist_actual = self.distancia_manhattan(pos_actual, destino)
                dist_desde_salida = self.distancia_manhattan(salida, destino)
                
                # Calcular costo total incluyendo llegar a la entrada
                costo_camino_entrada = self.calcular_costo_camino(pos_actual, entrada, datos_nivel)
                costo_entrada = datos_nivel['matrizInicial'][entrada[0]][entrada[1]]
                costo_salida = datos_nivel['matrizInicial'][salida[0]][salida[1]]
                costo_total = costo_camino_entrada + costo_entrada + costo_salida
                
                if energia >= costo_total and dist_desde_salida < dist_actual - 3:
                    energia_restante = energia - costo_total
                    beneficio = (
                        (dist_actual - dist_desde_salida) * 10 +  # Mayor peso al ahorro de distancia
                        energia_restante * 3 +                    # Más peso a la energía conservada
                        (300 if dist_desde_salida < 5 else 0)     # Bonus extra si nos deja muy cerca
                    )
                    
                    # Penalización si hay que dar muchas vueltas para llegar a la entrada
                    if dist_a_entrada > 2:
                        beneficio -= dist_a_entrada * 50
                    
                    gusanos_utiles.append({
                        'gusano': gusano,
                        'beneficio': beneficio,
                        'dist_entrada': dist_a_entrada,
                        'dist_salida': dist_desde_salida,
                        'energia_final': energia_restante
                    })
        
        return sorted(gusanos_utiles, key=lambda x: x['beneficio'], reverse=True)
    
    def evaluar_movimiento(self, x, y, destino, energia, datos_nivel):
        if self.es_alto_costo(x, y, datos_nivel):
            return float('-inf')
        
        dist_destino = self.distancia_manhattan([x, y], destino)
        costo_casilla = datos_nivel['matrizInicial'][x][y]
        
        # Penalización base por costo energético relativo a la energía disponible
        costo_relativo = costo_casilla / energia if energia > 0 else float('inf')
        
        if dist_destino <= self.DISTANCIA_CERCANA_META:
            return (
                -dist_destino * 15 +           # Máxima prioridad a acercarse
                -costo_casilla * 5 +           # Alta penalización por costo
                -costo_relativo * 1000 +       # Penalización por costo relativo
                energia * 3                     # Bonus por energía conservada
            )
        
        valor = (
            -dist_destino * 8 +               # Alta prioridad a acercarse
            -costo_casilla * 3 +              # Penalización por costo
            -costo_relativo * 500 +           # Penalización por costo relativo
            energia * 2                        # Bonus por energía
        )
        
        # Bonus por estar cerca de una zona de recarga si la energía está baja
        if energia < 50:
            for recarga in datos_nivel['zonasRecarga']:
                dist_recarga = self.distancia_manhattan([x, y], recarga[:2])
                if dist_recarga <= 2:  # Reducido el rango para ser más directo
                    valor += (recarga[2] - 1) * 300
        
        return valor
    
    def buscar_ruta(self, datos_nivel, x, y, destino_x, destino_y, energia, visitados, ruta_actual):
        self.iteraciones += 1
        
        if self.iteraciones > self.MAX_ITERACIONES or time.time() - self.tiempo_inicio > self.TIEMPO_MAXIMO:
            return False
        
        if x == destino_x and y == destino_y:
            pasos_actuales = len(ruta_actual)
            if (self.mejor_ruta is None or 
                energia > self.mejor_energia or
                (energia == self.mejor_energia and pasos_actuales < self.mejor_pasos)):
                self.mejor_ruta = ruta_actual.copy()
                self.mejor_energia = energia
                self.mejor_pasos = pasos_actuales
                self.ruta_encontrada = True
                print(f"Nueva mejor ruta - Pasos: {pasos_actuales}, Energía: {energia}")
            return True
        
        # Si ya encontramos una ruta y esta rama usa más pasos, abandonar
        if self.ruta_encontrada and len(ruta_actual) >= self.mejor_pasos:
            return False
        
        dist_a_meta = self.distancia_manhattan([x, y], [destino_x, destino_y])
        
        # Intentar camino directo primero si estamos cerca
        if dist_a_meta <= self.DISTANCIA_CERCANA_META:
            mejor_mov = self.encontrar_mejor_camino_directo(
                [x, y], [destino_x, destino_y], energia, datos_nivel, visitados
            )
            if mejor_mov:
                nuevo_x, nuevo_y = mejor_mov
                costo = datos_nivel['matrizInicial'][nuevo_x][nuevo_y]
                nueva_energia = energia - costo
                
                if nueva_energia > 0:
                    visitados.add((nuevo_x, nuevo_y))
                    if self.buscar_ruta(datos_nivel, nuevo_x, nuevo_y,
                                      destino_x, destino_y, nueva_energia,
                                      visitados, ruta_actual + [[nuevo_x, nuevo_y]]):
                        return True
                    visitados.remove((nuevo_x, nuevo_y))
        
        # Intentar usar gusanos si no estamos cerca
        gusanos_cercanos = self.encontrar_gusanos_cercanos(
            [x, y], [destino_x, destino_y], energia, datos_nivel, visitados
        )
        
        for gusano_info in gusanos_cercanos[:2]:
            gusano = gusano_info['gusano']
            entrada = gusano['entrada']
            salida = gusano['salida']
            
            if [x, y] != entrada and gusano_info['dist_entrada'] <= 2:  # Reducido a 2 para ser más directo
                nueva_energia = energia - datos_nivel['matrizInicial'][entrada[0]][entrada[1]]
                if nueva_energia > 0:
                    if self.buscar_ruta(datos_nivel, entrada[0], entrada[1],
                                      destino_x, destino_y, nueva_energia,
                                      visitados | {tuple(entrada)},
                                      ruta_actual + [entrada]):
                        return True
            
            elif [x, y] == entrada:
                nueva_energia = gusano_info['energia_final']
                visitados.add(tuple(salida))
                if self.buscar_ruta(datos_nivel, salida[0], salida[1],
                                  destino_x, destino_y, nueva_energia,
                                  visitados, ruta_actual + [salida]):
                    return True
                visitados.remove(tuple(salida))
        
        # Movimientos normales como último recurso
        movimientos = [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
        movimientos_valorados = []
        
        for dx, dy in movimientos:
            nuevo_x = x + dx
            nuevo_y = y + dy
            
            if (self.es_valido(nuevo_x, nuevo_y, datos_nivel) and 
                (nuevo_x, nuevo_y) not in visitados):
                
                costo = datos_nivel['matrizInicial'][nuevo_x][nuevo_y]
                if costo <= energia * 0.3 or (nuevo_x == destino_x and nuevo_y == destino_y):
                    valor = self.evaluar_movimiento(nuevo_x, nuevo_y,
                                                  [destino_x, destino_y],
                                                  energia, datos_nivel)
                    if valor != float('-inf'):
                        movimientos_valorados.append((valor, dx, dy))
        
        movimientos_valorados.sort(reverse=True)
        
        for _, dx, dy in movimientos_valorados[:2]:  # Reducido a 2 mejores movimientos
            nuevo_x = x + dx
            nuevo_y = y + dy
            
            costo = datos_nivel['matrizInicial'][nuevo_x][nuevo_y]
            nueva_energia = energia - costo
            
            for recarga in datos_nivel['zonasRecarga']:
                if [nuevo_x, nuevo_y] == recarga[:2]:
                    nueva_energia *= recarga[2]
            
            if nueva_energia > 0:
                visitados.add((nuevo_x, nuevo_y))
                if self.buscar_ruta(datos_nivel, nuevo_x, nuevo_y,
                                  destino_x, destino_y, nueva_energia,
                                  visitados, ruta_actual + [[nuevo_x, nuevo_y]]):
                    return True
                visitados.remove((nuevo_x, nuevo_y))
        
        return False
    
    def iniciar_busqueda(self, datos_nivel, origen, destino, energia_inicial):
        print(f"Iniciando búsqueda - Origen: {origen}, Destino: {destino}, Energía: {energia_inicial}")
        
        self.tiempo_inicio = time.time()
        self.iteraciones = 0
        self.mejor_ruta = None
        self.mejor_energia = float('-inf')
        self.mejor_pasos = float('inf')
        self.ruta_encontrada = False
        
        visitados = {(origen[0], origen[1])}
        ruta_inicial = [origen]
        
        if self.buscar_ruta(datos_nivel, origen[0], origen[1], 
                           destino[0], destino[1], energia_inicial,
                           visitados, ruta_inicial):
            print(f"¡Ruta encontrada! Pasos: {self.mejor_pasos}, Energía final: {self.mejor_energia}")
            return self.mejor_ruta
        else:
            print("No se encontró ruta")
            return None
