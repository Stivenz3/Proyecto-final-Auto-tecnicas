from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QPlainTextEdit, QFileDialog, QFrame, QTextEdit, QDialog, QRadioButton, QButtonGroup, QApplication
)
from PyQt6.QtCore import Qt, QSize, QRect
from PyQt6.QtGui import QIcon, QFont, QPainter, QColor
import os
from .afd_matricula import AFDMatricula
from .afd_placa import AFDPlaca

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        font = QFont("Consolas", 12)
        self.setFont(font)
        self.updateRequest.connect(self.update_line_number_area)
        self.textChanged.connect(self.update_line_number_area_width)
        self.update_line_number_area_width()

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.document().blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(),
                                              self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#2B2B2B"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        offset = self.contentOffset()
        top = self.blockBoundingGeometry(block).translated(offset).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#6C6C6C"))
                painter.drawText(0, int(top), self.line_number_area.width(),
                               self.fontMetrics().height(),
                               Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

class SelectorAFD(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar AFD")
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QDialog {
                background-color: #282A36;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QRadioButton {
                color: white;
                font-size: 12px;
                padding: 5px;
            }
            QPushButton {
                background-color: #44475A;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #6272A4;
            }
        """)
        
        layout = QVBoxLayout()
        titulo = QLabel("Seleccione el tipo de AFD a utilizar:")
        layout.addWidget(titulo)
        self.grupo_botones = QButtonGroup()
        self.radio_matricula = QRadioButton("Matrícula Universitaria (2023-IS-0841)")
        self.radio_matricula.setChecked(True)
        self.grupo_botones.addButton(self.radio_matricula)
        layout.addWidget(self.radio_matricula)
        self.radio_placa = QRadioButton("Placa Vehicular (ABC-1234-Q)")
        self.grupo_botones.addButton(self.radio_placa)
        layout.addWidget(self.radio_placa)
        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.clicked.connect(self.accept)
        layout.addWidget(btn_aceptar)
        self.setLayout(layout)
    
    def get_seleccion(self):
        return "matricula" if self.radio_matricula.isChecked() else "placa"

class InterfazAFD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Validador de AFDs")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #282A36;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #44475A;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #6272A4;
            }
            QTextEdit, QPlainTextEdit {
                background-color: #282A36;
                color: #F8F8F2;
                border: 1px solid #44475A;
                border-radius: 5px;
                font-family: 'Consolas';
                font-size: 14px;
                padding: 10px;
            }
        """)
        
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout = QVBoxLayout()
        widget_central.setLayout(layout)
        toolbar = QHBoxLayout()
        btn_cargar = QPushButton("  Cargar Archivo")
        btn_cargar.setIcon(QIcon("assets/icons/code.png"))
        btn_cargar.setIconSize(QSize(24, 24))
        btn_cargar.clicked.connect(self.cargar_archivo)
        toolbar.addWidget(btn_cargar)
        btn_guardar = QPushButton("  Guardar Cambios")
        btn_guardar.setIcon(QIcon("assets/icons/process.png"))
        btn_guardar.setIconSize(QSize(24, 24))
        btn_guardar.clicked.connect(self.guardar_cambios)
        toolbar.addWidget(btn_guardar)
        btn_analizar = QPushButton("  Analizar")
        btn_analizar.setIcon(QIcon("assets/icons/check.png"))
        btn_analizar.setIconSize(QSize(24, 24))
        btn_analizar.clicked.connect(self.analizar_contenido)
        toolbar.addWidget(btn_analizar)
        btn_cambiar = QPushButton("  Cambiar AFD")
        btn_cambiar.setIcon(QIcon("assets/icons/code.png"))
        btn_cambiar.setIconSize(QSize(24, 24))
        btn_cambiar.clicked.connect(self.cambiar_afd)
        toolbar.addWidget(btn_cambiar)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        self.editor = CodeEditor()
        self.editor.setPlaceholderText("El texto a validar aparecerá aquí...")
        layout.addWidget(self.editor)
        frame_resultados = QFrame()
        frame_resultados.setObjectName("resultados")
        frame_resultados.setStyleSheet("""
            #resultados {
                background-color: #44475A;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        layout_resultados = QVBoxLayout()
        frame_resultados.setLayout(layout_resultados)
        self.label_resultados = QLabel("Resultados de la Validación")
        self.label_resultados.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_resultados.addWidget(self.label_resultados)
        self.texto_resultados = QTextEdit()
        self.texto_resultados.setReadOnly(True)
        self.texto_resultados.setMinimumHeight(200)
        self.texto_resultados.setMaximumHeight(300)
        layout_resultados.addWidget(self.texto_resultados)
        frame_resultados.setMinimumHeight(250)
        frame_resultados.setMaximumHeight(350)
        layout.addWidget(frame_resultados)
        self.tipo_afd = "matricula"
        self.afd = AFDMatricula()
        self.archivo_actual = None
        
    def cargar_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo",
            "",
            "Archivos de texto (*.txt);;Todos los archivos (*.*)"
        )
        if archivo:
            try:
                self.archivo_actual = archivo
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                self.editor.setPlainText(contenido)
                self.texto_resultados.setText("Archivo cargado. Presiona 'Analizar' para validar el contenido.")
            except Exception as e:
                self.texto_resultados.setText(f"Error al cargar el archivo: {str(e)}")
    
    def analizar_contenido(self):
        if not self.editor.toPlainText().strip():
            self.texto_resultados.setText("Error: No hay contenido para analizar")
            return
        try:
            contenido = self.editor.toPlainText()
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as temp:
                temp.write(contenido)
                temp_path = temp.name
            resultados = self.afd.validar_archivo(temp_path)
            errores = [res for res in resultados if "Error" in res or "Inválido" in res]
            if errores:
                mensajes_mejorados = []
                for error in errores:
                    if "matricula" in self.tipo_afd:
                        if "formato" in error.lower():
                            error = error.replace("formato inválido", "El formato debe ser YYYY-CC-NNNN donde:\n  - YYYY: Año (4 dígitos)\n  - CC: Código de carrera (2 letras mayúsculas)\n  - NNNN: Número (4 dígitos)")
                    else:
                        if "formato" in error.lower():
                            error = error.replace("formato inválido", "El formato debe ser ABC-1234-T donde:\n  - ABC: 3 letras mayúsculas\n  - 1234: 4 dígitos\n  - T: Tipo de vehículo (1 letra mayúscula)")
                    mensajes_mejorados.append(error)
                self.texto_resultados.setText("Se encontraron los siguientes errores:\n\n" + "\n\n".join(mensajes_mejorados))
            else:
                self.texto_resultados.setText("No se encontraron errores en el contenido.")
            import os
            os.unlink(temp_path)
        except Exception as e:
            self.texto_resultados.setText(f"Error al analizar el contenido: {str(e)}")
    
    def guardar_cambios(self):
        if not self.archivo_actual:
            self.texto_resultados.setText("Error: No hay ningún archivo cargado")
            return
        try:
            contenido = self.editor.toPlainText()
            with open(self.archivo_actual, 'w', encoding='utf-8') as f:
                f.write(contenido)
            self.texto_resultados.setText("Cambios guardados con éxito.")
        except Exception as e:
            self.texto_resultados.setText(f"Error al guardar los cambios: {str(e)}")
    
    def cambiar_afd(self):
        dialogo = SelectorAFD(self)
        if dialogo.exec():
            nuevo_tipo = dialogo.get_seleccion()
            if nuevo_tipo != self.tipo_afd:
                self.tipo_afd = nuevo_tipo
                self.afd = AFDMatricula() if nuevo_tipo == "matricula" else AFDPlaca()
                self.editor.clear()
                self.texto_resultados.clear()
                self.archivo_actual = None
                tipo_texto = "matrícula universitaria" if nuevo_tipo == "matricula" else "placa vehicular"
                self.texto_resultados.setText(f"AFD cambiado a validador de {tipo_texto}")
    
    def ejecutar(self):
        dialogo = SelectorAFD(self)
        if dialogo.exec():
            self.tipo_afd = dialogo.get_seleccion()
            self.afd = AFDMatricula() if self.tipo_afd == "matricula" else AFDPlaca()
        self.show()