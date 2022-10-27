import config
import json, os
import xmltodict
import requests
from utils import Utils

Utils_obj = Utils()
Code = Utils_obj.httpStatusCodes()

UserID = os.environ.get('UserID')


def generateInspectionPin(event,context):
    request_body = Utils_obj.get_event_body(event)
    if not request_body:
        return Utils_obj.buildResp(Code['unprocess'],
                                   {"error": True,
                                    "error_message": "Not insufficient Request body"})

    registrationNumber = request_body.get('registrationNumber')
    if len(registrationNumber) > 9 :
        hashNumber = registrationNumber[4:6]
        lastNumber = registrationNumber[6:10]
    else:
        hashNumber = registrationNumber[4:5]  
        lastNumber = registrationNumber[5:9]
    xml_data = f"""<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:bag="http://com/bajajallianz/BagicMotorWS.wsdl" xmlns:typ="http://com/bajajallianz/BagicMotorWS.wsdl/types/">
    <x:Header/>
    <x:Body>
        <bag:pinProcessWs>
            <bag:pTransactionId>{request_body.get('enquiryId')}</bag:pTransactionId>
            <bag:pRegNoPart1>{registrationNumber[:2]}</bag:pRegNoPart1>
            <bag:pRegNoPart2>{registrationNumber[2:4]}</bag:pRegNoPart2>
            <bag:pRegNoPart3>{hashNumber}</bag:pRegNoPart3>
            <bag:pRegNoPart4>{lastNumber}</bag:pRegNoPart4>
            <bag:pUserName>webservice@firstadvisorinsurance.com</bag:pUserName>
            <bag:pFlag>{request_body.get('mobileNo')}~Y</bag:pFlag>
            <bag:pPinNumber_out></bag:pPinNumber_out>
            <bag:pPinStatus_out></bag:pPinStatus_out>
            <bag:pVchlDtlsObj_out>
                <typ:stringval57></typ:stringval57>
                <typ:stringval58></typ:stringval58>
                <typ:stringval55></typ:stringval55>
                <typ:stringval56></typ:stringval56>
                <typ:stringval59></typ:stringval59>
                <typ:stringval42></typ:stringval42>
                <typ:stringval43></typ:stringval43>
                <typ:stringval40></typ:stringval40>
                <typ:stringval41></typ:stringval41>
                <typ:stringval47></typ:stringval47>
                <typ:stringval46></typ:stringval46>
                <typ:stringval45></typ:stringval45>
                <typ:stringval44></typ:stringval44>
                <typ:stringval49></typ:stringval49>
                <typ:stringval48></typ:stringval48>
                <typ:stringval50></typ:stringval50>
                <typ:stringval54></typ:stringval54>
                <typ:stringval53></typ:stringval53>
                <typ:stringval52></typ:stringval52>
                <typ:stringval51></typ:stringval51>
                <typ:stringval30></typ:stringval30>
                <typ:stringval31></typ:stringval31>
                <typ:stringval32></typ:stringval32>
                <typ:stringval34></typ:stringval34>
                <typ:stringval33></typ:stringval33>
                <typ:stringval36></typ:stringval36>
                <typ:stringval35></typ:stringval35>
                <typ:stringval38></typ:stringval38>
                <typ:stringval37></typ:stringval37>
                <typ:stringval39></typ:stringval39>
                <typ:stringval60></typ:stringval60>
                <typ:stringval2></typ:stringval2>
                <typ:stringval3></typ:stringval3>
                <typ:stringval1></typ:stringval1>
                <typ:stringval6></typ:stringval6>
                <typ:stringval7></typ:stringval7>
                <typ:stringval4></typ:stringval4>
                <typ:stringval5></typ:stringval5>
                <typ:stringval20></typ:stringval20>
                <typ:stringval21></typ:stringval21>
                <typ:stringval8></typ:stringval8>
                <typ:stringval9></typ:stringval9>
                <typ:stringval29></typ:stringval29>
                <typ:stringval28></typ:stringval28>
                <typ:stringval27></typ:stringval27>
                <typ:stringval26></typ:stringval26>
                <typ:stringval25></typ:stringval25>
                <typ:stringval24></typ:stringval24>
                <typ:stringval23></typ:stringval23>
                <typ:stringval22></typ:stringval22>
                <typ:stringval10></typ:stringval10>
                <typ:stringval16></typ:stringval16>
                <typ:stringval15></typ:stringval15>
                <typ:stringval18></typ:stringval18>
                <typ:stringval17></typ:stringval17>
                <typ:stringval12></typ:stringval12>
                <typ:stringval11></typ:stringval11>
                <typ:stringval14></typ:stringval14>
                <typ:stringval13></typ:stringval13>
                <typ:stringval19></typ:stringval19>
            </bag:pVchlDtlsObj_out>
        </bag:pinProcessWs>
    </x:Body>
</x:Envelope>
"""

    print("---->")
    print(xml_data)

    # print(payload)
    auth_header = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://com/bajajallianz/BagicMotorWS.wsdl/pinStatusWs"
    }

    resp = requests.post(url=config.PIN_GENERATION,
                         data=xml_data,
                         headers=auth_header
                         )
    response_text = resp.text.replace('&lt;', '<').replace('&gt;', '>').replace('&#xD;', '\r')
    print(response_text)
    try:
            response_text = response_text.replace('<Message>', '<ErrorMessage>')
            response_json = json.loads(json.dumps(xmltodict.parse(response_text)))
    except xmltodict.expat.ExpatError:
            return Utils_obj.buildResp(Code['unprocess'], {"error": True, 'message': 'Error in getting response'})

    print(response_json)
    pinNumber = response_json.get('env:Envelope',{}).get('env:Body',{}).get('m:pinProcessWsResponse',{}).get('pPinNumber_out')
    pinStatus = response_json.get('env:Envelope',{}).get('env:Body',{}).get('m:pinProcessWsResponse',{}).get('pPinStatus_out')
    duplicatePin = response_json.get('env:Envelope',{}).get('env:Body',{}).get('m:pinProcessWsResponse',{}).get('pPinNumber_out',{}).get('@xsi:nil')
    
    api_response = {
         "pinNumber": pinNumber,
         "pinStatus": pinStatus
     }

    if duplicatePin:
        return Utils_obj.buildResp(Code['duplicate'],{"error": True,"error_message": "PIN Number is already generated for this vehicle"})

    else:
        return Utils_obj.buildResp(Code['ok'], api_response)



def checkInspectionPinStatus(event,context):
    request_body = Utils_obj.get_event_body(event)
    if not request_body:
        return Utils_obj.buildResp(Code['unprocess'],
                                   {"error": True,
                                    "error_message": "Not insufficient Request body"})
    
    enquiryId = request_body.get('enquiryId')
    
    #get the values of the registrationNumber
    registrationNumber = request_body.get('registrationNumber')
    if len(registrationNumber) > 9 :
        hashNumber = registrationNumber[4:6]
        lastNumber = registrationNumber[6:10]
    else:
        hashNumber = registrationNumber[4:5]  
        lastNumber = registrationNumber[5:9]  

    xml_data = f"""<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:bag="http://com/bajajallianz/BagicMotorWS.wsdl" xmlns:typ="http://com/bajajallianz/BagicMotorWS.wsdl/types/">
    <x:Header/>
    <x:Body>
        <bag:pinStatusWs>
            <bag:pRegNoPart1>{registrationNumber[:2]}</bag:pRegNoPart1>
            <bag:pRegNoPart2>{registrationNumber[2:4]}</bag:pRegNoPart2>
            <bag:pRegNoPart3>{hashNumber}</bag:pRegNoPart3>
            <bag:pRegNoPart4>{lastNumber}</bag:pRegNoPart4>
                        <bag:pPinList_out>
                <typ:WeoRecStrings10User>
                    <typ:stringval2></typ:stringval2>
                    <typ:stringval3></typ:stringval3>
                    <typ:stringval1></typ:stringval1>
                    <typ:stringval6></typ:stringval6>
                    <typ:stringval7></typ:stringval7>
                    <typ:stringval4></typ:stringval4>
                    <typ:stringval5></typ:stringval5>
                    <typ:stringval8></typ:stringval8>
                    <typ:stringval10></typ:stringval10>
                    <typ:stringval9></typ:stringval9>
                </typ:WeoRecStrings10User>
            </bag:pPinList_out>
            <bag:pErrorMessage_out></bag:pErrorMessage_out>
            <bag:pErrorCode_out></bag:pErrorCode_out>
        </bag:pinStatusWs>
    </x:Body>
</x:Envelope>
"""

    #print("---->")
    #print(xml_data)

    auth_header = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://com/bajajallianz/BagicMotorWS.wsdl/pinStatusWs"
    }

    resp = requests.post(url=config.PIN_GENERATION,
                         data=xml_data,
                         headers=auth_header
                         )
    response_text = resp.text.replace('&lt;', '<').replace('&gt;', '>').replace('&#xD;', '\r')
    try:
            response_text = response_text.replace('<Message>', '<ErrorMessage>')
            response_json = json.loads(json.dumps(xmltodict.parse(response_text)))
    except xmltodict.expat.ExpatError:
            return Utils_obj.buildResp(Code['unprocess'], {"error": True, 'message': 'Error in getting response'})

    #print(response_json)
    
    #Generate the Pin response
    pinNumber = response_json.get('env:Envelope',{}).get('env:Body',{}).get('m:pinStatusWsResponse',{}).get('pPinList_out',{}).get('typ:WeoRecStrings10User',{}).get('typ:stringval1')
    pinStatus = response_json.get('env:Envelope',{}).get('env:Body',{}).get('m:pinStatusWsResponse',{}).get('pPinList_out',{}).get('typ:WeoRecStrings10User',{}).get('typ:stringval2')
    pinStatusDesc = config.PIN_STATUS_LIST[pinStatus]
    api_response = {
         "enquiryId" : enquiryId,
         "inscpectionId": pinNumber,
         "status": {
             	"code": pinStatus,
                "description": pinStatusDesc
}
     } 

    return Utils_obj.buildResp(Code['ok'], api_response)
