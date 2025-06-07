import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QPushButton, QLabel, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap
from juego_mision.juego import JuegoMision
from automata_sintaxis.interfaz import InterfazAFD
import pygame

class MenuPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyecto Autómatas")
        self.setFixedSize(800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 10px;
                font-size: 14px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            #titulo {
                font-size: 32px;
                font-weight: bold;
                color: #ffffff;
                margin: 20px;
            }
            #descripcion {
                font-size: 16px;
                color: #cccccc;
                margin: 10px;
            }
            #boton-juego {
                background-color: #007AFF;
            }
            #boton-juego:hover {
                background-color: #0066CC;
            }
            #boton-analizador {
                background-color: #5856D6;
            }
            #boton-analizador:hover {
                background-color: #4744CA;
            }
            #boton-salir {
                background-color: #FF3B30;
            }
            #boton-salir:hover {
                background-color: #D63429;
            }
        """)
        
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        widget_central.setLayout(layout)
        
        # Título
        titulo = QLabel("Proyecto Tecnicas y Autómatas")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Descripción
        descripcion = QLabel("Seleccione el módulo que desea ejecutar")
        descripcion.setObjectName("descripcion")
        descripcion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(descripcion)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.HLine)
        separador.setStyleSheet("background-color: #333333;")
        layout.addWidget(separador)
        
        # Botones
        btn_juego = QPushButton("  Misión Interestelar")
        btn_juego.setObjectName("boton-juego")
        btn_juego.setIcon(QIcon("assets/icons/rocket.png"))
        btn_juego.setIconSize(QSize(32, 32))
        btn_juego.clicked.connect(self.iniciar_juego)
        layout.addWidget(btn_juego)
        
        # Botón AFDs
        btn_analizador = QPushButton("  Validador AFDs")
        btn_analizador.setObjectName("boton-analizador")
        btn_analizador.setIcon(QIcon("assets/icons/code.png"))
        btn_analizador.setIconSize(QSize(32, 32))
        btn_analizador.clicked.connect(self.iniciar_analizador)
        layout.addWidget(btn_analizador)
        
        # Botón Salir
        btn_salir = QPushButton("  Salir")
        btn_salir.setObjectName("boton-salir")
        btn_salir.setIcon(QIcon("assets/icons/error.png"))
        btn_salir.setIconSize(QSize(32, 32))
        btn_salir.clicked.connect(self.salir)
        layout.addWidget(btn_salir)
        
        # Agregar espaciado al final
        layout.addStretch()

    def closeEvent(self, event):
        self.salir()
        
    def iniciar_juego(self):
        self.hide()
        self.juego = JuegoMision()
        self.juego.ejecutar()
        self.close()
        
    def iniciar_analizador(self):
        """Inicia el validador de AFDs"""
        self.hide()
        self.analizador = InterfazAFD()
        self.analizador.ejecutar()
        # No cerramos la ventana principal aquí

    def salir(self):
        """Cierra completamente la aplicación"""
        QApplication.quit()
        sys.exit(0)

    def validar_nivel(self, datos):
        # Validar mínimo de estrellas gigantes
        if len(datos['estrellasGigantes']) < 5:
            raise ValueError("El nivel debe tener al menos 5 estrellas gigantes")
        
        # Validar valores de energía
        for fila in datos['matrizInicial']:
            for valor in fila:
                if valor < 1 or valor > 10:
                    raise ValueError("Los valores de energía deben estar entre 1 y 10")

    def destruir_agujero_negro(self, pos_estrella):
        # Obtener agujeros negros adyacentes
        adyacentes = self.obtener_agujeros_negros_adyacentes(pos_estrella)
        if adyacentes:
            # Destruir solo el primer agujero negro encontrado
            self.datos_nivel['agujerosNegros'].remove(adyacentes[0])
            return True
        return False

    def usar_agujero_gusano(self, entrada, salida):
        for i, gusano in enumerate(self.datos_nivel['agujerosGusano']):
            if gusano['entrada'] == entrada and gusano['salida'] == salida:
                # Eliminar el agujero de gusano después de usarlo
                self.datos_nivel['agujerosGusano'].pop(i)
                return True
        return False

def main():
    app = QApplication(sys.argv)
    
    # Establecer fuente global
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    ventana = MenuPrincipal()
    ventana.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
