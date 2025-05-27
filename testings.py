from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import random
import os

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
    try:
        wait = WebDriverWait(driver, 10)

        # Espera a que cargue el perfil
        wait.until(EC.presence_of_element_located((By.XPATH, "//header")))

        # Mostramos todos los botones del perfil
        buttons = driver.find_elements(By.XPATH, "//button")
        for btn in buttons:
            print(f"Botón encontrado: '{btn.text.strip()}'")

        # Intentamos hacer clic al botón que diga "Seguir" o "Follow"
        for btn in buttons:
            texto = btn.text.strip().lower()
            if texto in ['seguir', 'follow']:
                btn.click()
                print(f'Seguido: {profile_url}')
                return True

        print(f"No se encontró botón de seguir visible en {profile_url}")
        return False

    except Exception as e:
        print(f'Error al seguir a {profile_url}: {e}')
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
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
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
