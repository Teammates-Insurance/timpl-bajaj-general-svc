import constants


def validate_params(request_body, required_params):
    if not request_body:
        return False, "Input missing"
    for required_param in required_params:
        if required_param not in request_body:
            return False, "{} is mandatory field.".format(required_param)
        elif request_body[required_param] == "":
            return False, "{} is empty .".format(required_param)

    return True, ""


def validateProductType(pType):
    if pType not in constants.PRODUCTS_OFFERED:
        return False
    return True


def validateSubProductType(pType, subpType):
    if pType == "commercial":
        if subpType not in constants.SUB_PRODUCTS_OFFERED:
            return False
    return True


def validatePolicyHolderType(policyHolderTypeInput):
    if policyHolderTypeInput not in constants.POLICYHOLDERTYPE:
        return False
    return True


def validateInsuranceType(iType):
    if iType not in constants.INSURANCETYPELIST:
        return False
    return True


def validateProductOffered(pType, iType, newFlag):
    if newFlag:
        iType = "new"
    return constants.PRODUCT_CODE_TYPES.get(pType).get(iType)


def validateMotorProfile(mProfile, serviceType):
    required_params = constants.motorProfileValidation
    if serviceType == "proposal":
        required_params.extend(["chassisNo", "engineNo", "vehicleId"])
    validateStatus, validationMsg = validate_params(mProfile, required_params)
    return {"status": validateStatus, "error_msg": validationMsg}


def proposalInfo(reqObj):
    if reqObj.get("policyHolderType") == "Individual":
        required_params = constants.personalInfoValidation
    else:
        required_params = constants.corporateValidation

    personalInfo = reqObj.get("personalInfo")
    validateStatus, validationMsg = validate_params(personalInfo, required_params)

    if not validateStatus:
        return {"status": validateStatus, "error_msg": validationMsg}

    regAddress = reqObj.get("addresses", {}).get("registered")
    reqAddParam = constants.addressValidation
    validateStatus, validationMsg = validate_params(regAddress, reqAddParam)

    if not validateStatus:
        return {"status": validateStatus, "error_msg": validationMsg}

    comAddress = reqObj.get("addresses", {}).get("communication")
    validateStatus, validationMsg = validate_params(comAddress, reqAddParam)
    if not validateStatus:
        return {"status": validateStatus, "error_msg": validationMsg}

    return {"status": True, "error_msg": ""}
