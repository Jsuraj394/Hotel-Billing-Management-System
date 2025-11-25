# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models.functions import TruncMonth
from .models import Menu, Invoice
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import date, datetime, time
from django.utils.dateparse import parse_date
from django.db.models import Sum
from django.utils.timezone import localtime
from .forms import MenuForm
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from calendar import monthrange
from datetime import datetime, timedelta, date
from .models import Staff, StaffAttendance
from django.contrib import messages
from django.db.models import Max
from decimal import Decimal
from collections import defaultdict
import json
from django.shortcuts import render
from collections import defaultdict
from .models import Expense
from collections import OrderedDict
import os, json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max
from django.utils import timezone
from django.conf import settings
from .models import Menu, Invoice
from .forms import ExpenseForm
import os
import json
import platform
from datetime import datetime, time as dt_time
from collections import defaultdict, OrderedDict
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Max
from django.conf import settings
from .models import Menu, Invoice, Staff, StaffAttendance
from .forms import MenuForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest


@login_required
def edit_menu(request):
    items = Menu.objects.all().order_by('category', 'DishName')

    if request.method == 'POST':
        # CREATE
        if 'create' in request.POST:
            Menu.objects.create(
                DishName=request.POST['DishName'],
                price=request.POST['price'],
                category=request.POST['category'],
                image=request.FILES.get('image')  # returns None if no file
            )
            return redirect('edit_menu')

        # UPDATE
        if 'update' in request.POST:
            item = get_object_or_404(Menu, pk=request.POST['item_id'])
            item.DishName = request.POST['DishName']
            item.price = request.POST['price']
            item.category = request.POST['category']
            if request.FILES.get('image'):
                item.image = request.FILES['image']
            item.save()
            return redirect('edit_menu')

        # DELETE
        if 'delete' in request.POST:
            Menu.objects.filter(pk=request.POST['item_id']).delete()
            return redirect('edit_menu')

    return render(request, 'edit_menu.html', {'items': items})


@login_required
def generateBill(request):
    """
    Display menu grouped by category.
    Inputs named by dish.sno (primary key).
    """
    CATEGORIES = ['Breakfast', 'Rice', 'Thali', 'Main Course', 'Beverage']
    all_dishes = Menu.objects.all().order_by('category', 'DishName')
    category_items = OrderedDict()
    for cat in CATEGORIES:
        category_items[cat] = all_dishes.filter(category=cat)
    # print(category_items)
    return render(request, 'GenerateBill.html', {
        'category_items': category_items
    })

# @login_required
# def generateBill(request):
#     # menu_items = Menu.objects.all().order_by('category', 'sno')
#     menu_items = Menu.objects.all().order_by('category', 'DishName')
#     categories = {}
#     for item in menu_items:
#         categories.setdefault(item.category, []).append(item)
#     return render(request, 'GenerateBill.html', {
#         'category_items': categories
#     })




@login_required
def generate_bill_summary(request):
    """
    Process POST from generate_bill.
    Quantities come as {dish_pk: qty}.
    Saves JSON string of items in Invoice.items.
    """
    if request.method != 'POST':
        return redirect('generate_bill')

    total = 0
    items_list = []

    # Parse all qty inputs
    for key, val in request.POST.items():
        if key == 'csrfmiddlewaretoken':  #ignoroing the first element from HTML file as it is a CSRF token
            continue
        try:
            dish_pk = int(key)
            qty = int(val or 0)
        except (ValueError, TypeError):
            continue

        if qty < 1:
            continue

        dish = get_object_or_404(Menu, pk=dish_pk)
        line_total = dish.price * qty
        total += line_total
        # print(dish.DishName)

        items_list.append({
            'DishName': dish.DishName,
            'category': dish.category,
            'quantity': qty,
            'unit_price': float(dish.price),
            'line_total': float(line_total),
        })

    # Save invoice to file
    invoice_dir = os.path.join(settings.BASE_DIR, 'invoices')
    os.makedirs(invoice_dir, exist_ok=True)
    timestamp = timezone.localtime().strftime("%Y%m%d%H%M%S")
    file_path = os.path.join(invoice_dir, f'invoice_{timestamp}.txt')
    invoice_number = Invoice.objects.aggregate(Max('invoice_number'))['invoice_number__max']
    print(f"creating the invoice file for invoice number {invoice_number + 1}")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(
            f"            Swad Satva\n Heritage Plza Near Elpro Mall,\n       Chinchwadgaon, Pune\nMob.No:8956605744 B.No:{int(invoice_number) + 1}  \nDate:{timezone.localtime().strftime("%Y-%m-%d")}\n")
        f.write("=" * 33 + "\n")
        f.write(f"{'Item':15}{'Qty':>5} {'Price':>5} {'Total':>2}\n")
        f.write("-" * 33 + "\n")
        for it in items_list:
            name = it['DishName']
            qty = it['quantity']
            up = f"₹{int(it['unit_price'])}"
            lt = f"₹{int(it['line_total'])}"
            f.write(f"{name:15} {qty:>5} {up:>5} {lt:>2}\n")
        f.write("=" * 33 + "\n")
        f.write(f"{'               Grand Total':>10} ₹{int(total)}\n")
        f.write("\nThank you for order!\n")

    # Persist Invoice record
    # inv_number = Invoice.objects.aggregate(Max('invoice_number'))['invoice_number__max'] or 0
    # invoice = Invoice.objects.create(
    #     invoice_number=inv_number + 1,
    #     invoice_date=timezone.now(),
    #     items=json.dumps(items_list),
    #     total=f"{total:.2f}"
    # )

    inv_number = Invoice.objects.aggregate(Max('invoice_number'))['invoice_number__max'] or 0

    # Dump your Python list→string
    invoice = Invoice.objects.create(
        invoice_number=inv_number + 1,
        invoice_date=timezone.now(),
        items=json.dumps(items_list),
        total=f"{total:.2f}"
    )

    return render(request, 'bill_summary.html', {
        'items': items_list,
        'grand_total': total,
        'invoice': invoice,
    })


@login_required
def invoice_history(request):
    """
    Show past invoices with filters.
    Deserialize the JSON in Invoice.items into parsed_items.
    """
    # 1) Grab filter params
    invoice_number = request.GET.get('invoice_number', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # 2) Base queryset
    qs = Invoice.objects.order_by('-invoice_date')
    if invoice_number:
        qs = qs.filter(invoice_number=invoice_number)
    if start_date:
        qs = qs.filter(invoice_date__date__gte=start_date)
    if end_date:
        qs = qs.filter(invoice_date__date__lte=end_date)

    # 3) Build a list of dicts, parsing items JSON
    invoices = []
    for inv in qs:
        try:
            items = json.loads(inv.items)
        except json.JSONDecodeError:
            items = []

        invoices.append({
            'invoice_number': inv.invoice_number,
            'invoice_date': inv.invoice_date,
            'parsed_items': items,
            'total': inv.total,
        })

    # 4) Render
    return render(request, 'invoice_history.html', {
        'invoices': invoices,
        'invoice_number': invoice_number,
        'start_date': start_date,
        'end_date': end_date,
    })


@csrf_exempt
def print_invoice(request):
    """
    Print the latest .txt invoice via OS call.
    """
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request'}, status=400)

    invoice_dir = os.path.join(settings.BASE_DIR, 'invoices')
    try:
        latest = max(
            [os.path.join(invoice_dir, f) for f in os.listdir(invoice_dir)],
            key=os.path.getctime
        )
        print("Starting the printing process...")
        if platform.system() == "Windows":
            import win32api, win32print
            win32api.ShellExecute(0, "print", latest, None, ".", 0)
        else:
            os.system(f"lp '{latest}'")
        print("Invoice sent to printer Successfully !!!")
        # return JsonResponse({'message': '🖨️ Invoice sent to printer!'})
    except Exception as e:
        print(f"print failed {e}, please call +91 7057753364 or wait until he come")
        return JsonResponse({'message': f'❌ Printing failed: {e}'}, status=500)


@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    """
    Superuser view: show earnings, counts, and earnings-over-time chart.
    Filters by start_date/end_date query params.
    """
    # 1) Get query params
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # 2) Base queryset
    qs_all = Invoice.objects.all().order_by('invoice_date')
    qs_today = Invoice.objects.filter(
        invoice_date__date=localtime().date()
    )

    # 3) Apply date-range filters if provided
    filtered_qs = None
    if start_date_str and end_date_str:
        try:
            dt_start = parse_date(start_date_str)
            dt_end = parse_date(end_date_str)
            # include full end day
            end_dt = datetime.combine(dt_end, dt_time(23, 59, 59))
            filtered_qs = qs_all.filter(
                invoice_date__date__gte=dt_start,
                invoice_date__date__lte=end_dt
            )
        except Exception:
            filtered_qs = None

    # 4) Core metrics
    total_earnings = sum(Decimal(inv.total) for inv in qs_all) or Decimal('0.00')
    bills_today = qs_today.count()
    todays_earnings = sum(Decimal(inv.total) for inv in qs_today) or Decimal('0.00')
    customer_count = qs_all.count()  # or use distinct users if you have a user FK

    # 5) Filtered-range metrics
    if filtered_qs is not None:
        filtered_count = filtered_qs.count()
        filtered_earnings = sum(Decimal(inv.total) for inv in filtered_qs) or Decimal('0.00')
    else:
        filtered_count = None
        filtered_earnings = None

    # 6) Build chart data if filtered
    chart_labels = []
    chart_data = []
    if filtered_qs:
        daily_totals = defaultdict(Decimal)
        for inv in filtered_qs:
            d = localtime(inv.invoice_date).date()
            daily_totals[d] += Decimal(inv.total)
        # sort by date
        sorted_dates = sorted(daily_totals)
        chart_labels = [d.strftime("%Y-%m-%d") for d in sorted_dates]
        chart_data = [float(daily_totals[d]) for d in sorted_dates]

    return render(request, 'dashboard.html', {
        'start_date': start_date_str or '',
        'end_date': end_date_str or '',
        'total_earnings': total_earnings,
        'bills_today': bills_today,
        'customer_count': customer_count,
        'todays_earnings': todays_earnings,
        'filtered_count': filtered_count,
        'filtered_earnings': filtered_earnings,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    })


@login_required
def staff_management(request):
    """
    Shows a table of staff with one column per day of selected month.
    """
    # 1) Determine selected year/month
    selected_month = request.GET.get('month')
    if selected_month:
        year, mon = map(int, selected_month.split('-'))
    else:
        today = date.today()
        year, mon = today.year, today.month
        selected_month = f"{year:04d}-{mon:02d}"

    # 2) Build list of all dates in that month
    num_days = monthrange(year, mon)[1]
    days_in_month = [date(year, mon, d) for d in range(1, num_days + 1)]

    # 3) Fetch staff and attendance records
    staff_list = Staff.objects.all()
    attendance_qs = StaffAttendance.objects.filter(
        date__year=year, date__month=mon
    )
    # Map (staff_id, date) → present boolean
    present_map = {
        (att.staff.id, att.date): att.present
        for att in attendance_qs
    }

    # 4) Count present days per staff
    present_count_map = defaultdict(int)
    for (sid, dt), pres in present_map.items():
        if pres:
            present_count_map[sid] += 1

    # 5) Compute pro-rated salary
    monthly_salary_map = {}
    for staff in staff_list:
        per_day = staff.salary / Decimal(num_days)
        pres = present_count_map.get(staff.id, 0)
        monthly_salary_map[staff.id] = (per_day * pres).quantize(Decimal('0.01'))

    # 6) Assemble rows for template
    staff_rows = []
    for staff in staff_list:
        attendance = []
        for dt in days_in_month:
            attendance.append({
                'date': dt,
                'present': present_map.get((staff.id, dt), False)
            })
        staff_rows.append({
            'staff': staff,
            'attendance': attendance,
            'present_count': present_count_map.get(staff.id, 0),
            'salary_month': monthly_salary_map[staff.id],
        })

    return render(request, 'staff_management.html', {
        'staff_rows': staff_rows,
        'days_in_month': days_in_month,
        'selected_month': selected_month,
    })


@login_required
def mark_attendance(request):
    """
    AJAX endpoint to toggle attendance.
    Expects JSON: {staff_id, date:'YYYY-MM-DD', present: true/false}
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'invalid'}, status=400)

    try:
        payload = json.loads(request.body)
        staff_id = payload['staff_id']
        date_str = payload['date']
        present = payload['present']
    except (KeyError, ValueError, json.JSONDecodeError):
        return HttpResponseBadRequest('Bad payload')

    try:
        # dt = datetime.strptime(date_str, '%Y-%m-%d').date()
        dt = parse_date(date_str)
        if not dt:
            return HttpResponseBadRequest(f"Bad date format: {date_str}")
        staff = get_object_or_404(Staff, id=staff_id)
    except ValueError:
        return HttpResponseBadRequest('Bad date')

    StaffAttendance.objects.update_or_create(
        staff=staff,
        date=dt,
        defaults={'present': present}
    )
    return JsonResponse({'status': 'ok'})


@login_required
def add_staff(request):
    """
    Renders a form to add a new staff member and handles its submission.
    """
    if request.method == 'POST':
        # 1) Extract form data
        name = request.POST.get('name')
        age = request.POST.get('age')
        aadhar = request.POST.get('aadhar')
        address = request.POST.get('address')
        salary_str = request.POST.get('salary')
        joining_str = request.POST.get('joining_date')

        # 2) Parse numeric and date fields
        salary = Decimal(salary_str)
        joining_date = datetime.strptime(joining_str, '%Y-%m-%d').date()

        # 3) Create and save the Staff instance
        Staff.objects.create(name=name,age=age,aadhar_number=aadhar,address=address,salary=salary,joining_date=joining_date)

        # 4) Redirect back to the staff management table
        return redirect('staff_management')

    # GET: display empty form
    return render(request, 'add_staff.html')


@login_required
def edit_staff(request, staff_id):
    """
    Renders a form pre-filled with a staff member’s data and updates on POST.
    """
    staff = get_object_or_404(Staff, id=staff_id)

    if request.method == 'POST':
        # 1) Extract updated fields
        staff.name = request.POST.get('name')
        staff.age = request.POST.get('age')
        staff.aadhar_number = request.POST.get('aadhar')
        staff.address = request.POST.get('address')
        staff.salary = Decimal(request.POST.get('salary'))
        joining_str = request.POST.get('joining_date')
        staff.joining_date = datetime.strptime(joining_str, '%Y-%m-%d').date()

        # 2) Save changes
        staff.save()

        # 3) Return to staff overview
        return redirect('staff_management')

    # GET: render form with current data
    return render(request, 'edit_staff.html', {'staff': staff})


@login_required
def delete_staff(request, staff_id):
    """
    Deletes the specified staff member and redirects to the management view.
    """
    staff = get_object_or_404(Staff, id=staff_id)
    staff.delete()
    return redirect('staff_management')


def daily_summary(request):
    # Date‐range filtering (as before)
    start_date = request.GET.get('start_date')
    end_date   = request.GET.get('end_date')

    qs = Expense.objects.order_by('-date')
    if start_date:
        qs = qs.filter(date__gte=start_date)
    if end_date:
        qs = qs.filter(date__lte=end_date)

    # Build daily summary (unchanged)
    summary = defaultdict(lambda: {'total': 0, 'items': []})
    for exp in qs:
        summary[exp.date]['total'] += exp.amount
        summary[exp.date]['items'].append(exp)
    sorted_summary = dict(sorted(summary.items(), reverse=True))

    # Aggregate monthly spend
    monthly_qs = (
        qs
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    # Prepare lists for Chart.js
    monthly_labels = [item['month'].strftime('%b %Y') for item in monthly_qs]
    monthly_values = [float(item['total']) for item in monthly_qs]

    return render(request, 'ExpenseSummary.html', {
        'summary':        sorted_summary,
        'start_date':     start_date,
        'end_date':       end_date,
        'monthly_labels': monthly_labels,
        'monthly_values': monthly_values,
    })



def add_expense(request):
    import datetime as dt
    initial_data = {
        'date': dt.date.today(),
        'owner': 'Swad',
    }


    if request.method == 'POST':
        form = ExpenseForm(request.POST,initial=initial_data)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense added successfully')
            return redirect('daily_summary')
    else:
        form = ExpenseForm(initial=initial_data)

    return render(request, 'add_expense.html', {'form': form })




















# from django.utils import timezone
# from django.db.models import Sum
# from .models import Invoice
from collections import defaultdict
# from datetime import timedelta
from django.core.mail import send_mail

def get_last_3_days_invoice_summary():
    today = timezone.now().date()
    start_date = today - timedelta(days=2)  # includes today, yesterday, and day before

    invoices = Invoice.objects.filter(invoice_date__date__gte=start_date)

    daily_totals = defaultdict(float)
    for invoice in invoices:
        date_key = invoice.invoice_date.date()
        try:
            daily_totals[date_key] += float(invoice.total)
        except ValueError:
            continue  # skip if total is not a valid number

    return daily_totals




def send_invoice_summary_email():
    summary = get_last_3_days_invoice_summary()

    message_lines = ["📊 Invoice Summary for Last 3 Days:\n"]
    for date, total in sorted(summary.items()):
        message_lines.append(f"{date}: ₹{total:.2f}")

    message = "\n".join(message_lines)

    send_mail(
        subject="Daily Invoice Summary",
        message=message,
        from_email="swadsatva3@gmail.com",
        recipient_list=["swadsatva3@gmail.com"],
        fail_silently=False,
    )
