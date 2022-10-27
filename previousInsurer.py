INSURANCE_COMP = [
    {"Code": "1", "Name": "The New India Assurance Company Limited"},
    {"Code": "2", "Name": "Tata AIG General Insurance Company Limited"},
    {"Code": "3", "Name": "United India Insurance Company Limited"},
    {"Code": "4", "Name": "National Insurance Company Limited"},
    {"Code": "5", "Name": "The Oriental Insurance Company Limited"},
    {"Code": "6", "Name": "Bajaj Allianz General Insurance Co Ltd."},
    {"Code": "8", "Name": "ICICI Lombard General Insurance Company Limited."},
    {"Code": "9", "Name": "IFFCO Tokio General Insurance Company Limited."},
    {"Code": "10", "Name": "Reliance General Insurance Company Limited."},
    {"Code": "11", "Name": "Royal Sundaram General Insurance Co. Limited"},
    {"Code": "12", "Name": "HDFC ERGO General Insurance Company Limited."},
    {"Code": "13", "Name": "Cholamandalam MS General Insurance Company Limited."},
    {"Code": "17", "Name": "Future Generali India Insurance Company Limited."},
    {"Code": "18", "Name": "Universal Sompo General Insurance Company Limited"},
    {"Code": "20", "Name": "Shriram General Insurance Company Limited."},
    {"Code": "21", "Name": "Bharti AXA General Insurance Company Limited"},
    {"Code": "22", "Name": "Raheja QBE General Insurance Company Limited"},
    {"Code": "24", "Name": "SBI General Insurance Company Limited"},
    {"Code": "25", "Name": "L&T General Insurance Company Limited"},
    {"Code": "29", "Name": "Liberty general insurance limited"},
    {"Code": "30", "Name": "Magma HDI General Insurance Company Limited"},
    {"Code": "31", "Name": "KOTAK MAHINDRA GENERAL INSURANCE"},
    {"Code": "32", "Name": "DHFL General Insurance Limited"},
    {"Code": "33", "Name": "Acko General Insurance Limited"},
    {"Code": "34", "Name": "Go Digit General Insurance Limited"},
    {"Code": "43", "Name": "Edelweiss General Insurance Company Limited"},
]


def getInsurerCode(insurerNameInput):
    if insurerNameInput:
        response = [d for d in INSURANCE_COMP if d["Name"] == insurerNameInput]
        if not response:
            return False, "0"
        return True, response[0]["Code"]
    return False, "0"
