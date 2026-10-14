# home/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import HealthProfile, BarcodeHistory, DietPlan, ScannedProduct
import json
import cv2
import requests
import urllib.parse
try:
    from pyzbar.pyzbar import decode as pyzbar_decode
except Exception:
    pyzbar_decode = None
import random

def normalize_list(text):
    if not text:
        return []
    return [x.strip().lower() for x in text.split(",")]


def normalize_diet(diet):
    diet = diet.lower()
    if diet in ["veg", "vegetarian"]:
        return "veg"
    if diet in ["vegan"]:
        return "vegan"
    if diet in ["nonveg", "non-vegetarian"]:
        return "nonveg"
    return "veg"

CALORIE_MAP = {
    "vegetable poha": 250,
    "oats upma": 220,
    "moong dal chilla": 180,
    "sprouts chaat": 150,

    "brown rice + dal": 420,
    "chapati + mixed vegetable sabzi": 380,
    "millet khichdi": 350,

    "roti + lauki sabzi": 300,
    "vegetable khichdi": 320,
    "vegetable soup + salad": 200,

    "egg white omelette": 170,
    "boiled eggs + fruit": 250,
    "grilled chicken + salad": 400,
    "fish curry + brown rice": 450,
    "chicken soup": 280
}


INDIAN_DIET_PLANS = {
    "diabetes": {
        "veg": {
            "breakfast": [
                "vegetable poha",
                "oats upma",
                "moong dal chilla",
                "sprouts chaat"
            ],
            "lunch": [
                "brown rice + dal",
                "chapati + mixed vegetable sabzi",
                "millet khichdi"
            ],
            "dinner": [
                "roti + lauki sabzi",
                "vegetable khichdi",
                "vegetable soup + salad"
            ]
        },

        "vegan": {
            "breakfast": [
                "sprouts chaat",
                "vegetable poha (no peanuts)",
                "fruit bowl"
            ],
            "lunch": [
                "millet khichdi (no ghee)",
                "rice + vegetable curry",
                "chapati + bhindi"
            ],
            "dinner": [
                "vegetable soup",
                "roti + lauki sabzi"
            ]
        },

        "nonveg": {
            "breakfast": [
                "egg white omelette",
                "boiled eggs + fruit",
                "vegetable omelette"
            ],
            "lunch": [
                "grilled chicken + salad",
                "fish curry + brown rice",
                "chicken dalia"
            ],
            "dinner": [
                "chicken soup",
                "grilled fish + vegetables"
            ]
        }
    },

    "bp": {
        "veg": {
            "breakfast": ["idli", "vegetable upma", "fruit bowl"],
            "lunch": ["chapati + sabzi", "rice + dal (low salt)"],
            "dinner": ["vegetable soup", "roti + bhindi"]
        },

        "vegan": {
            "breakfast": ["fruit bowl", "oats porridge (water)"],
            "lunch": ["rice + vegetable curry", "chapati + lauki"],
            "dinner": ["vegetable soup"]
        },

        "nonveg": {
            "breakfast": ["boiled eggs", "egg white omelette"],
            "lunch": ["grilled fish + rice", "chicken curry (low salt)"],
            "dinner": ["chicken soup"]
        }
    },

    "thyroid": {
        "veg": {
            "breakfast": ["fruit bowl", "oats porridge"],
            "lunch": ["chapati + dal", "rice + sabzi"],
            "dinner": ["light khichdi"]
        },

        "vegan": {
            "breakfast": ["fruit bowl"],
            "lunch": ["rice + vegetable curry"],
            "dinner": ["vegetable soup"]
        },

        "nonveg": {
            "breakfast": ["boiled eggs"],
            "lunch": ["chicken curry + rice"],
            "dinner": ["grilled fish"]
        }
    }
}

ALLERGY_FILTERS = {
    "nuts": ["peanut", "cashew", "almond", "nut"],
    "gluten": ["wheat", "roti", "bread", "poha"],
    "lactose": ["milk", "curd", "paneer", "buttermilk"],
    "soy": ["soy", "soya"],
    "egg": ["egg", "omelette"],
}

# ==================== BASIC VIEWS ====================

# home/views.py
def home_page(request):
    return render(request, 'home/index.html', {'user': request.user}) 

# ==================== AUTHENTICATION VIEWS ====================

@csrf_exempt
def ajax_login(request):
    """Handle AJAX login requests"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'username': user.username,
                    'email': user.email
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid username or password'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def ajax_signup(request):
    """Handle AJAX signup requests"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Username already exists'
                })
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Email already registered'
                })
            
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Auto login after signup
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'username': user.username,
                'email': user.email
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def get_profile(request):
    return JsonResponse({
        "username": request.user.username,
        "email": request.user.email
    })

@login_required
def get_health_summary(request):
    profile = HealthProfile.objects.filter(user=request.user).first()

    if not profile:
        return JsonResponse({"exists": False})

    return JsonResponse({
        "exists": True,
        "condition": profile.health_conditions or "None",
        "allergies": profile.allergies or "None",
        "diet": profile.dietary_restrictions or "Not set"
    })

@login_required
def get_user_history(request):
    history = BarcodeHistory.objects.filter(user=request.user).order_by('-scanned_at')

    data = []
    for item in history:
        data.append({
            "product": item.product_name,
            "barcode": item.barcode,
            "time": item.scanned_at.strftime("%d %b %Y %H:%M")
        })

    return JsonResponse({"history": data})


def logout_view(request):
    """Handle logout"""
    logout(request)
    return redirect('home')

# ==================== HEALTH PROFILE VIEWS ====================

@csrf_exempt
@login_required
def save_health_profile(request):
    if request.method == "POST":
        data = json.loads(request.body)

        profile, created = HealthProfile.objects.get_or_create(user=request.user)

        profile.health_conditions = data.get("condition", "")
        profile.allergies = data.get("allergies", "")
        profile.dietary_restrictions = data.get("diet", "")
        profile.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False})


# ==================== PRODUCT VIEWS ====================

@csrf_exempt
def ajax_save_product(request):
    """Save scanned product to user's history"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            if request.user.is_authenticated:
                barcode = data.get("barcode") or data.get("barcode_number") or ""
                name = data.get("name") or data.get("product_name") or "Unknown Product"
                nutri_str = json.dumps(data.get("nutrition", {}))
                
                # Create history entry
                history = BarcodeHistory.objects.create(
                    user=request.user,
                    barcode=barcode,
                    product_name=name
                )
                
                # Create scanned product entry
                ScannedProduct.objects.create(
                    user=request.user,
                    barcode=barcode,
                    product_name=name,
                    nutritional_info=nutri_str
                )
                
                return JsonResponse({
                    'success': True,
                    'product_id': history.id,
                    'message': 'Product saved successfully to history'
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'Product scanned as guest (log in to save history)'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# ==================== DIET PLAN VIEWS ====================

def estimate_calories(meal_list):
    total = 0
    for meal in meal_list:
        total += CALORIE_MAP.get(meal, 250)  # safe fallback
    return total


def generate_indian_diet(condition, allergies, diet_type):
    condition = condition.lower()

    if "diabetes" in condition:
        condition = "diabetes"
    elif "bp" in condition or "pressure" in condition:
        condition = "bp"
    elif "thyroid" in condition:
        condition = "thyroid"
    else:
        condition = "diabetes"

    diet_type = normalize_diet(diet_type)
    allergies = normalize_list(allergies)

    disease_plan = INDIAN_DIET_PLANS.get(condition)
    diet_plan = disease_plan.get(diet_type) or disease_plan["veg"]

    final_plan = {}

    for meal, options in diet_plan.items():
        random.shuffle(options)
        safe_items = []

        for food in options:
            blocked = False
            for allergy in allergies:
                for bad in ALLERGY_FILTERS.get(allergy, []):
                    if bad in food:
                        blocked = True
            if not blocked:
                safe_items.append(food)

        if not safe_items:
            safe_items = options

        final_plan[meal] = random.sample(
            safe_items,
            min(2, len(safe_items))
        )

    return final_plan



@login_required
def get_diet_plan(request):
    profile = HealthProfile.objects.get(user=request.user)

    diet_plan = generate_indian_diet(
        condition=profile.health_conditions or "",
        allergies=profile.allergies or "",
        diet_type=profile.dietary_restrictions or ""
    )


    return JsonResponse({
        "meals": [
            {
                "title": " / ".join(diet_plan["breakfast"]),
                "calories": estimate_calories(diet_plan["breakfast"])
            },
            {
                "title": " / ".join(diet_plan["lunch"]),
                "calories": estimate_calories(diet_plan["lunch"])
            },
            {
                "title": " / ".join(diet_plan["dinner"]),
                "calories": estimate_calories(diet_plan["dinner"])
            }
        ],
        "note": "Personalized Indian diet generated dynamically"
    })


# ==================== ALTERNATIVES VIEWS ====================

def is_high_risk(product, health):
    sugar = product.get("nutrition", {}).get("sugar", 0)
    fat = product.get("nutrition", {}).get("fat", 0)
    nutri = product.get("nutriScore", "C")

    condition = health.get("condition", "").lower()

    if "diabetes" in condition and sugar > 10:
        return True
    if "bp" in condition and fat > 15:
        return True
    if nutri in ["D", "E"]:
        return True

    return False

@csrf_exempt
@login_required
def ajax_alternatives(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_name = data.get("name", "")
            sugar = float(data.get("nutrition", {}).get("sugar", {}).get("value", 0))
            fat = float(data.get("nutrition", {}).get("fat", {}).get("value", 0))

            profile = HealthProfile.objects.get(user=request.user)
            condition = (profile.health_conditions or "").lower()

            harmful = False
            reason = ""

            # Simple rule engine (works well in hackathon)
            if "diabetes" in condition and sugar > 10:
                harmful = True
                reason = "High sugar not suitable for diabetes"

            if "bp" in condition and fat > 20:
                harmful = True
                reason = "High fat not suitable for BP patients"

            alternatives = []

            if harmful:
                # Fetch healthier alternatives from OpenFoodFacts
                try:
                    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={urllib.parse.quote(product_name)}&search_simple=1&json=1&page_size=5"
                    headers = {"User-Agent": "NutriHealthApp/1.0 (nutrihealth@local.dev)"}
                    res = requests.get(url, headers=headers, timeout=5)
                    result = res.json()

                    for item in result.get("products", [])[:3]:
                        alternatives.append({
                            "name": item.get("product_name", "Unknown"),
                            "brand": item.get("brands", "Unknown"),
                            "nutriscore": item.get("nutriscore_grade", "N/A")
                        })
                except Exception as api_err:
                    print(f"Error querying alternatives: {api_err}")

            return JsonResponse({
                "harmful": harmful,
                "reason": reason,
                "alternatives": alternatives
            })

        except Exception as e:
            return JsonResponse({"error": str(e)})

# ==================== BARCODE & QR SCAN VIEW ====================

def scan_barcode_and_get_food(request):
    """Scan barcode or QR code using camera and get product info"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return JsonResponse({
            "success": False,
            "error": "Could not access computer camera. Please use browser camera or enter barcode manually."
        }, status=200)

    qr_detector = cv2.QRCodeDetector()
    try:
        barcode_detector = cv2.barcode.BarcodeDetector()
    except Exception:
        barcode_detector = None

    detected_code = None
    frames_checked = 0
    max_frames = 60  # Scan for max ~2-3 seconds to prevent freezing the server

    try:
        while frames_checked < max_frames:
            ret, frame = cap.read()
            frames_checked += 1
            if not ret or frame is None:
                continue

            # 1. Try OpenCV native 1D barcode detector
            if barcode_detector is not None:
                try:
                    res = barcode_detector.detectAndDecode(frame)
                    # OpenCV 5 returns (decoded_info, decoded_type, points)
                    info = res[0]
                    if isinstance(info, (list, tuple)):
                        for code_str in info:
                            if code_str and str(code_str).strip():
                                detected_code = str(code_str).strip()
                                break
                    elif isinstance(info, str) and info.strip():
                        detected_code = info.strip()
                    if detected_code:
                        break
                except Exception:
                    pass

            # 2. Try OpenCV QR Code detector
            try:
                data, _, _ = qr_detector.detectAndDecode(frame)
                if data and data.strip():
                    detected_code = data.strip()
                    break
            except Exception:
                pass

            # 3. Try pyzbar if available
            if pyzbar_decode is not None:
                try:
                    barcodes = pyzbar_decode(frame)
                    if barcodes:
                        detected_code = barcodes[0].data.decode("utf-8").strip()
                        break
                except Exception:
                    pass
    finally:
        cap.release()
        cv2.destroyAllWindows()

    if not detected_code:
        return JsonResponse({
            "success": False,
            "message": "No barcode or QR code detected. Ensure good lighting and hold the code steadily in front of the camera."
        }, status=200)

    # If the code is a URL, extract barcode if present in query parameters
    barcode_to_query = detected_code
    if detected_code.startswith("http://") or detected_code.startswith("https://"):
        try:
            parsed = urllib.parse.urlparse(detected_code)
            params = urllib.parse.parse_qs(parsed.query)
            for k in ["barcode", "gtin", "ean", "code", "id"]:
                if k in params:
                    barcode_to_query = params[k][0]
                    break
        except Exception:
            pass

    # Query OpenFoodFacts with required User-Agent
    headers = {"User-Agent": "NutriHealthApp/1.0 (nutrihealth@local.dev)"}
    try:
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_to_query}.json"
        data = requests.get(url, headers=headers, timeout=5).json()

        if data.get("status") == 1:
            product = data.get("product", {})
            return JsonResponse({
                "success": True,
                "barcode": barcode_to_query,
                "raw_code": detected_code,
                "product_name": product.get("product_name") or product.get("product_name_en") or "Unknown Product",
                "brand": product.get("brands") or "N/A",
                "nutriscore": (product.get("nutriscore_grade") or "N/A").upper(),
                "ingredients": product.get("ingredients_text") or "",
                "nutrition": {
                    "calories": product.get("nutriments", {}).get("energy_kcal_100g", "N/A"),
                    "protein": product.get("nutriments", {}).get("proteins_100g", "N/A"),
                    "carbs": product.get("nutriments", {}).get("carbohydrates_100g", "N/A"),
                    "fiber": product.get("nutriments", {}).get("fiber_100g", "N/A"),
                    "sugar": product.get("nutriments", {}).get("sugars_100g", "N/A"),
                    "fat": product.get("nutriments", {}).get("fat_100g", "N/A")
                }
            })

        return JsonResponse({
            "success": True,
            "barcode": barcode_to_query,
            "raw_code": detected_code,
            "message": f"Code '{barcode_to_query}' was detected, but it is not listed in the food database."
        })
    except Exception as e:
        return JsonResponse({
            "success": True,
            "barcode": barcode_to_query,
            "raw_code": detected_code,
            "message": f"Code '{barcode_to_query}' detected. Could not reach product database: {str(e)}"
        })