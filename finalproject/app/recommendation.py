# from django.db.models import Avg
# from .models import Product, ProductReview

# def recommend_products(user=None, budget=None, min_rating=4, top_n=10):
#     related_products = []
#     best_products = []

#     # If user is authenticated, check their ratings
#     if user and user.is_authenticated:
#         user_reviews = ProductReview.objects.filter(user=user)

#         if user_reviews.exists():
#             rated_product_ids = user_reviews.values_list('product_id', flat=True)
#             rated_products = Product.objects.filter(id__in=rated_product_ids)
            
#             # Extract categories, brands, and tags of rated products
#             categories = rated_products.values_list('category', flat=True)
#             brands = rated_products.values_list('brand', flat=True)
#             tags = rated_products.values_list('tags', flat=True)

#             # Fetch related products (excluding already rated ones)
#             related_products = Product.objects.annotate(avg_rating=Avg('productreview__rating'))\
#                 .filter(avg_rating__gte=min_rating, category__in=categories, brand__in=brands)\
#                 .exclude(id__in=rated_product_ids)\
#                 .distinct()

#             # Calculate value score for related products
#             for product in related_products:
#                 product.value_score = calculate_value_score(product)

#             # Sort related products by value score
#             related_products = sorted(related_products, key=lambda x: x.value_score, reverse=True)[:top_n]

#     # General best products (highest value score)
#     products = Product.objects.annotate(avg_rating=Avg('productreview__rating')).filter(avg_rating__gte=min_rating)

#     for product in products:
#         product.value_score = calculate_value_score(product)

#     # Sort by value score and take top N best products
#     best_products = sorted(products, key=lambda x: x.value_score, reverse=True)[:top_n]

#     return related_products, best_products


# def calculate_value_score(product):
#     if product.price > 0:
#         return float(product.avg_rating or 0) / float(product.price)
#     return 0

from django.db.models import Avg, Q
from .models import Product, ProductReview, Order, OrderItem
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split

# Load data and train model
def train_model():
    reviews = ProductReview.objects.all().values("user_id", "product_id", "rating")
    df = pd.DataFrame(list(reviews))
    
    if df.empty:
        return None  # No reviews available
    
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[['user_id', 'product_id', 'rating']], reader)
    trainset, _ = train_test_split(data, test_size=0.2)
    
    model = SVD()
    model.fit(trainset)
    
    return model

# Predict recommendations
model = train_model()
def recommend_products(user=None, top_n=10):
    if not model or not user or not user.is_authenticated:
        return [], []  # Return empty lists if no model or user not logged in

    rated_products = ProductReview.objects.filter(user=user).values_list('product_id', flat=True)
    ordered_products = OrderItem.objects.filter(user=user).values_list('product', flat=True)
    
    all_past_products = set(rated_products) | set(ordered_products)
    print(all_past_products)
    all_products = Product.objects.exclude(id__in=all_past_products)  # Exclude already interacted products
    
    predictions = []
    for product in all_products:
        print(product,product.id)
        # Ensure product.id is used as an integer
        if isinstance(product.id, int):  # Check if it's an integer
            pred = model.predict(user.id, product.id).est  # Correctly use the integer id
        else:
            print(f"Skipping product {product.name} with non-integer ID.")
            continue
        predictions.append((product, pred))
    
    # Sort products by predicted rating
    recommendations = sorted(predictions, key=lambda x: x[1], reverse=True)[:top_n]
    related_products = [product for product, _ in recommendations]
    
    # Best overall products (top-rated globally)
    best_products = Product.objects.annotate(avg_rating=Avg('productreview__rating'))\
                    .filter(avg_rating__gte=4)\
                    .order_by('-avg_rating')[:top_n]
    
    return related_products, best_products
