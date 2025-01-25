from django.db.models import Avg

def recommend_products(user=None, budget=None, min_rating=4, top_n=10):
    from .models import Product

    # Annotate products with average rating
    products = Product.objects.annotate(avg_rating=Avg('productreview__rating')).filter(avg_rating__gte=min_rating)

    # Iterate over individual product objects to calculate value score
    recommended_products = []
    for product in products:
        product.value_score = calculate_value_score(product)  # Make sure calculate_value_score uses product.price
        recommended_products.append(product)

    # Sort by value_score
    recommended_products = sorted(recommended_products, key=lambda x: x.value_score, reverse=True)[:top_n]

    return recommended_products


def calculate_value_score(product):
    if product.price > 0:  # Avoid division by zero
        return float(product.avg_rating) / float(product.price)
    return 0


