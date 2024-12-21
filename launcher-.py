import os
import sys
import stat
import configparser
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QPushButton, QWidget, QMessageBox, QInputDialog
)
from PyQt5.QtGui import QPixmap

# Configuración de GitHub
REPO_OWNER = "chiveta"  # Reemplazar con tu nombre de usuario
REPO_NAME = "LauncherGears3"  # Reemplazar con el nombre del repositorio
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/tags"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}"

def remove_readonly(file_path):
    """Quitar el modo solo lectura de un archivo."""
    if os.path.exists(file_path):
        os.chmod(file_path, os.stat(file_path).st_mode | stat.S_IWRITE)

def set_readonly(file_path):
    """Restaurar el modo solo lectura de un archivo."""
    if os.path.exists(file_path):
        os.chmod(file_path, os.stat(file_path).st_mode & ~stat.S_IWRITE)

class VersionManager:
    """Gestión de versiones del script desde GitHub."""

    @staticmethod
    def obtener_versiones():
        try:
            response = requests.get(GITHUB_API_URL)
            if response.status_code == 200:
                tags = response.json()
                return [tag['name'] for tag in tags]
            else:
                QMessageBox.critical(None, "Error", f"No se pudo obtener versiones. Código: {response.status_code}")
                return []
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error al obtener versiones: {e}")
            return []

    @staticmethod
    def descargar_version(version):
        try:
            script_url = f"{RAW_BASE_URL}/{version}/launcher.py"
            response = requests.get(script_url)

            if response.status_code == 200:
                # Sobrescribir el archivo actual
                with open(__file__, 'w', encoding='utf-8') as file:
                    file.write(response.text)
                QMessageBox.information(None, "Actualización", f"Versión {version} descargada con éxito. Reinicia el programa.")
            else:
                QMessageBox.critical(None, "Error", f"No se pudo descargar la versión {version}. Código: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error al descargar la versión {version}: {e}")

class PreviewSimulator:
    def __init__(self):
        self.images = {
            "Low": {
                "FOV70": QPixmap("fov70_low.png"),
                "FOV120": QPixmap("fov120_low.png")
            },
            "Medium": {
                "FOV70": QPixmap("fov70_medium.png"),
                "FOV120": QPixmap("fov120_medium.png")
            },
            "High": {
                "FOV70": QPixmap("fov70_high.png"),
                "FOV120": QPixmap("fov120_high.png")
            },
            "Epic": {
                "FOV70": QPixmap("fov70_epic.png"),
                "FOV120": QPixmap("fov120_epic.png")
            }
        }

    def generate_preview(self, target_fov, graphics_level):
        if target_fov == 70:
            return self.images[graphics_level]["FOV70"]
        elif target_fov == 120:
            return self.images[graphics_level]["FOV120"]
        else:
            return self.images[graphics_level]["FOV70"]

class OptionsWindow(QMainWindow):
    def __init__(self, ini_paths, camera_paths):
        super().__init__()
        self.setWindowTitle("Options")
        self.setGeometry(150, 150, 1000, 600)

        self.ini_paths = ini_paths
        self.camera_paths = camera_paths
        self.configs = {"SP": configparser.ConfigParser(), "MP": configparser.ConfigParser()}
        self.load_ini_files()

        self.simulator = PreviewSimulator()

        layout = QHBoxLayout()

        # Set background image
        self.background_label = QLabel(self)
        self.set_background("bg1.png")

        # Singleplayer Options
        sp_layout = QVBoxLayout()
        sp_label = QLabel("Singleplayer Options")
        sp_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold ;")
        sp_layout.addWidget(sp_label)

        self.sp_fields = self.create_option_fields(sp_layout, "SP")
        layout.addLayout(sp_layout)

        # Multiplayer Options
        mp_layout = QVBoxLayout()
        mp_label = QLabel("Multiplayer Options")
        mp_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        mp_layout.addWidget(mp_label)

        self.mp_fields = self.create_option_fields(mp_layout, "MP")
        layout.addLayout(mp_layout)

        # Preview Area
        self.preview_label = QLabel(self)
        self.preview_label.setFixedSize(400, 300)
        self.preview_label.setStyleSheet("border: 2px solid white;")
        layout.addWidget(self.preview_label)

        # Save Button
        save_button = QPushButton("Save")
        save_button.setStyleSheet("color: white; font-size: 14px;")
        save_button.clicked.connect(self.save_all_configs)

        # Update Button
        update_button = QPushButton("Check for Updates")
        update_button.setStyleSheet("color: white; font-size: 14px;")
        update_button.clicked.connect(self.check_for_updates)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(save_button)
        main_layout.addWidget(update_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.update_preview()

    def check_for_updates(self):
        """Verificar y descargar actualizaciones disponibles."""
        versions = VersionManager.obtener_versiones()
        if versions:
            version, ok = QInputDialog.getItem(self, "Select Version", "Available Versions:", versions, 0, False)
            if ok and version:
                VersionManager.descargar_version(version)

    def load_ini_files(self):
        """Cargar archivos INI."""
        for mode, path in self.ini_paths.items():
            if os.path.exists(path):
                try:
                    config = configparser.RawConfigParser(strict=False)
                    config.read(path)
                    self.configs[mode] = config
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error al cargar el archivo {path}: {e}")

    def set_background(self, image_path):
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            self.background_label.setPixmap(pixmap)
            self.background_label.setScaledContents(True)
            self.background_label.setGeometry(self.rect())
        else:
            QMessageBox.critical(self, "Error", f"Background image '{image_path}' not found.")
            self.close()

    def resizeEvent(self, event):
        self.background_label.setGeometry(self.rect())
        super().resizeEvent(event)

    def create_option_fields(self, layout, mode):
        fields = {}
        config = self.configs[mode]

        def on_field_change():
            self.update_preview(mode)

        # Idioma
        lang_label = QLabel("Idioma:")
        lang_label.setStyleSheet("color: white;")
        lang_field = QComboBox()
        lang_field.addItems([
            "INT - Inglés", "ESM - Español (México)", "ESN - Español (España)",
            "FRA - Francés", "ITA - Italiano", "JAP - Japonés",
            "DEU - Alemán", "CHN - Chino", "CZE - Checo",
            "HUN - Húngaro", "POL - Polaco", "PTB - Portugués (Brasil)",
            "RUS - Ruso"
        ])
        lang_field.currentIndexChanged.connect(on_field_change)
        layout.addWidget(lang_label)
        layout.addWidget(lang_field)
        fields["Idioma"] = lang_field

        # Resolución
        res_label = QLabel("Resolución:")
        res_label.setStyleSheet("color: white;")
        res_field = QLineEdit("1920x1080")
        res_field.textChanged.connect(on_field_change)
        layout.addWidget(res_label)
        layout.addWidget(res_field)
        fields["Resolución"] = res_field

        # FOV
        fov_label = QLabel("FOV:")
        fov_label.setStyleSheet("color: white;")
        fov_field = QSpinBox()
        fov_field.setRange(70, 120)
        fov_field.setValue(90)
        fov_field.valueChanged.connect(on_field_change)
        layout.addWidget(fov_label)
        layout.addWidget(fov_field)
        fields["FOV"] = fov_field

        # FPS
        fps_min_label = QLabel("FPS Mínimos:")
        fps_min_label.setStyleSheet("color: white;")
        fps_min_field = QSpinBox()
        fps_min_field.setRange(5, 120)
        fps_min_field.setValue(30)
        fps_min_field.valueChanged.connect(on_field_change)
        layout.addWidget(fps_min_label)
        layout.addWidget(fps_min_field)
        fields["FPS Mínimos"] = fps_min_field

        fps_max_label = QLabel("FPS Máximos:")
        fps_max_label.setStyleSheet("color: white;")
        fps_max_field = QSpinBox()
        fps_max_field.setRange(30, 240)
        fps_max_field.setValue(120)
        fps_max_field.valueChanged.connect(on_field_change)
        layout.addWidget(fps_max_label)
        layout.addWidget(fps_max_field)
        fields["FPS Máximos"] = fps_max_field

        # Gráficos
        graphics_label = QLabel("Gráficos:")
        graphics_label.setStyleSheet("color: white;")
        graphics_field = QComboBox()
        graphics_field.addItems(["Low", "Medium", "High", "Epic"])
        graphics_field.currentIndexChanged.connect(on_field_change)
        layout.addWidget(graphics_label)
        layout.addWidget(graphics_field)
        fields["Gráficos"] = graphics_field

        return fields

    def save_all_configs(self):
        """Guardar configuraciones en los INI de forma independiente."""
        try:
            self.save_config("SP", self.sp_fields)
            self.save_config("MP", self.mp_fields)

            self.update_preview("SP")

            QMessageBox.information(self, "Guardado", "Configuraciones guardadas correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la configuración: {e}")

    def save_config(self, mode, fields):
        """Guardar configuración para un modo (SP o MP)."""
        ini_path = self.ini_paths[mode]
        camera_path = self.camera_paths[mode]

        remove_readonly(ini_path)
        remove_readonly(camera_path)

        with open(ini_path, 'r+', encoding='utf-8') as file:
            lines = file.readlines()
            file.seek(0)
            for line in lines:
                if "ResX=" in line:
                    file.write(f"ResX={fields['Resolución'].text().split('x')[0]}\n")
                elif "ResY=" in line:
                    file.write(f"ResY={fields['Resolución'].text().split('x')[1]}\n")
                elif "Language=" in line:
                    file.write(f"Language={fields['Idioma'].currentText().split(' - ')[0]}\n")
                elif "MinSmoothedFrameRate=" in line:
                    file.write(f"MinSmoothedFrameRate={fields['FPS Mínimos'].value()}\n")
                elif "MaxSmoothedFrameRate=" in line:
                    file.write(f"MaxSmoothedFrameRate={fields['FPS Máximos'].value()}\n")
                elif "GraphicsQuality=" in line:  # Asegúrate de que esta clave exista
                    file.write(f"GraphicsQuality={fields['Gráficos'].currentText()}\n")  # Guarda la calidad gráfica
                else:
                    file.write(line)
            file.truncate()

        with open(camera_path, 'r+', encoding='utf-8') as file:
            lines = file.readlines()
            file.seek(0)
            current_section = None

            for line in lines:
                if "[" in line and "]" in line:
                    current_section = line.strip()

                if current_section == "[GearGame.GameplayCam_Cover]" and "FOVAngle=" in line:
                    file.write(f"FOVAngle={fields['FOV'].value()}\n")
                elif current_section == "[GearGame.GearGameplayCameraMode]" and "FOVAngle=" in line:
                    file.write(f"FOVAngle={fields['FOV'].value()}\n")
                else:
                    file.write(line)
            file.truncate()

        set_readonly(ini_path)
        set_readonly(camera_path)

    def update_preview(self, mode="SP"):
        """Actualizar la vista previa en función del modo (SP o MP) seleccionado."""
        try:
            if mode == "SP":
                target_fov = self.sp_fields["FOV"].value()
                graphics_level = self.sp_fields["Gráficos"].currentText()
            elif mode == "MP":
                target_fov = self.mp_fields["FOV"].value()
                graphics_level = self.mp_fields["Gráficos"].currentText()

            base_image = self.simulator.images[graphics_level]["FOV120"]

            if not isinstance(base_image, QPixmap):
                print("Error: La imagen base no es un QPixmap.")
                return

            width = base_image.width()
            height = base_image.height()

            interpolation_ratio = (target_fov - 70) / 50.0
            crop_width = int(width * (1 - interpolation_ratio) / 2)
            crop_height = int(height * (1 - interpolation_ratio) / 2)

            cropped_pixmap = base_image.copy(
                crop_width, crop_height, width - 2 * crop_width, height - 2 * crop_height
            )

            self.preview_label.setPixmap(cropped_pixmap.scaled(
                self.preview_label.width(),
                self.preview_label.height()
            ))
        except Exception as e:
            print(f"Error al actualizar la vista previa: {e}")

class Launch3r(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gears of War 3 Launcher")
        self.setGeometry(100, 100, 800, 600)

        self.ini_paths = {
            "SP": r"C:/Program Files/Microsoft Games/Gears of War 3/SP/GearGame/Config/GearEngine.ini",
            "MP": r"C:/Program Files/Microsoft Games/Gears of War 3/MP/GearGame/Config/GearEngine.ini",
        }

        self.camera_paths = {
            "SP": r"C:/Program Files/Microsoft Games/Gears of War 3/SP/GearGame/Config/GearCamera.ini",
            "MP": r"C:/Program Files/Microsoft Games/Gears of War 3/MP/GearGame/Config/GearCamera.ini",
        }

        self.init_ui()

    def init_ui(self):
        self.background_label = QLabel(self)
        self.set_background("bg.png")

        layout = QVBoxLayout()

        singleplayer_button = QPushButton("Singleplayer")
        singleplayer_button.clicked.connect(self.launch_singleplayer)
        layout.addWidget(singleplayer_button)

        multiplayer_button = QPushButton("Multiplayer")
        multiplayer_button.clicked.connect(self.launch_multiplayer)
        layout.addWidget(multiplayer_button)

        options_button = QPushButton("Options")
        options_button.clicked.connect(self.open_options)
        layout.addWidget(options_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def set_background(self, image_path):
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            self.background_label.setPixmap(pixmap)
            self.background_label.setScaledContents(True)
            self.background_label.setGeometry(self.rect())
        else:
            QMessageBox.critical(self, "Error", f"Background image '{image_path}' not found.")
            sys.exit()

    def resizeEvent(self, event):
        self.background_label.setGeometry(self.rect())
        super().resizeEvent(event)

    def launch_singleplayer(self):
        exe_path = r"C:/Program Files/Microsoft Games/Gears of War 3/SP/Binaries/Win64/SP.exe"
        if os.path.exists(exe_path):
            os.system(f'"{exe_path}"')
        else:
            QMessageBox.critical(self, "Error", "Singleplayer executable not found!")

    def launch_multiplayer(self):
        exe_path = r"C:/Program Files/Microsoft Games/Gears of War 3/MP/Binaries/Win64/MP.exe"
        if os.path.exists(exe_path):
            os.system(f'"{exe_path}"')
        else:
            QMessageBox.critical(self, "Error", "Multiplayer executable not found!")

    def open_options(self):
        self.options_window = OptionsWindow(self.ini_paths, self.camera_paths)
        self.options_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = Launch3r()
    launcher.show()
    sys.exit(app.exec_())
