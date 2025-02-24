from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import os
import time
from datetime import date
from urllib.parse import unquote  # Import unquote to decode URL-encoded strings

# Data Structure Looks like 
# [{'item-name': 'Peito de Frango em Vácuo', 'item-price': '€5,99', 'date': '09/13/2024'}]

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Replace with a fixed secret key for production

# Connection string
CONNECTION_STRING = os.getenv("MONGO_URI")

def init_driver():
    # Initialize the Edge WebDriver
    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service)
    driver.maximize_window()
    return driver

# Routing to index.html
@app.route("/")
def home():
    return render_template('index.html')

@app.route("/search")
def search():
    query = request.args.get('search', '')
    
    client = MongoClient(CONNECTION_STRING)
    db = client['Preços']
    collection = db['Talho']
    
    # Use case-insensitive regex to match any part of the item name
    results = collection.find({"item-name": {"$regex": query, "$options": "i"}})

    results_list = list(results)

    return render_template('search_results.html', results=results_list)

@app.route("/item_page")
def showcase():
    # Decode the URL-encoded item_name
    item_name = unquote(request.args.get('item_name', ''))
    
    # Pass the decoded item_name to the template
    return render_template('item_page.html', item_name=item_name)

# Route to scanner.html
@app.route("/scanner")
def scanner():
    return render_template("scanner.html")

# "Routing" not really to activate script
@app.route("/run-script")
def run_script():
    try:
        driver = init_driver()
        url = "https://www.continente.pt/peixaria-e-talho/talho/"
        driver.get(url)
        
        # Accept cookies
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))).click()
        time.sleep(5)  # Wait for the page to load fully

        def click_see_more_button():
            try:
                # Find and click the "See More" button
                see_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search-view-more-products-button"))
                )
                see_more_button.click()
                time.sleep(8)  # Wait for new products to load
                return True
            except Exception as e:
                print("No more 'See More' button or failed to click:", e)
                return False
            
        # Keep clicking "See More" button until it disappears
        while click_see_more_button():
            pass  # Keep clicking until no more items are loaded

        # Now update `page_source` after clicking the "See More" button multiple times
        page_source = driver.page_source  

        # Use BeautifulSoup to parse the page source
        soup = BeautifulSoup(page_source, 'html.parser')

        today = date.today()
        data = []

        # Extract product names and prices
        product_name = soup.find_all("h2", class_="pwc-tile--description col-tile--description")
        product_prices = soup.find_all("span", class_="ct-price-formatted")

        # Append the Name and Prices to respective lists
        for name, price in zip(product_name, product_prices):
            data.append({
                "item-name": name.get_text(strip=True),
                "item-price": price.get_text(strip=True),
                "date": today.strftime('%m/%d/%Y')
            })

        driver.quit()  # Quit the browser after scraping

        # Connect to MongoDB and insert data
        client = MongoClient(CONNECTION_STRING)
        db = client['Preços']
        collection = db['Talho']

        if data:
            collection.insert_many(data)
            print("Data inserted successfully into MongoDB!")
        else:
            print("No data to insert.")

        # Return data as HTML response
        return f"{data}"

    except Exception as e:
        print("Error:", e)
        return "<h1>Error</h1><p>Unable to access the website at the moment. Please try again later.</p>"


if __name__ == "__main__":
    app.run(debug=True)

