from ignorant.core import *
from ignorant.localuseragent import *


async def snapchat(phone, country_code, client, out):
    name = "snapchat"
    domain = "snapchat.com"
    method = "register"
    frequent_rate_limit=False
    convert_to_country_code={'1': 'VI', '49': 'DE', '33': 'FR', '44': 'JE', '247': 'AC', '376': 'AD', '971': 'AE', '93': 'AF', '355': 'AL', '374': 'AM', '244': 'AO', '54': 'AR', '43': 'AT', '61': 'CX', '297': 'AW', '358': 'FI', '994': 'AZ', '387': 'BA', '880': 'BD', '32': 'BE', '226': 'BF', '359': 'BG', '973': 'BH', '257': 'BI', '229': 'BJ', '590': 'MF', '673': 'BN', '591': 'BO', '599': 'CW', '55': 'BR', '975': 'BT', '267': 'BW', '375': 'BY', '501': 'BZ', '243': 'CD', '236': 'CF', '242': 'CG', '41': 'CH', '225': 'CI', '682': 'CK', '56': 'CL', '237': 'CM', '86': 'CN', '57': 'CO', '506': 'CR', '53': 'CU', '238': 'CV', '357': 'CY', '420': 'CZ', '253': 'DJ', '45': 'DK', '213': 'DZ', '593': 'EC', '372': 'EE', '20': 'EG', '212': 'MA', '291': 'ER', '34': 'ES', '251': 'ET', '679': 'FJ', '500': 'FK', '691': 'FM', '298': 'FO', '241': 'GA', '995': 'GE', '594': 'GF', '233': 'GH', '350': 'GI', '299': 'GL', '220': 'GM', '224': 'GN', '240': 'GQ', '30': 'GR', '502': 'GT', '245': 'GW', '592': 'GY', '852': 'HK', '504': 'HN', '385': 'HR', '509': 'HT', '36': 'HU', '62': 'ID', '353': 'IE', '972': 'IL', '91': 'IN', '246': 'IO', '964': 'IQ', '98': 'IR', '354': 'IS', '39': 'VA', '962': 'JO', '81': 'JP', '254': 'KE', '996': 'KG', '855': 'KH', '686': 'KI', '269': 'KM', '850': 'KP', '82': 'KR', '965': 'KW', '7': 'RU', '856': 'LA', '961': 'LB', '423': 'LI', '94': 'LK', '231': 'LR', '266': 'LS', '370': 'LT', '352': 'LU', '371': 'LV', '218': 'LY', '377': 'MC', '373': 'MD', '382': 'ME', '261': 'MG', '692': 'MH', '389': 'MK', '223': 'ML', '95': 'MM', '976': 'MN', '853': 'MO', '596': 'MQ', '222': 'MR', '356': 'MT', '230': 'MU', '960': 'MV', '265': 'MW', '52': 'MX', '60': 'MY', '258': 'MZ', '264': 'NA', '687': 'NC', '227': 'NE', '672': 'NF', '234': 'NG', '505': 'NI', '31': 'NL', '47': 'SJ', '977': 'NP', '674': 'NR', '683': 'NU', '64': 'NZ', '968': 'OM', '507': 'PA', '51': 'PE', '689': 'PF', '675': 'PG', '63': 'PH', '92': 'PK', '48': 'PL', '508': 'PM', '970': 'PS', '351': 'PT', '680': 'PW', '595': 'PY', '974': 'QA', '262': 'YT', '40': 'RO', '381': 'RS', '250': 'RW', '966': 'SA', '677': 'SB', '248': 'SC', '249': 'SD', '46': 'SE', '65': 'SG', '290': 'TA', '386': 'SI', '421': 'SK', '232': 'SL', '378': 'SM', '221': 'SN', '252': 'SO', '597': 'SR', '211': 'SS', '239': 'ST', '503': 'SV', '963': 'SY', '268': 'SZ', '235': 'TD', '228': 'TG', '66': 'TH', '992': 'TJ', '690': 'TK', '670': 'TL', '993': 'TM', '216': 'TN', '676': 'TO', '90': 'TR', '688': 'TV', '886': 'TW', '255': 'TZ', '380': 'UA', '256': 'UG', '598': 'UY', '998': 'UZ', '58': 'VE', '84': 'VN', '678': 'VU', '681': 'WF', '685': 'WS', '967': 'YE', '27': 'ZA', '260': 'ZM', '263': 'ZW'}

    headers = {
        'User-Agent': random.choice(ua["browsers"]["chrome"]),
        'Accept': '*/*',
        'Accept-Language': 'en,en-US;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'Origin': 'https://accounts.snapchat.com',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-GPC': '1',
        'TE': 'Trailers',
    }
    try:
        response = await client.get("https://accounts.snapchat.com", headers=headers)
    except :
        out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                    "rateLimit": True,
                    "exists": False})
        return()

    data = {
      'phone_country_code': convert_to_country_code[country_code],
      'phone_number': phone,
      'xsrf_token': response.cookies["xsrf_token"]
    }

    response = await client.post('https://accounts.snapchat.com/accounts/validate_phone_number', headers=headers, data=data)
    try:
        status = response.json()["status_code"]
        if status=="TAKEN_NUMBER":
            out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                        "rateLimit": False,
                        "exists": True})
        elif status=="OK":
            out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                        "rateLimit": False,
                        "exists": False})

        else:
            out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                        "rateLimit": True,
                        "exists": False})
    except:
        out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                    "rateLimit": True,
                    "exists": False})
