from utils import Utils
from datetime import date
import constants
import previousInsurer

Utils_obj = Utils()

PREMIUM_MAP = {
    "ownDamageCover": "OD",
    "thirdPartyCover": "ACT",
    "ncbDiscount": "NCB",
    "paCover": "PA_DFT",
    "zeroDepreciation": "S3",
    "roadsideAssistance": "S1",
    "engineProtection": "S4",
    "ncbProtector": "",
    "keyReplacement": "S13",
    "consumables": "",
    "dailyAllowance": "",
    "returnToInvoice": "",
    "tyreProtection": "",
    "lossOfPersonalBelongins": "S14",
    "rimProtection": "",
    "electricalAssecories": "ELECACC",
    "nonElectricalAssecories": "NELECACC",
    "externalCng": "CNG",
    "externalCngTP": "",
    "paidDriver": "LLO",
    "unnamedPassenger": "PA",
    "aaieDiscount": "AAM",
    "araiApproval": "",
    "tppdDiscount": "",
    "voluntaryDiscount": "VOLEX",
}


def fetchVehicleType(pType, vTypeCode):
    if pType == "commercial":
        return vTypeCode
    else:
        return constants.PRODUCT_CODE_TYPES.get(pType).get("vehicleTypeCode")


def getCpa(cpaObj):
    if not cpaObj["isDl"]:
        return "DRVL", 0
    else:
        if cpaObj["isEcpa"]:
            return "ACPA", 0
        else:
            return "MCPA", 1


def getVD(vdAmount):
    if vdAmount:
        return int(float(vdAmount))
    return 0


def getAddonsDict(addons):
    addonsList = []
    if addons.get("externalCng"):
        addonsList.append({"paramdesc": "CNG", "paramref": "CNG"})
    if addons.get("electricalAssecories"):
        addonsList.append({"paramdesc": "ELECACC", "paramref": "ELECACC"})
    if addons.get("nonElectricalAssecories"):
        addonsList.append({"paramdesc": "NELECACC", "paramref": "NELECACC"})
    if addons.get("paidDriver"):
        addonsList.append({"paramdesc": "LLO", "paramref": "LLO"})
    if addons.get("unnamedPassenger"):
        addonsList.append({"paramdesc": "PA", "paramref": "PA"})
    if addons.get("voluntaryDiscount"):
        addonsList.append({"paramdesc": "VOLEX", "paramref": "VOLEX"})

    return addonsList


def getNcb(ipt):
    if ipt and ipt.get("isNcb"):
        return (
            0,
            constants.ncbObj.get(ipt.get("currentNcb")),
            constants.ncbObj.get(ipt.get("newNcb")),
        )
    return 1, 0, 0


def getProductCode(pType, iType, newFlag):
    if newFlag:
        iType = "new"
    return constants.PRODUCT_CODE_TYPES.get(pType).get(iType)


def getPolicyType(newFlag, isRenewal=False):
    if isRenewal:
        typeF = "renewal"
    elif newFlag:
        typeF = "new"
    else:
        typeF = "rollover"
    return constants.POLICYTYPE.get(typeF)


def getInsuredCount(vInfo, aInfo):
    if aInfo.get("unnamedPassenger"):
        return vInfo.get("carryingcapacity", "0")
    return "0"


def getCubicCapacityOfVehicle(vInfo):
    if vInfo.get("cubiccapacity") == "nan":
        return vInfo.get("VEHICLE_GVW")
    else:
        return vInfo.get("cubiccapacity")


def getAddonsBundle(addon, pType):
    addon_bundle = ""
    if pType == constants.PRODUCTS_OFFERED[1]:
        if addon.get("engineProtection") or addon.get("consumables"):
            addon_bundle = "DRIVE_ASSURE_SILVER"
        elif addon.get("zeroDepreciation"):
            addon_bundle = "DRIVE_ASSURE_BASIC"
    elif pType == constants.PRODUCTS_OFFERED[0]:
        if addon.get("lossOfPersonalBelongins"):
            addon_bundle = "DRIVE_ASSURE_PACK_PLUS"
        elif addon.get("zeroDepreciation") or addon.get("engineProtection"):
            addon_bundle = "DRIVE_ASSURE_PACK"

    return addon_bundle


def getTpPolicyInfo(pcode, tpinfo, prevPolInfo):
    resp = ""
    if pcode in ["1870", "1871"] and tpinfo:
        termStartDt = Utils_obj.date_style(prevPolInfo.get("riskStartDate"))
        tInsStatus, insurerCode = previousInsurer.getInsurerCode(tpinfo["insurerName"])
        address = tpinfo["insurerName"] if tpinfo["insurerName"] else ""
        policyNo = tpinfo["policyNo"] if tpinfo["policyNo"] else ""
        noOfClaims = tpinfo.get("noOfClaims", "0")
        tpTermEndDt = Utils_obj.date_style(tpinfo.get("riskEndDate"))
        tpTermStartDt = Utils_obj.date_style(tpinfo.get("riskStartDate"))
        resp = (
            termStartDt
            + "~"
            + insurerCode
            + "~"
            + address
            + "~"
            + policyNo
            + "~"
            + tpTermEndDt
            + "~"
            + noOfClaims
            + "~"
            + "3"
            + "~"
            + tpTermStartDt
            + "~"
        )
    return resp


def getNomineeInfo(cpaFlag, nObj):
    if not nObj:
        return ""
    elif cpaFlag == 'MCPA':
        if nObj.get("name") !="" and nObj.get("relation") !="":
            return "~"+nObj.get("name")+"~"+nObj.get("relation")
        else:
            return ""
    else:
        return ""


def get_vehicle_premium_body(vehicle_info, rto_info, inputObj):
    mProfile = inputObj["motorProfile"]
    pPolicyInfo = inputObj["prePolicyInfo"]
    ncbInfo = inputObj["ncbInfo"]
    cpaInfo = inputObj["cpaInfo"]
    tpPolicyInfo = inputObj["tpPolicyInfo"]
    addonsInfo = inputObj["addons"]
    nominee = inputObj.get("nominee",None)
    policyHolderType = inputObj["policyHolderType"].lower()
    productType = inputObj["productType"].lower()
    insuranceType = inputObj["insuranceType"].lower()
    isNew = mProfile["isNew"]
    isRenewal = False

    product_code = getProductCode(productType, insuranceType, isNew)
    pol_type = getPolicyType(isNew, isRenewal)
    vehicleTypeCode = fetchVehicleType(
        productType, vehicle_info.get("VEHICLE_TYPE_CODE")
    )

    registrationNo = "NEW" if isNew else mProfile.get("registrationNo").replace("-", "")

    termEndDate = Utils_obj.date_style(inputObj.get("riskEndDate"))
    termStartDate = Utils_obj.date_style(inputObj.get("riskStartDate"))
    idv = "0" if product_code in ["1805", "1806"] else inputObj.get("selectedIDV", "0")

    registrationDate = Utils_obj.date_style(mProfile.get("registrationDate"))
    manfYear = mProfile.get("manufactureDate")[0:4]

    cpaFlag, cpaTerm = getCpa(cpaInfo)
    previousClaimStatus, previousNcb, currentNcb = getNcb(ncbInfo)
    vdAmount = getVD(addonsInfo.get("voluntaryDiscount", None))

    total_insured_unnamed_passenger = getInsuredCount(vehicle_info, addonsInfo)
    if not isNew:
        pInsStatus, pInsCode = previousInsurer.getInsurerCode(
            pPolicyInfo["insurerName"]
        )
    else:
        pInsStatus, pInsCode = True, 1

    addon_bundle = getAddonsBundle(addonsInfo, productType)
    extcol36 = getTpPolicyInfo(product_code, tpPolicyInfo, pPolicyInfo)
    extcol38 = getNomineeInfo(cpaFlag, nominee)

    return {
        "vehiclecode": vehicle_info.get("vehiclecode"),
        "city": rto_info[4],
        "weomotpolicyin": {
            "contractid": "0",
            "poltype": pol_type,
            "product4digitcode": product_code,
            "deptcode": "18",
            "branchcode": "0",
            "termstartdate": termStartDate,
            "termenddate": termEndDate,
            "tpfintype": "1",
            "hypo": inputObj.get("financierName", ""),
            "vehicletypecode": vehicleTypeCode,
            "vehicletype": vehicle_info.get("vehicletype"),
            "miscvehtype": "0",
            "vehiclemakecode": vehicle_info.get("vehiclemakecode"),
            "vehiclemake": vehicle_info.get("vehiclemake"),
            "vehiclemodelcode": vehicle_info.get("vehiclemodelcode"),
            "vehiclemodel": vehicle_info.get("vehiclemodel"),
            "vehiclesubtypecode": vehicle_info.get("vehiclesubtypecode"),
            "vehiclesubtype": vehicle_info.get("vehiclesubtype"),
            "fuel": vehicle_info.get("fuel"),
            "zone": rto_info[7],
            "engineno": mProfile["engineNo"] if mProfile["engineNo"] else "",
            "chassisno": mProfile["chassisNo"] if mProfile["chassisNo"] else "",
            "registrationno": registrationNo,
            "registrationdate": registrationDate,
            "registrationlocation": rto_info[4],
            "regilocother": rto_info[1],
            "carryingcapacity": vehicle_info.get("carryingcapacity"),
            "cubiccapacity": getCubicCapacityOfVehicle(vehicle_info),
            "yearmanf": manfYear,
            "color": "",
            "vehicleidv": idv,
            "ncb": currentNcb,
            "addloading": "0",
            "addloadingon": "0",
            "spdiscrate": "0",
            "elecacctotal": addonsInfo["electricalAssecories"]
            if addonsInfo["electricalAssecories"]
            else "0",
            "nonelecacctotal": addonsInfo["nonElectricalAssecories"]
            if addonsInfo["nonElectricalAssecories"]
            else "0",
            "prvpolicyref": None
            if pPolicyInfo == None
            else pPolicyInfo.get("policyNo"),
            "prvexpirydate": None
            if pPolicyInfo == None
            else Utils_obj.date_style(pPolicyInfo.get("riskEndDate")),
            "prvinscompany": "1" if pPolicyInfo == None else pInsCode,
            "prvncb": previousNcb,
            "prvclaimstatus": previousClaimStatus,
            "automembership": 1 if addonsInfo.get("aaieDiscount") else 0,
            "partnertype": constants.POLICYHOLDERTYPEObj.get(policyHolderType),
        },
        "accessorieslist": [
            {
                "contractid": "0",
                "acccategorycode": "0",
                "acctypecode": "0",
                "accmake": "0",
                "accmodel": "0",
                "acciev": "0",
                "acccount": "0",
            }
        ],
        "paddoncoverlist": getAddonsDict(addonsInfo),
        "motextracover": {
            "geogextn": "",
            "noofpersonspa": total_insured_unnamed_passenger,
            "suminsuredpa": addonsInfo["unnamedPassenger"]
            if addonsInfo["unnamedPassenger"]
            else "0",
            "suminsuredtotalnamedpa": "0",
            "cngvalue": addonsInfo["externalCng"] if addonsInfo["externalCng"] else "0",
            "noofemployeeslle": "0",
            "noofpersonsllo": "1" if addonsInfo["paidDriver"] else "0",
            "fibreglassvalue": "0",
            "sidecarvalue": "0",
            "nooftrailers": "0",
            "totaltrailervalue": "0",
            "voluntaryexcess": vdAmount,
            "covernoteno": "",
            "covernotedate": "",
            "subimdcode": "",
            "extrafield1": "",
            "extrafield2": "",
            "extrafield3": "",
        },
        "questlist": [{"questionref": "", "contractid": "", "questionval": ""}],
        "detariffobj": {
            "vehpurchasetype": "",
            "vehpurchasedate": "",
            "monthofmfg": "",
            "registrationauth": "",
            "bodytype": "",
            "goodstranstype": "",
            "natureofgoods": "",
            "othergoodsfrequency": "",
            "permittype": "",
            "roadtype": "",
            "vehdrivenby": "",
            "driverexperience": "",
            "clmhistcode": "",
            "incurredclmexpcode": "",
            "driverqualificationcode": "",
            "tacmakecode": "",
            "extcol1": "",
            "extcol2": "",
            "extcol3": "",
            "extcol4": "",
            "extcol5": "",
            "extcol6": "",
            "extcol7": "",
            "extcol8": cpaFlag,
            "extcol9": "",
            "extcol10": addon_bundle,
            "extcol11": "",
            "extcol12": "",
            "extcol13": "",
            "extcol14": "",
            "extcol15": "",
            "extcol16": "",
            "extcol17": "",
            "extcol18": "",
            "extcol19": "",
            "extcol20": constants.PAYMENT_CALLBACK_URL
            + "systemId="
            + inputObj.get("systemId", "")
            + "&",
            "extcol21": "",
            "extcol22": "",
            "extcol23": "",
            "extcol24": cpaTerm,
            "extcol25": "",
            "extcol26": "",
            "extcol27": "",
            "extcol28": "",
            "extcol29": "",
            "extcol30": "",
            "extcol31": "",
            "extcol32": "",
            "extcol33": "",
            "extcol34": "",
            "extcol35": "",
            "extcol36": extcol36,
            "extcol37": "",
            "extcol38": extcol38,
            "extcol39": "",
            "extcol40": "",
        },
        "transactionid": inputObj.get("quotationId", "0"),
        "transactiontype": "MOTOR_WEBSERVICE",
        "contactno": inputObj.get("personalInfo", {}).get("mobile", "9999912123"),
    }


def get_vehicle_proposal_body(vehicle_info, rto_info, inputObj):
    reqObj = get_vehicle_premium_body(vehicle_info, rto_info, inputObj)
    del reqObj["city"]
    del reqObj["vehiclecode"]
    del reqObj["transactiontype"]
    del reqObj["contactno"]
    policyHolderType = inputObj["policyHolderType"].lower()

    personalInfo = inputObj.get("personalInfo", {})
    addresses = inputObj.get("addresses", {})

    if policyHolderType == "corporate":
        firstName = inputObj.get("companyName", "")
    else:
        firstName = personalInfo.get("firstName", "")

    # inspectionId = inputObj.get("inspectionId", "")

    proposalObj = {
        "rcptlist": [{}],
        "custdetails": {
            "parttempid": "",
            "firstname": firstName,
            "middlename": "",
            "surname": personalInfo.get("lastName", ""),
            "addline1": addresses.get("communication").get("addressLine1", ""),
            "addline2": addresses.get("communication").get("addressLine2", ""),
            "addline3": "",
            "addline5": "",
            "pincode": addresses.get("communication").get("postalCode", ""),
            "email": personalInfo.get("email", ""),
            "telephone1": personalInfo.get("mobile", ""),
            "telephone2": personalInfo.get("mobile", ""),
            "mobile": personalInfo.get("mobile", ""),
            "delivaryoption": "",
            "poladdline1": addresses.get("registered").get("addressLine1", ""),
            "poladdline2": addresses.get("registered").get("addressLine2", ""),
            "poladdline3": "",
            "poladdline5": "",
            "polpincode": addresses.get("registered").get("postalCode", ""),
            "password": constants.AuthToken,
            "cptype": constants.POLICYHOLDERTYPEObj.get(policyHolderType),
            "profession": "",
            "dateofbirth": Utils_obj.date_style(personalInfo.get("dob")),
            "availabletime": "",
            "institutionname": inputObj.get("companyName"),
            "existingyn": "N",
            "loggedin": "",
            "mobilealerts": "",
            "emailalerts": "",
            "title": "",
            "partid": "",
            "status1": "",
            "status2": "",
            "status3": "",
        },
        "premiumdetails": {
            "ncbamt": "0",
            "addloadprem": "0",
            "totalodpremium": "0",
            "totalactpremium": "0",
            "totalnetpremium": "0",
            "totalpremium": "0",
            "netpremium": "0",
            "finalpremium": "0",
            "spdisc": "0",
            "servicetax": "0",
            "stampduty": "0",
            "collpremium": "0",
            "imtout": "",
            "totaliev": "0",
        },
        "potherdetails": {
            "imdcode": "",
            "covernoteno": "",
            "leadno": "",
            "ccecode": "",
            "runnercode": "",
            "extra1": "",
            "extra2": "",
            "extra3": "",
            "extra4": "",
            "extra5": "",
        },
        "premiumpayerid": "0",
        "paymentmode": "CC",
    }

    reqObj.update(proposalObj)
    return reqObj


def premium_map(resp):
    out = {}
    for k, v in PREMIUM_MAP.items():
        out[k] = formatPremiumResp(resp.get(v, "0"))

    return out


def prepare_addons_response(premiumsummerylist):
    resp = {}
    for p in premiumsummerylist:
        resp[p["paramref"]] = float(p["od"]) + float(p["act"])

    return resp


def prepare_response(request_body, premium_response):
    response = request_body
    netPremium = grossPremium = totalTax = ""
    if not premium_response.get("errorcode"):
        netPremium = premium_response["premiumdetails"]["netpremium"]
        grossPremium = premium_response["premiumdetails"]["finalpremium"]
        totalTax = premium_response["premiumdetails"]["servicetax"]

    resp = prepare_addons_response(premium_response.get("premiumsummerylist", []))

    premiumBreakup = premium_map(resp)
    cngPremium = int(float(premiumBreakup.get("externalCng")))
    print(cngPremium)
    if cngPremium > 0 and request_body.get("insuranceType") != "SAOD":
        premiumBreakup.update(
            {
                "externalCng": formatPremiumResp(cngPremium - 60),
                "externalCngTP": formatPremiumResp(60),
            }
        )
    print(premiumBreakup)
    premiumBreakup.update(
        {
            "ownDamageCover": formatPremiumResp(
                premium_response.get("premiumdetails", {}).get("totalodpremium")
            )
        }
    )

    response.update(
        {
            "netPremium": formatPremiumResp(netPremium),
            "grossPremium": formatPremiumResp(grossPremium),
            "totalTax": formatPremiumResp(totalTax),
            "providerName": constants.PROVIDER_NAME,
            "quotationId": premium_response.get("transactionid"),
            "quotationDate": date.today().strftime("%Y-%m-%d"),
            "premiumBreakup": premiumBreakup,
            "vehicleIDV": {
                "defaultValue": formatPremiumResp(
                    premium_response.get("premiumdetails", {}).get("totaliev", "0")
                ),
                "minValue": formatPremiumResp(
                    premium_response.get("premiumdetails", {}).get("totaliev", "0")
                )
                if not request_body.get("selectedIDV")
                else None,
                "maxValue": formatPremiumResp(
                    float(
                        premium_response.get("premiumdetails", {}).get("totaliev", "0")
                    )
                    * 1.1
                )
                if not request_body.get("selectedIDV")
                else None,
            },
        }
    )

    return response


def prepare_renewal_response(request_body, premium_response):
    vehicleInfo = premium_response.get("motextracoverout")
    motorInfo = premium_response.get("weomotpolicyinout")
    customerInfo = premium_response.get("custdetailsout")
    regList = fetchRegNo(motorInfo.get("registrationno"))

    motorProfile = {
        "registrationNo": regList[0],
        "rtoLoc": regList[1],
        "make": motorInfo.get("vehiclemake"),
        "model": motorInfo.get("vehiclemodel"),
        "variant": motorInfo.get("vehiclesubtype"),
        "fuelType": Utils_obj.getKeyByValue(constants.FUEL_TYPE, motorInfo.get("fuel")),
        "cc": motorInfo.get("cubiccapacity"),
        "vehicleId": vehicleInfo.get("extrafield1"),
        "manufactureDate": Utils_obj.changeDateFormat(
            motorInfo.get("registrationdate")
        ),
        "purchaseDate": Utils_obj.changeDateFormat(motorInfo.get("registrationdate")),
        "registrationDate": Utils_obj.changeDateFormat(
            motorInfo.get("registrationdate")
        ),
        "engineNo": motorInfo.get("engineno"),
        "chassisNo": motorInfo.get("chassisno"),
    }
    policyHolderInfo = {
        "policyholderType": Utils_obj.getKeyByValue(
            constants.POLICYHOLDERTYPEObj, motorInfo.get("partnertype")
        ),
        "firstName": customerInfo.get("firstname")
        + " "
        + customerInfo.get("middlename"),
        "lastName": customerInfo.get("surname"),
        "email": customerInfo.get("email"),
        "mobile": customerInfo.get("mobile"),
        "dob": Utils_obj.changeDateFormat(customerInfo.get("dateofbirth")),
        "companyName": customerInfo.get("institutionname"),
    }
    address = {
        "registered": {
            "postalCode": customerInfo.get("polpincode"),
            "addressLine1": customerInfo.get("poladdline1"),
            "addressLine2": customerInfo.get("poladdline2"),
            "city": customerInfo.get("poladdline3"),
            "state": customerInfo.get("poladdline5"),
            "country": "India",
        },
        "communication": {
            "postalCode": customerInfo.get("pincode"),
            "addressLine1": customerInfo.get("addline1"),
            "addressLine2": customerInfo.get("addline2"),
            "city": customerInfo.get("addline3"),
            "state": customerInfo.get("addline5"),
        },
    }

    return {
        "motorProfile": motorProfile,
        "policyHolderInfo": policyHolderInfo,
        "address": address,
    }


def fetchRegNo(inputStr):
    splitIndex = 6
    if len(inputStr) == 9:
        splitIndex = 5

    stateCode = inputStr[:2]
    cityCode = inputStr[2:-splitIndex]
    hashCode = inputStr[4:splitIndex]
    regCode = inputStr[-4:]

    return [
        stateCode + "-" + cityCode + "-" + hashCode + "-" + regCode,
        stateCode + "-" + cityCode,
    ]


def formatPremiumResp(iptResp):
    return Utils_obj.formatInIndianCurrency(iptResp)
