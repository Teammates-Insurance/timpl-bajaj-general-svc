import collections
import config
import json
from readData import get_vehicle_details 

from fuzzywuzzy import fuzz, process
from utils import Utils

Utils_obj = Utils()
Code = Utils_obj.httpStatusCodes()
VEHICLE_MASTER = {}


def premium_6w(event, context):
    request_body = Utils_obj.get_event_body(event)
    if not request_body:
        return Utils_obj.buildResp(Code['badrequest'],
                                   {"error": True,
                                    "error_message": "Input is not proper"})
    
    pSubType =  request_body.get("productSubType", None)
    make  = request_body.get("vehicleManufacturer", None)
    model  = request_body.get("vehicleModel", None)
    variant  = request_body.get("vehicleVariant", None)
    fuel  = request_body.get("fuelType", None)
    rto = request_body.get("rtoLocation", None)

    if pSubType == None or make == None or model == None or variant == None or rto == None or fuel == None:
        return Utils_obj.buildResp(Code['badrequest'],
                                   {"error": True,
                                    "error_message": "Input is not proper"})


    status, vehicle_info = get_vehicle_details(pSubType, make, model, variant, fuel.upper()[0])
    
    # print()

    if not status:
        return Utils_obj.buildResp(Code['badrequest'], {
            "error": True,
            "error_message": "Vehicle Not Found"})
    print(vehicle_info)
    # exit("===>")

    # get RTO information
    status, rto_info = Utils_obj.get_rto_details(
        request_body.get("rtoLocation", "").upper())
    
    if not status:
        return Utils_obj.buildResp(Code['badrequest'], {
            "error": True,
            "error_message": "RTO Not Found"})

    add_info = config.get_addons(request_body)
    request_sig = config.get_vehicle_premium_body(vehicle_info,
                                                  rto_info, request_body, add_info)

    print("Premium Request ==>", request_sig)
    status_req, premium_response = Utils_obj.execute_request(
        config.CALCULATE_PREMIUM, request_sig)

    print("Premium Response => ", premium_response)


    if status_req:
        return_response = config.prepare_response(vehicle_info, rto_info,
                                                  request_body, premium_response)
        return Utils_obj.buildResp(Code['ok'], return_response)
    else:
        return Utils_obj.buildResp(Code['unprocess'], premium_response)


def issuepolicy_6w(event, context):
    request_body = Utils_obj.get_event_body(event)
    if not request_body:
        return Utils_obj.buildResp(Code['badrequest'],
                                   {"error": True,
                                    "error_message": "Input is not proper"})
    
    pSubType =  request_body.get("productSubType", None)
    make  = request_body.get("vehicleManufacturer", None)
    model  = request_body.get("vehicleModel", None)
    variant  = request_body.get("vehicleVariant", None)
    fuel  = request_body.get("fuelType", None)
    rto = request_body.get("rtoLocation", None)

    if pSubType == None or make == None or model == None or variant == None or rto == None or fuel == None:
        return Utils_obj.buildResp(Code['badrequest'],
                                   {"error": True,
                                    "error_message": "Input is not proper"})


    status, vehicle_info = get_vehicle_details(pSubType, make, model, variant, fuel.upper()[0])
    
    if not status:
        return Utils_obj.buildResp(Code['badrequest'], {
            "error": True,
            "error_message": "Vehicle Not Found"})
    print(vehicle_info)
    
    # get RTO information
    status, rto_info = Utils_obj.get_rto_details(
        request_body.get("rtoLocation", "").upper())
    if not status:
        return Utils_obj.buildResp(Code['unprocess'], rto_info)

    add_info = config.get_addons(request_body)
    request_sig = config.get_vehicle_premium_body(vehicle_info,
                                                  rto_info, request_body, add_info)

    print("Premium Request ==>", request_sig)
    status_req, premium_response = Utils_obj.execute_request(
        config.CALCULATE_PREMIUM, request_sig)

    print("Premium Response => ", premium_response)


    if not status_req:
        return Utils_obj.buildResp(Code['unprocess'], premium_response)

    print("Premium Request ==>", request_sig)
    return_response = config.prepare_response(vehicle_info, rto_info,
                                              request_body, premium_response)

    request_sig = config.get_vehicle_issue_policy_body(vehicle_info,
                                                       rto_info, request_body, add_info)

    request_sig["transactionid"] = premium_response.get("transactionid")

    status_req, premium_response2 = Utils_obj.execute_request(
        config.ISSUE_POLICY, request_sig)

    print("Issue policy Response => ", premium_response2)

    if status_req:
        return_response['personalInfo'] = request_body.get('personalInfo')
        return_response['nominee'] = request_body.get('nominee')
        return_response['pospInfo'] = request_body.get('pospInfo')
        # return_response['ProposalNo'] = premium_response2.get('policyref')
        return_response['ProposalNo'] = premium_response.get("transactionid")
        return_response['engineNumber'] = request_body.get('engineNumber')
        return_response['vehicleIdentificationNumber'] = request_body.get(
            'vehicleIdentificationNumber')
        return_response['previousInsurerName'] = request_body.get(
            'previousInsurerName')
        return_response['previousInsurancePolicyNo'] = request_body.get(
            'previousInsurancePolicyNo')
        return_response['insuranceType'] = request_body.get('insuranceType')
        return_response['vehicleIDV'] = float(
            premium_response.get('premiumdetails', {}).get('totaliev', "0")),

        return Utils_obj.buildResp(Code['ok'], return_response)
    else:
        return Utils_obj.buildResp(Code['unprocess'], premium_response2)