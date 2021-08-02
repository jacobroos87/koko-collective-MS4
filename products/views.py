from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower
from reviews.models import Reviews
from reviews.forms import ReviewForm
from .models import Product, Category, ProductImage
from .forms import ProductForm, ImageForm
from django.forms import modelformset_factory
from wishlist.models import Wishlist
from profiles.models import UserProfile

# Create your views here.


def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request,
                               ("You didn't enter any search criteria!"))
                return redirect(reverse('products'))

            queries = Q(name__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)
    
    if request.user.is_authenticated:
        user = UserProfile.objects.get(user=request.user)
    else:
        user = None

    reviews = Reviews.objects.filter(product=product)
    try:
        product_review = Reviews.objects.get(user=user, product=product)
        edit_review_form = ReviewForm(instance=product_review)

    except Reviews.DoesNotExist:
        edit_review_form = None

    review_form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'edit_review_form': edit_review_form,
    }
    print(context)

    return render(request, 'products/product_detail.html', context)


@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    ImageFormSet = modelformset_factory(ProductImage, form=ImageForm, extra=3)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ImageFormSet(request.POST, request.FILES, queryset=ProductImage.objects.none())

        if form.is_valid() and formset.is_valid():
            post_form = form.save(commit=False)
            user = request.user.id
            user = get_object_or_404(UserProfile, pk=user)
            post_form.user = user
            post_form.save()
            form.save_m2m()

            for form in formset.cleaned_data:
                if 'image' in form:
                    image = form['image']
                    photo = ProductImage(product=post_form, image=image)
                    photo.save()

            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail'))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
            return redirect(reverse('add_product'))
    else:
        form = ProductForm()
        formset = ImageFormSet(queryset=ProductImage.objects.none())

    template = 'products/add_product.html'
    context = {
        'form': form,
        'formset': formset,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))
