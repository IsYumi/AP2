from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_fluxo_compra_e2e():    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("http://localhost:8000/")

        driver.find_element(By.ID, "input-produto").send_keys("teclado")
        driver.find_element(By.ID, "input-cartao").send_keys("1234 5678")
        
        driver.find_element(By.ID, "btn-comprar").click()

        WebDriverWait(driver, 5).until(
            EC.text_to_be_present_in_element((By.ID, "mensagem"), "Compra aprovada")
        )

        mensagem_final = driver.find_element(By.ID, "mensagem").text
        assert "Compra aprovada" in mensagem_final

    finally:
        driver.quit()