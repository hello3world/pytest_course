from src.ecommerce import Product, OrderError, process_order
from datetime import datetime
import pytest



def test_process_order():
    bananas = Product(
        name="Bananas",
        price=0.5,
        stock=100
    )
    
    processing_result = process_order(
        product=bananas,
        quantity=5,
        is_premium_user=False,
        order_time=datetime(2023, 1, 1, 12, 0, 0)
        )
    
    assert processing_result['product'] == "Bananas"
    assert processing_result['total'] == 0.5 * 5
    

def test_process_order_premium_user():
    bananas = Product(
        name="Bananas",
        price=0.5,
        stock=100
    )
    
    processing_result = process_order(
        product=bananas,
        quantity=5,
        is_premium_user=True,
        order_time=datetime(2023, 1, 1, 12, 0, 0)
        )
    
    assert processing_result['product'] == "Bananas"
    assert processing_result['total'] == (0.5 * 5) - (0.1 * 0.5 * 5)
    
def test_process_order_not_avaliable():
    bananas = Product(
        name="Bananas",
        price=0.5,
        stock=100
    )
    
    with pytest.raises(OrderError):
        process_order(
            product=bananas,
            quantity=101,
            is_premium_user=False,
            order_time=datetime(2023, 1, 1, 12, 0, 0)
            )
    