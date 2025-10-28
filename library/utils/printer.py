from escpos.printer import Usb
from datetime import datetime

def print_transaction(transaction):
    """Print transaction details and books using XPrinter (USB)."""
    try:
        # 🖨️ Configure your printer (adjust vendor/product IDs to match your printer)
        p = Usb(0x0483, 0x5743, timeout=0)  # Example: XPrinter USB IDs
        
        p.set(align='center', bold=True, double_height=True)
        p.text("Library Transaction Receipt\n")
        p.set(align='center')
        p.text("--------------------------------\n")

        # Header info
        p.set(align='left', bold=False, double_height=False)
        p.text(f"Transaction ID: {transaction.transaction_id}\n")
        p.text(f"User: {transaction.user_name} ({transaction.user_id})\n")
        p.text(f"Status: {transaction.status}\n")
        p.text(f"Checkout Date: {transaction.checkout_date:%Y-%m-%d %H:%M}\n")
        p.text(f"Due Date: {transaction.due_date:%Y-%m-%d}\n")
        p.text("--------------------------------\n")

        # Books
        p.set(align='left', bold=True)
        p.text("Books:\n")
        p.set(align='left', bold=False)
        for book in transaction.books.all():
            p.text(f"- {book.rfid} | {book.program.name if book.program else ''}\n")

        p.text("--------------------------------\n")
        p.set(align='center')
        p.text(f"Printed: {datetime.now():%Y-%m-%d %H:%M}\n")
        p.text("Thank you!\n\n\n")
        
        p.cut()
        p.close()

    except Exception as e:
        print("Printer Error:", e)
