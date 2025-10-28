# library/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from ..models import Transaction, Book, TransactionItem

@csrf_exempt
@require_http_methods(["POST"])
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
            reservation_date = data.get('reservationDate')
            books_data = data.get('books', [])
            
            print(f"User ID: {user_id}")
            print(f"Reservation Date: {reservation_date}")
            print(f"Number of books: {len(books_data)}")
            print("-" * 30)
            
            # Create Transaction
            transaction = Transaction.objects.create(
                user_id=user_id,
                reservation_date=reservation_date or timezone.now()
            )
            
            # Process each book
            transaction_items = []
            for i, book_data in enumerate(books_data, 1):
                print(f"Book {i}:")
                print(f"  ID: {book_data.get('id', 'N/A')}")
                print(f"  Title: {book_data.get('title', 'N/A')}")
                print(f"  Author: {book_data.get('author', 'N/A')}")
                
                # Find or create book
                book, created = Book.objects.get_or_create(
                    id=book_data.get('id'),
                    defaults={
                        'title': book_data.get('title', 'Unknown Title'),
                        'author': book_data.get('author', 'Unknown Author'),
                        'description': book_data.get('description', ''),
                        'category': book_data.get('category', 'other'),
                        'publication_year': book_data.get('year', 2023),
                        'pages': book_data.get('pages', 0),
                        'rating': book_data.get('rating', 0.0),
                        'total_copies': 1,
                        'available_copies': 1,
                    }
                )
                
                # Create transaction item
                transaction_item = TransactionItem.objects.create(
                    transaction=transaction,
                    book=book,
                    quantity=1
                )
                transaction_items.append({
                    'id': book.id,
                    'title': book.title,
                    'author': book.author
                })
            
            print("=" * 50)
            print(f"TRANSACTION CREATED: {transaction.transaction_id}")
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
                    'reservation_date': transaction.reservation_date.isoformat(),
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
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)

@require_http_methods(["GET"])
def transaction_list(request):
    """
    Get list of transactions
    """
    try:
        transactions = Transaction.objects.all()[:50]  # Limit to 50 transactions
        
        transaction_list = []
        for transaction in transactions:
            books = []
            for item in transaction.transactionitem_set.all():
                books.append({
                    'title': item.book.title,
                    'author': item.book.author
                })
            
            transaction_list.append({
                'transaction_id': transaction.transaction_id,
                'user_id': transaction.user_id,
                'status': transaction.status,
                'reservation_date': transaction.reservation_date.isoformat(),
                'total_books': transaction.total_books,
                'books': books
            })
        
        return JsonResponse({
            'transactions': transaction_list,
            'count': len(transaction_list)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error retrieving transactions: {str(e)}'
        }, status=500)