class AFDPlaca:
    def __init__(self):
        # Estados del autómata
        self.estados = {
            'q0': 'inicio',
            'q1': 'primera_letra',
            'q2': 'segunda_letra',
            'q3': 'tercera_letra',
            'q4': 'primer_guion',
            'q5': 'primer_digito',
            'q6': 'segundo_digito',
            'q7': 'tercer_digito',
            'q8': 'cuarto_digito',
            'q9': 'segundo_guion',
            'q10': 'letra_tipo',
            'qf': 'aceptacion'
        }
        
        self.estado_actual = 'q0'
        self.caracter_actual = 0
        
    def es_letra_mayuscula(self, char):
        return char.isalpha() and char.isupper()
        
    def es_digito(self, char):
        return char.isdigit()
        
    def procesar_caracter(self, char):
        if self.estado_actual == 'q0' and self.es_letra_mayuscula(char):
            self.estado_actual = 'q1'
        elif self.estado_actual == 'q1' and self.es_letra_mayuscula(char):
            self.estado_actual = 'q2'
        elif self.estado_actual == 'q2' and self.es_letra_mayuscula(char):
            self.estado_actual = 'q3'
        elif self.estado_actual == 'q3' and char == '-':
            self.estado_actual = 'q4'
        elif self.estado_actual == 'q4' and self.es_digito(char):
            self.estado_actual = 'q5'
        elif self.estado_actual == 'q5' and self.es_digito(char):
            self.estado_actual = 'q6'
        elif self.estado_actual == 'q6' and self.es_digito(char):
            self.estado_actual = 'q7'
        elif self.estado_actual == 'q7' and self.es_digito(char):
            self.estado_actual = 'q8'
        elif self.estado_actual == 'q8' and char == '-':
            self.estado_actual = 'q9'
        elif self.estado_actual == 'q9' and self.es_letra_mayuscula(char):
            self.estado_actual = 'qf'
        else:
            return False
        return True
        
    def validar_cadena(self, cadena):
        self.estado_actual = 'q0'
        self.caracter_actual = 0
        
        for i, char in enumerate(cadena):
            self.caracter_actual = i
            if not self.procesar_caracter(char):
                return False, i, f"Carácter inválido: {char}"
                
        return self.estado_actual == 'qf', self.caracter_actual, "La cadena no está completa"
        
    def validar_archivo(self, ruta_archivo):
        resultados = []
        try:
            with open(ruta_archivo, 'r') as f:
                for i, linea in enumerate(f, 1):
                    linea = linea.strip()
                    es_valida, pos_error, mensaje = self.validar_cadena(linea)
                    if not es_valida:
                        resultados.append(f"Error en línea {i}, posición {pos_error + 1}: {mensaje}")
                    else:
                        resultados.append(f"Línea {i}: Placa válida")
            return resultados
        except FileNotFoundError:
            return ["Error: No se encontró el archivo"]
        except Exception as e:
            return [f"Error al procesar el archivo: {str(e)}"] 