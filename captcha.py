import time
import httpx
import logging

# 获取日志记录器
logger = logging.getLogger("captcha")

class ttocr:
    # 集中管理配置信息
    APPKEY = ""
    SUBMIT_URL = "http://api.ttocr.com/api/recognize"
    RESULT_URL = "http://api.ttocr.com/api/results"

    @staticmethod
    def recognize(gt: str, challenge: str):
        """提交验证码识别任务"""
        params = {
            "appkey": ttocr.APPKEY,
            "gt": gt,
            "challenge": challenge,
            "itemid": 388,
            "referer": "https://app.mihoyo.com",
            "userAgent": "Mozilla/5.0 (Linux; Android 12; Mi 10) AppleWebKit/537.36 Chrome/99 Mobile"
        }
        
        try:
            # 设置合理的超时时间，防止挂起
            with httpx.Client(timeout=10.0) as client:
                res = client.post(ttocr.SUBMIT_URL, data=params)
                res.raise_for_status()
                result = res.json()
                
                if result.get("status") == 1:
                    result_id = result.get("resultid")
                    logger.info(f"验证码任务提交成功，ResultID: {result_id}")
                    return result_id
                else:
                    logger.error(f"验证码提交失败，服务端返回状态码：{result.get('status')}")
        except Exception as e:
            logger.exception("提交识别任务时发生异常")  # 自动记录堆栈
            
        return None

    @staticmethod
    def results(resultid: str):
        """轮询获取识别结果"""
        if not resultid:
            return None

        params = {
            "appkey": ttocr.APPKEY,
            "resultid": resultid
        }

        # 60秒轮询时限
        deadline = time.monotonic() + 60
        
        # 复用 Client 连接池，减少 Server Disconnected 风险
        with httpx.Client(timeout=5.0) as client:
            while time.monotonic() < deadline:
                try:
                    res = client.post(ttocr.RESULT_URL, data=params)
                    res.raise_for_status()
                    data = res.json()

                    if data.get("status") == 1 and data.get("data"):
                        logger.info("验证码识别成功")
                        return {
                            "challenge": data.get("data").get("challenge"),
                            "validate": data.get("data").get("validate"),
                        }
                    
                    logger.debug("识别中，等待重试...")
                    
                except (httpx.RemoteProtocolError, httpx.HTTPError) as e:
                    # 针对常见的服务器断连进行容错
                    logger.warning(f"网络异常: {e}，正在尝试恢复连接...")
                except Exception:
                    logger.exception("获取结果过程中发生未知错误")
                
                time.sleep(2.0)  # 适当的请求间隔保护
                
        logger.error("验证码识别超时")
        return None


def get_captcha_result(gt: str, challenge: str) -> dict:
    """验证码处理核心逻辑封装"""
    resultid = ttocr.recognize(gt, challenge)
    if resultid:
        return ttocr.results(resultid)
    return None

# 以下函数保持原有的接口兼容性
def game_captcha(gt: str, challenge: str) -> dict:
    return get_captcha_result(gt, challenge)

def bbs_captcha(gt: str, challenge: str) -> dict:
    return get_captcha_result(gt, challenge)
