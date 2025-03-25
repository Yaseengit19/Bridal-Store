# Bridal Store with Makeup Artists Booking

A Django web application for a bridal store that allows customers to browse bridal products and services, and book makeup artists for their special day. The application provides an intuitive platform for brides to select makeup artists, view product details, and make bookings online.

Features
>> Bridal Products Store: Browse a variety of bridal products including dresses, accessories, and more.
>> Razorpay payment Integration test mode.
>> Makeup Artist Booking: Customers can view available makeup artists and book their services for a specific date and time.
>> User Authentication: Support for user registration, login, and profile management.
>> Admin Dashboard: Admin panel for managing products, makeup artists, and user bookings.
>> Search and Filter: Users can search for products and makeup artists and filter based on categories and availability.

Tech Stack
Backend: Python, Django
Frontend: HTML, CSS, JavaScript
Database: SQLite (or any other database like PostgreSQL, MySQL, etc.)

Authentication: Django’s built-in authentication system

Hosting: Can be hosted on platforms like Heroku, AWS, or DigitalOcean (depending on your setup)

Installation
Prerequisites
Python 3.13

pip (Python package installer)

Steps to Run the Project Locally
Clone the repository:

>>bash
git clone https://github.com/yourusername/bridal-store-booking.git(this is a sample ,copy from my repository)
cd bridal-store

Set up a virtual environment (recommended):
>>bash
python -m venv venv
Activate the virtual environment:

Windows:

>>bash
.\venv\Scripts\activate
macOS/Linux:

>>bash
source venv/bin/activate
Install the required dependencies:

>>bash
pip install -r requirements.txt
Set up the database:

Apply the migrations to set up your database:

>>bash
python manage.py migrate
Create a superuser (for admin access):

>>bash
python manage.py createsuperuser
Follow the prompts to create an admin user.

Run the development server:

>>bash
python manage.py runserver
Access the application:

Open your browser and go to http://127.0.0.1:8000/ to view the application.


Usage
User Features:
>>Browse Bridal Products: View and explore different bridal products, their descriptions, and prices.

>>Makeup Artist Booking: Choose makeup artists based on their expertise and availability, and make bookings.

>>Manage Bookings: View upcoming bookings and their status on the user dashboard.

Admin Features:
>>Manage Products: Add, update, or delete bridal products from the store.

>>Manage Makeup Artists: Add or update makeup artist profiles and their availability.

>>View Bookings: Approve or reject booking requests and manage customer appointments.

Development
To contribute to the development of this project, follow these steps:

Fork the repository and clone it to your local machine.

Create a new branch for your feature or fix.

Install the required dependencies by running pip install -r requirements.txt.

Make your changes and test locally.

Commit your changes with a clear and concise message.

Push your changes to your fork and open a pull request to the main repository.

Contributing
If you’d like to contribute to this project, feel free to fork the repository, open an issue, or submit a pull request. Contributions are welcome!
