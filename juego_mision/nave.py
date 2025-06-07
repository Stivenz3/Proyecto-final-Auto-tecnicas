class Nave:
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
