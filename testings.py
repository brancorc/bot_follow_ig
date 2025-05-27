from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import random
import os
import uuid

INSTAGRAM_USER = os.environ['IG_USER']
INSTAGRAM_PASS = os.environ['IG_PASS']
SEGUIDORES_FILE = 'seguidores_messi_243.txt'

def login(driver):

    driver.get('https://www.instagram.com/accounts/login/')

    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.NAME, 'username')))

    driver.find_element(By.NAME, 'username').send_keys(INSTAGRAM_USER)

    driver.find_element(By.NAME, 'password').send_keys(INSTAGRAM_PASS + Keys.ENTER)

    time.sleep(10)

    wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'/explore/')]")))

    print('Login exitoso.')

def follow_user(driver, profile_url):
    driver.get(profile_url)
    print(f"Navegando a: {profile_url}")

    # Espera a que cargue el header del perfil, indicativo de que la página ha cargado
    if not wait_for_element(driver, By.XPATH, "//header", 20): # Aumentado el timeout
        print(f"Timeout: No se pudo cargar la cabecera del perfil: {profile_url}")
        driver.save_screenshot(f"profile_load_failed_{profile_url.split('/')[-2] if profile_url.split('/')[-2] else 'profile'}.png")
        return False

    time.sleep(random.uniform(3, 5)) # Pequeña espera adicional para que todo se asiente

    follow_button = None
    try:
        # Intento 1: Selector más específico para botón "Follow" o "Seguir" (considerando variaciones comunes)
        # Este busca un botón dentro de la sección principal que no sea "Message" o "Contact"
        # y cuyo texto sea "Follow" o "Seguir".
        possible_buttons_xpath = (
            "//div[@role='main']//button[not(contains(.,'Message')) and not(contains(.,'Mensaje')) and not(contains(.,'Contact')) and not(contains(.,'Contacto'))] | "
            "//header//button[not(contains(.,'Message')) and not(contains(.,'Mensaje')) and not(contains(.,'Contact')) and not(contains(.,'Contacto'))]"
        )
        
        # Esperar a que al menos un botón candidato sea clickeable
        # WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, possible_buttons_xpath)))
        
        all_buttons_in_section = driver.find_elements(By.XPATH, possible_buttons_xpath)
        print(f"Encontrados {len(all_buttons_in_section)} botones candidatos en {profile_url}")

        for btn in all_buttons_in_section:
            try:
                btn_text = btn.text.strip().lower()
                if btn.is_displayed() and btn.is_enabled() and btn_text in ['follow', 'seguir']:
                    print(f"Botón candidato: '{btn.text.strip()}' (visible y habilitado)")
                    follow_button = btn
                    break # Encontramos nuestro botón
            except Exception as e_btn_check:
                print(f"Error al inspeccionar un botón candidato: {repr(e_btn_check)}")
                continue
        
        if follow_button:
            print(f"Botón de seguir encontrado: '{follow_button.text.strip()}' para {profile_url}. Intentando click.")
            # A veces es necesario hacer scroll para que el elemento sea clickeable
            # driver.execute_script("arguments[0].scrollIntoView(true);", follow_button)
            # time.sleep(0.5)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(follow_button)).click()
            print(f'Seguido: {profile_url}')
            time.sleep(random.uniform(2,4)) # Pausa después de seguir
            return True
        else:
            print(f"No se encontró botón de 'Seguir' o 'Follow' activo y visible en {profile_url} con los selectores probados.")
            driver.save_screenshot(f"no_follow_button_{profile_url.split('/')[-2] if profile_url.split('/')[-2] else 'profile'}.png")
            return False # No se pudo seguir

    except Exception as e:
        # Imprimir más detalles de la excepción
        print(f"Error EXCEPCIÓN al intentar seguir a {profile_url}:")
        print(f"  Tipo de error: {type(e)}")
        print(f"  Mensaje (repr): {repr(e)}") # repr(e) a veces da más info que str(e)
        print(f"  Mensaje (str): {str(e)}")
        driver.save_screenshot(f"follow_error_{profile_url.split('/')[-2] if profile_url.split('/')[-2] else 'profile'}.png")
        return False


def remove_first_line(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if len(lines) > 1:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines[1:])
    else:
        os.remove(filepath)

def main():

    options = webdriver.ChromeOptions()
    
    options.add_argument('--headless=new') # IMPORTANTE: usa el nuevo modo headless
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu') # A veces ayuda en headless
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    options.add_argument("--window-size=1920,1080")
    
    # IMPORTANTE: Especificar un directorio de datos de usuario único
    unique_user_data_dir = f"/tmp/chrome-user-data-{uuid.uuid4()}" # Necesitas 'import uuid' al inicio del script
    options.add_argument(f"--user-data-dir={unique_user_data_dir}")
    print(f"Usando directorio de datos de usuario único: {unique_user_data_dir}")
    
    driver = webdriver.Chrome(options=options)

    try:
        login(driver)

        count = 0
        while count < 25:
            if not os.path.exists(SEGUIDORES_FILE):
                print("Archivo vacío o no existe.")
                break

            with open(SEGUIDORES_FILE, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()

            if not first_line:
                print("No hay más usuarios para seguir.")
                break

            success = follow_user(driver, first_line)
            if success:
                remove_first_line(SEGUIDORES_FILE)
                count += 1
            time.sleep(random.uniform(3, 7))  # Pausa entre cada follow
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
