import config
import validate
import json
import constants
from datetime import date
from fuzzywuzzy import fuzz, process
from utils import Utils
import readData

Utils_obj = Utils()
Code = Utils_obj.httpStatusCodes()


def getVehiclesByMake(payload):
    body = Utils_obj.update(constants.VEHICLE_MAKE_BODY, payload)
    respStatus, vehicleResp = Utils_obj.execute_request(constants.VEHICLE_MAKE, body)
    if not respStatus:
        return False, vehicleResp
    return True, vehicleResp.get("vehiclemasterlist")


# @lru_cache(maxsize=1000)
def vehiclemodelcode(mProfile, pType, pSubType):
    if pType == "commercial":
        status, cvResponse = readData.get_vehicle_details(mProfile, pSubType)
        return status, cvResponse
    make = mProfile.get("make")
    fuel = mProfile.get("fuelType").lower()
    vehicleId = mProfile.get("vehicleId")
    cc = mProfile.get("cc")
    model = mProfile.get("model").lower()
    variant = mProfile.get("variant").lower()

    pCode = constants.PRODUCT_CODE_TYPES.get(pType).get("comprehensive")

    vehicleReqBody = {"productcode": pCode, "vehiclemake": make}
    status, data = getVehiclesByMake(vehicleReqBody)

    if not status:
        return False, {"code": 401, "error_message": data.get("error_message")}

    if not data:
        return False, {"code": 400, "error_message": "Vehicle details not found"}

    if vehicleId:
        vehicleList = [d for d in data if d["vehiclecode"] == vehicleId]
        if not vehicleList:
            return False, {"code": 400, "error_message": "Vehicle details not found"}

        return True, vehicleList[0]
    else:
        vehicleList = [d for d in data if d["fuel"] == constants.FUEL_TYPE.get(fuel)]

        model_set = set()
        subtype_set = set()
        for d in vehicleList:
            model_set.add(d.get("vehiclemodel").lower())

        print("#######")
        print(model_set)
        print(model+ " "+variant)
        modelSort = process.extractOne(model+ " "+variant, model_set, scorer=fuzz.token_sort_ratio)
        print("#######")
        print(modelSort)

        vehicleList = [
            d for d in vehicleList if d["vehiclemodel"].lower() == modelSort[0]
        ]

        if not vehicleList:
            return False, {"code": 400, "error_message": "Vehicle details not found"}

        # vehicleList = [d for d in vehicleList if d["cubiccapacity"] == cc]

        # if not vehicleList:
        #     return False, {"code": 400, "error_message": "Vehicle details not found"}

        for d in vehicleList:
            subtype_set.add(d.get("vehiclesubtype").lower())

        subtype = process.extract(variant, subtype_set, scorer=fuzz.token_sort_ratio)
        print("#######")
        print(subtype)
        if not subtype[0][0]:
            return False, {"code": 400, "error_message": "Vehicle details not found"}

        vehicleList = [
            d for d in vehicleList if d["vehiclesubtype"].lower() == subtype[0][0]
        ]
        print("#######")
        print(vehicleList)
        if not vehicleList:
            return False, {"code": 400, "error_message": "Vehicle details not found"}

        return True, vehicleList[0]


def calculate_premium(event, context):
    request_body = Utils_obj.get_event_body(event)
    processReqObj = processPayload(request_body)

    if processReqObj.get("error"):
        return Utils_obj.buildResp(
            Code["badrequest"]
            if processReqObj.get("code") != 401
            else Code["authorization"],
            {"error": True, "error_message": processReqObj.get("error_message")},
        )

    vehicle_info = processReqObj.get("vInfo")
    rto_info = processReqObj.get("rInfo")

    request_sig = config.get_vehicle_premium_body(vehicle_info, rto_info, request_body)

    print("----> Quote Payload")
    print(request_sig)

    apiRespStatus, apiResp = Utils_obj.execute_request(
        constants.CALCULATE_PREMIUM, request_sig
    )

    print("----> Quote Response")
    print(apiRespStatus)
    print(apiResp)

    if not apiRespStatus:
        return Utils_obj.buildResp(Code["unprocess"], apiResp)

    request_body["motorProfile"]["vehicleId"] = vehicle_info.get("vehiclecode")
    return_response = config.prepare_response(request_body, apiResp)
    return Utils_obj.buildResp(Code["ok"], return_response)


def processPayload(request_body, sType="quote"):
    productType = request_body.get("productType", "").lower()
    productSubType = request_body.get("productSubType", "").lower()
    insuranceType = request_body.get("insuranceType", "").lower()
    policyHolderType = request_body.get("policyHolderType", "").lower()
    motorProfile = request_body.get("motorProfile", {})

    productOffered = validate.validateProductOffered(
        productType, insuranceType, motorProfile.get("isNew")
    )
    if not productOffered:
        return {
            "error": True,
            "error_message": "Sorry, We can not offer the product you are searching",
            "vInfo": {},
            "rInfo": {},
            "code": 400,
        }

    required_params = constants.commonAttributeValidation
    if sType == "proposal":
        required_params.extend(["quotationId", "selectedIDV"])

    validateStatus, validationMsg = validate.validate_params(
        request_body, required_params
    )

    if not validateStatus:
        return {
            "error": True,
            "error_message": validationMsg,
            "vInfo": {},
            "rInfo": {},
            "code": 400,
        }

    motorValidationObj = validate.validateMotorProfile(motorProfile, sType)
    if not motorValidationObj.get("status"):
        return {
            "error": True,
            "error_message": motorValidationObj.get("error_msg"),
            "vInfo": {},
            "rInfo": {},
            "code": 400,
        }

    if sType == "proposal":
        proposalValidationObj = validate.proposalInfo(request_body)
        if not proposalValidationObj.get("status"):
            return {
                "error": True,
                "error_message": proposalValidationObj.get("error_msg"),
                "vInfo": {},
                "rInfo": {},
                "code": 400,
            }

    if not validate.validateProductType(productType):
        return {
            "error": True,
            "error_message": "Invalid Product Type",
            "vInfo": {},
            "rInfo": {},
            "code": 400,
        }

    if not validate.validateSubProductType(productType, productSubType):
        return {
            "error": True,
            "error_message": "Invalid Product Subtype",
            "vInfo": {},
            "rInfo": {},
            "code": 400,
        }

    if not validate.validateInsuranceType(insuranceType):
        return {
            "error": True,
            "error_message": "Invalid Insurance Type",
            "vInfo": {},
            "rInfo": {},
            "code": 400,
        }

    if not validate.validatePolicyHolderType(policyHolderType):
        return {
            "error": True,
            "error_message": "Wrong Policyholder Type",
            "vInfo": {},
            "rInfo": {},
            "code": 400,
        }

    print("Before Vehicle Info")
    status, vehicle_info = vehiclemodelcode(motorProfile, productType, productSubType)
    print("After Vehicle Info")

    if not status:
        return {
            "error": True,
            "error_message": vehicle_info.get("error_message"),
            "vInfo": {},
            "rInfo": {},
            "code": vehicle_info.get("code"),
        }

    rtoLoc = motorProfile.get("rtoLoc")
    status, rto_info = Utils_obj.get_rto_details(rtoLoc)
    if not status:
        return {
            "error": True,
            "error_message": rto_info,
            "vInfo": {},
            "rInfo": {},
            "code": 400,
        }

    return {
        "error": False,
        "error_message": "",
        "vInfo": vehicle_info,
        "rInfo": rto_info,
        "code": 400,
    }


def create_proposal(event, context):
    request_body = Utils_obj.get_event_body(event)
    processReqObj = processPayload(request_body, "proposal")
    if processReqObj.get("error"):
        return Utils_obj.buildResp(
            Code["badrequest"]
            if processReqObj.get("code") != 401
            else Code["authorization"],
            {"error": True, "error_message": processReqObj.get("error_message")},
        )

    vehicle_info = processReqObj.get("vInfo")
    rto_info = processReqObj.get("rInfo")

    premiumCalReq = config.get_vehicle_premium_body(
        vehicle_info, rto_info, request_body
    )

    premStatus, premResp = Utils_obj.execute_request(
        constants.CALCULATE_PREMIUM, premiumCalReq
    )

    if not premStatus:
        return Utils_obj.buildResp(Code["unprocess"], premResp)

    return_response = config.prepare_response(request_body, premResp)

    request_sig = config.get_vehicle_proposal_body(vehicle_info, rto_info, request_body)

    apiRespStatus, apiResp = Utils_obj.execute_request(
        constants.ISSUE_POLICY, request_sig
    )

    if apiRespStatus:
        return_response = request_body
        return_response["proposalId"] = request_body.get("quotationId")
        return_response["proposalDate"] = date.today().strftime("%Y-%m-%d")
        return Utils_obj.buildResp(Code["ok"], return_response)
    return Utils_obj.buildResp(Code["unprocess"], apiResp)


def generatePaymentLink(event, context):
    request_body = Utils_obj.get_event_body(event)
    validateStatus, validationMsg = validate.validate_params(
        request_body, constants.paymentValidation
    )
    if not validateStatus:
        return Utils_obj.buildResp(
            Code["badrequest"], {"error": True, "error_message": validationMsg}
        )

    applicationId = request_body.get("proposalId", None)

    return Utils_obj.buildResp(
        Code["ok"],
        {
            "paymentUrl": constants.API_PAYMENT_URL.format(applicationId),
            "paymentGatewayType": "paymentUrl",
            "providerName": constants.PROVIDER_NAME,
        },
    )


def downloadPolicy(event, context):
    request_body = Utils_obj.get_event_body(event)
    validateStatus, validationMsg = validate.validate_params(
        request_body, constants.policyValidation
    )
    if not validateStatus:
        return Utils_obj.buildResp(
            Code["badrequest"], {"error": True, "error_message": validationMsg}
        )
    enquiryId = request_body.get("enquiryId", None)
    policyNo = request_body.get("policyNo", None)

    body = constants.POLICY_DOWNLOAD_BODY.copy()
    body["policynum"] = policyNo
    status, out = Utils_obj.execute_request(constants.API_DOWNLOAD_URL, body)
    status = Code["ok"] if status else Code["unprocess"]
    formattedResponse = {
        "policyNo": policyNo,
        "policyDocument": out.get("fileByteObj").replace("\n",""),
        "type": constants.POLICYDOWNLOADTYPE
    }
    return Utils_obj.buildResp(status, formattedResponse)


def fetchPolicyInfoByPolicyNo(event, context):
    request_body = Utils_obj.get_event_body(event)
    validateStatus, validationMsg = validate.validate_params(
        request_body, constants.renewalValidation
    )
    if not validateStatus:
        return Utils_obj.buildResp(
            Code["badrequest"], {"error": True, "error_message": validationMsg}
        )

    registrationNo = request_body.get("registrationNo", None)
    registrationNo = registrationNo.replace("-", "")
    policyNo = request_body.get("policyNo", None)
    inputReq = {"prvpolicyref": policyNo, "registrationno": registrationNo}
    body = Utils_obj.update(constants.POLICY_RENEWAL_BODY, inputReq)
    final_dict = {"weomotpolicyin": body}
    status, out = Utils_obj.execute_request(constants.RENEWAL_DATA, final_dict)

    if not status:
        return Utils_obj.buildResp(Code["unprocess"], out)

    return_response = config.prepare_renewal_response(request_body, out)
    return Utils_obj.buildResp(Code["ok"], return_response)
