# Copyright 2024 DataRobot, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import time
from typing import Optional

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.e2e.utils import str_to_bool

username = os.environ.get("APP_USERNAME", "")
password = os.environ.get("APP_PASSWORD", "")
app_id = os.environ.get("APP_ID", "")
host = os.environ.get("DR_HOST", "").rstrip("/")
app_url = os.environ.get("APP_URL", None)

# Define the login URL and the URL to test after login
login_url = f"{host}/sign-in"

if not app_url:
    app_url = f"{host}/custom_applications/{app_id}/"


run_visual = str_to_bool(os.environ.get("RUN_VISUAL", "True"))

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def browser() -> webdriver.Chrome:  # type: ignore
    options = Options()

    if not run_visual:
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--disable-gpu")
        options.add_argument(
            "--no-sandbox"
        )  # it is important to run selenium with chrome into docker.
    driver = webdriver.Chrome(options=options)

    yield driver

    # Teardown
    # driver.quit()


# ficture of APP_URL
@pytest.fixture(scope="session")
def get_app_url() -> Optional[str]:
    return app_url


@pytest.fixture(scope="session")
def check_if_logged_in(browser: webdriver.Chrome) -> bool:
    # Check if the browser is currently on the HOST page (check if it contains HOST in the URL)
    if host in browser.current_url:
        # Check if local storage contains apc_user_id
        try:
            apc_user_id: Optional[str] = browser.execute_script(
                "return localStorage.getItem('apc_user_id')"
            )  # type: ignore
            if apc_user_id:
                return True
        except Exception as e:
            logger.error(f"Error accessing localStorage: {e}")

    # Open the login URL
    browser.get(login_url)

    # Wait for the username field to be present
    # Wait for the username field to be present using different possible selectors
    selectors = [
        (By.ID, "signInInputUsername"),
        (By.NAME, "email"),
        (By.CSS_SELECTOR, "[test-id='signInInputUsername']"),
    ]

    for by, value in selectors:
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((by, value))
            )
            break
        except Exception:
            continue
    else:
        raise Exception("Username field not found using any of the provided selectors")

    # Perform login
    # Find the username and password fields and enter the credentials
    # Try to find the username and password fields using different possible selectors
    username_selectors = [
        (By.ID, "signInInputUsername"),
        (By.NAME, "email"),
        (By.CSS_SELECTOR, "[test-id='signInInputUsername']"),
    ]
    password_selectors = [
        (By.ID, "signInInputPassword"),
        (By.NAME, "password"),
        (By.CSS_SELECTOR, "[test-id='signInInputPassword']"),
    ]

    for by, value in username_selectors:
        try:
            username_field = browser.find_element(by, value)
            break
        except Exception:
            continue
    else:
        raise Exception("Username field not found using any of the provided selectors")

    for by, value in password_selectors:
        try:
            password_field = browser.find_element(by, value)
            break
        except Exception:
            continue
    else:
        raise Exception("Password field not found using any of the provided selectors")
    username_field.send_keys(username)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)

    # Wait for the page to load after login
    # glitchy login page, need to wait a bit longer
    time.sleep(10)
    # refresh then wait again
    browser.get(host)
    time.sleep(10)
    # Check if login was successful by checking localStorage again
    try:
        apc_user_id = browser.execute_script(
            "return localStorage.getItem('apc_user_id')"
        )  # type: ignore
        if apc_user_id:
            return True
    except Exception as e:
        logger.error(f"Error accessing localStorage after login: {e}")

    return False
