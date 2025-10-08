import cv2
import numpy as np
import pyautogui
import time
import threading
import keyboard

COLOR_OBJETIVO = 155, 82, 73 # ejemplo: negro
TOLERANCIA = 1
detener = False


def capturar_pantalla():
    captura = pyautogui.screenshot()
    return np.array(captura)[:, :, ::-1]  # RGB → BGR


def encontrar_pixeles_color(img, color_rgb, tolerancia=30):
    color_bgr = tuple(reversed(color_rgb))
    min_color = np.array([max(0, c - tolerancia) for c in color_bgr])
    max_color = np.array([min(255, c + tolerancia) for c in color_bgr])
    mascara = cv2.inRange(img, min_color, max_color)
    puntos = cv2.findNonZero(mascara)
    return puntos if puntos is not None else []


def editar_puntos(img, puntos):
    print("🖱 Fase de edición: clic para quitar/agregar puntos. ENTER = continuar, ESC = cancelar.")
    puntos_activos = set(tuple(p[0]) for p in puntos)
    img_mostrar = img.copy()

    def actualizar_vista():
        temp = img.copy()
        for x, y in puntos_activos:
            cv2.circle(temp, (x, y), 3, (0, 0, 255), -1)
        cv2.imshow("Editor de puntos", temp)

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            punto = (x, y)
            # Buscar el punto más cercano (si hay)
            cercano = min(puntos_activos, key=lambda p: (p[0]-x)**2 + (p[1]-y)**2, default=None)
            if cercano and abs(cercano[0]-x) < 3 and abs(cercano[1]-y) < 3:
                puntos_activos.remove(cercano)
                print(f"❌ Quitado punto {cercano}")
            else:
                puntos_activos.add(punto)
                print(f"➕ Agregado punto {punto}")
            actualizar_vista()

    cv2.namedWindow("Editor de puntos")
    cv2.setMouseCallback("Editor de puntos", click_event)
    actualizar_vista()

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # ENTER
            cv2.destroyAllWindows()
            return list(puntos_activos)
        elif key == 27:  # ESC
            cv2.destroyAllWindows()
            return []


def monitor_panic():
    global detener
    keyboard.wait("esc")
    detener = True
    print("\n🛑 Botón de pánico activado.")


def ejecutar_clicks(puntos):
    global detener
    print(f"⚠ Vas a hacer clic automáticamente en {len(puntos)} puntos.")
    confirmar = input("¿Deseas continuar? (s/n): ").strip().lower()
    if confirmar != "s":
        print("❌ Cancelado por el usuario.")
        return

    print("🖱 Ejecutando clics reales en 3 segundos...")
    print("👉 Presiona ESC en cualquier momento para detener.")
    time.sleep(3)

    threading.Thread(target=monitor_panic, daemon=True).start()

    for i, (x, y) in enumerate(puntos):
        if detener:
            break
        pyautogui.click(x, y)
        print(f"✔ ({i+1}/{len(puntos)}) Clic en ({x}, {y})")
        time.sleep(0.02)

    if detener:
        print("⛔ Proceso detenido por el usuario.")
    else:
        print("✅ Todos los clics ejecutados.")


def main():
    print("🔍 Capturando pantalla...")
    pantalla = capturar_pantalla()
    puntos = encontrar_pixeles_color(pantalla, COLOR_OBJETIVO, TOLERANCIA)
    print(f"Encontrados {len(puntos)} puntos con color {COLOR_OBJETIVO}.")

    if not len(puntos):
        print("No se encontraron coincidencias.")
        return

    puntos_editados = editar_puntos(pantalla, puntos)
    if not puntos_editados:
        print("❌ Cancelado o sin puntos restantes.")
        return

    ejecutar_clicks(puntos_editados)


if __name__ == "__main__":
    main()
