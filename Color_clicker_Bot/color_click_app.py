import cv2
import numpy as np
import pyautogui
from PIL import Image

# === CONFIGURACIÓN ===
COLOR_OBJETIVO = (209, 128, 81)  # RGB que querés buscar
TOLERANCIA = 1  # margen de error de color (0 = exacto)
clicks_realizados = set()
clics_reales_activados = False


def capturar_pantalla():
    captura = pyautogui.screenshot()
    return np.array(captura)[:, :, ::-1]  # convierte a formato BGR (OpenCV)


def encontrar_pixeles_color(img, color_rgb, tolerancia=30):
    color_bgr = tuple(reversed(color_rgb))
    min_color = np.array([max(0, c - tolerancia) for c in color_bgr])
    max_color = np.array([min(255, c + tolerancia) for c in color_bgr])
    mascara = cv2.inRange(img, min_color, max_color)
    puntos = cv2.findNonZero(mascara)
    return puntos if puntos is not None else []


def mostrar_interfaz(img, puntos):
    global clicks_realizados, clics_reales_activados

    img_mostrar = img.copy()
    for p in puntos:
        x, y = p[0]
        cv2.circle(img_mostrar, (x, y), 4, (0, 0, 255), -1)

    ventana = "Buscador de color (ESC para salir)"
    cv2.imshow(ventana, img_mostrar)

    def click_event(event, x, y, flags, param):
        global clicks_realizados
        if event == cv2.EVENT_LBUTTONDOWN:
            for p in puntos:
                px, py = p[0]
                if abs(px - x) < 3 and abs(py - y) < 3:
                    if (px, py) not in clicks_realizados:
                        print(f"✔ Clic válido en ({px}, {py})")
                        clicks_realizados.add((px, py))
                        if clics_reales_activados:
                            pyautogui.click(px, py)
                            print("🖱 Clic real ejecutado en pantalla")
                    else:
                        print(f"⚠ Ya hiciste clic en ({px}, {py}) antes")
                    break

    cv2.setMouseCallback(ventana, click_event)

    while True:
        evento = cv2.waitKey(1) & 0xFF
        if evento == 27:  # ESC para salir
            break

    cv2.destroyAllWindows()


def main():
    global clics_reales_activados

    print("🔍 Capturando pantalla y buscando color...")
    pantalla = capturar_pantalla()
    puntos = encontrar_pixeles_color(pantalla, COLOR_OBJETIVO, TOLERANCIA)
    print(f"✅ Encontrados {len(puntos)} puntos con color {COLOR_OBJETIVO}")

    # Confirmación de clic real
    respuesta = input("¿Deseas habilitar clics reales en pantalla? (s/n): ").strip().lower()
    if respuesta == "s":
        print("⚠ Los clics reales están ACTIVADOS. Tené cuidado, afectarán tu pantalla real.")
        clics_reales_activados = True
    else:
        print("🔒 Los clics reales están DESACTIVADOS. Solo se mostrarán las coordenadas.")

    mostrar_interfaz(pantalla, puntos)


if __name__ == "__main__":
    main()

