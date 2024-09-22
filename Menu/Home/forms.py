from django import forms

class userDetailFormDineIn(forms.Form):
    
        name = forms.CharField(max_length=100,required= True)
        phoneNo = forms.CharField(max_length=15,required= True)
        otp = forms.CharField(max_length=6,required= True)
    
class userDetailFormDriveThru(userDetailFormDineIn):
        vehicleNo = forms.CharField( max_length=15, required=True)
        vehicleName = forms.CharField( max_length=20, required=True)
