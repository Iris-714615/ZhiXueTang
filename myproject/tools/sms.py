from ronglian_sms_sdk import SmsSDK
import json
class Sms:
    """短信验证码"""
    def __init__(self):
       
        self.accId = '2c94811c9ac8c114019dbe8db18e38c2'
        self.accToken = 'ddee263d6877407daf2245a59a84573c'
        self.appId = '2c94811c9ac8c114019dbe8db21838c9'

    def send_message(self, mobile, code):
        sdk = SmsSDK(self.accId, self.accToken, self.appId)
        tid = '1'
        mobile = mobile
        datas = (code, 1)
        resp = sdk.sendMessage(tid, mobile, datas)
        data  = json.loads(resp)
        if data['statusCode'] == '000000':
            return True
        else:
            return False
        return resp
    
sms = Sms()
# res = sms.send_message('18567311174', '1234')
# print(res)