import numpy as np
import nibabel as nib
import os
from tkinter import filedialog, Tk
from .ui import EditorUI
from .constants import DEFAULT_BRUSH_SIZE, COLORS

class ImageEditor:
    def __init__(self):
        self._initialize_variables()
        self.ui = EditorUI(self)
        
    def _initialize_variables(self):
        """Inicializa todas las variables de instancia"""
        self.image_data = None
        self.image = None
        self.current_slice = 0
        self.mask = None
        self.drawing = False
        self.drawing_enabled = False
        self.images = []
        self.image_names = []
        self.current_image_index = 0
        self.brush_size = DEFAULT_BRUSH_SIZE
        self.current_color = 'red'  # Color por defecto
        
    def load_image(self, file_path=None):
        """Carga una imagen desde un archivo"""
        if file_path is None:
            root = Tk()
            root.withdraw()
            file_paths = filedialog.askopenfilenames(
                title="Seleccionar imágenes",
                filetypes=[
                    ("NIfTI files", "*.nii *.nii.gz"), 
                    ("Archivos guardados", "*.npy"),
                    ("All files", "*.*")
                ]
            )
            if not file_paths:
                return
        
            for file_path in file_paths:
                if file_path.endswith('.npy'):
                    self.load_saved_image(file_path)
                else:
                    self._load_single_image(file_path)
            
    def _load_single_image(self, file_path):
        """Carga una sola imagen"""
        try:
            self.image_data = nib.load(file_path)
            self.image = self.image_data.get_fdata()
            self.mask = np.zeros_like(self.image, dtype=np.uint8)
            self.current_slice = self.image.shape[2] // 2
            
            self.images.append((self.image, self.mask))
            self.image_names.append(os.path.basename(file_path))
            self.current_image_index = len(self.images) - 1
            
            self.ui.update_display()
        except Exception as e:
            print(f"Error al cargar la imagen: {str(e)}")
            
    def save_image(self):
        """Guarda la imagen con la máscara aplicada"""
        if self.image is None or self.mask is None:
            return
            
        root = Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            title="Guardar imagen editada",
            defaultextension=".npy",
            filetypes=[("NumPy files", "*.npy"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                save_data = {
                    'image': self.image,
                    'mask': self.mask,
                    'color': self.current_color
                }
                np.save(file_path, save_data)
            except Exception as e:
                print(f"Error al guardar: {str(e)}")
                
    def load_saved_image(self, file_path=None):
        """Carga una imagen previamente guardada"""
        if file_path is None:
            root = Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                title="Cargar imagen guardada",
                filetypes=[("Archivos guardados", "*.npy"), ("All files", "*.*")]
            )
            if not file_path:
                return
    
        try:
            saved_data = np.load(file_path, allow_pickle=True).item()
            self.image = saved_data['image']
            self.mask = saved_data['mask']
            self.current_color = saved_data.get('color', 'red')
        
            self.images.append((self.image, self.mask))
            self.image_names.append(os.path.basename(file_path))
            self.current_image_index = len(self.images) - 1
            self.current_slice = self.image.shape[2] // 2
        
            self.ui.update_display()
        except Exception as e:
            print(f"Error al cargar: {str(e)}")
    
    def toggle_drawing(self):
        """Activa/desactiva el modo de dibujo"""
        self.drawing_enabled = not self.drawing_enabled
        self.ui.update_drawing_button()
        self.ui.update_display()
        
    def change_slice(self, slice_num):
        """Cambia a una capa específica"""
        if self.image is not None and 0 <= slice_num < self.image.shape[2]:
            self.current_slice = slice_num
            self.ui.update_display()
            
    def clear_current_slice(self):
        """Limpia la máscara de la capa actual"""
        if self.mask is not None:
            self.mask[..., self.current_slice] = 0
            self.ui.update_display()
        
    def change_image(self, direction):
        """Cambia a la imagen anterior o siguiente"""
        if direction == 'prev' and self.current_image_index > 0:
            self.current_image_index -= 1
            self._load_current_image()
        elif direction == 'next' and self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
            self._load_current_image()
            
    def _load_current_image(self):
        """Carga la imagen actualmente seleccionada"""
        self.image, self.mask = self.images[self.current_image_index]
        self.current_slice = self.image.shape[2] // 2
        self.ui.update_display()
        
    def set_color(self, color):
        """Establece el color actual para dibujar"""
        if color in COLORS:
            self.current_color = color
            self.ui.update_display()
        
    def start(self):
        """Inicia la aplicación"""
        self.ui.show()