from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import os
import uuid # Para generar nombres únicos

print("INICIO DEL SCRIPT TESTINGS.PY") # Debug print

INSTAGRAM_USER = os.environ.get('IG_USER')
INSTAGRAM_PASS = os.environ.get('IG_PASS')

print(f"Valor de INSTAGRAM_USER al inicio: '{INSTAGRAM_USER}' (Tipo: {type(INSTAGRAM_USER)})") # Debug print
print(f"Valor de INSTAGRAM_PASS al inicio: '{INSTAGRAM_PASS}' (Tipo: {type(INSTAGRAM_PASS)})") # Debug print

SEGUIDORES_FILE = 'seguidores_messi_243.txt' # Asegúrate que este es el nombre correcto
MAX_FOLLOWS_PER_RUN = 25 # Puedes ajustar esto

# --- FUNCIONES AUXILIARES (DEFINIRLAS AQUÍ, ANTES DE QUE SE USEN) ---
def wait_for_element(driver, by, value, timeout=10):
    """Espera a que un elemento esté presente y visible."""
    try:
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )
    except TimeoutException:
        print(f"Timeout: Elemento no encontrado o no visible: {by}={value}")
        return None
    except Exception as e:
        print(f"Error en wait_for_element ({by}={value}): {repr(e)}")
        return None

def click_button_if_present(driver, by, value, timeout=5):
    """Intenta hacer clic en un botón si está presente, sin fallar si no lo está."""
    try:
        button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        button.click()
        print(f"Clickeado botón: {by}={value}")
        time.sleep(random.uniform(1,2)) # Pequeña pausa después de clickear pop-up
        return True
    except TimeoutException:
        # print(f"Botón no encontrado o no clickeable (Timeout): {by}={value}")
        return False
    except NoSuchElementException:
        # print(f"Botón no encontrado (NoSuchElement): {by}={value}")
        return False
    except Exception as e:
        print(f"Error inesperado al clickear botón {by}={value}: {repr(e)}")
        return False

# --- Lógica Principal del Bot ---
def login(driver):
    if not INSTAGRAM_USER or not INSTAGRAM_PASS: # Esta comprobación ya está en __main__, pero no hace daño aquí
        print("Error en login: Faltan credenciales IG_USER o IG_PASS.")
        return False

    driver.get('https://www.instagram.com/accounts/login/')
    print("Página de login cargada.")

    username_field = wait_for_element(driver, By.NAME, 'username', 20)
    if not username_field:
        print("Campo de usuario no encontrado.")
        driver.save_screenshot("login_username_field_not_found.png")
        return False
    username_field.send_keys(INSTAGRAM_USER)

    try:
        password_field = driver.find_element(By.NAME, 'password')
        password_field.send_keys(INSTAGRAM_PASS + Keys.ENTER)
        print("Credenciales enviadas.")
    except NoSuchElementException:
        print("Campo de contraseña no encontrado.")
        driver.save_screenshot("login_password_field_not_found.png")
        return False

    time.sleep(random.uniform(7,12))

    clicked_not_now_save_info = click_button_if_present(driver, By.XPATH, "//button[contains(text(),'Ahora no') or contains(text(),'Not now') or .//div[contains(text(),'Ahora no') or contains(text(),'Not now')]]")
    if not clicked_not_now_save_info:
        click_button_if_present(driver, By.XPATH, "//div[@role='button'][contains(.,'Ahora no') or contains(.,'Not Now')]")

    clicked_not_now_notifications = click_button_if_present(driver, By.XPATH, "//button[contains(text(),'Ahora no') or contains(text(),'Not Now')]")
    if not clicked_not_now_notifications:
        click_button_if_present(driver, By.XPATH, "//div[@role='dialog']//button[contains(.,'Ahora no') or contains(.,'Not Now')]")

    if wait_for_element(driver, By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div[2]", 20): #espera a que cargue el menu de botones
        print('Login exitoso.')
        return True
    else:
        print('Fallo en el login o no se pudo verificar el elemento post-login.')
        driver.save_screenshot("login_failed_or_verification_failed.png")
        print("Pantallazo 'login_failed_or_verification_failed.png' guardado.")
        return False

def follow_user(driver, profile_url):
    driver.get(profile_url)
    print(f"Navegando a: {profile_url}")

    if not wait_for_element(driver, By.XPATH, "//header", 20):
        print(f"Timeout: No se pudo cargar la cabecera del perfil: {profile_url}")
        driver.save_screenshot(f"profile_load_failed_{profile_url.split('/')[-1] or 'profile'}.png")
        return False

    time.sleep(random.uniform(3, 5))

    follow_button = None
    try:
        xpaths_to_try = [
            "//button[descendant-or-self::*[contains(text(),'Seguir') or contains(text(),'Follow')] and not(ancestor-or-self::*[contains(@aria-label, 'Mensaje') or contains(@aria-label, 'Message')]) and not(ancestor-or-self::*[contains(text(),'Message') or contains(text(),'Mensaje')])]",
            "//div[@role='button'][contains(.,'Seguir') or contains(.,'Follow')]",
            "//button[contains(text(),'Seguir')]",
            "//button[contains(text(),'Follow')]",
            "//div[@aria-label='Seguir']",
            "//div[@aria-label='Follow']"
        ]
        print(f"Intentando encontrar botón de seguir para {profile_url}...")
        for i, xpath in enumerate(xpaths_to_try):
            try:
                possible_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                if possible_button.is_displayed() and possible_button.is_enabled():
                    btn_text = possible_button.text.strip().lower()
                    if btn_text in ['seguir', 'follow'] or 'seguir' in btn_text or 'follow' in btn_text:
                        follow_button = possible_button
                        print(f"  Botón encontrado con XPath {i+1}: '{possible_button.text.strip()}'")
                        break
            except TimeoutException:
                continue
            except Exception as e_xpath:
                print(f"  Error probando XPath {i+1}: {repr(e_xpath)}")
                continue

        if follow_button:
            print(f"Intentando click en botón: '{follow_button.text.strip()}' para {profile_url}")
            follow_button.click()
            print(f'Seguido: {profile_url}')
            time.sleep(random.uniform(2,4))
            return True
        else:
            print(f"No se encontró botón de 'Seguir' o 'Follow' activo y visible en {profile_url} con los XPaths probados.")
            already_following_texts = ['siguiendo', 'following', 'solicitado', 'requested']
            page_text_lower = driver.page_source.lower()
            is_already_following = any(text in page_text_lower for text in already_following_texts)
            if is_already_following:
                print(f"Parece que ya se sigue o se ha solicitado seguir a {profile_url}.")
            driver.save_screenshot(f"no_follow_button_{profile_url.split('/')[-1] or 'profile'}.png")
            return False

    except Exception as e:
        print(f"Error EXCEPCIÓN al intentar seguir a {profile_url}:")
        print(f"  Tipo de error: {type(e)}")
        print(f"  Mensaje (repr): {repr(e)}")
        print(f"  Mensaje (str): {str(e)}")
        driver.save_screenshot(f"follow_error_{profile_url.split('/')[-1] or 'profile'}.png")
        return False

def remove_first_line_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if lines:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines[1:])
            print(f"Línea eliminada de {filepath}")
        else:
            print(f"Archivo {filepath} ya estaba vacío.")
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    print(f"Archivo {filepath} vacío eliminado.")
                except Exception as e_rm:
                    print(f"Error al eliminar archivo vacío {filepath}: {repr(e_rm)}")
    except FileNotFoundError:
        print(f"Archivo {filepath} no encontrado para eliminar línea.")
    except Exception as e:
        print(f"Error al procesar {filepath} para eliminar línea: {repr(e)}")

def main():
    print("Iniciando bot (dentro de main())...")
    options = webdriver.ChromeOptions()
    
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    options.add_argument("--window-size=1920,1080")

    unique_user_data_dir = f"/tmp/chrome-user-data-{uuid.uuid4()}"
    options.add_argument(f"--user-data-dir={unique_user_data_dir}")
    print(f"Usando directorio de datos de usuario único: {unique_user_data_dir}")

    driver = None
    successful_follows = 0
    try:
        driver = webdriver.Chrome(options=options)
        print("Driver de Chrome inicializado.")

        if not login(driver):
            print("Fallo en el login. Abortando ejecución de main().")
            return

        while successful_follows < MAX_FOLLOWS_PER_RUN:
            if not os.path.exists(SEGUIDORES_FILE) or os.path.getsize(SEGUIDORES_FILE) == 0:
                print(f"Archivo {SEGUIDORES_FILE} vacío o no existe. Terminando ciclo de follows.")
                break

            profile_to_follow = ""
            try:
                with open(SEGUIDORES_FILE, 'r', encoding='utf-8') as f:
                    profile_to_follow = f.readline().strip()
            except Exception as e:
                print(f"Error al leer {SEGUIDORES_FILE}: {repr(e)}")
                break

            if not profile_to_follow:
                print(f"No hay más usuarios en {SEGUIDORES_FILE} (línea leída vacía). Terminando ciclo de follows.")
                break

            print(f"\nIntentando seguir perfil: {profile_to_follow} ({successful_follows + 1}/{MAX_FOLLOWS_PER_RUN})")
            success = follow_user(driver, profile_to_follow)

            if success:
                remove_first_line_from_file(SEGUIDORES_FILE)
                successful_follows += 1
                print(f"Follow exitoso. Total seguidos en esta ejecución: {successful_follows}")
            else:
                print(f"No se pudo seguir o hubo un error con {profile_to_follow}. No se elimina de la lista por defecto.")

            sleep_duration = random.uniform(45, 120)
            print(f"Pausando por {sleep_duration:.2f} segundos...")
            time.sleep(sleep_duration)

    except Exception as e:
        print(f"Error GENERAL en la ejecución principal (main()): {repr(e)}")
        if driver:
            try:
                driver.save_screenshot("main_error_screenshot.png")
                print("Pantallazo 'main_error_screenshot.png' guardado.")
            except Exception as e_ss:
                print(f"No se pudo guardar el pantallazo del error principal: {repr(e_ss)}")
    finally:
        if driver:
            print("Cerrando driver...")
            driver.quit()
        print(f"Bot finalizado. Seguidos en esta ejecución: {successful_follows}")
        # import shutil # Descomentar si quieres limpiar el user_data_dir
        # if os.path.exists(unique_user_data_dir):
        #     try:
        #         shutil.rmtree(unique_user_data_dir)
        #         print(f"Directorio de datos de usuario {unique_user_data_dir} eliminado.")
        #     except Exception as e_rm:
        #         print(f"No se pudo eliminar {unique_user_data_dir}: {repr(e_rm)}")

if __name__ == '__main__':
    print("DENTRO DE IF __NAME__ == '__MAIN__'")
    print(f"  Verificando INSTAGRAM_USER: '{INSTAGRAM_USER}'")
    print(f"  Verificando INSTAGRAM_PASS: '{INSTAGRAM_PASS}'")

    if not INSTAGRAM_USER or not INSTAGRAM_PASS: # Comprueba si son None o string vacío
        print("CRÍTICO: Las variables de entorno IG_USER o IG_PASS no están configuradas (o son vacías) en el momento de la verificación.")
        print("Asegúrate de que los secrets en GitHub Actions tengan valores NO VACÍOS y que el workflow los pase.")
    else:
        print("Variables de entorno IG_USER e IG_PASS parecen estar seteadas con valores. Llamando a main().")
        main()
    print("FIN DE IF __NAME__ == '__MAIN__'")

print("FIN DEL SCRIPT TESTINGS.PY") # Debug print
