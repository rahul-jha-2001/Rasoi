import razorpay
client = razorpay.Client(auth=("rzp_test_0TCgKYha7Z1qmJ", "A395cCxvpe09LgrsD2lHAfvl"))
client.set_app_details({"title" : "django", "version" : "1.8.17"})


order =  client.order.create({
  "amount": 50000,
  "currency": "INR",
  "receipt": "receipt#1",
  "partial_payment":False,
  "notes": {
    "key1": "value3",
    "key2": "value2"
  }
})
print(order)