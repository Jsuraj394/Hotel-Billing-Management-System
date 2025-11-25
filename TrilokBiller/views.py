# Username (leave blank to use 'surajjad'): Jsuraj394
# Email address: jsuraj394@gmail.com
# Password: Jsuraj@394
# Password (again): Jsuraj@394


# to create new user : python manage.py createsuperuser

# pip install weasyprint
# pip install xhtml2pdf




from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render,redirect
import datetime
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # <- This line is where login happens
            return redirect('home')  # Or whatever your landing page is
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')














def home(request):
    return render(request,"Home.html")


def generateBill(request):
    return render(request,"GenerateBill.html")


def about(request):
    print("this is about")
    # return HttpResponse("<h1> this is test about successfully</h1>")
    return render(request,"aboutUs.html",{})

def contact(request):
    print("this is contact")
    # return HttpResponse("<h1> this is test contact successfully</h1>")
    return render(request,"contactUs.html",{})




@csrf_exempt
def contact_submit(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            subject = f"📝 Contact Message from 😊{name}"
            body = f"Sender Name: {name}\nSender Email: {email}\n\nMessage:\n{message}"

            send_mail(
                subject,
                body,
                'support@kitchenstrilok.com',  # From email (can be same as recipient)
                ['support@kitchenstrilok.com'],  # To email
                fail_silently=False,
            )

            return JsonResponse({'message': '✅ Message sent successfully!'})

        return JsonResponse({'message': '❌ Missing fields'}, status=400)

    return JsonResponse({'message': 'Invalid request'}, status=400)

