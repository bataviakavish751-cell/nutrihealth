# 🥗 NutriHealth - Smart Nutrition & Barcode Guidance

**NutriHealth** is an AI-powered nutrition and diet guidance web application built with **Django**. It enables users to scan food packaging barcodes and QR codes, inspect complete nutritional profiles, evaluate personal health risks (such as Diabetes and High Blood Pressure), discover healthier food alternatives, and generate personalized Indian diet plans based on their unique medical conditions and allergies.

---

## ✨ Key Features

### 📷 1. Multi-Mode Barcode & QR Code Scanner
- **Live In-Browser Camera Scanner:** Uses `html5-qrcode` to scan both **1D food barcodes** (EAN-13, EAN-8, UPC-A, UPC-E, Code-128) and **2D QR codes** in real time.
- **Packet Photo Upload:** Upload or take a clear photo of food packaging for instant barcode decoding—ideal for glossy or curved plastic packets where webcams struggle with autofocus.
- **OpenCV Server Camera:** Server-side scan powered by OpenCV's built-in `cv2.barcode.BarcodeDetector` and `cv2.QRCodeDetector`.
- **Smart URL/QR Handler:** Extracts barcode parameters from promotional and FSSAI QR links on packets.
- **Instant Test Samples:** One-click test buttons for popular products (*Coca-Cola, Nutella, Lay's Classic, Maggi Noodles*).

### 📊 2. Nutritional Analysis & Nutri-Score
- Fetches detailed nutrient information per 100g: Calories, Protein, Carbohydrates, Dietary Fiber, Sugars, and Total Fat.
- Visual **Nutri-Score badge** (`A` through `E`) based on global nutrition benchmarks.
- Powered by the **OpenFoodFacts API** with automated fallback to the **Spoonacular Food API**.

### 🩺 3. Health Risk Evaluation & Alternatives
- Compares scanned food against the user's active **Health Profile**:
  - **Diabetes:** Flags products with high sugar (> 10g per 100g).
  - **High Blood Pressure (BP):** Flags products with high saturated fat (> 20g per 100g).
- Suggests **healthier product alternatives** in the same food category with better Nutri-Scores.

### 🍛 4. Personalized Indian Diet Planner
- Generates tailored daily meal plans for **Breakfast**, **Lunch**, and **Dinner**.
- Tailored to:
  - **Health Condition:** Diabetes, Hypertension (High BP), Thyroid.
  - **Dietary Preference:** Vegetarian, Vegan, Non-Vegetarian.
  - **Allergy Filter:** Excludes foods containing allergens like Nuts, Gluten, Lactose, Soy, or Egg.
  - **Calorie Estimation:** Estimates total meal calories dynamically.

### 👤 5. User Profiles & Scan History
- User registration and AJAX authentication.
- Automatically saves scanned products to user history in the database.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.12+, Django 6.x |
| **Database** | SQLite3 |
| **Computer Vision** | OpenCV (`opencv-python`), `pyzbar` |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), FontAwesome 6 |
| **Client-Side Scanner**| `html5-qrcode` |
| **External APIs** | OpenFoodFacts API (Free, open-source), Spoonacular API |

---

## 📁 Project Structure

```text
django_project/
├── myproject/
│   ├── db.sqlite3                  # SQLite Database
│   ├── manage.py                   # Django Management Script
│   ├── myproject/                  # Project Configuration
│   │   ├── settings.py             # Settings & Middleware
│   │   ├── urls.py                 # Root URL Routing
│   │   ├── wsgi.py                 # WSGI entry point
│   │   └── asgi.py                 # ASGI entry point
│   └── home/                       # Main Application
│       ├── models.py               # HealthProfile, BarcodeHistory, DietPlan, ScannedProduct
│       ├── views.py                # Scanner logic, Diet generator, Alternatives engine
│       ├── urls.py                 # App URL patterns (/scan/, /diet-plan/, etc.)
│       ├── static/                 # Static CSS & JS assets
│       │   └── home/
│       │       ├── style.css
│       │       └── script.js
│       └── templates/              # HTML Templates
│           └── home/
│               └── index.html      # Single Page Application Frontend
└── README.md                       # Project Documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ (Python 3.12 or 3.14 recommended)
- Web browser with camera permissions enabled (Chrome, Edge, Firefox, or Safari)

### 2. Installation

1. Open a terminal in the project directory:
   ```powershell
   cd D:\django_project\myproject
   ```

2. Install dependencies:
   ```powershell
   pip install django opencv-python pyzbar requests
   ```

3. Run database migrations:
   ```powershell
   python manage.py migrate
   ```

4. Verify system check:
   ```powershell
   python manage.py check
   ```

### 3. Run the Development Server

Start the local server:
```powershell
python manage.py runserver
```

Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

---

## 📖 How to Use the App

1. **Set Up Your Health Profile:**
   - Scroll to the **"Know Yourself"** section.
   - Enter your medical conditions (e.g. *Diabetes*, *BP*), dietary preference (*Veg / Vegan / Non-Veg*), and any allergies (*Gluten, Lactose, Nuts*).
2. **Scan a Food Packet:**
   - Go to the **"Scan Products"** section.
   - Choose one of the scanning options:
     - Click **"Start Live Camera"** to scan a packet barcode in front of your webcam or phone camera.
     - Click **"Upload Packet Photo"** to select a photo of the packet's barcode.
     - Type in a 13-digit barcode manually or click any **Quick test** button (e.g. *Coca-Cola*).
3. **Review Results:**
   - View the Nutri-Score, macro breakdown, and safety status.
   - If the food is flagged as unsuitable for your condition, browse the **"Healthier Alternatives"** recommendations below.
4. **Get Your Diet Plan:**
   - Scroll to **"Your Diet Plan"** to view customized meal suggestions for the day.

---

## 🔌 API Integrations

- **OpenFoodFacts API (Primary):**
  - Endpoint: `https://world.openfoodfacts.org/api/v0/product/<barcode>.json`
  - Free and open database requiring no secret API key.
- **Spoonacular API (Fallback):**
  - Endpoint: `https://api.spoonacular.com/food/products/barcode/<barcode>?apiKey=<API_KEY>`
  - Configured in `index.html` as an automated fallback for unlisted items.

---

## 📄 License
This project is developed for educational and health-awareness purposes.
