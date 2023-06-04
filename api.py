from config import API_TOKEN
import requests


def add_order(link, amount, service):
    url = "http://global-smm.ru/api/v1/order/add"
    params = {
        "link": link,
        "amount": amount,
        "service": service,
        "access_token": API_TOKEN
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200 and data.get("success"):
        order_id = data["data"]["order"]
        print("Order added successfully. Order ID:", order_id)
        return True
    else:
        print("Произошла ошибка при выполнении заказа накрутки.\nСтатус код: ", data.get("error"))
