import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import ImageGrab
import numpy as np
import re
from collections import OrderedDict
from colorspacious import cspace_convert

# ---------- Funciones de color ----------
def hex_to_lab(hex_color):
    hex_color = hex_color.lstrip("#")
    rgb = [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return cspace_convert(rgb, "sRGB1", "CIELab")

def delta_e(lab1, lab2):
    return np.linalg.norm(lab1 - lab2)

def color_mas_parecido(color_hex, paleta_guia, umbral=12):
    lab_color = hex_to_lab(color_hex)
    mejor = None
    mejor_hex = None
    menor_dist = float("inf")
    for nombre, hex_base in paleta_guia.items():
        lab_base = hex_to_lab(hex_base)
        dist = delta_e(lab_color, lab_base)
        if dist < menor_dist:
            menor_dist = dist
            mejor = nombre
            mejor_hex = hex_base
    if menor_dist <= umbral:
        return mejor, mejor_hex, menor_dist
    else:
        return None, None, menor_dist

# ---------- Overlay ----------
class Overlay(QtWidgets.QWidget):
    def __init__(self, grid_size=50, pixel_size=15, text_size=12):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.items = []
        self.pixel_size = pixel_size
        self.text_size = text_size
        self.margin = 20
        self.grid_size = grid_size
        total_size = self.grid_size * self.pixel_size + self.margin * 2
        self.setGeometry(100, 100, total_size, total_size)

    def show_items(self, items):
        self.items = items
        self.update()
        self.show()

    def paintEvent(self, event):
        if not self.items:
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setFont(QtGui.QFont("Segoe UI", self.text_size, QtGui.QFont.Bold))
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 120))

        for pt, texto, hex_color in self.items:
            rect_x = self.margin + pt.x() * self.pixel_size
            rect_y = self.margin + pt.y() * self.pixel_size
            rect = QtCore.QRect(rect_x, rect_y, self.pixel_size, self.pixel_size)

            # Pintar fondo del píxel
            painter.setBrush(QtGui.QColor(hex_color))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawRect(rect)

            # Texto centrado con contraste
            r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
            luminance = (0.299*r + 0.587*g + 0.114*b)
            text_color = QtCore.Qt.black if luminance > 186 else QtCore.Qt.white
            painter.setPen(text_color)
            painter.drawText(rect, QtCore.Qt.AlignCenter, texto)

        painter.end()

# ---------- Main Window ----------
class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pixel Art - Guía de Colores")
        self.setGeometry(200, 200, 700, 500)
        layout = QtWidgets.QVBoxLayout(self)

        self.html_input = QtWidgets.QPlainTextEdit()
        self.html_input.setPlaceholderText("Pega aquí el HTML con los botones de colores...")
        layout.addWidget(self.html_input)

        self.cargar_btn = QtWidgets.QPushButton("Cargar paleta desde HTML")
        layout.addWidget(self.cargar_btn)

        self.info_label = QtWidgets.QLabel("Presiona F8 para capturar colores ampliados alrededor del mouse")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.leyenda_label = QtWidgets.QLabel()
        self.leyenda_label.setWordWrap(True)
        self.leyenda_label.setMinimumHeight(200)
        layout.addWidget(self.leyenda_label)

        self.cargar_btn.clicked.connect(self.cargar_paleta)

        self.paleta = {}
        self.umbral = 12
        self.overlay = Overlay(grid_size=50, pixel_size=15, text_size=12)
        self.grabKeyboard()

    def cargar_paleta(self):
        html = self.html_input.toPlainText()
        if not html.strip():
            self.info_label.setText("⚠ Por favor, pega el HTML antes de cargar la paleta.")
            return

        hex_codes = re.findall(r'id="(#(?:[0-9A-Fa-f]{6}))"', html)
        if not hex_codes:
            self.info_label.setText("⚠ No se encontraron códigos hex en el HTML.")
            return

        self.paleta = {}
        for i, hexc in enumerate(hex_codes, start=1):
            key = f"1-{i}"
            self.paleta[key] = hexc

        self.info_label.setText(f"Paleta cargada con {len(self.paleta)} colores.")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F8:
            self.capturar_colores_ampliados()

    def capturar_colores_ampliados(self):
        if not self.paleta:
            self.info_label.setText("⚠ Debes cargar la paleta primero.")
            return

        cursor = QtGui.QCursor.pos()
        size = 200
        step = 10  # puedes aumentar si quieres muestrear menos densamente
        half = size // 2
        x1, y1 = cursor.x() - half, cursor.y() - half
        x2, y2 = cursor.x() + half, cursor.y() + half
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        np_img = np.array(img)[:, :, :3]

        # Extraer colores únicos con posiciones relativas (0..grid_size-1)
        unique_colors = OrderedDict()
        for y in range(0, np_img.shape[0], step):
            for x in range(0, np_img.shape[1], step):
                r, g, b = np_img[y, x]
                hex_pixel = f"#{r:02X}{g:02X}{b:02X}"
                rel_x = x * self.overlay.grid_size // np_img.shape[1]
                rel_y = y * self.overlay.grid_size // np_img.shape[0]
                if hex_pixel not in unique_colors:
                    unique_colors[hex_pixel] = []
                unique_colors[hex_pixel].append((rel_x, rel_y))

        # Calcular color más parecido y asignar número
        color_info = []
        for i, (hex_color, positions) in enumerate(unique_colors.items(), start=1):
            nombre, hex_base, dist = color_mas_parecido(hex_color, self.paleta, self.umbral)
            if nombre is None:
                nombre = "Sin coincidencia"
            color_info.append({
                "index": i,
                "hex_color": hex_color,
                "nombre": nombre,
                "dist": dist,
                "positions": positions
            })

        # Preparar lista para overlay
        items = []
        for info in color_info:
            for pos in info["positions"]:
                pt = QtCore.QPoint(pos[0], pos[1])
                items.append((pt, str(info["index"]), info["hex_color"]))

        # Mostrar overlay
        self.overlay.show_items(items)

        # Leyenda con nombres
        leyenda = "Colores detectados:\n"
        for info in color_info:
            leyenda += f"{info['index']}: {info['nombre']} ({info['hex_color']}) ΔE={info['dist']:.2f}\n"
        self.leyenda_label.setText(leyenda)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
