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



def data_center(request):
    return render(request,'registrar/folder/list.html')