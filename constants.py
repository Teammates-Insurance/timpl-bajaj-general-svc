import os

SERVICE_BASE_URL = os.environ.get(
    "SERVICE_BASE_URL", "http://webservicesint.bajajallianz.com/"
)

PAYMENT_CALLBACK_URL = (
    os.environ.get(
        "PAYMENT_CALLBACK_URL",
        "https://crm.insurancekarlo.com/process-response.php",
    )
    + "?"
)

UserID = os.environ.get("UserID", "webservice@real.com")
AuthToken = os.environ.get("AuthToken", "newpas12")
PamentURL = os.environ.get(
    "PamentURL",
    "http://webservicesint.bajajallianz.com/Insurance/WS/new_cc_payment.jsp",
)

ENDPOINTS = {
    "webservice": "BjazMotorWebservice/",
    "download": "BjazDownloadPDFWs/policypdfdownload",
    "payment": "Insurance/WS/new_cc_payment.jsp",
    "pingeneration": "BagicMotorWS/BagicMotorWSPort?WSDL",
}

API_PAYMENT_URL = (
    PamentURL + "?requestId={}&Username=" + UserID + "&sourceName=WS_MOTOR"
)
API_BASE_URL = SERVICE_BASE_URL + ENDPOINTS.get("webservice")
API_DOWNLOAD_URL = SERVICE_BASE_URL + ENDPOINTS.get("download")

VEHICLE_MASTER = API_BASE_URL + "getallvehiclemaster"
VEHICLE_MAKE = API_BASE_URL + "getallvehiclemake"
CALCULATE_PREMIUM = API_BASE_URL + "calculatemotorpremiumsig"
ISSUE_POLICY = API_BASE_URL + "issuepolicy"
TRANS_STATUS = API_BASE_URL + "getpgtransstatus"
RENEWAL_DATA = API_BASE_URL + "getrnwdata"


PROVIDER_NAME = "bajaj-general"
POLICYHOLDERTYPE = ["individual", "corporate"]
INSURANCETYPELIST = ["comprehensive", "tp", "saod"]
PRODUCTS_OFFERED = ["car", "bike", "commercial"]
SUB_PRODUCTS_OFFERED = ["pcv", "gcv", "misc"]

ncbObj = {"0.00": 0, "20.00": 20, "25.00": 25, "35.00": 35, "45.00": 45, "50.00": 50}

SUB_PRODUCTS_OBJ = {
    "pcv": "passenger carrying",
    "gcv": "goods carrying",
    "misc": "miscellaneous",
    "trailer": "trailer",
}

POLICYTYPE = {"new": "1", "renewal": "2", "rollover": "3"}

PRODUCT_CODE_TYPES = {
    "car": {
        "comprehensive": "1801",
        "tp": "1805",
        "saod": "1870",
        "new": "1825",
        "vehicleTypeCode": "22",
    },
    "bike": {
        "comprehensive": "1802",
        "tp": "1806",
        "saod": "1871",
        "new": "1826",
        "vehicleTypeCode": "21",
    },
    "commercial": {
        "comprehensive": "1803",
        "tp": "1831",
        "saod": None,
        "new": None,
        "vehicleTypeCode": None,
    },
}

FUEL_TYPE = {"petrol": "P", "diesel": "D", "cng": "C", "lpg": "C"}

V_TYPE = {"car": 4, "bike": 2, "commercial": 6}
POLICYHOLDERTYPEObj = {"individual": "P", "corporate": "I"}

PIN_STATUS_LIST = {
    "PIN_APPRD": "PIN APPROVED",
    "PGNR_PNDNG": "PIN PENDING FOR APPROVAL",
    "PIN_RJTD": "PIN REJECTED",
    "PIN_ONHOLD": "PIN ONHONLD",
    "PIN_CLS": "PIN CLOSE",
    "PGNR_ALTD": "PIN GENERATED,AGENCY ALLOCATED",
    "DOC_PNDNG": "DOC\IMG UPLOADING PENDING",
    "PIN_ISSD": "PIN ISSUED",
}

VEHICLE_MASTER_BODY = {"productcode": ""}

VEHICLE_MAKE_BODY = {"productcode": "", "vehiclemake": ""}

POLICY_DOWNLOAD_BODY = {
    "pdfmode": "WS_POLICY_PDF",
    "policynum": "",
}

POLICY_RENEWAL_BODY = {"poltype": "2", "prvpolicyref": "", "registrationno": ""}

motorProfileValidation = [
    "rtoLoc",
    "make",
    "isNew",
    "model",
    "variant",
    "fuelType",
    "registrationNo",
    "cc",
    "manufactureDate",
    "purchaseDate",
    "registrationDate",
]

commonAttributeValidation = [
    "enquiryId",
    "productType",
    "insuranceType",
    "policyHolderType",
    "riskStartDate",
    "riskEndDate",
]

personalInfoValidation = [
    "email",
    "firstName",
    "lastName",
    "mobile",
    "dob",
    "maritalStatus",
    "gender",
]

corporateValidation = []
addressValidation = ["addressLine1", "addressLine2", "city", "state"]
paymentValidation = ["proposalId"]
policyValidation = ["policyNo", "enquiryId"]
renewalValidation = ["policyNo", "registrationNo"]
POLICYDOWNLOADTYPE = "content"