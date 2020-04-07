import json

from django.utils import timezone
from django.http import JsonResponse
from oauth2_provider.models import AccessToken

from foodtaskerapp.models import Restaurant, Meal, Order, OrderDetails
from foodtaskerapp.serializers import RestaurantSerializer, MealSerializer

def customer_get_restaurants(request):
	restaurants = RestaurantSerializer(
		Restaurant.objects.all().order_by("-id"),
		many = True,
		context = {"request": request}
		).data

	return JsonResponse({"restaurants": restaurants})

def customer_get_meals(reuqest):
		meals = MealSerializer(
			Meal.objects.filter(restaurant_id = restaurant_id).order_by("-id"),
			many = True,
			context = {"request": request}
			)
		return JsonResponse({"meals": meals})

def customer_add_order(reuqest):

	"""
		params:
			access_token
			restaurant_id
			address
			order_details (json format), example:
				{{"meal_id":1, "quantity": 2},{"meal_id": 2, "quantity": 3}}

			retun 
			{"status": "success"}


	"""
	if request.method == "POST":
		access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
			expires_gt = timezone.now())


		customer =access_token.user.customer

		if Order.objects.filter(customer = customer).exclude(status = Order.DELIVERED):
			return JsonResponse({"status": "fail", "error": "Your last order must be completed"})

		if not request.POST["address"]:
			return JsonResponse({"status": "failed", "error": "Address is required."})

		order_details = json.load(request.POST["order_details"])

		order_total = 0
		for meal in order_details:
			order_total += Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"]

		if len(order_details) > 0:
			#STEP 1 -Create Order
			order = Order.objects.create(
				customer = customer,
				restaurant_id = request.POST["restaurant_id"],
				total = order_total,
				status = Order.COOKING,
				address = request.POST["address"]
				)

			#STEP 2 - Create order details

			for meal in order_details:
				OrderDetails.objects.create(
					order = order,
					meal_id = meal["meal_id"],
					quantity = meal["quantity"],
					sub_total = Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"]
					)
			return JsonResponse({"status": "success"})

def customer_get_latest_order(reuqest):
		return JsonResponse({})