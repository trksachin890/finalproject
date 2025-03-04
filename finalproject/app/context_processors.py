from .models import Wishlist  # Adjust based on your model
def wishlist_context(request):
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlists = Wishlist.objects.filter(user=request.user)
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    else:
        wishlists = []
    return {'wishlists': wishlists,'wishlist_count': wishlist_count}
