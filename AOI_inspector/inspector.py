'''
    sistema de comparación por blobs
    usando Tkinter + OpenCV
    Revisión: v1.0 2024-06-20
    Autor: Carlos Fdez

        Este script permite cargar dos imágenes, una de referencia y otra de inspección,
        seleccionar manualmente blobs circulares en la imagen de referencia, definir un
        rectángulo patrón, y luego comparar ambas imágenes basándose en la posición de los blobs
        y el contenido del rectángulo patrón. El resultado de la comparación se muestra en una ventana emergente.
        Requiere las librerías: opencv-python, numpy, Pillow, tkinter
        Instalación: pip install opencv-python numpy Pillow



'''


import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# ==========================
# FUNCIONES AUXILIARES
# ==========================

def detectar_blobs(img_gray):
    """Detecta blobs circulares en una imagen y devuelve sus coordenadas."""
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 20
    params.maxArea = 5000
    params.filterByCircularity = True
    params.minCircularity = 0.6
    params.filterByColor = False
    params.filterByConvexity = False
    params.filterByInertia = False
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(img_gray)
    pts = np.array([kp.pt for kp in keypoints], dtype=np.float32)
    return pts, keypoints

def cv2_to_tk(img_cv):
    """Convierte imagen OpenCV a formato compatible con Tkinter."""
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    return ImageTk.PhotoImage(img_pil)

# ==========================
# CLASE PRINCIPAL
# ==========================

class InspectorApp:
    def __init__(self, master):
        self.master = master
        master.title("Sistema de comparación por blobs - Tkinter + OpenCV")

        # --- variables ---
        self.img_ref = None
        self.img_test = None
        self.img_ref_disp = None
        self.img_test_disp = None
        self.localizadores = []
        self.rect_start = None
        self.rect_end = None

        # --- interfaz ---
        self.frame = tk.Frame(master)
        self.frame.pack()

        self.btn_cargar_ref = tk.Button(self.frame, text="Cargar referencia", command=self.cargar_referencia)
        self.btn_cargar_ref.grid(row=0, column=0, padx=5, pady=5)

        self.btn_cargar_test = tk.Button(self.frame, text="Cargar inspección", command=self.cargar_inspeccion)
        self.btn_cargar_test.grid(row=0, column=1, padx=5, pady=5)

        self.btn_detectar = tk.Button(self.frame, text="Comparar imágenes", command=self.comparar, state=tk.DISABLED)
        self.btn_detectar.grid(row=0, column=2, padx=5, pady=5)

        self.canvas = tk.Canvas(master, width=800, height=600, bg="gray")
        self.canvas.pack(padx=10, pady=10)

        self.status = tk.Label(master, text="Cargue las imágenes", anchor="w")
        self.status.pack(fill=tk.X)

        self.canvas.bind("<Button-1>", self.click_event)
        self.canvas.bind("<Button-3>", self.click_derecho)

    # ==========================
    # FUNCIONES DE INTERFAZ
    # ==========================

    def cargar_referencia(self):
        path = filedialog.askopenfilename(title="Seleccionar imagen de referencia")
        if not path:
            return
        self.img_ref = cv2.imread(path)
        self.mostrar_imagen(self.img_ref)
        self.status.config(text="Imagen de referencia cargada. Haga clic para definir blobs localizadores.")

    def cargar_inspeccion(self):
        path = filedialog.askopenfilename(title="Seleccionar imagen de inspección")
        if not path:
            return
        self.img_test = cv2.imread(path)
        if self.img_ref is not None:
            self.btn_detectar.config(state=tk.NORMAL)
        self.status.config(text="Imagen de inspección cargada.")

    def mostrar_imagen(self, img):
        img_resized = cv2.resize(img, (800, 600))
        self.img_ref_disp = img_resized
        self.tk_img = cv2_to_tk(img_resized)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

    def click_event(self, event):
        """Clic izquierdo para agregar localizadores."""
        if self.img_ref is None:
            return
        x, y = event.x, event.y
        self.localizadores.append((x, y))
        self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="red")
        self.status.config(text=f"Localizador agregado en ({x},{y})")

    def click_derecho(self, event):
        """Clic derecho para definir el rectángulo patrón."""
        if self.rect_start is None:
            self.rect_start = (event.x, event.y)
            self.status.config(text="Inicio del rectángulo definido. Haz clic derecho de nuevo para cerrar.")
        else:
            self.rect_end = (event.x, event.y)
            self.canvas.create_rectangle(*self.rect_start, *self.rect_end, outline="yellow", width=2)
            self.status.config(text="Rectángulo patrón definido.")

    # ==========================
    # PROCESO DE COMPARACIÓN
    # ==========================

    def comparar(self):
        if self.img_ref is None or self.img_test is None:
            messagebox.showerror("Error", "Debe cargar ambas imágenes.")
            return
        if len(self.localizadores) < 2:
            messagebox.showwarning("Aviso", "Debe seleccionar al menos 2 blobs de referencia.")
            return
        if self.rect_start is None or self.rect_end is None:
            messagebox.showwarning("Aviso", "Debe definir el rectángulo patrón.")
            return

        # Escalamos coordenadas al tamaño original
        scale_x = self.img_ref.shape[1] / 800
        scale_y = self.img_ref.shape[0] / 600
        loc_ref = np.array([[x*scale_x, y*scale_y] for (x, y) in self.localizadores], dtype=np.float32)

        # Detectar blobs en la imagen de inspección
        gray_test = cv2.cvtColor(self.img_test, cv2.COLOR_BGR2GRAY)
        pts_test, _ = detectar_blobs(gray_test)

        if len(pts_test) < len(loc_ref):
            messagebox.showerror("Error", "No se detectaron suficientes blobs en la imagen de inspección.")
            return

        # Emparejar por proximidad
        matched = []
        for p in loc_ref:
            dists = np.linalg.norm(pts_test - p, axis=1)
            idx = np.argmin(dists)
            matched.append(pts_test[idx])
        loc_test = np.array(matched, dtype=np.float32)

        # Calcular homografía
        if len(loc_ref) >= 4:
            H, _ = cv2.findHomography(loc_test, loc_ref, cv2.RANSAC)
            img_test_aligned = cv2.warpPerspective(self.img_test, H, (self.img_ref.shape[1], self.img_ref.shape[0]))
        else:
            M = cv2.estimateAffine2D(loc_test, loc_ref)[0]
            img_test_aligned = cv2.warpAffine(self.img_test, M, (self.img_ref.shape[1], self.img_ref.shape[0]))

        # Extraer ROI patrón
        x1 = int(min(self.rect_start[0], self.rect_end[0]) * scale_x)
        y1 = int(min(self.rect_start[1], self.rect_end[1]) * scale_y)
        x2 = int(max(self.rect_start[0], self.rect_end[0]) * scale_x)
        y2 = int(max(self.rect_start[1], self.rect_end[1]) * scale_y)

        roi_ref = self.img_ref[y1:y2, x1:x2]
        roi_test = img_test_aligned[y1:y2, x1:x2]

        diff = cv2.absdiff(roi_ref, roi_test)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        mean_diff = np.mean(diff_gray)

        umbral = 15
        resultado = "✅ Conforme" if mean_diff <= umbral else "❌ No conforme"
        messagebox.showinfo("Resultado", f"{resultado}\nDiferencia media: {mean_diff:.2f}")

        cv2.imshow("Diferencias", diff_gray)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


# ==========================
# EJECUCIÓN
# ==========================
if __name__ == "__main__":
    root = tk.Tk()
    app = InspectorApp(root)
    root.mainloop()
