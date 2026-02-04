from datetime import datetime, timedelta


class Product:
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock


class OrderError(Exception):
    pass


def process_order(product: Product, quantity: int, is_premium_user: bool, order_time: datetime) -> dict:
    if quantity <= 0:
        raise OrderError("Quantity must be greater than 0")

    if quantity > product.stock:
        raise OrderError("Not enough stock available")

    total = product.price * quantity
    discount = 0

    if is_premium_user:
        discount = 0.10 * total
        total -= discount

    product.stock -= quantity

    is_expedited = order_time.hour < 15

    estimated_delivery = order_time + timedelta(days=1 if is_expedited else 3)

    return {
        "product": product.name,
        "quantity": quantity,
        "discount": round(discount, 2),
        "total": round(total, 2),
        "estimated_delivery": estimated_delivery.strftime('%Y-%m-%d'),
        "expedited": is_expedited,
    }
