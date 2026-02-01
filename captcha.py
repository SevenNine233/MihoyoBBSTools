import httpx
import time


class ttocr:
    def recognize(gt: str, challenge: str):
        submit_url = "http://api.ttocr.com/api/recognize"
        params = {
            "appkey": "9f4aace9e81822ef9906bedfcb931149",
            "gt": gt,
            "challenge": challenge,
            "itemid": "388",
            "referer": 'https://act.mihoyo.com'
        }
        for _ in range(10):
            res = httpx.post(submit_url, data=params)
            result = res.json()
            if result.get("status") == 1:
                return result.get("resultid")
            time.sleep(2)
        return None


    def results(resultid: str):
        result_url = "http://api.ttocr.com/api/results"
        params = {
            "appkey": "9f4aace9e81822ef9906bedfcb931149",
            "resultid": resultid
        }
        if resultid == "":
            return None
        else:
            for _ in range(10):
                res = httpx.post(result_url, data=params)
                data = res.json()
                if data.get("status") == 1:
                    datajson = {
                        "challenge":data["data"]["challenge"],
                        "validate":data["data"]["validate"]
                    }
                    return datajson
                time.sleep(2)
            return None


def game_captcha(gt: str, challenge: str) -> dict:
    resultid = ttocr.recognize(gt, challenge)
    time.sleep(2)
    data = ttocr.results(resultid)
    return data


def bbs_captcha(gt: str, challenge: str) -> dict:
    resultid = ttocr.recognize(gt, challenge)
    time.sleep(2)
    data = ttocr.results(resultid)
    return data
