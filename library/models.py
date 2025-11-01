from django.db import models
from django.utils import timezone
import uuid

# Your existing models (keep these)
class Department(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Program(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="programs",
        default=1        
    )
    abbrv = models.CharField(max_length=50)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.department.name})"

class Marc21FieldCategory(models.Model):
    """
    Parent model representing a MARC21 tag range category.
    """
    code_range = models.CharField(max_length=10, unique=True, verbose_name="Tag Range")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    class Meta:
        db_table = "marc21_field_category"
        verbose_name = "MARC21 Field Category"
        verbose_name_plural = "MARC21 Field Categories"
        ordering = ["code_range"]

    def __str__(self):
        return f"{self.code_range}"

class Marc21Field(models.Model):
    """
    Child model representing individual MARC21 fields.
    """
    category = models.ForeignKey(
        Marc21FieldCategory,
        on_delete=models.CASCADE,
        related_name="fields"
    )
    field_code = models.CharField(max_length=10, verbose_name="MARC Tag")
    field_name = models.TextField(verbose_name="Field Name")
    label = models.CharField(max_length=255, verbose_name="Label")
    is_searchable = models.BooleanField(default=True, verbose_name="Searchable")
    is_hidden = models.BooleanField(default=True, verbose_name="Hidden")
    is_required = models.BooleanField(default=True, verbose_name="Required")

    class Meta:
        db_table = "marc21_field"
        verbose_name = "MARC21 Field"
        verbose_name_plural = "MARC21 Fields"
        ordering = ["field_code"]

    def __str__(self):
        return f"{self.field_code} – {self.label}"

class Book(models.Model):
    program = models.ForeignKey('Program', on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.rfid

class BookDetail(models.Model):
    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
        related_name="book_details"
    )
    marc21_field = models.ForeignKey(
        "Marc21Field",
        on_delete=models.CASCADE,
        related_name="field_details"
    )
    value = models.TextField(
        blank=True,
        null=True,
        default=None,
        verbose_name="Value"
    )

    def __str__(self):
        field_code = getattr(self.marc21_field, "tag", "Unknown Field")
        return f"{field_code}: {self.value[:50]}" if self.value else field_code

    class Meta:
        verbose_name = "Book Detail"
        verbose_name_plural = "Book Details"




# NEW TRANSACTION MODELS
class Transaction(models.Model):
    TRANSACTION_STATUS = [
        ('reserved', 'Reserved'),
        ('checked_out', 'Checked Out'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Transaction identification
    transaction_id = models.CharField(max_length=20, unique=True, editable=False)
    
    # User information
    user_id = models.CharField(max_length=50)  # Library ID number
    user_name = models.CharField(max_length=100, blank=True, null=True)
    user_email = models.CharField(max_length=100, blank=True, null=True)
    
    # Books in this transaction (linked to your existing Book model)
    books = models.ManyToManyField(Book, through='TransactionItem')
    
    # Dates
    reservation_date = models.DateTimeField(default=timezone.now)
    checkout_date = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    return_date = models.DateTimeField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='reserved')
    
    # Additional information
    notes = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.user_id}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)
    
    def generate_transaction_id(self):
        """Generate a unique transaction ID in format TXN-YYYYMMDD-XXXXX"""
        date_part = timezone.now().strftime('%Y%m%d')
        random_part = uuid.uuid4().hex[:5].upper()
        return f"TXN-{date_part}-{random_part}"
    
    @property
    def total_books(self):
        return self.books.count()
    
    @property
    def is_overdue(self):
        if self.due_date and timezone.now() > self.due_date and self.status != 'returned':
            return True
        return False
    
    def mark_as_checked_out(self):
        """Mark transaction as checked out and set due date"""
        self.status = 'checked_out'
        self.checkout_date = timezone.now()
        self.due_date = timezone.now() + timezone.timedelta(days=14)  # 14 days loan period
        self.save()
    
    def mark_as_returned(self):
        """Mark transaction as returned"""
        self.status = 'returned'
        self.return_date = timezone.now()
        self.save()
    
    class Meta:
        ordering = ['-created_at']

class TransactionItem(models.Model):
    """Intermediate model for Transaction-Book relationship"""
    status = models.CharField(max_length=20, default='reserved',blank=True,null=True)
    rfid = models.CharField(max_length=50, blank=True, null=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    # Item-specific information
    quantity = models.IntegerField(default=1)
    reserved_at = models.DateTimeField(auto_now_add=True)
    
    # If you want to track individual copy numbers
    copy_number = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.book.rfid} in {self.transaction.transaction_id}"
    
    class Meta:
        unique_together = ['transaction', 'book']


