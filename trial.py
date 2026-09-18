# =========================================================
# SMART FARMER PROCUREMENT - SIMULATED IVR SYSTEM
# (Simulates a phone call using text input instead of a keypad)
# =========================================================
import pickle
from datetime import datetime

AGRI_STACK_FILE = "agristack_farmers.dat"   # pretend "AgriStack" government database
BOOKINGS_FILE = "bookings.dat"              # our own booking records

# ---------------------------------------------------------
# STEP 0: Fake AgriStack database (in real life, this data
# already exists in the government system - we're just
# pretending to look it up, like the real IVR would).
# ---------------------------------------------------------
def setup_fake_agristack():
    """Creates sample farmer records so we have something to look up."""
    farmers = {
        "1001": {"name": "Ramesh Kumar", "village": "Kheda", "crop": "Paddy", "estimated_tonnes": 5},
        "1002": {"name": "Sita Devi", "village": "Rampur", "crop": "Wheat", "estimated_tonnes": 3},
        "1003": {"name": "Mohan Lal", "village": "Bhiarpur", "crop": "Maize", "estimated_tonnes": 7},
    }
    with open(AGRI_STACK_FILE, "wb") as f:
        pickle.dump(farmers, f)

def load_agristack():
    with open(AGRI_STACK_FILE, "rb") as f:
        return pickle.load(f)

# ---------------------------------------------------------
# STEP 1: Booking storage helpers (same style as your
# pickle-based encryption project)
# ---------------------------------------------------------
def load_bookings():
    try:
        with open(BOOKINGS_FILE, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return []

def save_bookings(bookings):
    with open(BOOKINGS_FILE, "wb") as f:
        pickle.dump(bookings, f)

# ---------------------------------------------------------
# STEP 2: Daily slot capacity (Token Engine, from your slide)
# ---------------------------------------------------------
SLOT_CAPACITY = 5  # max farmers per time window, for demo purposes

def count_bookings_in_slot(bookings, time_window):
    return sum(1 for b in bookings if b["time_window"] == time_window)

# ---------------------------------------------------------
# STEP 3: The core "IVR CALL" simulation
# ---------------------------------------------------------
def simulate_call():
    print("\n📞  Incoming call to 1800-1234-5678 (AgriStack Procurement Line)")
    print("🔊  'Welcome. Please enter your AgriStack enrolment number.'")
    enrolment_no = input("👉 Enter enrolment number: ").strip()

    agristack = load_agristack()

    if enrolment_no not in agristack:
        print("🔊  'Sorry, we could not find your enrolment. Please contact your local agent.'")
        return

    profile = agristack[enrolment_no]
    print(f"\n🔊  'Hello {profile['name']} from {profile['village']}.'")
    print(f"🔊  'Your registered crop: {profile['crop']}, estimated {profile['estimated_tonnes']} tonnes.'")

    print("\n🔊  IVR MENU:")
    print("   1. Book a Pickup")
    print("   2. Check Market Price")
    print("   3. Reschedule Pickup")
    print("   4. Speak to an Agent")
    choice = input("👉 Press a number: ").strip()

    bookings = load_bookings()

    if choice == "1":
        book_pickup(enrolment_no, profile, bookings)
    elif choice == "2":
        check_price(profile["crop"])
    elif choice == "3":
        reschedule_pickup(enrolment_no, bookings)
    elif choice == "4":
        print("🔊  'Connecting you to an agent... (simulated)'")
    else:
        print("🔊  'Invalid option. Goodbye.'")

# ---------------------------------------------------------
# STEP 4: Booking a pickup (Token Engine + Slot Rules)
# ---------------------------------------------------------
def book_pickup(enrolment_no, profile, bookings):
    print("\n🔊  'Let's book your pickup.'")
    quantity = input("👉 Confirm actual quantity in tonnes: ").strip()

    print("🔊  'Choose pickup window: 1-Morning, 2-Midday, 3-Afternoon'")
    window_choice = input("👉 Press a number: ").strip()
    windows = {"1": "Morning", "2": "Midday", "3": "Afternoon"}
    time_window = windows.get(window_choice, "Morning")

    # Check slot capacity (Daily Capacity rule from your slide)
    current_count = count_bookings_in_slot(bookings, time_window)
    if current_count >= SLOT_CAPACITY:
        print(f"🔊  '{time_window} slot is full. You've been added to the waitlist.'")
        status = "Waitlisted"
    else:
        status = "Confirmed"

    notes = input("👉 Any special notes (or press Enter to skip): ").strip()

    booking_ref = f"BK{len(bookings) + 1:04d}"
    token = current_count + 1

    new_booking = {
        "enrolment_no": enrolment_no,
        "name": profile["name"],
        "village": profile["village"],
        "crop": profile["crop"],
        "quantity": quantity,
        "time_window": time_window,
        "notes": notes,
        "booking_ref": booking_ref,
        "token": token,
        "status": status,
        "date_booked": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    bookings.append(new_booking)
    save_bookings(bookings)

    # Simulated SMS confirmation (Communication layer from your slide)
    print("\n📩 SMS Sent:")
    print(f"   Dear {profile['name']}, Booking Ref: {booking_ref}, Token: {token}")
    print(f"   Pickup Window: {time_window}, Status: {status}")
    print(f"   Crop: {profile['crop']}, Quantity: {quantity} tonnes\n")

# ---------------------------------------------------------
# STEP 5: Check market price (dummy Mandi price data)
# ---------------------------------------------------------
def check_price(crop):
    prices = {"Paddy": 2310, "Wheat": 2125, "Maize": 1962}
    price = prices.get(crop, 2000)
    print(f"\n🔊  'Current price for {crop} is ₹{price} per quintal at your nearest mandi.'\n")

# ---------------------------------------------------------
# STEP 6: Reschedule an existing booking
# ---------------------------------------------------------
def reschedule_pickup(enrolment_no, bookings):
    existing = [b for b in bookings if b["enrolment_no"] == enrolment_no]
    if not existing:
        print("🔊  'No existing booking found for you.'")
        return

    print("🔊  'Choose new pickup window: 1-Morning, 2-Midday, 3-Afternoon'")
    window_choice = input("👉 Press a number: ").strip()
    windows = {"1": "Morning", "2": "Midday", "3": "Afternoon"}
    new_window = windows.get(window_choice, "Morning")

    existing[-1]["time_window"] = new_window
    save_bookings(bookings)
    print(f"🔊  'Your pickup has been rescheduled to {new_window}.'\n")

# ---------------------------------------------------------
# STEP 7: Simple "admin dashboard" - view all bookings
# ---------------------------------------------------------
def admin_dashboard():
    bookings = load_bookings()
    if not bookings:
        print("\n📊 No bookings yet.\n")
        return
    print("\n📊 ---- PROCUREMENT DASHBOARD ----")
    print(f"{'Token':<6}{'Name':<15}{'Village':<12}{'Crop':<10}{'Qty':<6}{'Window':<10}{'Status'}")
    for b in bookings:
        print(f"{b['token']:<6}{b['name']:<15}{b['village']:<12}{b['crop']:<10}{b['quantity']:<6}{b['time_window']:<10}{b['status']}")
    print(f"\nTotal Bookings: {len(bookings)}\n")

# ---------------------------------------------------------
# MAIN MENU - lets you simulate multiple calls, or view dashboard
# ---------------------------------------------------------
def main():
    setup_fake_agristack()  # reset sample data each run
    while True:
        print("\n========== FARMER PROCUREMENT SYSTEM ==========")
        print("1. Simulate a Farmer Call (IVR)")
        print("2. View Admin Dashboard")
        print("3. Exit")
        choice = input("👉 Enter your choice: ").strip()

        if choice == "1":
            simulate_call()
        elif choice == "2":
            admin_dashboard()
        elif choice == "3":
            print("Thank you for using the system!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
