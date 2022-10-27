import collections.abc

import constants
import csv
import datetime
import json
import os
import re
import requests


class Utils:
    def __init__(self):
        self.rto_dict = {}
        self.rto_file = "./RTO-master.csv"
        self.create_rto_dict()

    def execute_request(self, url, payload, headers={}):
        if not headers.get("Content-Type"):
            headers["Content-Type"] = "application/json"
        if not payload.get("userid"):
            payload["userid"] = constants.UserID
        if not payload.get("password"):
            payload["password"] = constants.AuthToken

        print("===> Payload for download")
        print(payload)

        request_status = requests.request(
            "POST", url, data=json.dumps(payload), headers=headers
        )

        if request_status.status_code == 200:
            if not request_status.content in ["", None]:
                request_output = request_status.json()
                if not request_output.get("errorlist"):
                    return True, request_output
                else:
                    return False, {
                        "error": True,
                        "error_message": "Error on Insurance company : "
                        + " ".join(
                            [p.get("errtext") for p in request_output.get("errorlist")]
                        ),
                    }
            else:
                return False, {
                    "error": True,
                    "error_message": "Error on Insurance company : No Response",
                }
        else:
            return False, request_status.json()

    def get_event_body(self, event):
        if type(event.get("body")) is dict:
            request_body = event.get("body")
        else:
            request_body = json.loads(event.get("body"))
        return request_body

    def httpStatusCodes(self):
        return {
            "ok": {"code": 200, "status": "Ok"},
            "created": {"code": 201, "status": "Created"},
            "badrequest": {"code": 400, "status": "Request payload empty"},
            "internalservererror": {"code": 500, "status": "Internal ServerError"},
            "unprocess": {"code": 422, "status": "Unable to Process"},
            "duplicate": {"code": 201, "status": "Duplicate response"},
            "authorization": {"code": 401, "status": "Unautorized"},
        }

    def buildResp(self, code, result, ContentType="application/json"):
        if ContentType == "application/xml":
            return_data = {
                "statusCode": code["code"],
                "headers": {
                    "Content-Type": "application/plain",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True,
                },
                "body": result,
            }
        else:
            return_data = {
                "statusCode": code["code"],
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True,
                },
                "body": json.dumps(result),
            }

        return return_data

    def get_sample_json(self, sample_json_file):
        try:
            with open(sample_json_file) as json_file:
                data = json.load(json_file)
                return True, data
        except Exception as e:
            return False, {"error": True, "error_message": e.__str__()}

    def get_rto_details(self, rto):
        if not self.rto_dict:
            self.create_rto_dict()

        pattern = re.compile(r"\s+")
        rto_lower = re.sub(pattern, "", rto).lower()

        if self.rto_dict.get(rto_lower):
            return True, self.rto_dict[rto_lower]
        else:
            return False, {"error": True, "error_message": "RTO details not found"}

    def create_rto_dict(self):
        pattern = re.compile(r"\s+")
        with open(self.rto_file, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                rto_code = re.sub(pattern, "", row[2]).lower()
                self.rto_dict[rto_code] = row

    def date_style(self, date):
        if not date:
            return date
        return datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d-%b-%Y")

    def update(self, d, u):
        for k, v in u.items():
            if isinstance(v, collections.abc.Mapping):
                d[k] = self.update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    def date_computation(
        self, date_initial, difference, difference_param="days", new_format="%d-%b-%Y"
    ):
        datetime_obj = datetime.datetime.strptime(date_initial, "%Y-%m-%d").date()
        new_date = datetime_obj + datetime.timedelta(days=difference)
        return new_date.strftime(new_format)

    def changeDateFormat(
        self, date_str, input_format="%d-%b-%Y", output_format="%Y-%m-%d"
    ):
        output_date = ""
        if date_str:
            date_object = datetime.datetime.strptime(date_str, input_format)
            output_date = date_object.strftime(output_format)
        return output_date

    def getKeyByValue(self, dictIpt, valueInput):
        key_list = list(dictIpt.keys())
        val_list = list(dictIpt.values())
        position = val_list.index(valueInput)
        return key_list[position].upper()

    def formatInIndianCurrency(self, ipt):
        return "{:.2f}".format(float(ipt))
