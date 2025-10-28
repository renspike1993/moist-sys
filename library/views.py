from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Marc21Field, Marc21FieldCategory, Book, BookDetail,Department,Program,Transaction, TransactionItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import  BookForm
import random
from .forms import BookDetailFormSet, BookDetailEditForm
from django.db.models import Count
import json
from django.core.paginator import Paginator

from.utils.printer import print_transaction

def reservation_api(request):
    """
    Handle reservation creation from the frontend and store in Transaction model
    """
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            
            print("=" * 50)
            print("RECEIVED RESERVATION DATA:")
            print("=" * 50)
            
            # Extract data
            user_id = data.get('userId', 'No user ID provided')
            reservation_date_str = data.get('reservationDate')
            books_data = data.get('books', [])
            
            print(f"User ID: {user_id}")
            print(f"Reservation Date: {reservation_date_str}")
            print(f"Number of books: {len(books_data)}")
            print("-" * 30)
            
            # Convert reservation date string to datetime object
            if reservation_date_str:
                from django.utils.dateparse import parse_datetime
                reservation_date = parse_datetime(reservation_date_str)
                if not reservation_date:
                    # If parsing fails, use current time
                    reservation_date = timezone.now()
            else:
                reservation_date = timezone.now()
            
            # Create Transaction
            transaction = Transaction.objects.create(
                user_id=user_id,
                reservation_date=reservation_date
            )
            
            # Process each book
            transaction_items = []
            for i, book_data in enumerate(books_data, 1):
                print(f"Book {i}:")
                print(f"  ID: {book_data.get('id', 'N/A')}")
                print(f"  RFID: {book_data.get('rfid', 'N/A')}")
                
                # Find book by ID (since we're getting ID from frontend)
                book_id = book_data.get('id')
                book_rfid = book_data.get('rfid')
                try:
                    if book_id:
                        book = Book.objects.get(id=book_id)
                    else:
                        print(f"  ERROR: No ID provided for book {i}")
                        continue
                    
                    # Create transaction item
                    transaction_item = TransactionItem.objects.create(
                        transaction=transaction,
                        book=book,
                        rfid=book_rfid,
                        quantity=1
                    )
                    
                    # Try to get book title from BookDetail
                    title_detail = BookDetail.objects.filter(
                        book=book,
                        marc21_field__field_code='245'  # MARC21 title field
                    ).first()
                    
                    author_detail = BookDetail.objects.filter(
                        book=book,
                        marc21_field__field_code='100'  # MARC21 author field
                    ).first()
                    
                    transaction_items.append({
                        'id': book.id,
                        'title': title_detail.value if title_detail else "No title",
                        'author': author_detail.value if author_detail else "Unknown Author",
                        'rfid': book_rfid
                    })
                    print(transaction_items)
                    # print(f"  ✅ Added to transaction: {book.rfid}")
                    
                except Book.DoesNotExist:
                    print(f"  ❌ Book not found with ID: {book_id}")
                    continue
            
            print("=" * 50)
            print(f"TRANSACTION CREATED: {transaction.transaction_id}")
            print(f"Total books added: {len(transaction_items)}")
            print("=" * 50)
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': f'Transaction created successfully for {len(transaction_items)} book(s)',
                'transactionId': transaction.transaction_id,
                'transactionData': {
                    'id': transaction.id,
                    'transaction_id': transaction.transaction_id,
                    'user_id': transaction.user_id,
                    'status': transaction.status,
                    'reservation_date': transaction.reservation_date.isoformat() if hasattr(transaction.reservation_date, 'isoformat') else str(transaction.reservation_date),
                    'total_books': transaction.total_books,
                    'books': transaction_items
                }
            }, status=201)
            
        except json.JSONDecodeError as e:
            print("ERROR: Invalid JSON data received")
            print(f"Error details: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)
# Add this new view to list transactions
def transaction_list(request):
    """
    Get list of all transactions
    """
    transactions = Transaction.objects.all().order_by('-created_at')
    
    transaction_data = []
    for transaction in transactions:
        books = []
        for item in transaction.transactionitem_set.all():
            # Get book title from BookDetail if available
            title_detail = BookDetail.objects.filter(
                book=item.book, 
                marc21_field__field_code='245'  # MARC21 field for title
            ).first()
            title = title_detail.value if title_detail else f"RFID: {item.book.rfid}"
            
            books.append({
                'rfid': item.book.rfid,
                'title': title,
                'reserved_at': item.reserved_at
            })
        
        transaction_data.append({
            'transaction': transaction,
            'books': books
        })
    
    return render(request, 'transaction/list.html', {
        'transaction_data': transaction_data
    })


def search_book(request):
    books = Book.objects.all()
    page_number = request.GET.get('page', 1)
    paginator = Paginator(books, 5)
    page_obj = paginator.get_page(page_number)

    data = []
    for book in page_obj:
        details = [
            {
                'field_code': bd.marc21_field.field_code,
                'field_description': bd.marc21_field.field_name,
                'value': bd.value
            }
            for bd in BookDetail.objects.filter(book=book).select_related('marc21_field')
        ]


        rfid = BookDetail.objects.filter(book=book, marc21_field_id=180).first()

        summary = BookDetail.objects.filter(book=book, marc21_field_id=115).first()
        copies = BookDetail.objects.filter(book=book, marc21_field_id=180).count()- TransactionItem.objects.filter(book=book,status='reserved').count()

        
        data.append({
            'book_id': book.id,
            'rfid': rfid.value if rfid else None,
            'image': book.image,
            'copies': copies or 0,
            'summary': summary.value if summary else None,
            'marc_21': details,
        })
    return render(request, 'search.html', {
        'books': data,
        'page_obj': page_obj,  # ✅ pagination object
    })

def check_rfid(request, rfid):
    """AJAX endpoint to check if a given RFID exists."""
    exists = BookDetail.objects.filter(value=rfid,).exists()
    return JsonResponse({'exists': exists})


def get_books(request):
    marc_field_ids = [9]  # ✅ multiple IDs
    books = (
        BookDetail.objects
        .filter(marc21_field_id__in=marc_field_ids)  # WHERE marc_21_field_id IN (...)
        .values('book_id', 'book__rfid', 'value', 'marc21_field_id','book__created_at')
        .annotate(total=Count('id'))
        .order_by('book_id')
    )
    return render(request, 'book/list.html', {'books': books})

def marc21_settings(request):
    if request.method == 'POST':
        field_id = request.POST.get('field_id')
        field_code = request.POST.get('field_code')
        field_name = request.POST.get('field_name')
        label = request.POST.get('label')
        category_id = request.POST.get('category')
        is_searchable = request.POST.get('is_searchable') == 'on'
        is_hidden = request.POST.get('is_hidden') == 'on'
        is_required = request.POST.get('is_required') == 'on'

        category = get_object_or_404(Marc21FieldCategory, id=category_id)

        if field_id:  # Update existing field
            marc_field = get_object_or_404(Marc21Field, id=field_id)
            marc_field.field_code = field_code
            marc_field.field_name = field_name
            marc_field.label = label
            marc_field.category = category
            marc_field.is_searchable = is_searchable
            marc_field.is_hidden = is_hidden
            marc_field.is_required = is_required
            marc_field.save()
            messages.success(request, "MARC21 field updated successfully!")
        else:  # Create new field
            Marc21Field.objects.create(
                field_code=field_code,
                field_name=field_name,
                label=label,
                category=category,
                is_searchable=is_searchable,
                is_hidden=is_hidden,
                is_required=is_required
            )
            messages.success(request, "MARC21 field created successfully!")

        return redirect('marc21_settings')

    # 🔹 Group fields by category (nested structure)
    categories = Marc21FieldCategory.objects.prefetch_related('fields').all().order_by('code_range')

    grouped_fields = []
    for category in categories:
        grouped_fields.append({
            'category': category,
            'fields': category.fields.all().order_by('field_code')
        })

    return render(request, 'setting/marc21_field.html', {
        'grouped_fields': grouped_fields,
        'categories': categories,
    })





@csrf_exempt  # or use @csrf_protect with proper token header (see below)
def update_marc21_field(request):
    if request.method == "POST":
        field_id = request.POST.get("id")
        column = request.POST.get("column")
        value = request.POST.get("value") == "true"

        try:
            field = Marc21Field.objects.get(id=field_id)
            setattr(field, column, value)
            field.save(update_fields=[column])
            return JsonResponse({"success": True})
        except Marc21Field.DoesNotExist:
            return JsonResponse({"success": False, "error": "Field not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})


def delete_marc21_field(request, pk):
    marc_field = get_object_or_404(Marc21Field, pk=pk)
    marc_field.delete()
    messages.success(request, "MARC21 field deleted successfully!")
    return redirect('marc21_settings')



def get_departments(request):
    departments = Department.objects.all()
    return render(request, 'department/list.html', {
        'departments': departments
    })
    



def get_programs(request):
    programs = Program.objects.all()
    return render(request, 'program/list.html', {
        'programs': programs
    })    
    

def get_ched_requirements(request):
    return render(request, 'requirements.html')    
        



# 📘 1. List all books
def book_list(request):
    books = Book.objects.all().order_by('-created_at')
    return render(request, 'book/book_list.html', {'books': books})
# 📘 2. Get Specific Book
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if "edit" in request.GET:  # edit mode
        if request.method == "POST":
            form = BookDetailEditForm(request.POST, book=book)
            if form.is_valid():
                # Save updated values
                for field_code, value in form.cleaned_data.items():
                    marc_field = Marc21Field.objects.get(field_code=field_code)
                    detail, _ = BookDetail.objects.get_or_create(
                        book=book,
                        marc21_field=marc_field,
                        defaults={"value": value}
                    )
                    detail.value = value
                    detail.save()

                messages.success(request, "✅ Book MARC21 fields updated successfully.")
                return redirect("book_detail", pk=book.pk)
        else:
            form = BookDetailEditForm(book=book)

        return render(request, "book/book_edit.html", {"book": book, "form": form})

    # default: view mode
    book_details = book.book_details.select_related("marc21_field").all()
    return render(request, "book/book_detail.html", {"book": book, "book_details": book_details})


# ➕ 3. Add a new book
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, "✅ Book added successfully!")
            # Redirect to its edit page (example: /books/12/?edit=true)
            return redirect(f'/books/{book.id}/?edit=true')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = BookForm()

    return render(request, 'book/book_form.html', {'form': form, 'title': 'Add Book'})

# ✏️ 4. Update an existing book
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Book updated successfully!")
            return redirect('book_detail', pk=book.pk)
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = BookForm(instance=book)

    return render(request, 'book/book_form.html', {'form': form, 'title': 'Edit Book'})
# ❌ 5. Delete a book
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, "🗑️ Book deleted successfully!")
        return redirect('book_list')

    return render(request, 'book/book_confirm_delete.html', {'book': book})


def transaction_detail(request, pk):
    """Display full transaction details, including related books."""
    transaction = Transaction.objects.filter(pk=pk).first()
    print(transaction)
    books = transaction.books.all()  # Get all books linked to this transaction
    # transaction_items = transaction.select_related('book')

    return render(request, 'transactions/transaction_detail.html', {
        'transaction': transaction,
        'books': books
    })


def transaction_list(request):
    """Display all transactions with pagination."""
    transactions = Transaction.objects.all().order_by('-created_at')
    paginator = Paginator(transactions, 10)  # 10 per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'transactions/transaction_list.html', {
        'page_obj': page_obj
    })


def transaction_create(request):
    """Create a new reservation or checkout."""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user_name = request.POST.get('user_name')
        user_email = request.POST.get('user_email')
        book_ids = request.POST.getlist('books')

        transaction = Transaction.objects.create(
            user_id=user_id,
            user_name=user_name,
            user_email=user_email,
            status='reserved'
        )

        # Link selected books
        for book_id in book_ids:
            book = Book.objects.get(pk=book_id)
            transaction.books.add(book)

        messages.success(request, f'Transaction {transaction.transaction_id} created successfully.')
        return redirect('transaction_list')

    books = Book.objects.all()
    return render(request, 'transactions/transaction_form.html', {
        'books': books
    })


def transaction_checkout(request, pk):
    """Mark a transaction as checked out."""
    transaction = get_object_or_404(Transaction, pk=pk)
    transaction.mark_as_checked_out()
    
    print_transaction(transaction)
    
    messages.success(request, f'Transaction {transaction.transaction_id} marked as checked out.')
    return redirect('transaction_detail', pk=transaction.pk)

def transaction_item_checkout(request, pk):
    """Mark an individual TransactionItem as checked out."""
    item = get_object_or_404(TransactionItem, pk=pk)

    if item.status != 'checked_out':
        item.status = 'checked_out'
        item.save()
        messages.success(request, f'Book  checked out successfully.')
    else:
        messages.warning(request, f'Book is already checked out.')

    return redirect('transaction_detail', pk=item.transaction.pk)


def transaction_item_return(request, pk):
    """Mark an individual TransactionItem as returned."""
    item = get_object_or_404(TransactionItem, pk=pk)

    if item.status != 'returned':
        item.status = 'returned'
        item.save()
        messages.success(request, f'Book has been marked as returned.')
    else:
        messages.warning(request, f'Book is already marked as returned.')

    return redirect('transaction_detail', pk=item.transaction.pk)

def transaction_return(request, pk):
    """Mark a transaction as returned."""
    transaction = get_object_or_404(Transaction, pk=pk)
    transaction.mark_as_returned()
    messages.success(request, f'Transaction {transaction.transaction_id} marked as returned.')
    return redirect('transaction_detail', pk=transaction.pk)