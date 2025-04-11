import unittest
import time
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import HtmlTestRunner

class MedicalWebTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        cls.driver.maximize_window()
        cls.base_url = "http://localhost/medicalweb"
        cls.screenshots_dir = "screenshots"
        cls.reports_dir = "reports"
        os.makedirs(cls.screenshots_dir, exist_ok=True)
        os.makedirs(cls.reports_dir, exist_ok=True)

    def take_screenshot(self, name):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{self.screenshots_dir}/{name}_{timestamp}.png"
        self.driver.save_screenshot(filename)
        return filename

    def safe_click(self, element):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1)
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)
    
    def test_1_agendar_cita(self):
        """Agendar Cita: Llenar y enviar formulario de cita"""
        driver = self.driver
        try:
            # Entrar a la página principal
            driver.get(f"{self.base_url}/index.php")
            self.take_screenshot("medicalweb_home")
            
            # Hacer clic en el botón "Agendar Cita"
            btn_agendar = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Agendar Cita')]"))
            )
            self.safe_click(btn_agendar)
            self.take_screenshot("antes_cita")
            
            # Llenar el formulario (lado Izquierdo)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "nombre"))
            ).send_keys("PacienteTest")
            driver.find_element(By.ID, "apellido").send_keys("Prueba")
            driver.find_element(By.ID, "email").send_keys("paciente@test.com")
            driver.find_element(By.ID, "telefono").send_keys("8095551212")
            
            # Seleccionar el tipo de identificación: "cedula"
            select_tipo = Select(driver.find_element(By.ID, "tipo_identificacion"))
            select_tipo.select_by_value("cedula")
            
            # Esperar a que aparezca el campo de cédula y llenarlo con valor aleatorio
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "cedula"))
            )
            random_cedula = str(random.randint(100000000, 999999999))
            driver.find_element(By.ID, "cedula").send_keys(random_cedula)
            
            # Lado Derecho: Seleccionar Especialidad (primera opción tras el placeholder)
            select_especialidad = Select(driver.find_element(By.ID, "especialidad"))
            select_especialidad.select_by_index(1)
            
            # Seleccionar Médico (primera opción, asumiendo que es "Juan Perez")
            select_medico = Select(driver.find_element(By.ID, "medico"))
            select_medico.select_by_index(1)
            
            # Llenar la fecha de cita (formato YYYY-MM-DD) y seleccionar hora "08:00"
            driver.find_element(By.ID, "fecha").send_keys("04-14-2025")
            select_hora = Select(driver.find_element(By.ID, "hora"))
            select_hora.select_by_index(1)
            
            # (Observaciones se dejan en blanco)
            self.take_screenshot("formulario_cita_completo")
            
            # Enviar el formulario
            submit_btn = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Agendar Cita')]"))
            )
            self.safe_click(submit_btn)
            
            # Verificar mensaje de éxito
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'cita ha sido agendada')]"))
            )
            self.take_screenshot("cita_agendada")
        
        except Exception as e:
            self.take_screenshot("error_agendar_cita")
            raise

    def test_2_iniciar_sesion(self):
        """Iniciar Sesión: Login con usuario admin y clave 123"""
        driver = self.driver
        try:
            # Volver a la página principal
            driver.get(f"{self.base_url}/index.php")
            self.take_screenshot("antes_login")
            
            # Hacer clic en el botón "Iniciar Sesión"
            btn_login = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Iniciar Sesión')]"))
            )
            self.safe_click(btn_login)
            self.take_screenshot("login_view")
            
            # Completar el formulario de login
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.NAME, "nombre_usuario"))
            ).send_keys("admin")
            driver.find_element(By.NAME, "clave").send_keys("123")
            driver.find_element(By.XPATH, "//button[contains(text(),'Ingresar')]").click()
            
            # Esperar redirección al panel (se verifica que se vea "MedicalWeb")
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'MedicalWeb')]"))
            )
            self.take_screenshot("login_exitoso")
        
        except Exception as e:
            self.take_screenshot("error_iniciar_sesion")
            raise

    def test_3a_ver_citas(self):
        """Ver Citas: Acceder a la lista de citas"""
        driver = self.driver
        try:
            # Desde el panel, hacer clic en "Ver Citas" en la sidebar
            ver_citas_link = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Ver Citas"))
            )
            self.safe_click(ver_citas_link)
            self.take_screenshot("ver_citas")
        except Exception as e:
            self.take_screenshot("error_ver_citas")
            raise

    def test_3b_editar_cita(self):
        """Editar Cita: Seleccionar y editar el primer elemento"""
        driver = self.driver
        try:
            # Seleccionar el primer enlace "Editar" de la lista de citas
            editar_links = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'btn-warning') and contains(text(),'Editar')]"))
            )
            if len(editar_links) > 0:
                self.safe_click(editar_links[0])
                self.take_screenshot("editar_cita")
                
                # En la página de edición, modificar Fecha y Hora
                fecha_input = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "fecha"))
                )
                fecha_input.clear()
                fecha_input.send_keys("2025-05-01")  # nueva fecha
                
                hora_input = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "hora"))
                )
                # En este ejemplo se asume que es un input time; si fuera un select, se usaría Select()
                hora_input.clear()
                hora_input.send_keys("13:30")
                self.take_screenshot("editar_cita_completo")
                
                # Guardar cambios
                guardar_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Guardar Cambios')]"))
                )
                self.safe_click(guardar_btn)
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Datos guardados')]"))
                )
                self.take_screenshot("cita_editada")
            else:
                raise Exception("No se encontró enlace para editar ninguna cita")
            
        except Exception as e:
            self.take_screenshot("error_editar_cita")
            raise

    def test_3c_eliminar_cita(self):
        """Eliminar Cita: Eliminar el primer elemento de la lista"""
        driver = self.driver
        try:
            # Se asume que ya se está en la lista de citas (si no, se debe navegar a "Ver Citas")
            eliminar_links = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'btn-danger') and contains(text(),'Eliminar')]"))
            )
            if len(eliminar_links) > 0:
                self.safe_click(eliminar_links[0])
                # Esperar confirmación del navegador y aceptarla
                WebDriverWait(driver, 10).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert.accept()
                self.take_screenshot("cita_eliminada")
            else:
                raise Exception("No se encontró enlace para eliminar ninguna cita")
            
        except Exception as e:
            self.take_screenshot("error_eliminar_cita")
            raise

    def test_3d_logout(self):
        """Cerrar Sesión: Hacer logout y confirmar la acción"""
        driver = self.driver
        try:
            # Hacer clic en "Cerrar Sesión"
            cerrar_link = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Cerrar Sesión"))
            )
            self.safe_click(cerrar_link)
            # Si aparece un diálogo de confirmación, aceptarlo
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            driver.switch_to.alert.accept()
            self.take_screenshot("logout_exitoso")
        except Exception as e:
            self.take_screenshot("error_logout")
            raise

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

class CustomHTMLTestRunner(HtmlTestRunner.HTMLTestRunner):
    def _exc_info_to_string(self, err, test):
        exctype, value, tb = err
        return str(value)

if __name__ == "__main__":
    unittest.main(
        testRunner=HtmlTestRunner.HTMLTestRunner(
            output='reports',
            report_title='Pruebas Automatizadas - MedicalWeb',
            report_name='TestReport',
            combine_reports=True,
            add_timestamp=True,
            verbosity=2
        )
    )