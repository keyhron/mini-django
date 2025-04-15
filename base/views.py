import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse,HttpResponseBadRequest
from .models import Product, Hub, Category
from .forms import ProductForm, ImportProductCSVForm, ProductFilterForm

# Create your views here.
def home(request):
    products = Product.objects.all()
    form = ProductFilterForm(request.GET)

    if form.is_valid():
        query = form.cleaned_data.get('query')
        selected_categories = form.cleaned_data.get('categories')
        selected_hubs = form.cleaned_data.get('hubs')

        if query:
            products = products.filter(name__icontains=query)

        if selected_categories:
            products = products.filter(categories__in=selected_categories)

        if selected_hubs:
            products = products.filter(hubs__in=selected_hubs)

    context = {
        'products': products,
        'form': form,
    }
    return render(request, 'base/home.html', context)

def createProduct(request):
    form = ProductForm()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        stock = request.POST.get('stock')
        price = request.POST.get('price')
        category_ids = request.POST.getlist('categories')
        hub_ids = request.POST.getlist('hubs')

        stock = int(stock) if stock else 0
        price = float(price) if price else None

        product = Product.objects.create(
            name=name,
            description=description,
            stock=stock,
            price=price
        )

        categories = Category.objects.filter(id__in=category_ids)
        hubs = Hub.objects.filter(id__in=hub_ids)
        product.categories.set(categories)
        product.hubs.set(hubs)
        product.save() 

        return redirect('home')
    
    context = {"form": form}
    return render(request, 'base/product-form.html', context)

def updateProduct(request,pk):
    product = Product.objects.get(id=pk)
    form = ProductForm(instance=product)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        
        stock = request.POST.get('stock')
        price = request.POST.get('price')
        product.stock = int(stock) if stock else 0
        product.price = float(price) if price else None

        category_ids = request.POST.getlist('categories')
        hub_ids = request.POST.getlist('hubs')
        categories = Category.objects.filter(id__in=category_ids)
        hubs = Hub.objects.filter(id__in=hub_ids)
        
        product.categories.set(categories)
        product.hubs.set(hubs)
        product.save() 

        return redirect('home')
    
    context = {"form": form}
    return render(request, 'base/product-form.html', context)

def deleteProduct(request, pk):
    product = get_object_or_404(Product, id=pk)
    if request.method == 'POST':
        product.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

def importProducts(request):
    if request.method == 'POST':
        form = ImportProductCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file'].read().decode('utf-8').splitlines()
            reader = csv.reader(csv_file)

            try:
                next(reader)  # Skip the header row, (TODO: Question if the header exist)
            except StopIteration:
                # Handle empty CSV file
                messages.warning(request, "El archivo CSV está vacío.")
                return redirect('import-products')

            # Initialize counters
            imported_count = 0
            updated_count = 0
            skipped_count = 0
            error_count = 0

            # Read each row in the CSV file
            for row in reader:
                if len(row) < 4:
                    messages.warning(request, f"Fila incompleta ignorada: {row}")
                    skipped_count += 1
                    continue

                name = row[0].strip()
                categories = row[1].strip()
                hubs = row[2].strip()
                price = row[3].strip()

                if not name or not categories or not hubs:
                    messages.warning(request, f"Fila incompleta (falta nombre, categoría o hub) ignorada: {row}")
                    skipped_count += 1
                    continue

                product = None

                try:
                    product, product_created = Product.objects.get_or_create(name=name, defaults={'price': None})
                    product.categories.clear()
                    product.hubs.clear()

                    for cat_name in [c.strip() for c in categories.split(',') if c.strip()]:
                        category_instance, _ = Category.objects.get_or_create(name=cat_name)
                        product.categories.add(category_instance)

                    for hub_name in [h.strip() for h in hubs.split(',') if h.strip()]:
                        hub_instance, _ = Hub.objects.get_or_create(name=hub_name)
                        product.hubs.add(hub_instance)

                    if price:
                        try:
                            product.price = float(price)
                        except ValueError:
                            raise ValueError(f"Formato de precio inválido: '{price}'")

                    product.save()

                    if product_created:
                        imported_count += 1
                    else:
                        updated_count += 1
                        
                # Handle errors
                except ValueError as ve:
                    messages.error(request, f"Error procesando la fila '{name}': {ve}")
                    error_count += 1
                    if product:
                        pass

                except Exception as e:
                    messages.error(request, f"Error proccesandoo la fila '{name}': {e}")
                    error_count += 1
                    if product:
                        pass

            messages.success(request, f"Importación completada. {imported_count} productos creados, {updated_count} productos actualizados, {skipped_count} filas ignoradas, {error_count} errores.")
    else:
        form = ImportProductCSVForm()
    return render(request, 'base/import-products.html', {'form': form})

def exportProducts(request):
    form = ProductFilterForm()
    if request.method == 'POST':
        form = ProductFilterForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            selected_categories = form.cleaned_data.get('categories')
            selected_hubs = form.cleaned_data.get('hubs')

            products = Product.objects.all()

            if query:
                products = products.filter(name__icontains=query)
            if selected_categories:
                products = products.filter(categories__in=selected_categories)
            if selected_hubs:
                products = products.filter(hubs__in=selected_hubs)

            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="productos.csv"'
            writer = csv.writer(response)
            writer.writerow(['Nombre del producto', 'Categorías', 'Hubs', 'Precio'])
            for product in products:
                category_names = ", ".join(cat.name for cat in product.categories.all())
                hub_names = ", ".join(hub.name for hub in product.hubs.all())
                writer.writerow([product.name, category_names, hub_names, product.price if product.price is not None else ''])
            return response
    return render(request, 'base/export-products.html', {'form': form})