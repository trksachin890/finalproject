from .models import Wishlist  # Adjust based on your model
def wishlist_context(request):
    if request.user.is_authenticated:
        wishlists = Wishlist.objects.filter(user=request.user)
    else:
        wishlists = []
    return {'wishlists': wishlists}
