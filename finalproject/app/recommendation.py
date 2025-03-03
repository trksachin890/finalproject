import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from django.db.models import Avg, Count, Q
from .models import Product, ProductReview, OrderItem

# Function to load data and train the recommendation model
def train_model():
    # Query all product reviews from the database
    reviews = ProductReview.objects.all().values("user_id", "product_id", "rating")
    # Convert the query set to a pandas DataFrame
    df = pd.DataFrame(list(reviews))
    
    # Check if the DataFrame is empty (no reviews available)
    if df.empty:
        return None  # No reviews available, return None
    
    # Define the rating scale for the Surprise library
    reader = Reader(rating_scale=(1, 5))
    # Load data from the DataFrame for Surprise
    data = Dataset.load_from_df(df[['user_id', 'product_id', 'rating']], reader)
    # Split the data into training and testing sets (80% train, 20% test)
    trainset, _ = train_test_split(data, test_size=0.2)
    
    # Initialize the SVD (Singular Value Decomposition) model
    model = SVD()
    # Train the model on the training set
    model.fit(trainset)
    
    # Return the trained model
    return model

# Train the recommendation model
model = train_model()

# Function to recommend products
def recommend_products(user=None, top_n=10):
    # Compute top products based on high average ratings and high order count
    top_products = Product.objects.annotate(
        avg_rating=Avg('productreview__rating'),  # Calculate the average rating of each product
        order_count=Count('orderitem')  # Count the number of orders for each product
    ).filter(avg_rating__gte=4).order_by('-order_count', '-avg_rating')[:top_n]  # Filter and sort products
    
    # Initialize an empty list for related products
    related_products = []
    # If the user is authenticated, personalize recommendations
    if user and user.is_authenticated:
        # Get the list of product IDs that the user has rated
        user_rated_products = ProductReview.objects.filter(user=user).values_list('product_id', flat=True)
        # Get the list of product IDs that the user has ordered
        user_ordered_products = OrderItem.objects.filter(user=user).values_list('product_id', flat=True)
        # Combine both lists to get a unique set of products the user has interacted with
        user_interacted_products = set(user_rated_products) | set(user_ordered_products)
        
        # Extract user preferences based on their interactions
        user_categories = Product.objects.filter(id__in=user_interacted_products).values_list('category', flat=True)
        user_brands = Product.objects.filter(id__in=user_interacted_products).values_list('brand', flat=True)
        
        # Fetch related products based on category and brand, excluding already interacted products
        related_products = Product.objects.annotate(
            avg_rating=Avg('productreview__rating'),  # Calculate the average rating of each product
            order_count=Count('orderitem')  # Count the number of orders for each product
        ).filter(
            Q(category__in=user_categories) | Q(brand__in=user_brands),  # Match products in the same categories or brands
            avg_rating__gte=4  # Filter products with an average rating of 4 or higher
        ).exclude(id__in=user_interacted_products).order_by('-order_count', '-avg_rating')[:top_n]  # Exclude already interacted products and sort
    
    # Return the lists of related products and top products
    return list(related_products), list(top_products)