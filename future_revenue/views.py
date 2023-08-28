import os
from calendar import month_abbr
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout, update_session_auth_hash
from django.conf import settings
from django.db.models import Sum

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from matplotlib.dates import date2num

from .models import ProductCategory, Product, SalesData
from .forms import UploadDataForm
from .analytics import forecast_revenue  # Import your prediction function



def handle_not_found(request, exception):
    return render(request, 'page_404/404.html')



def index(request):
    return render(request, 'home.html')



def managerLogin(request,):
    if not request.user.is_authenticated or request.user.is_manager != True:
        if request.method == "POST":
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, email=email, password=password)

            if user is not None and user.is_manager == True:
                login(request, user)
                messages.success(
                    request, ('Hi '+user.first_name+', Welcome back to the dashboard!'))
                return redirect(dashboard)
            else:
                messages.error(
                    request, ('User Email or Password is not correct! Try agin...'))
                return redirect(managerLogin)
        else:
            context = {'title': 'Manager Login', }
            return render(request, 'dashboard/login.html', context)
    else:
        return redirect(dashboard)



@login_required(login_url='manager_login')
def managerLogout(request):
    logout(request)
    messages.info(request, ('You are now Logged out.'))
    return redirect(managerLogin)



@login_required(login_url='manager_login')
def dashboard(request):
    if request.user.is_authenticated and request.user.is_manager == True:
        context = {
            'title': 'Dashboard',
            'dash_active': 'active',
        }
        return render(request, 'dashboard/dashboard.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(managerLogin)


@login_required(login_url='manager_login')
def managerProfile(request):
    if request.user.is_authenticated and request.user.is_manager == True:
        if 'update_password' in request.POST:
            old_password = request.POST.get("old_pass")
            new_password = request.POST.get("pass1")
            confirmed_new_password = request.POST.get("pass2")

            if old_password and new_password and confirmed_new_password:
                user = get_user_model().objects.get(email=request.user.email)

                if not user.check_password(old_password):
                    messages.error(
                        request, "Your old password is not correct!")
                    return redirect(managerProfile)

                else:
                    if len(new_password) < 5:
                        messages.warning(request, "Your password is too weak!")
                        return redirect(managerProfile)

                    elif new_password != confirmed_new_password:
                        messages.error(
                            request, "Your new password not match the confirm password !")
                        return redirect(managerProfile)

                    else:
                        user.set_password(new_password)
                        user.save()
                        update_session_auth_hash(request, user)

                        messages.success(
                            request, "Your password has been changed successfully.!")
                        return redirect(managerProfile)

            else:
                messages.error(request, "Error , All fields are required !")
                return redirect(managerProfile)

        else:
            context = {
                'title': 'Profile',
            }
            return render(request, 'dashboard/profile.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(managerLogin)




@login_required(login_url='manager_login')
def product_category(request):
    if request.user.is_authenticated and request.user.is_manager == True:
        # getting product_category
        categoryData = ProductCategory.objects.filter()
        context = {
            'title': 'Manager - Product Categories List',
            'category_active': 'active',
            'categories': categoryData,
        }
        return render(request, 'dashboard/categories_list.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(managerLogin)



@login_required(login_url='manager_login')
def product_list(request):
    if request.user.is_authenticated and request.user.is_manager == True:
        # getting products
        productData = Product.objects.filter()
        context = {
            'title': 'Manager - Products List',
            'productList_active': 'active',
            'products': productData,
        }
        return render(request, 'dashboard/product_list.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(managerLogin)



@login_required(login_url='manager_login')
def sales_data(request,):
    if request.user.is_authenticated and request.user.is_manager == True:
        if request.method == 'POST':
            form = UploadDataForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = form.cleaned_data['file']
                try:
                    data_frame = pd.read_csv(uploaded_file)
                    for index, row in data_frame.iterrows():
                        date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
                        product_category_name = row['Product Category']
                        product_name = row['Product']
                        product_price = row['Price']
                        sales_amount = row['Sales Amount']
                        quantity_sold = row['Quantity Sold']
                        
                        # Get or create Product Category
                        product_category, _ = ProductCategory.objects.get_or_create(name=product_category_name)
                        
                        # Check if a ProductCategory with the same name exists
                        existing_category = ProductCategory.objects.filter(name=product_category_name).first()
                        
                        # If a ProductCategory with the same name exists, use it; otherwise, create a new ProductCategory
                        if existing_category:
                            product_category = existing_category
                        
                        # Check if a Product with the same name exists
                        existing_product = Product.objects.filter(name=product_name).first()
                        
                        # If a Product with the same name exists, use it; otherwise, create a new Product
                        if existing_product:
                            product = existing_product
                        else:
                            product = Product.objects.create(name=product_name, price=product_price, category=product_category)
                        
                        # Create SalesData using Product's ID
                        SalesData.objects.create(date=date, product=product, quantity_sold=quantity_sold, sales_amount=sales_amount)
                    return redirect(sales_data)
                except Exception as e:
                    messages.error(request,  f"Error processing CSV file: {e}")
                    return redirect(sales_data)
            else:
                messages.error(request,  "CSV File required!\nPlease upload CSV file")
                return redirect(sales_data)
        else:
            form = UploadDataForm()
            # getting sales data
            foundData = SalesData.objects.filter().order_by('-date')
            context = {
                'title': 'Manager - Sales Data',
                'salesData_active': 'active',
                'sales_data': foundData,
                'form': form,
            }
            return render(request, 'dashboard/sales_data.html', context)
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(managerLogin)




@login_required(login_url='manager_login')
def sales_trend(request, product_id):
    if request.user.is_authenticated and request.user.is_manager == True:
        product = Product.objects.get(pk=product_id)
        sales_data = SalesData.objects.filter(product=product).order_by('date')
        
        # Ensure that sales_data contains valid instances
        if not sales_data.exists():
            return render(request, 'sales_trend.html', {'product': product, 'error_message': 'No sales data available.'})
        
        dates = [data.date for data in sales_data]
        sales_amounts = [data.sales_amount for data in sales_data]

        # Prepare data for linear regression
        x = date2num(dates)
        y = sales_amounts
        x = x.reshape(-1, 1)

        # Create and fit linear regression model
        model = LinearRegression()
        model.fit(x, y)
        y_pred = model.predict(x)

        plt.figure(figsize=(10, 6))
        plt.plot(dates, sales_amounts, marker='o', label='Actual Sales')
        plt.plot(dates, y_pred, color='red', label='Linear Regression')
        plt.title(f"Sales Trend for {product.name} (Linear Regression)")
        plt.xlabel("Date")
        plt.ylabel("Sales Amount")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.legend()

        subfolder = 'sales_trends'
        plot_filename = f"sales_trend_{product.id}.png"
        plot_path = os.path.join(settings.MEDIA_ROOT, subfolder, plot_filename)
        os.makedirs(os.path.dirname(plot_path), exist_ok=True)  # Create subfolder if it doesn't exist

        plt.savefig(plot_path)
        plt.close()

        plot_url = os.path.join(settings.MEDIA_URL, subfolder, plot_filename)
        context = {
            'title': 'Manager - Sales Data',
            'salesData_active': 'active',
            'product': product,
            'plot_path': plot_url
        }
        return render(request, 'dashboard/sales_trend.html', context)
    
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(managerLogin)



@login_required(login_url='manager_login')
def predict_revenue(request, product_id):
    if request.user.is_authenticated and request.user.is_manager == True:
        product = Product.objects.get(pk=product_id)
        sales_data = SalesData.objects.filter(product=product).order_by('date')
        
        # Ensure that sales_data contains valid instances
        if not sales_data.exists():
            return render(request, 'predict_revenue.html', {'product': product, 'error_message': 'No sales data available.'})
        
        dates = [data.date for data in sales_data]
        sales_amounts = [data.sales_amount for data in sales_data]

        # Create a DataFrame for time series analysis
        df = pd.DataFrame({'Date': dates, 'SalesAmount': sales_amounts})
        df['Date'] = pd.to_datetime(df['Date'])  # Convert 'Date' column to datetime
        
        # Aggregate sales data by month
        df['Month'] = df['Date'].dt.month
        monthly_sales = df.groupby(['Month'])['SalesAmount'].sum().reset_index()

        # Predict future sales for same months in the next year
        current_year = datetime.now().year
        next_year = current_year + 1
        future_months = [datetime(next_year, month, 1) for month in range(1, 13)]  # From January to December

        # Interpolate missing data to match the length of future_months
        if len(future_months) != len(monthly_sales):
            monthly_sales = monthly_sales.set_index('Month')
            monthly_sales = monthly_sales.reindex(range(1, 13))
            monthly_sales['SalesAmount'] = monthly_sales['SalesAmount'].interpolate()

        plt.figure(figsize=(10, 6))
        plt.plot(future_months, monthly_sales['SalesAmount'], marker='o', label='Predicted Sales')
        plt.title(f"Predicted Monthly Sales Trend for {product.name} in {next_year}")
        plt.xlabel("Month")
        plt.ylabel("Sales Amount")
        plt.xticks(future_months, [month_abbr[i] for i in range(1, 13)])  # Use abbreviated month names
        plt.tight_layout()
        plt.legend()

        subfolder = 'predictions'
        plot_filename = f"predicted_monthly_sales_{product.id}.png"
        plot_path = os.path.join(settings.MEDIA_ROOT, subfolder, plot_filename)
        os.makedirs(os.path.dirname(plot_path), exist_ok=True)  # Create subfolder if it doesn't exist
        
        plt.savefig(plot_path)
        plt.close()

        plot_url = os.path.join(settings.MEDIA_URL, subfolder, plot_filename)
        context = {
            'title': 'Manager - Sales Data',
            'salesData_active': 'active',
            'product': product,
            'plot_path': plot_url
        }
        return render(request, 'dashboard/predict_revenue.html', context)
    
    else:
        messages.warning(request, ('You have to login to view the page!'))
        return redirect(managerLogin)

# Abbreviated month names
month_abbr = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']