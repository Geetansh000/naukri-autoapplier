from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from app.config import EMAIL, PWD, LOGIN_URL


def login(driver):
    driver.get("https://www.naukri.com/nlogin/login")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "usernameField"))
    ).send_keys(EMAIL)
    driver.find_element(By.ID, "passwordField").send_keys(PWD)
    driver.find_element(
        By.XPATH, "//button[contains(text(),'Login') and contains(@class,'blue-btn')]"
    ).click()

    print("✅ Login submitted...")
    WebDriverWait(driver, 15).until(EC.url_contains(LOGIN_URL))
    print("✅ Logged in successfully.")
