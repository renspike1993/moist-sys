from django import forms
from .models import Marc21Field,BookDetail
from django.forms import modelformset_factory
from .models import Book,Department
from django.utils.safestring import mark_safe



class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter department name',
            }),
        }
        labels = {
            'name': 'Department Name',
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['program', 'image']
        widgets = {
            'program': forms.Select(attrs={'class': 'form-select'}),  # dropdown
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class BookDetailEditForm(forms.Form):
    """
    Displays all visible MARC21 fields for a specific book.
    Pre-fills values, adds red * for required fields, and orders by field_code.
    """

    def __init__(self, *args, **kwargs):
        book = kwargs.pop("book", None)
        super().__init__(*args, **kwargs)

        # ✅ Only include visible fields, ordered by field_code
        all_fields = Marc21Field.objects.filter(is_hidden=False).order_by('field_code')

        # Preload existing values for this book
        existing_details = {}
        if book:
            existing_details = {
                d.marc21_field.field_code: d.value
                for d in book.book_details.select_related("marc21_field")
            }

        # ✅ Dynamically create form fields
        for field in all_fields:
            value = existing_details.get(field.field_code, "")

            # Red * for required fields
            label_text = field.label or field.field_code
            if field.is_required:
                label_text = mark_safe(f'{label_text} <span style="color:red">*</span>')

            self.fields[field.field_code] = forms.CharField(
                label=label_text,
                initial=value,
                required=field.is_required,
                widget=forms.Textarea(
                    attrs={
                        "class": "form-control",
                        "rows": 2,
                        "placeholder": field.label or field.field_code,
                    }
                ),
            )
        



class BookDetailForm(forms.ModelForm):
    class Meta:
        model = BookDetail
        fields = ['marc21_field', 'value']
        widgets = {
            'marc21_field': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }



BookDetailFormSet = modelformset_factory(
    BookDetail,
    form=BookDetailForm,
    extra=1,             # allow adding 1 new field
    can_delete=True      # allow deleting existing ones
)





class Marc21DynamicForm(forms.Form):
    """
    Dynamically generated form based on visible MARC21 fields.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fetch all visible MARC21 fields
        visible_fields = Marc21Field.objects.filter(is_hidden=False).order_by('field_code')

        for field in visible_fields:
            label = f"{field.label or field.field_name} [{field.field_code}] "  # include code in label
            required = field.is_required

            # Create the form field dynamically
            form_field = forms.CharField(
                label=label,
                required=required,
                widget=forms.TextInput(attrs={
                    "class": "form-control",
                   
                    "data-field-code": field.field_code,  # include field_code as an HTML data attribute
                })
            )

            # Store field_code as custom metadata (for backend reference)
            form_field.field_code = field.field_code

            self.fields[field.field_code] = form_field
