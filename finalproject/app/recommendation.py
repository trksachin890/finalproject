
from django.db.models import Avg, Q
from .models import Product, ProductReview, Order, OrderItem
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from django.db.models import Avg, Count, Q
from .models import Product, ProductReview, OrderItem

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
    # Compute top products based on high ratings and high order count
    top_products = Product.objects.annotate(
        avg_rating=Avg('productreview__rating'),
        order_count=Count('orderitem')
    ).filter(avg_rating__gte=4).order_by('-order_count', '-avg_rating')[:top_n]
    
    # If the user is authenticated, personalize recommendations
    related_products = []
    if user and user.is_authenticated:
        user_rated_products = ProductReview.objects.filter(user=user).values_list('product_id', flat=True)
        user_ordered_products = OrderItem.objects.filter(user=user).values_list('product_id', flat=True)
        user_interacted_products = set(user_rated_products) | set(user_ordered_products)
        
        # Extract preferences from user interactions
        user_categories = Product.objects.filter(id__in=user_interacted_products).values_list('category', flat=True)
        user_brands = Product.objects.filter(id__in=user_interacted_products).values_list('brand', flat=True)
        
        # Fetch related products based on category and brand, excluding already interacted products
        related_products = Product.objects.annotate(
            avg_rating=Avg('productreview__rating'),
            order_count=Count('orderitem')
        ).filter(
            Q(category__in=user_categories) | Q(brand__in=user_brands),
            avg_rating__gte=4
        ).exclude(id__in=user_interacted_products).order_by('-order_count', '-avg_rating')[:top_n]
    
    return list(related_products), list(top_products)
