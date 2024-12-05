from django.shortcuts import render
from app.database import insert_item , update_item_by_scanned_code_sold , update_item_by_scanned_code_back_to_inventory, update_item_by_scanned_code
import mysql.connector as sql
from app.read_data import get_items_details_with_expiring_warranty, get_missing_items_details, fetch_rented_items, fetch_sold_items,fetch_inventory_items, get_inventory_status, calculate_warranty_end_date,authenticate_user, authenticate_admin, insert_user, list_all_users, routine_check ,fetch_users_by_scanned_code
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from pyzbar.pyzbar import decode
from PIL import Image

item_name = ''
specs = ''
s_code = ''
comment = ''
dc = ''
wil = ''

id = ''
password = ''

user_id = None

# Create your views here.
def user_login(request):
    global user_id
    print(f"Request method: {request.method}")
    
    if request.method == "POST":
        print('Entered POST method')
        id = request.POST.get('user-id', '')
        password = request.POST.get('password', '')
        print(id,':',password)
        data = authenticate_user(id, password)
        user_id = data
        print(f"Authentication result: {data}")
        if data:
            return JsonResponse({"authenticated": True})
        else:
            return JsonResponse({"authenticated": False, "message": "Invalid ID or password."}, status=401)
    else:
        print('Entered GET method - Rendering the login page')

    return render(request, 'user_login.html')

def admin_login(request):
    global user_id
    print(f"Request method: {request.method}")
    
    if request.method == "POST":
        print('Entered POST method')

        # Extract user ID and password from the request
        id = request.POST.get('user-id', '')
        password = request.POST.get('password', '')

        # Authenticate user
        user_id_1, role = authenticate_admin(id, password)
        user_id = user_id_1
        print(f"Authentication result: User ID = {user_id_1}, Role = {role}")

        # Prepare response based on authentication and role
        if user_id and role.lower() == "admin":
            print("Authentication successful. User has admin access.")
            return JsonResponse({"authenticated": True, "message": "Admin login successful."})
        else:
            print("Authentication failed or user is not an admin.")
            return JsonResponse({
                "authenticated": False,
                "message": "Invalid ID or password, or insufficient privileges."
            })

    else:
        print('Entered GET method - Rendering the login page')
    
    # Render the login page for GET requests
    return render(request, 'admin_login_2.html')


def add_users(request):
    if user_id:
        if request.method == 'POST':
            try:
                # Parse JSON data from request body
                data = json.loads(request.body)
                user_name = data.get('userName')
                full_name = data.get('fullName')
                password = data.get('password')

                # Call your database function to insert the user
                insert_user(user_name, full_name, password, 'Staff')

                # Return updated user list
                users = list_all_users()
                return JsonResponse({'message': 'User added successfully!', 'users': users}, status=200)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

        # For GET requests, render the dashboard with the user list
        users = list_all_users()
        return render(request, 'add_users.html', {'users': users})
    else:
        return render(request, 'user_login.html')
 
def dashboard(request):
    if user_id:
        users = get_inventory_status()
        print(users)
        return render(request, 'dashboard.html', users)
 

def home(request):
    if user_id:
        return render(request, 'home.html')
    else:
        return render(request, 'user_login.html')

def home_2(request):
    if user_id:
        return render(request, 'home_2.html')
    else:
        return render(request, 'user_login.html')

def rent(request):
    global s_code, comment, dc, wil, user_id
    print(user_id)
    if user_id:
        if request.method == "POST":
            if request.FILES.get("captured_image"):
                try:
                    # Decode the uploaded image
                    uploaded_file = request.FILES["captured_image"]
                    print('got uploaded file')
                    image = Image.open(uploaded_file)
                    print('got image')
                    decoded_objects = decode(image)
                    print('got decoded_objects')
                    if decoded_objects:
                        s_code = decoded_objects[0].data.decode("utf-8")
                    else:
                        s_code = "No QR/Barcode detected."
                    return JsonResponse({"s_code": s_code})
                except Exception as e:
                    return JsonResponse({"error": f"Error decoding image: {str(e)}"}, status=500)

            # Handle form data when submitting the entire form
            dc = request.POST.get("rDC", "")
            wil = request.POST.get("rWIL", "")
            s_code = request.POST.get("rcode", "")
            comment = request.POST.get("rcomment", "")

            # Insert into the database
            update_item_by_scanned_code(user_id,s_code, 'Rented', comment, dc, wil)
            return render(request, "Rent.html")
        
        return render(request,'Rent.html')
    else:
        return render(request, 'user_login.html')

def sell(request):
    global s_code, dc, wil, comment, user_id
    print(user_id)
    if user_id:
        if request.method == "POST":
            if request.FILES.get("captured_image"):
                try:
                    # Decode the uploaded image
                    uploaded_file = request.FILES["captured_image"]
                    print('got uploaded file')
                    image = Image.open(uploaded_file)
                    print('got image')
                    decoded_objects = decode(image)
                    print('got decoded_objects')
                    if decoded_objects:
                        s_code = decoded_objects[0].data.decode("utf-8")
                    else:
                        s_code = "No QR/Barcode detected."
                    return JsonResponse({"s_code": s_code})
                except Exception as e:
                    return JsonResponse({"error": f"Error decoding image: {str(e)}"}, status=500)

            # Handle form data when submitting the entire form
            dc = request.POST.get("rDC", "")
            wil = request.POST.get("rWIL", "")
            s_code = request.POST.get("rcode", "")
            comment = request.POST.get("rcomment", "")

            # Insert into the database
            update_item_by_scanned_code_sold(user_id,s_code, 'Sold', comment, dc, wil)
            return render(request, "Selling.html")
            
        return render(request,'Selling.html')
    else:
        return render(request, 'user_login.html')

def retrieve(request):
    global  s_code, comment, user_id
    print(user_id)
    if user_id:
        if request.method == "POST":
            if request.FILES.get("captured_image"):
                try:
                    # Decode the uploaded image
                    uploaded_file = request.FILES["captured_image"]
                    print('got uploaded file')
                    image = Image.open(uploaded_file)
                    print('got image')
                    decoded_objects = decode(image)
                    print('got decoded_objects')
                    if decoded_objects:
                        s_code = decoded_objects[0].data.decode("utf-8")
                    else:
                        s_code = "No QR/Barcode detected."
                    return JsonResponse({"s_code": s_code})
                except Exception as e:
                    return JsonResponse({"error": f"Error decoding image: {str(e)}"}, status=500)

            # Handle form data when submitting the entire form
            rdc = request.POST.get("rRDC", "")
            s_code = request.POST.get("rcode", "")
            comment = request.POST.get("rcomment", "")

            # Insert into the database
            update_item_by_scanned_code_back_to_inventory(user_id,s_code, 'Inventory', comment, rdc)
            return render(request, "Retrieving.html")
            
        return render(request, 'Retrieving.html')
    else:
        return render(request, 'user_login.html')
    
def add_to_inventory(request):
    global item_name, s_code, comment, specs, user_id
    print(user_id)
    if user_id:
        if request.method == "POST":
            if request.FILES.get("captured_image"):
                try:
                    # Decode the uploaded image
                    uploaded_file = request.FILES["captured_image"]
                    print('got uploaded file')
                    image = Image.open(uploaded_file)
                    print('got image')
                    decoded_objects = decode(image)
                    print('got decoded_objects')
                    if decoded_objects:
                        s_code = decoded_objects[0].data.decode("utf-8")
                    else:
                        s_code = "No QR/Barcode detected."
                    return JsonResponse({"s_code": s_code})
                except Exception as e:
                    return JsonResponse({"error": f"Error decoding image: {str(e)}"}, status=500)

            # Handle form data when submitting the entire form
            item_name = request.POST.get("ritemname", "")
            specs = request.POST.get("rspecs", "")
            s_code = request.POST.get("rcode", "")
            comment = request.POST.get("rcomment", "")
            vendor_name = request.POST.get("rvname", "")
            invoice_number = request.POST.get("rinum", "")
            purchase_date = request.POST.get("rpurchase_date", "")
            warranty_months = request.POST.get("rwmon", "")
            warranty_end = calculate_warranty_end_date(purchase_date,int(warranty_months))

            # Insert into the database
            insert_item(user_id, item_name, specs, s_code, "Inventory", comment, vendor_name , invoice_number, purchase_date, warranty_months, warranty_end)
            return render(request, "Add_to_inventory.html")

        return render(request, "Add_to_inventory.html")
    else:
        return render(request, 'user_login.html')

def routine_check_1(request):
    if user_id:
        if request.method == 'POST':
            try:
                data = json.loads(request.body)  # Parse JSON payload
                scanned_items = data.get('scanned_items', [])  # Get scanned items

                # Simulated database items
                database_items = routine_check(user_id,scanned_items)

                # Identify missing items
                missing_items = {key: value for key, value in database_items.items() if key not in scanned_items}

                # Return missing items as JSON
                return JsonResponse(missing_items)

            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        elif request.method == 'GET':
            # Render the HTML template on GET requests
            return render(request, 'routine_check.html')

        else:
            return JsonResponse({'error': 'Invalid request method'}, status=405)
    else:
        return render(request, 'user_login.html')
    
@csrf_exempt
def item_history(request):
    if user_id:
        if request.method == "POST":
            data = json.loads(request.body)
            code = data.get("code")

            # Dummy data representing history for the code
            history = fetch_users_by_scanned_code(code)
            
            return JsonResponse(history, safe=False)
        return render(request, 'item_history.html')
    else:
        return render(request, 'user_login.html')
    
def inventory(request):
    if user_id:
        result = fetch_inventory_items()
        print(result)
        return render(request, 'inventory.html',{'items': result})
    
def rented(request):
    if user_id:
        result = fetch_rented_items()
        print(result)
        return render(request, 'rented.html',{'items': result})
    
def sold(request):
    if user_id:
        result = fetch_sold_items()
        print(result)
        return render(request, 'sold.html',{'items': result})
    
def missing(request):
    if user_id:
        result = get_missing_items_details()
        print(result)
        return render(request, 'missing.html',{'items': result})
    
def warranty(request):
    if user_id:
        result = get_items_details_with_expiring_warranty()
        print(result)
        return render(request, 'warranty.html',{'items': result})