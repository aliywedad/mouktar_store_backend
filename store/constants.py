
from datetime import datetime


thePhone=36373903
 
accountData={
"id_client":"0001", #
"username":"agent hamoudy", #
"server_expire_date":"2025-10-30", #
"chatId":"7696764572",
"agancy":"lvirdows and leti7adiye",
"expireDate":"2025-10-08 00:00",
"contact":"0000000",
}

def is_subscription_valid():
    expire_date_str = accountData.get("expireDate")
    expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d %H:%M")
    now = datetime.now()
    return now < expire_date



 