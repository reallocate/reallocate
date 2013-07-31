from website import settings
import website.base as base
from urllib import urlencode
from urllib2 import urlopen, Request
from django.http import HttpResponse

# TODO: verify that this is not a duplicate message from paypal - not an issue with money, but we
# could give people double credit for a single donation

# code taken + modified from http://kbeezie.com/paypal-ipn-python/
# sandbox acct is testsandbox@reallocate.org/pw=sandboxtest

def verify_ipn(data):
	# prepares provided data set to inform PayPal we wish to validate the response
	data["cmd"] = "_notify-validate"
	params = urlencode(data)

	# sends the data and request to the PayPal Sandbox
    # TODO: change off of sandbox for testing
	req = Request("""https://www.sandbox.paypal.com/cgi-bin/webscr""", params)
	req.add_header("Content-type", "application/x-www-form-urlencoded")
	# reads the response back from PayPal
	response = urlopen(req)
	status = response.read()

	# If not verified
	if not status == "VERIFIED":
		return False

	# if not the correct receiver ID TODO: replace with receiver ID for reallocate (secure merchant ID)
	if not data["receiver_id"] == settings.PAYPAL_MERCHANT_ID:
		return False

	# if not the correct currency
	if not data["mc_currency"] == "USD":
		return False

	return True

def receive_paypal(request):
    if request.method == "GET":
        return HttpResponse("This url is meant to be used with POST")
        
    """ receive paypal messages """
    data = request.POST.dict()
    
    # If there is no txn_id in the received arguments don't proceed
    if not "txn_id" in data:
        return "No Parameters"

    # Verify the data received with Paypal
    if not verify_ipn(data):
        return "Unable to Verify"

    # If verified, store desired information about the transaction
    reference = data["txn_id"]
    amount = data["mc_gross"]
    email = data["payer_email"]
    name = data["first_name"] + " " + data["last_name"]
    status = data["payment_status"]

    print "payment received"

    # TODO: write that this ocurred
    
