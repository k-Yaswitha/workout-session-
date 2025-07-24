#!/usr/bin/env python3
"""
Demo Gym Booking Website - Flask Application

This is a demo website that simulates a real gym booking system
for demonstrating the workout reservation bot.

Author: Workout Session Bot Demo
Version: 1.0.0
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime, timedelta
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'demo_secret_key_change_in_production'

# Demo data storage (in production, use a proper database)
USERS = {
    'demo_user': {
        'password': generate_password_hash('demo_password'),
        'name': 'Demo User',
        'email': 'demo@example.com'
    },
    'john_doe': {
        'password': generate_password_hash('password123'),
        'name': 'John Doe',
        'email': 'john@example.com'
    }
}

# Available time slots
TIME_SLOTS = [
    '06:00 AM', '07:00 AM', '08:00 AM', '09:00 AM', '10:00 AM',
    '11:00 AM', '12:00 PM', '01:00 PM', '02:00 PM', '03:00 PM',
    '04:00 PM', '05:00 PM', '06:00 PM', '07:00 PM', '08:00 PM'
]

DURATIONS = ['30 minutes', '60 minutes', '90 minutes', '120 minutes']

# Bookings storage (date -> time_slot -> user)
BOOKINGS = {}

# Simulate some existing bookings
def initialize_demo_bookings():
    """Initialize some demo bookings to make it realistic."""
    today = datetime.now()
    for i in range(14):  # Next 14 days
        date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
        BOOKINGS[date] = {}
        
        # Randomly book some slots
        import random
        for _ in range(random.randint(2, 8)):
            time_slot = random.choice(TIME_SLOTS)
            if time_slot not in BOOKINGS[date]:
                BOOKINGS[date][time_slot] = {
                    'user': random.choice(['john_doe', 'existing_user_1', 'existing_user_2']),
                    'duration': random.choice(DURATIONS),
                    'booked_at': datetime.now().isoformat()
                }

# Initialize demo data
initialize_demo_bookings()


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in USERS and check_password_hash(USERS[username]['password'], password):
            session['user'] = username
            session['user_name'] = USERS[username]['name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout user."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    """User dashboard."""
    if 'user' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('login'))
    
    # Get user's bookings
    user_bookings = []
    for date, slots in BOOKINGS.items():
        for time_slot, booking_info in slots.items():
            if booking_info['user'] == session['user']:
                user_bookings.append({
                    'date': date,
                    'time': time_slot,
                    'duration': booking_info['duration'],
                    'booked_at': booking_info['booked_at']
                })
    
    # Sort by date
    user_bookings.sort(key=lambda x: x['date'])
    
    return render_template('dashboard.html', bookings=user_bookings)


@app.route('/book', methods=['GET', 'POST'])
def book():
    """Booking page."""
    if 'user' not in session:
        flash('Please log in to make a booking.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        date = request.form['date']
        time_slot = request.form['time_slot']
        duration = request.form['duration']
        
        # Validate inputs
        if not date or not time_slot or not duration:
            flash('Please fill in all fields.', 'error')
            return render_template('book.html', time_slots=TIME_SLOTS, durations=DURATIONS)
        
        # Check if date is valid (not in the past)
        try:
            booking_date = datetime.strptime(date, '%Y-%m-%d').date()
            if booking_date < datetime.now().date():
                flash('Cannot book for past dates.', 'error')
                return render_template('book.html', time_slots=TIME_SLOTS, durations=DURATIONS)
        except ValueError:
            flash('Invalid date format.', 'error')
            return render_template('book.html', time_slots=TIME_SLOTS, durations=DURATIONS)
        
        # Check if slot is available
        if date not in BOOKINGS:
            BOOKINGS[date] = {}
        
        if time_slot in BOOKINGS[date]:
            flash(f'Time slot {time_slot} on {date} is already booked. Please choose another time.', 'error')
            return render_template('book.html', time_slots=TIME_SLOTS, durations=DURATIONS)
        
        # Make the booking
        BOOKINGS[date][time_slot] = {
            'user': session['user'],
            'duration': duration,
            'booked_at': datetime.now().isoformat()
        }
        
        flash(f'Booking confirmed successfully! Your workout is scheduled for {time_slot} on {date} ({duration}).', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('book.html', time_slots=TIME_SLOTS, durations=DURATIONS)


@app.route('/api/available-slots')
def api_available_slots():
    """API endpoint to check available slots for a specific date."""
    date = request.args.get('date')
    if not date:
        return jsonify({'error': 'Date parameter required'}), 400
    
    if date not in BOOKINGS:
        available_slots = TIME_SLOTS.copy()
    else:
        available_slots = [slot for slot in TIME_SLOTS if slot not in BOOKINGS[date]]
    
    return jsonify({
        'date': date,
        'available_slots': available_slots,
        'total_slots': len(TIME_SLOTS),
        'available_count': len(available_slots)
    })


@app.route('/api/booking-status')
def api_booking_status():
    """API endpoint to get booking status for multiple dates."""
    dates = request.args.getlist('dates')
    if not dates:
        # Return next 7 days by default
        today = datetime.now()
        dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    
    status = {}
    for date in dates:
        if date not in BOOKINGS:
            available_count = len(TIME_SLOTS)
        else:
            available_count = len(TIME_SLOTS) - len(BOOKINGS[date])
        
        status[date] = {
            'total_slots': len(TIME_SLOTS),
            'booked_slots': len(BOOKINGS.get(date, {})),
            'available_slots': available_count,
            'availability_percentage': (available_count / len(TIME_SLOTS)) * 100
        }
    
    return jsonify(status)


@app.route('/schedule')
def schedule():
    """View the gym schedule."""
    # Get next 14 days
    today = datetime.now()
    schedule_data = {}
    
    for i in range(14):
        date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
        day_name = (today + timedelta(days=i)).strftime('%A')
        
        slots = {}
        for time_slot in TIME_SLOTS:
            if date in BOOKINGS and time_slot in BOOKINGS[date]:
                slots[time_slot] = 'booked'
            else:
                slots[time_slot] = 'available'
        
        schedule_data[date] = {
            'day_name': day_name,
            'slots': slots
        }
    
    return render_template('schedule.html', schedule=schedule_data, time_slots=TIME_SLOTS)


@app.route('/admin')
def admin():
    """Admin panel (for demo purposes)."""
    return render_template('admin.html', bookings=BOOKINGS, users=USERS)


@app.errorhandler(404)
def page_not_found(e):
    """404 error handler."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """500 error handler."""
    return render_template('500.html'), 500


# Template filters
@app.template_filter('datetime')
def datetime_filter(value):
    """Format datetime for templates."""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except:
            return value
    return value.strftime('%Y-%m-%d %H:%M:%S')


@app.template_filter('date')
def date_filter(value):
    """Format date for templates."""
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d').date()
        except:
            return value
    return value.strftime('%B %d, %Y')


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Run the app
    print("🏋️ Starting Demo Gym Booking Website...")
    print("📱 Visit http://localhost:5000 to access the website")
    print("👤 Demo credentials: username='demo_user', password='demo_password'")
    print("🤖 Bot target URL: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)