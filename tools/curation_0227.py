"""Auditable historical estimates used where no compatible regional survey exists.
All entries here are estimates, including rounded census-informed approximations.
No religion distribution is inferred from income, density or random state IDs.
"""
# Compact positive shares are normalized by the builder. Labels are exclusive
# scenario categories; syncretic East Asian practices share a combined category.
RELIGION_NATIONAL={
'RUS':{'Orthodox':54,'Sunni':8,'Nonreligious':34,'Buddhist':1,'Christian (other)':2,'Jewish':1},
'CHN':{'Nonreligious':55,'Chinese folk religion':23,'Buddhist':12,'Protestant':5,'Catholic':1,'Sunni':2,'Tibetan Buddhist':1,'Other religions':1},
'VNM':{'Nonreligious':65,'Vietnamese folk religion':18,'Buddhist':9,'Catholic':6.5,'Protestant':.5,'Cao Dai':.7,'Hoa Hao':.3},
'KOR':{'Nonreligious':50,'Buddhist':24,'Protestant':18,'Catholic':8},
'PRK':{'Nonreligious':70,'Traditional / folk':15,'Chondoist':12,'Buddhist':2,'Christian':1},
'ITA':{'Catholic':88,'Nonreligious':10,'Sunni':1,'Other religions':1},
'UKR':{'Orthodox':64,'Nonreligious':22,'Greek Catholic':9,'Protestant':3,'Sunni':1,'Jewish':1},
'EST':{'Nonreligious':62,'Lutheran':14,'Orthodox':20,'Other religions':4},
'LVA':{'Lutheran':22,'Catholic':24,'Orthodox':17,'Nonreligious':34,'Other religions':3},
'LTU':{'Catholic':79,'Orthodox':4,'Protestant':1,'Nonreligious':14,'Other religions':2},
'SVN':{'Catholic':65,'Orthodox':3,'Sunni':3,'Nonreligious':27,'Other religions':2},
'MKD':{'Orthodox':65,'Sunni':32,'Other religions':3},
'XKX':{'Sunni':90,'Orthodox':6,'Catholic':3,'Other religions':1},
'SOM':{'Sunni':99,'Other religions':1},'ESH':{'Sunni':99,'Other religions':1},
'YEM':{'Sunni':60,'Shia (Zaydi)':39,'Other religions':1},
'COG':{'Catholic':50,'Protestant':30,'Traditional / folk':15,'Sunni':2,'Other religions':3},
'COD':{'Catholic':50,'Protestant':35,'Traditional / folk':10,'Sunni':3,'Other religions':2},
'GNQ':{'Catholic':85,'Protestant':5,'Traditional / folk':7,'Other religions':3},
'ERI':{'Orthodox':45,'Sunni':48,'Catholic':4,'Protestant':2,'Other religions':1},
'CIV':{'Sunni':35,'Catholic':17,'Protestant':14,'Traditional / folk':21,'Nonreligious':13},
'GMB':{'Sunni':90,'Christian':8,'Traditional / folk':2},
'GNB':{'Sunni':45,'Traditional / folk':40,'Catholic':12,'Protestant':3},
'TZA':{'Christian':40,'Sunni':35,'Traditional / folk':25},
'MYS':{'Sunni':60,'Buddhist':19,'Christian':9,'Hindu':7,'Chinese folk religion':3,'Other religions':2},
'SGP':{'Buddhist':42.5,'Taoist / folk':8.5,'Sunni':15,'Christian':15,'Hindu':4,'Nonreligious':15},
'NPL':{'Hindu':81,'Buddhist':11,'Sunni':4,'Kirat':3,'Other religions':1},
'MDV':{'Sunni':99,'Other religions':1},
'FSM':{'Catholic':50,'Protestant':47,'Other religions':3},
'WSM':{'Protestant':64,'Catholic':20,'Latter-day Saint':13,'Other religions':3},
'TON':{'Protestant':65,'Catholic':16,'Latter-day Saint':17,'Other religions':2},
'CPV':{'Catholic':90,'Protestant':6,'Other religions':4},
'GRL':{'Lutheran':90,'Other Christian':5,'Nonreligious':5},
'FRO':{'Lutheran':83,'Other Christian':14,'Nonreligious':3},
'ATG':{'Protestant':72,'Catholic':10,'Other Christian':10,'Nonreligious':8},
'BHS':{'Protestant':80,'Catholic':14,'Other religions':6},
'KNA':{'Protestant':75,'Catholic':12,'Other Christian':8,'Other religions':5},
'GTM':{'Catholic':62,'Protestant':30,'Maya traditions':3,'Nonreligious':5},
'NRU':{'Protestant':65,'Catholic':30,'Other religions':5},
'TLS':{'Catholic':93,'Protestant':3,'Sunni':1,'Traditional / folk':3},
'IRQ':{'Shia':60,'Sunni':35,'Christian':3,'Yazidi':2},
'ETH':{'Orthodox':46,'Sunni':34,'Protestant':15,'Traditional / folk':4,'Catholic':1},
'SDN':{'Sunni':93,'Traditional / folk':5,'Christian':2},
'SSD':{'Christian':45,'Traditional / folk':50,'Sunni':5},
'SYR':{'Sunni':74,'Alawite':11,'Christian':10,'Druze':3,'Shia':1,'Other religions':1},
'LBN':{'Shia':28,'Sunni':27,'Maronite':22,'Orthodox':8,'Druze':7,'Other Christian':7,'Other religions':1},
'GBR':{'Protestant':56,'Catholic':10,'Sunni':2.7,'Hindu':1,'Sikh':.6,'Jewish':.5,'Nonreligious':22,'Other / not stated':7.2},
}
# Explicit per-controller departures from a parent-country proxy.
RELIGION_CONTROLLER={
'SHN':{'Buddhist':90,'Christian':5,'Traditional / folk':5},
'CHE':{'Sunni':95,'Orthodox':3,'Other religions':2},
'KAC':{'Protestant':62,'Catholic':10,'Buddhist':20,'Traditional / folk':8},
'KAR':{'Buddhist':48,'Christian':42,'Traditional / folk':10},
'WAA':{'Traditional / folk':65,'Buddhist':25,'Christian':10},
'ACE':{'Sunni':98,'Christian':1,'Other religions':1},
'KUR':{'Sunni':90,'Yazidi':5,'Christian':4,'Other religions':1},
'PUK':{'Sunni':93,'Shia':3,'Christian':2,'Other religions':2},
'IEK':{'Sunni':97,'Other religions':3},
'HAM':{'Sunni':99,'Christian':1},'PAL':{'Sunni':96,'Christian':4},
'NCY':{'Sunni':98,'Other religions':2},'HEZ':{'Shia':85,'Christian':10,'Sunni':5},
'TML':{'Hindu':78,'Catholic':12,'Protestant':5,'Sunni':5},
}
# Per-state religion overrides: historical regional patterns, rounded estimates.
# Tuple: owner tag, matching name fragment, distribution. Long/specific patterns
# take precedence; exact IDs may also be supplied for misleading broad names.
REGIONAL_RELIGION=[
('CHI','Xinjiang',{'Sunni':53,'Nonreligious':32,'Chinese folk religion':10,'Buddhist':3,'Christian':2}),
('CHI','Tibet',{'Tibetan Buddhist':82,'Nonreligious':14,'Chinese folk religion':3,'Sunni':1}),
('CHI','Qinghai',{'Tibetan Buddhist':27,'Sunni':25,'Nonreligious':32,'Chinese folk religion':14,'Christian':2}),
('CHI','Ningxia',{'Sunni':35,'Nonreligious':40,'Chinese folk religion':20,'Buddhist':4,'Christian':1}),
('SYR','As-Suwayda',{'Druze':85,'Christian':9,'Sunni':6}),
('SYR','Latakia',{'Alawite':58,'Sunni':30,'Christian':11,'Other religions':1}),
('SYR','Tartus',{'Alawite':68,'Sunni':18,'Christian':13,'Other religions':1}),
('SYR','Homs',{'Sunni':65,'Alawite':18,'Christian':15,'Shia':2}),
('SYR','Hama',{'Sunni':82,'Alawite':10,'Christian':6,'Shia':2}),
('SYR','Al-Hasakah',{'Sunni':78,'Christian':19,'Yazidi':2,'Other religions':1}),
('SYR','Idlib',{'Sunni':96,'Christian':2,'Shia':2}),
('SYR','Deir ez-Zor',{'Sunni':98,'Christian':1,'Shia':1}),
('SYR','Raqqa',{'Sunni':96,'Christian':3,'Other religions':1}),
('SYR','Daraa',{'Sunni':89,'Christian':7,'Druze':4}),
('RAJ','Punjab',{'Sikh':60,'Hindu':37,'Sunni':2,'Christian':1}),
('RAJ','Jammu and Kashmir',{'Sunni':67,'Hindu':29,'Sikh':2,'Buddhist':1,'Christian':1}),
('RAJ','Ladakh',{'Tibetan Buddhist':45,'Shia':40,'Sunni':10,'Hindu':4,'Christian':1}),
('RAJ','Sikkim',{'Hindu':61,'Buddhist':28,'Christian':7,'Kirat':3,'Other religions':1}),
('RAJ','Kerala',{'Hindu':56,'Sunni':25,'Christian':19}),
('RAJ','Goa',{'Hindu':66,'Catholic':27,'Sunni':6,'Other religions':1}),
('RAJ','Nagaland',{'Protestant':88,'Hindu':8,'Sunni':2,'Traditional / folk':2}),
('RAJ','Mizoram',{'Protestant':87,'Buddhist':8,'Hindu':4,'Other religions':1}),
('RAJ','Meghalaya',{'Christian':70,'Hindu':13,'Traditional / folk':13,'Sunni':4}),
('RAJ','Manipur',{'Hindu':46,'Christian':35,'Sunni':8,'Traditional / folk':11}),
('RAJ','Assam',{'Hindu':65,'Sunni':31,'Christian':3,'Other religions':1}),
('RAJ','Arunachal',{'Traditional / folk':35,'Christian':22,'Hindu':25,'Buddhist':15,'Sunni':2,'Other religions':1}),
('RAJ','West Bengal',{'Hindu':73,'Sunni':25,'Christian':1,'Other religions':1}),
('RAJ','Bihar',{'Hindu':83,'Sunni':16,'Other religions':1}),
('RAJ','Jharkhand',{'Hindu':69,'Sunni':14,'Traditional / folk':13,'Christian':4}),
('RAJ','Braj',{'Hindu':81,'Sunni':18,'Other religions':1}),
('RAJ','Delhi',{'Hindu':82,'Sunni':12,'Sikh':4,'Christian':1,'Jain':1}),
('RAJ','Tamil Nadu',{'Hindu':88,'Sunni':6,'Christian':6}),
('RAJ','Karnataka',{'Hindu':84,'Sunni':12,'Christian':2,'Jain':1,'Other religions':1}),
('RAJ','Telangana',{'Hindu':86,'Sunni':12,'Christian':2}),
('RAJ','Andhra Pradesh',{'Hindu':91,'Sunni':7,'Christian':2}),
('RAJ','Odisha',{'Hindu':94,'Christian':3,'Sunni':2,'Other religions':1}),
('RAJ','Chhattisgarh',{'Hindu':94,'Traditional / folk':3,'Christian':2,'Sunni':1}),
('RAJ','Vidarbha',{'Hindu':80,'Buddhist':10,'Sunni':8,'Other religions':2}),
('RAJ','Maharashtra',{'Hindu':82,'Sunni':11,'Buddhist':5,'Other religions':2}),
('NIG','Biafra',{'Christian':90,'Traditional / folk':8,'Sunni':2}),
('NIG','Borno',{'Sunni':80,'Christian':15,'Traditional / folk':5}),
('NIG','Sokoto',{'Sunni':94,'Christian':4,'Traditional / folk':2}),
('NIG','Kano',{'Sunni':80,'Christian':17,'Traditional / folk':3}),
('NIG','Kebbi',{'Sunni':85,'Christian':12,'Traditional / folk':3}),
('NIG','Benue',{'Christian':76,'Sunni':15,'Traditional / folk':9}),
('NIG','Lagos',{'Christian':55,'Sunni':40,'Traditional / folk':5}),
('ETH','Somali',{'Sunni':96,'Orthodox':3,'Other religions':1}),
('ETH','Afar',{'Sunni':95,'Orthodox':4,'Other religions':1}),
('ETH','Amhara',{'Orthodox':82,'Sunni':17,'Other religions':1}),
('ETH','Tigray',{'Orthodox':94,'Sunni':5,'Other religions':1}),
('ETH','Southern',{'Protestant':45,'Orthodox':25,'Traditional / folk':20,'Sunni':10}),
('ETH','Gambela',{'Protestant':60,'Traditional / folk':25,'Orthodox':10,'Sunni':5}),
('TNZ','Zanzibar',{'Sunni':98,'Christian':1,'Other religions':1}),
('SOV','Tatarstan',{'Sunni':50,'Orthodox':35,'Nonreligious':15}),
('SOV','Bashkortostan',{'Sunni':50,'Orthodox':30,'Nonreligious':20}),
('SOV','Dagestan',{'Sunni':88,'Shia':5,'Orthodox':4,'Nonreligious':3}),
('SOV','Ingushetia',{'Sunni':96,'Orthodox':2,'Other religions':2}),
('SOV','Kabardino',{'Sunni':60,'Orthodox':25,'Nonreligious':15}),
('SOV','Karachay',{'Sunni':55,'Orthodox':30,'Nonreligious':15}),
('SOV','Kalmykia',{'Tibetan Buddhist':50,'Orthodox':25,'Nonreligious':25}),
('SOV','Tuva',{'Tibetan Buddhist':60,'Traditional / folk':20,'Nonreligious':15,'Orthodox':5}),
('SOV','Buryatia',{'Tibetan Buddhist':30,'Orthodox':30,'Nonreligious':30,'Traditional / folk':10}),
('IRQ','Basra',{'Shia':80,'Sunni':17,'Christian':2,'Other religions':1}),
('IRQ','Najaf',{'Shia':97,'Sunni':2,'Other religions':1}),
('IRQ','Karbala',{'Shia':97,'Sunni':2,'Other religions':1}),
('IRQ','Maysan',{'Shia':95,'Sunni':4,'Other religions':1}),
('IRQ','Muthanna',{'Shia':96,'Sunni':3,'Other religions':1}),
('IRQ','Dhi Qar',{'Shia':96,'Sunni':3,'Other religions':1}),
('IRQ','Al-Qādisiyyah',{'Shia':94,'Sunni':5,'Other religions':1}),
('IRQ','Wasit',{'Shia':85,'Sunni':13,'Christian':1,'Other religions':1}),
('IRQ','Al Anbar',{'Sunni':96,'Shia':3,'Other religions':1}),
('IRQ','Saladin',{'Sunni':88,'Shia':10,'Other religions':2}),
('IRQ','Nineveh',{'Sunni':68,'Christian':12,'Yazidi':12,'Shia':7,'Other religions':1}),
('IRQ','Kirkuk',{'Sunni':72,'Shia':18,'Christian':8,'Other religions':2}),
('BOS','Republika Srpska',{'Orthodox':82,'Sunni':11,'Catholic':5,'Other religions':2}),
('BOS','Herzegovina',{'Catholic':60,'Sunni':28,'Orthodox':10,'Other religions':2}),
('BOS','Bosnia',{'Sunni':68,'Catholic':20,'Orthodox':10,'Other religions':2}),
('BOS','Posavina',{'Catholic':60,'Sunni':28,'Orthodox':10,'Other religions':2}),
('CAN','Quebec',{'Catholic':82,'Protestant':5,'Nonreligious':10,'Other religions':3}),
('USA','Utah',{'Latter-day Saint':62,'Protestant':17,'Catholic':7,'Nonreligious':12,'Other religions':2}),
('USA','Massachusetts',{'Catholic':48,'Protestant':25,'Nonreligious':20,'Jewish':4,'Other religions':3}),
('USA','Mississippi',{'Protestant':83,'Catholic':5,'Nonreligious':10,'Other religions':2}),
('USA','Alabama',{'Protestant':80,'Catholic':6,'Nonreligious':12,'Other religions':2}),
('USA','Oregon',{'Protestant':43,'Catholic':15,'Nonreligious':35,'Other religions':7}),
('USA','New York',{'Catholic':40,'Protestant':27,'Jewish':8,'Nonreligious':20,'Other religions':5}),
('USA','Hawaii',{'Protestant':30,'Catholic':20,'Buddhist':15,'Nonreligious':30,'Other religions':5}),
('GER','Bayern',{'Catholic':65,'Protestant':22,'Nonreligious':9,'Sunni':3,'Other religions':1}),
('GER','Franken',{'Catholic':46,'Protestant':39,'Nonreligious':11,'Sunni':3,'Other religions':1}),
('GER','Rhineland',{'Catholic':50,'Protestant':30,'Nonreligious':15,'Sunni':4,'Other religions':1}),
('GER','Saarland',{'Catholic':65,'Protestant':20,'Nonreligious':11,'Sunni':3,'Other religions':1}),
('GER','Saxony',{'Nonreligious':72,'Protestant':23,'Catholic':3,'Sunni':1,'Other religions':1}),
('GER','Brandenburg',{'Nonreligious':75,'Protestant':20,'Catholic':3,'Other religions':2}),
('GER','Thuringia',{'Nonreligious':63,'Protestant':30,'Catholic':5,'Other religions':2}),
('GER','Berlin',{'Nonreligious':58,'Protestant':24,'Catholic':9,'Sunni':7,'Other religions':2}),
('ENG','Northern Ireland',{'Protestant':46,'Catholic':40,'Nonreligious':10,'Other / not stated':4}),
('ENG','Greater London',{'Protestant':38,'Catholic':15,'Sunni':8,'Hindu':4,'Jewish':2,'Sikh':2,'Nonreligious':19,'Other / not stated':12}),
('LEB','Mount Lebanon',{'Maronite':40,'Orthodox':12,'Other Christian':8,'Druze':18,'Sunni':12,'Shia':10}),
('LEB','North',{'Sunni':62,'Maronite':23,'Orthodox':10,'Other Christian':4,'Other religions':1}),
('LEB','Beqaa',{'Shia':50,'Sunni':25,'Maronite':12,'Orthodox':6,'Druze':5,'Other Christian':2}),
('BRM','Chin',{'Protestant':75,'Catholic':10,'Buddhist':10,'Traditional / folk':5}),
('BRM','Rahmanland',{'Sunni':80,'Buddhist':18,'Other religions':2}),
('IND','Aceh',{'Sunni':98,'Other religions':2}),
('IND','Bali',{'Hindu':88,'Sunni':9,'Christian':2,'Other religions':1}),
('IND','Papua',{'Protestant':62,'Catholic':24,'Sunni':10,'Traditional / folk':4}),
('IND','Sulawesi',{'Sunni':78,'Protestant':15,'Catholic':5,'Other religions':2}),
('PHI','Mindanao',{'Catholic':64,'Sunni':26,'Protestant':7,'Traditional / folk':3}),
]
# Larger education indices increase tertiary/secondary attainment relative to
# primary/below-primary; all are estimates, later balanced to national benchmarks.
EDUCATION_CONTEXT={
'CHI':{'Tibet':.55,'Xinjiang':.8,'Guizhou':.7,'Yunnan':.8,'Qinghai':.7,'Beijing':1.6,'Shanghai':1.5,'Tianjin':1.3,'Pearl River':1.25,'Nanjing':1.3},
'RAJ':{'Bihar':.7,'Braj':.8,'Jharkhand':.75,'Chhattisgarh':.8,'Kerala':1.4,'Tamil Nadu':1.15,'Delhi':1.5,'Goa':1.3,'Himachal':1.2,'Ladakh':.8},
'PAK':{'Islamabad':1.6,'Balochistan':.65,'Pashto Tribal':.6,'Malakand':.8,'Central Punjab':1.15},
'COL':{'Cundinamarca':1.3,'Amazonia':.75,'Pacífico':.8,'Antioquia':1.15},
'MOR':{'Rabat':1.3,'Casablanca':1.25,'Souss':.8,'Tafilalet':.75},
'USA':{'Massachusetts':1.3,'Washington, D.C.':1.5,'Mississippi':.8,'West Virginia':.8},
'BRA':{'São Paulo':1.2,'Rio de Janeiro':1.2,'Maranhão':.75,'Piauí':.75},
'SOV':{'Moscow City':1.5,'Saint Petersburg':1.4,'Dagestan':.85,'Tuva':.8},
'AFG':{'Kabul':1.4},'TAL':{'Kabul':1.4},
}
# If a national education series is missing, choose a disclosed historical
# regional peer / broad national development model, never an empty profile.
EDUCATION_PROXIES={'AZE':'ARM','BLR':'UKR','BOS':'CRO','SER':'CRO','KOS':'ALB','KYR':'KAZ','TRK':'KAZ','UZB':'KAZ','NKO':'MON','FAO':'DEN','GRN':'DEN','LEB':'JOR','HEZ':'JOR','NAU':'FIJ','TIM':'IND','MIC':'FIJ','SAM':'FIJ','TON':'FIJ','SOL':'PAP','VAN':'PAP','TUL':'FIJ','BHU':'NEP','VER':'SEN','BFA':'MAL','GUB':'GUI','SAO':'GAB','ERI':'ETH','EGU':'CAM','DJI':'ETH','COM':'TNZ','SOM':'ETH','SML':'ETH','PUN':'ETH','JUB':'ETH','SNA':'ETH','SWS':'ETH','AIA':'ETH','SHA':'MOR','NIG':'GAH','BAH':'BAR','ANT':'BAR','DMI':'BAR','GRA':'BAR','STK':'BAR','STL':'BAR','STV':'BAR'}
# Source raster omits some tiny islands/territories; known historical resident
# orders of magnitude. Uninhabited glaciers/reefs/bases are not invented cities.
SMALL_POPULATION={
'Nauru':10000,'Tuvalu':9600,'Pitcairn Islands':47,'Ascension':1100,'Gibraltar':27700,
'Saint Helena':5200,'Falkland Islands':2900,'British Indian Ocean Territory':0,
'South Georgia and the South Sandwich Islands':0,'Wake Island':0,'Diego Garcia':0,
'Guantanamo Bay':0,'NSA Bahrain':0,'Hawally':0,'Siachen Glacier':0,'Bir Tawil':0,
'Aksai Chin':0,'Shaksgam Valley':0,'Paracel Islands':0,'Western Spratlys':0,
}

# Additional documented regional estimates. No random/density-derived religion.
RELIGION_NATIONAL['PAK']={'Sunni':76,'Shia':20,'Hindu':1.8,'Christian':1.6,'Other religions':.6}
def region_group(tag,names,shares):
 for name in names:REGIONAL_RELIGION.append((tag,name,shares.copy()))
region_group('CHI',['Heilongjiang','Songjiang','Jilin','Liaoning','Liaoxi'],{'Nonreligious':65,'Chinese folk religion':15,'Buddhist':10,'Protestant':6,'Catholic':2,'Sunni':1,'Other religions':1})
region_group('CHI',['Hebei','Shandong','Jiaodong','Henan','Shanxi'],{'Nonreligious':60,'Chinese folk religion':24,'Buddhist':8,'Protestant':4,'Catholic':2,'Sunni':2})
region_group('CHI',['Guangdong','Pearl River','Fujian','Zhejiang'],{'Nonreligious':43,'Chinese folk religion':30,'Buddhist':18,'Protestant':5,'Catholic':2,'Sunni':1,'Other religions':1})
region_group('CHI',['Inner Mongolia','Hulunbuir'],{'Nonreligious':62,'Chinese folk religion':20,'Tibetan Buddhist':10,'Buddhist':4,'Christian':3,'Sunni':1})
region_group('CHI',['Yunnan'],{'Nonreligious':33,'Chinese folk religion':35,'Buddhist':20,'Christian':9,'Sunni':3})
region_group('CHI',['Gansu'],{'Nonreligious':50,'Chinese folk religion':25,'Sunni':10,'Tibetan Buddhist':10,'Christian':5})
region_group('CHI',['Western Sichuan'],{'Nonreligious':28,'Tibetan Buddhist':35,'Chinese folk religion':20,'Buddhist':12,'Christian':4,'Sunni':1})
region_group('RAJ',['Gujarat','Saurashtra'],{'Hindu':90,'Sunni':9,'Jain':.7,'Christian':.3})
region_group('RAJ',['Rajasthan','Marwar'],{'Hindu':89,'Sunni':8,'Sikh':1.5,'Jain':1,'Other religions':.5})
region_group('RAJ',['Himachal'],{'Hindu':95,'Sunni':2,'Buddhist':1,'Sikh':1,'Other religions':1})
region_group('RAJ',['Haryana'],{'Hindu':89,'Sunni':6,'Sikh':4,'Other religions':1})
region_group('RAJ',['Madhya Pradesh','Malwa'],{'Hindu':91,'Sunni':7,'Jain':1,'Other religions':1})
region_group('RAJ',['Puducherry'],{'Hindu':86,'Christian':7,'Sunni':6,'Other religions':1})
region_group('RAJ',['Tripura'],{'Hindu':86,'Sunni':8,'Buddhist':3,'Christian':3})
region_group('PAK',['Gilgit'],{'Shia':45,'Ismaili':25,'Sunni':29,'Other religions':1})
region_group('PAK',['Balochistan'],{'Sunni':96,'Shia':2,'Hindu':1,'Other religions':1})
region_group('PAK',['Malakand','Khyber','Pashto Tribal'],{'Sunni':96,'Shia':3,'Other religions':1})
region_group('PAK',['Sindh'],{'Sunni':70,'Shia':22,'Hindu':6,'Christian':1,'Other religions':1})
region_group('CAN',['British Columbia'],{'Protestant':32,'Catholic':19,'Nonreligious':35,'Sikh':4,'Buddhist':3,'Other religions':7})
region_group('CAN',['Alberta'],{'Protestant':42,'Catholic':26,'Nonreligious':25,'Other religions':7})
region_group('CAN',['Saskatchewan','Manitoba'],{'Protestant':48,'Catholic':30,'Nonreligious':17,'Other religions':5})
region_group('CAN',['Ontario'],{'Catholic':34,'Protestant':35,'Nonreligious':16,'Sunni':3,'Hindu':2,'Jewish':2,'Other religions':8})
region_group('CAN',['New Brunswick'],{'Catholic':53,'Protestant':35,'Nonreligious':10,'Other religions':2})
region_group('CAN',['Newfoundland','Nova Scotia','Prince Edward'],{'Protestant':50,'Catholic':40,'Nonreligious':8,'Other religions':2})
region_group('USA',['Georgia','South Carolina','North Carolina','Tennessee','Kentucky','Oklahoma','Arkansas'],{'Protestant':75,'Catholic':9,'Nonreligious':13,'Other religions':3})
region_group('USA',['New Jersey','Connecticut','Rhode Island','Pennsylvania'],{'Catholic':42,'Protestant':33,'Nonreligious':17,'Jewish':4,'Other religions':4})
region_group('USA',['Idaho','Montana','Wyoming','Colorado','Washington','Nevada','Alaska'],{'Protestant':45,'Catholic':20,'Nonreligious':28,'Other religions':7})
region_group('USA',['Minnesota','Wisconsin','Iowa','Nebraska','North Dakota','South Dakota'],{'Protestant':52,'Catholic':30,'Nonreligious':15,'Other religions':3})
region_group('USA',['California'],{'Catholic':32,'Protestant':34,'Nonreligious':24,'Buddhist':3,'Jewish':2,'Other religions':5})
region_group('USA',['Texas'],{'Protestant':55,'Catholic':30,'Nonreligious':12,'Other religions':3})
region_group('USA',['Louisiana'],{'Catholic':40,'Protestant':47,'Nonreligious':10,'Other religions':3})
region_group('USA',['Puerto Rico'],{'Catholic':78,'Protestant':17,'Nonreligious':4,'Other religions':1})
region_group('GER',['Saxony-Anhalt','Mecklenburg'],{'Nonreligious':72,'Protestant':23,'Catholic':3,'Other religions':2})
region_group('GER',['Schleswig','Lower Saxony'],{'Protestant':58,'Catholic':15,'Nonreligious':22,'Sunni':4,'Other religions':1})
region_group('GER',['North Rhine'],{'Catholic':42,'Protestant':29,'Nonreligious':22,'Sunni':6,'Other religions':1})
region_group('ENG',['Scotland','Scottish'],{'Protestant':43,'Catholic':16,'Nonreligious':29,'Sunni':1,'Other / not stated':11})
region_group('MAY',['Sabah','Sarawak'],{'Sunni':40,'Christian':40,'Buddhist':12,'Traditional / folk':5,'Other religions':3})
region_group('SIA',['Pattani'],{'Sunni':80,'Buddhist':19,'Other religions':1})
RELIGION_NATIONAL.update({'CUB':{'Catholic':50,'Afro-Cuban traditions':20,'Nonreligious':25,'Protestant':4,'Other religions':1},'TUV':{'Protestant':97,'Catholic':1,'Christian (other)':1,'Other religions':1},'MRT':{'Sunni':99,'Other religions':1},'SAU':{'Sunni':85,'Shia':10,'Christian':3,'Hindu':1,'Other religions':1}})
# Foreign ownership does not erase the surrounding resident population/culture.
region_group('USA',['Hawally'],{'Sunni':65,'Shia':25,'Christian':6,'Hindu':3,'Other religions':1})
region_group('USA',['NSA Bahrain'],{'Shia':55,'Sunni':35,'Christian':6,'Hindu':3,'Other religions':1})
region_group('USA',['Guantanamo'],{'Catholic':50,'Afro-Cuban traditions':20,'Nonreligious':25,'Protestant':4,'Other religions':1})
region_group('USA',['Kiribati'],{'Catholic':55,'Protestant':42,'Other religions':3})
region_group('USA',['Wake Island'],{'Protestant':80,'Catholic':8,'Latter-day Saint':6,'Other religions':6})
region_group('USA',['American Samoa'],{'Protestant':63,'Catholic':20,'Latter-day Saint':14,'Other religions':3})
region_group('USA',['Guam','Mariana'],{'Catholic':80,'Protestant':12,'Buddhist':3,'Other religions':5})
region_group('FRA',['Mayotte'],{'Sunni':97,'Catholic':2,'Other religions':1})
region_group('FRA',['Wallis'],{'Catholic':98,'Other religions':2})
region_group('FRA',['French Polynesia'],{'Protestant':52,'Catholic':30,'Latter-day Saint':8,'Other religions':10})
region_group('FRA',['New Caledonia'],{'Catholic':60,'Protestant':30,'Nonreligious':8,'Other religions':2})
region_group('FRA',['Martinique','Guadeloupe','Saint Martin'],{'Catholic':80,'Protestant':10,'Nonreligious':8,'Other religions':2})
EDUCATION_CONTEXT['USA'].update({'Kiribati':.45,'Wake Island':.45,'American Samoa':.6,'Guam':.8,'Mariana':.7,'Hawally':.9,'NSA Bahrain':.9})
EDUCATION_CONTEXT['FRA']={'Mayotte':.35,'Wallis':.6,'French Polynesia':.75,'New Caledonia':.8,'French Guiana':.7,'Île-de-France':1.3}
