"""Build scenario currency names from SIX ISO 4217 current/historical XML lists.

Usage: python tools/import_currency_names.py current.xml historical.xml
Country assignments are explicit 2000-01-01 scenario choices, not exchange rates
or MD's reserve-currency ideas. De facto territories use the named local unit.
"""
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAIRS = '''ABK:RUB ACE:IDR AFG:AFA AFR:SLL AGL:AOA AIA:SOS ALB:ALL ALG:DZD ANT:XCD ARG:ARS ARM:AMD AST:AUD AUS:EUR AZE:AZM BAH:BSD BAN:BDT BAR:BBD BEL:EUR BEN:XOF BFA:XOF BHR:BHD BHU:BTN BLR:BYR BLZ:BZD BOL:BOB BOS:BAM BOT:BWP BRA:BRL BRM:MMK BRU:BND BUL:BGN BUR:BIF CAM:XAF CAN:CAD CAR:XAF CBD:KHR CDI:XOF CHA:XAF CHE:RUB CHI:CNY CHL:CLP CNG:XAF COL:COP COM:KMF COS:CRC CRO:HRK CUB:CUP CYP:CYP CZE:CZK DEN:DKK DJI:DJF DMI:XCD DOM:DOP DRC:CDF ECU:ECS EGU:XAF EGY:EGP ELS:SVC ENG:GBP ERI:ERN EST:EEK ETH:ETB FAO:DKK FIJ:FJD FIN:EUR FRA:EUR FYR:MKD GAB:XAF GAH:GHC GAM:GMD GEO:GEL GER:EUR GRA:XCD GRE:GRD GRN:DKK GUA:GTQ GUB:XOF GUI:GNF GUY:GYD HAI:HTG HAM:ILS HEZ:LBP HKG:HKD HOL:EUR HON:HNL HUN:HUF ICE:ISK IEK:IQD IND:IDR IRE:EUR IRQ:IQD ISR:ILS ITA:EUR JAM:JMD JAP:JPY JOR:JOD JUB:SOS KAC:MMK KAR:MMK KAZ:KZT KEN:KES KOR:KRW KOS:DEM KUR:IQD KUW:KWD KYR:KGS LAO:LAK LAT:LVL LBA:LYD LEB:LBP LES:LSL LIB:LRD LIT:LTL LUR:LRD LUX:EUR MAC:MOP MAD:MGF MAL:XOF MAU:MRO MAY:MYR MEX:MXN MIC:USD MLC:CDF MLD:MVR MLT:MTL MLV:MDL MLW:MWK MNT:DEM MON:MNT MOR:MAD MOZ:MZM MRT:MUR NAM:NAD NCY:TRL NEP:NPR NGR:XOF NIC:NIO NIG:NGN NKO:KPW NKR:AMD NPM:NPR NRY:NOK NZL:NZD OMA:OMR PAK:PKR PAL:ILS PAN:PAB PAP:PGK PAR:PYG PER:IRR PHI:PHP POL:PLN POR:EUR PRU:PEN PUK:IQD PUN:SOS QAT:QAR RAJ:INR RCD:CDF ROM:ROL RWA:RWF SAF:ZAR SAM:WST SAO:STD SAU:SAR SEN:XOF SER:YUM SEY:SCR SHA:MAD SHN:MMK SIA:THB SIE:SLL SIN:SGD SLO:SKK SLV:SIT SNA:SOS SOL:SBD SOM:SOS SOO:RUB SOV:RUB SPR:EUR SRI:LKR SSU:SDD STK:XCD STL:XCD STV:XCD SUD:SDD SUR:SRG SWA:SZL SWE:SEK SWI:CHF SWS:SOS SYR:SYP TAI:TWD TAJ:TJR TAL:AFA TML:LKR TNZ:TZS TOG:XOF TON:TOP TRI:TTD TRK:TMM TUL:AUD TUN:TND TUR:TRL UAE:AED UGA:UGX UKR:UAH UNI:AOA URG:UYU USA:USD UZB:UZS VAN:VUV VEN:VEB VER:CVE VIE:VND WAA:MMK YEM:YER ZAM:ZMK ZIM:ZWD NAU:AUD TIM:IDR'''


def main():
    names, hashes = {}, {}
    for filename in reversed(sys.argv[1:]):
        raw = Path(filename).read_bytes()
        hashes[Path(filename).name] = hashlib.sha256(raw).hexdigest()
        for item in ET.fromstring(raw).iter():
            code = item.findtext('Ccy')
            name = item.findtext('CcyNm')
            if code and name: names[code] = name
    # Clear names where ISO's historical row uses a qualifier or generic unit.
    names.update({'JPY':'Japanese yen', 'GBP':'Pound sterling', 'RUB':'Russian ruble',
                  'CNY':'Chinese yuan', 'AFA':'Afghani', 'DEM':'Deutsche Mark',
                  'YUM':'Yugoslav dinar', 'BYR':'Belarusian ruble'})
    codes = dict(pair.split(':') for pair in PAIRS.split())
    countries = json.loads((ROOT/'data/world.json').read_text(encoding='utf-8'))['countries']
    result = {tag: {'code':codes[tag], 'name':names[codes[tag]]} for tag in countries if tag not in ('SML','PMR')}
    result['SML'] = {'code':'', 'name':'Somaliland shilling'}
    result['PMR'] = {'code':'', 'name':'Transnistrian ruble'}
    assert set(result) == set(countries)
    data = {'source': {'date':'2000-01-01', 'current':'https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-one.xml', 'historical':'https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-three.xml', 'sha256':hashes, 'policy':'Scenario national currency names only; no reserve-currency, exchange-rate or monetary simulation. Euro uses the accounting unit introduced in 1999.'}, 'countries':result}
    (ROOT/'data/currencies_2000.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n',encoding='utf-8',newline='\n')
    print(len(result), 'currency names')


if __name__ == '__main__': main()
