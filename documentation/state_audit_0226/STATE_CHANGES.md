# Bunny World 0.2.0.26 — State detail

Apply to the confirmed 0.2.0.25 project (GitHub main at aeacb59). This is a changed-files patch. Close Godot, extract into the project root, replace files, run Prepare_BunnyWorld.bat, then start a fresh campaign in Godot 4.5.1 Standard or export a new release EXE. Old campaign saves belong to the previous scenario.

29 new states; 224 countries, 1,264 states, 13,308 land provinces. All four canonical province tiles are byte-identical to .25, including Antarctica. No province was cut, added or deleted. Every country retains exactly its population, building inventory, building-slot total and province ownership. Shared borders and map resources are rebuilt from the same province membership source.

| Country | Before | After | MD guide |
|---|---:|---:|---:|
| China | 35 | 44 | 43 |
| Syria | 8 | 14 | 15 |
| India | 40 | 44 | 45 |
| Morocco | 7 | 11 | 11 |
| Pakistan | 8 | 11 | 12 |
| Colombia | 5 | 8 | 8 |

Taiwan and Afghanistan are unchanged. The Philippines and all other explicit exclusions are unchanged. Previously approved mergers remain, including one Micronesia state, four Papua New Guinea states, the Mindanao union, Mariana Islands and the Hawaii island exceptions. No removed island, reef, military-base or tiny-territory state is recreated.

## New states and whole-province membership

| ID | Country | New state | Member province IDs |
|---:|---|---|---|
| 1828 | China | Hulunbuir | 1774, 1777, 1779, 1781, 1790, 1792, 1793, 1813, 1829, 1832, 1842, 1844, 1845, 1846, 1848, 1856, 1878, 1899, 1901 |
| 1829 | China | Songjiang | 2005, 2008, 2009, 2010, 2013, 2014, 2017, 2021, 2022, 2023, 2025, 2029, 2030, 2031, 2033, 2037, 2040, 2041, 2042, 2046, 2049, 2050, 2051, 2053, 2057, 2058, 2059, 2064, 2065, 2066, 2067, 2071, 2075, 2078, 2079 |
| 1830 | China | Liaoxi | 2121, 2125, 2127, 2129, 2130, 2135, 2136, 2139, 2146, 2148, 2150, 2151, 2154, 2159, 2160, 2164, 2165 |
| 1831 | China | Pearl River Delta | 2210, 2211, 2212, 2216, 2220, 2221, 2225, 2226, 2230, 2234 |
| 1832 | China | Western Guangdong | 2214, 2215, 2217, 2227, 2231 |
| 1833 | China | Nanjing | 2315, 2328, 2338 |
| 1834 | China | Jiaodong | 2342, 2345, 2353, 2355, 2361, 2367, 2369, 2372, 2374, 2377 |
| 1835 | China | Northern Hebei | 2384, 2387, 2388, 2393, 2394, 2395, 2396, 2399, 2400, 2401, 2403, 2406, 2408 |
| 1836 | China | Western Sichuan | 2454, 2456, 2458, 2460, 2461, 2462, 2465, 2466, 2467, 2468, 2469, 2471, 2472, 2473, 2474, 2477, 2480, 2481, 2483, 2484, 2491, 2492, 2493, 2495, 2497, 2498, 2500, 2501, 2503, 2505, 2507, 2510, 2511, 2513, 2515 |
| 1837 | Syria | As-Suwayda | 10320, 10321, 10322, 14015 |
| 1838 | Syria | Hama | 10329, 10330, 10331, 10332, 14027, 14028, 14029 |
| 1839 | Syria | Tartus | 10283, 10285, 10286 |
| 1840 | Syria | Idlib | 10316, 10317, 14013, 14014 |
| 1841 | Syria | Qalamoun | 10289, 10294 |
| 1842 | Syria | Southern Deir ez-Zor | 14017, 14018, 14023, 14025 |
| 1843 | India | Vidarbha | 7746, 7752, 7756, 7757, 7763, 7764 |
| 1845 | India | Malwa–Nimar | 7836, 7840, 7842, 7848, 7849, 7851, 7862 |
| 1846 | India | Marwar | 7612, 7620, 7624, 7625, 7631, 7633, 7634, 7635, 7640 |
| 1847 | India | Saurashtra–Kutch | 7645, 7646, 7647, 7653, 7654, 7655, 7656 |
| 1848 | Pakistan | Northern Punjab | 6836, 6840, 6847 |
| 1849 | Pakistan | Southern Punjab | 6837, 6839, 6843, 6848, 6849, 6850 |
| 1850 | Pakistan | Malakand | 6804, 6810, 6811 |
| 1851 | Morocco | Tanger–Tetouan | 6343, 6346, 6350, 6358, 6363, 6365, 6408 |
| 1852 | Morocco | Fès–Taza | 6323, 6328, 6330, 6331, 6333, 6334, 6336, 6338 |
| 1853 | Morocco | Rabat–Salé–Gharb | 6342, 6345, 6357, 6360, 6364, 6366, 6368, 6369 |
| 1854 | Morocco | Casablanca–Chaouia–Doukkala | 6341, 6352, 6353, 6359, 6361, 6367, 6370, 6383, 6384, 6391, 6392 |
| 1855 | Colombia | Santander | 3010, 3012, 3019 |
| 1856 | Colombia | Central Andes | 2988, 3035, 3036, 3041, 3045 |
| 1857 | Colombia | Pacífico | 2987, 2989, 2995, 2997, 2998, 3033, 3034, 3038, 3040, 3043, 3044 |

## Every reviewed regional grouping

These are whole-province approximations of real regional units, not exact administrative polygons. Maximum native land-pixel overlap determines a boundary province; no rectangular cuts or new fragments. Modern administrative references guide placement and names, without asserting that every division had the same legal boundary in 2000. MD supplies counts/naming context only; no MD geometry is used.

Songjiang is a gameplay grouping of the listed southern/eastern Heilongjiang prefectures, rather than a claim to reproduce the historic province. Northern Hebei includes Tangshan and Qinhuangdao to retain a connected mainland grouping around Beijing/Tianjin. Western Sichuan includes Panzhihua with Liangshan. Western Guangdong keeps Yunfu with the western coastal region so that neither mainland remainder is disconnected.

Morocco uses real pre-2015 member regions: composite names explicitly identify the regions grouped together. The incorrectly placed Casablanca-Settat label is replaced. Colombia uses department groups, transferring Meta to Orinoquía, Boyacá to Cundinamarca–Boyacá and Córdoba to Caribe. Retained Caribbean islands/banks remain merged into Caribe.

### CHI_179

- **Inner Mongolia (179)** — population 41,798,820; capital Baotou. Reference members: Alxa, Baotou, Baynnur, Chifeng, Hohhot, Ordos, Tongliao, UlaanChab, Wuhai, XilinGol, Xing'an. Provinces: 1767, 1768, 1769, 1770, 1771, 1772, 1773, 1775, 1776, 1778, 1780, 1782, 1783, 1784, 1785, 1786, 1787, 1788, 1789, 1791, 1794, 1795, 1796, 1797, 1798, 1799, 1800, 1801, 1802, 1803, 1804, 1805, 1806, 1807, 1808, 1809, 1810, 1811, 1812, 1814, 1815, 1816, 1817, 1818, 1819, 1820, 1821, 1822, 1823, 1824, 1825, 1826, 1827, 1828, 1830, 1831, 1833, 1834, 1835, 1836, 1837, 1838, 1839, 1840, 1841, 1843, 1847, 1849, 1850, 1851, 1852, 1853, 1854, 1855, 1857, 1858, 1859, 1860, 1861, 1862, 1863, 1864, 1865, 1866, 1867, 1868, 1869, 1870, 1871, 1872, 1873, 1874, 1875, 1876, 1877, 1879, 1880, 1881, 1882, 1883, 1884, 1885, 1886, 1887, 1888, 1889, 1890, 1891, 1892, 1893, 1894, 1895, 1896, 1897, 1898, 1900, 1902, 1903.
- **Hulunbuir (1828)** — population 4,070,598; capital Hulunbuir administrative centre. Reference members: Hulunbuir. Provinces: 1774, 1777, 1779, 1781, 1790, 1792, 1793, 1813, 1829, 1832, 1842, 1844, 1845, 1846, 1848, 1856, 1878, 1899, 1901.

Boundary/source-fit review: province 1793: 55.4% winning share, 99.9% source coverage. Full per-province vote counts are in data/state_plan_0226.json. Zero coverage occurs at source shoreline/remote-island mismatches, assigned to the nearest existing regional group, never a new island state.

### CHI_182

- **Heilongjiang (182)** — population 11,551,320; capital Daqing. Reference members: Daqing, Daxing'anling, Hegang, Heihe, Qiqihar, Suihua, Yichun. Provinces: 2006, 2007, 2011, 2012, 2015, 2016, 2018, 2019, 2020, 2024, 2026, 2027, 2028, 2032, 2034, 2035, 2036, 2038, 2039, 2043, 2044, 2045, 2047, 2048, 2052, 2054, 2055, 2056, 2060, 2061, 2062, 2063, 2068, 2069, 2070, 2072, 2073, 2074, 2076, 2077.
- **Songjiang (1829)** — population 11,839,636; capital Harbin. Reference members: Harbin, Jiamusi, Jixi, Mudanjiang, Qitaihe, Shuangyashan. Provinces: 2005, 2008, 2009, 2010, 2013, 2014, 2017, 2021, 2022, 2023, 2025, 2029, 2030, 2031, 2033, 2037, 2040, 2041, 2042, 2046, 2049, 2050, 2051, 2053, 2057, 2058, 2059, 2064, 2065, 2066, 2067, 2071, 2075, 2078, 2079.

Boundary/source-fit review: province 2016: 56.5% winning share, 100.0% source coverage. Full per-province vote counts are in data/state_plan_0226.json. Zero coverage occurs at source shoreline/remote-island mismatches, assigned to the nearest existing regional group, never a new island state.

### CHI_184

- **Liaoning (184)** — population 31,586,405; capital Shenyang. Reference members: Anshan, Benxi, Dalian, Dandong, Fushun, Liaoyang, Shenyang, Tieling. Provinces: 2119, 2120, 2122, 2123, 2124, 2126, 2128, 2131, 2132, 2133, 2134, 2137, 2138, 2140, 2141, 2142, 2143, 2145, 2147, 2152, 2153, 2155, 2156, 2157, 2158, 2161, 2162, 2163.
- **Liaoxi (1830)** — population 11,260,522; capital Jinxi. Reference members: Chaoyang, Fuxin, Huludao, Jinzhou, Panjin. Provinces: 2121, 2125, 2127, 2129, 2130, 2135, 2136, 2139, 2146, 2148, 2150, 2151, 2154, 2159, 2160, 2164, 2165.

Boundary/source-fit review: province 2151: 50.2% winning share, 99.9% source coverage. Full per-province vote counts are in data/state_plan_0226.json. Zero coverage occurs at source shoreline/remote-island mismatches, assigned to the nearest existing regional group, never a new island state.

### CHI_187

- **Guangdong (187)** — population 25,698,156; capital Shantou. Reference members: Chaozhou, Heyuan, Jieyang, Meizhou, Qingyuan, Shantou, Shanwei, Shaoguan. Provinces: 2213, 2218, 2219, 2222, 2223, 2224, 2228, 2229, 2232, 2233, 2235, 2236, 2237, 2238.
- **Pearl River Delta (1831)** — population 49,472,873; capital Guangzhou. Reference members: Dongguan, Foshan, Guangzhou, Huizhou, Jiangmen, Shenzhen, Zhaoqing, Zhongshan, Zhuhai. Provinces: 2210, 2211, 2212, 2216, 2220, 2221, 2225, 2226, 2230, 2234.
- **Western Guangdong (1832)** — population 13,672,952; capital Zhanjiang. Reference members: Maoming, Yangjiang, Yunfu, Zhanjiang. Provinces: 2214, 2215, 2217, 2227, 2231.

### CHI_192

- **Jiangsu (192)** — population 65,080,024; capital Xuzhou. Reference members: Changzhou, Huai'an, Lianyungang, Nantong, Suqian, Suzhou, Taizhou, Wuxi, Xuzhou, Yancheng, Yangzhou, Zhenjiang. Provinces: 2316, 2317, 2318, 2319, 2320, 2321, 2322, 2323, 2324, 2325, 2326, 2327, 2329, 2330, 2331, 2332, 2333, 2334, 2335, 2336, 2337, 2339, 2340.
- **Nanjing (1833)** — population 11,689,474; capital Nanjing. Reference members: Nanjing. Provinces: 2315, 2328, 2338.

### CHI_193

- **Shandong (193)** — population 71,388,740; capital Zibo. Reference members: Binzhou, Dezhou, Dongying, Heze, Jinan, Jining, Laiwu, Liaocheng, Linyi, Rizhao, Tai'an, Weifang, Zaozhuang, Zibo. Provinces: 2341, 2343, 2344, 2346, 2347, 2348, 2349, 2350, 2351, 2352, 2354, 2356, 2357, 2358, 2359, 2360, 2362, 2363, 2365, 2366, 2368, 2370, 2371, 2373, 2375, 2376, 2378, 2379, 2380, 2381, 2382.
- **Jiaodong (1834)** — population 21,294,661; capital Qingdao. Reference members: Qingdao, Weihai, Yantai. Provinces: 2342, 2345, 2353, 2355, 2361, 2367, 2369, 2372, 2374, 2377.

### CHI_194

- **Hebei (194)** — population 38,589,307; capital Shijiazhuang. Reference members: Baoding, Cangzhou, Handan, Hengshui, Langfang, Shijiazhuang, Xingtai. Provinces: 2383, 2385, 2386, 2389, 2390, 2391, 2392, 2397, 2398, 2402, 2404, 2405, 2407, 2410.
- **Northern Hebei (1835)** — population 30,101,545; capital Tangshan. Reference members: Chengde, Qinhuangdao, Tangshan, Zhangjiakou. Provinces: 2384, 2387, 2388, 2393, 2394, 2395, 2396, 2399, 2400, 2401, 2403, 2406, 2408.

### CHI_197

- **Sichuan (197)** — population 61,181,810; capital Chengdu. Reference members: Bazhong, Chengdu, Dazhou, Deyang, Guang'an, Guangyuan, Leshan, Luzhou, Meishan, Mianyang, Nanchong, Neijiang, Neijiang]], Suining, Ya'an, Yibin, Zigong, Ziyang. Provinces: 2445, 2446, 2447, 2448, 2449, 2450, 2451, 2452, 2453, 2455, 2457, 2459, 2463, 2464, 2470, 2475, 2476, 2478, 2479, 2482, 2485, 2486, 2487, 2488, 2489, 2490, 2494, 2496, 2499, 2502, 2504, 2506, 2508, 2509, 2512, 2514.
- **Western Sichuan (1836)** — population 22,924,260; capital Panzhihua. Reference members: GarzêTibetan, LiangshanYi, NgawaTibetanandQiang, Panzhihua. Provinces: 2454, 2456, 2458, 2460, 2461, 2462, 2465, 2466, 2467, 2468, 2469, 2471, 2472, 2473, 2474, 2477, 2480, 2481, 2483, 2484, 2491, 2492, 2493, 2495, 2497, 2498, 2500, 2501, 2503, 2505, 2507, 2510, 2511, 2513, 2515.

Boundary/source-fit review: province 2499: 53.3% winning share, 100.0% source coverage. Full per-province vote counts are in data/state_plan_0226.json. Zero coverage occurs at source shoreline/remote-island mismatches, assigned to the nearest existing regional group, never a new island state.

### SYR_1797

- **Daraa–Quneitra (1797)** — population 884,057; capital Dar‘ā. Reference members: Western al-Samadania, Daraa, Quneitra. Provinces: 10323, 10324, 10328, 10337, 10338, 14016.
- **As-Suwayda (1837)** — population 261,543; capital As-Suwayda administrative centre. Reference members: As-Suwayda. Provinces: 10320, 10321, 10322, 14015.

### SYR_1798

- **Homs (1798)** — population 1,950,386; capital Homs. Reference members: Homs. Provinces: 10276, 10277, 10278, 10279, 10280, 10281, 10282, 13982, 13983, 13984, 13985, 13986, 13987, 13988, 13989, 13990, 13991, 13992, 13993, 13994, 13995, 13996, 13997, 13998.
- **Hama (1838)** — population 681,168; capital Hamah. Reference members: Hama. Provinces: 10329, 10330, 10331, 10332, 14027, 14028, 14029.

### SYR_1799

- **Latakia (1799)** — population 1,174,370; capital Latakia. Reference members: Latakia. Provinces: 10318, 10319.
- **Tartus (1839)** — population 246,547; capital Tartus administrative centre. Reference members: Tartus. Provinces: 10283, 10285, 10286.

### SYR_1803

- **Aleppo (1803)** — population 4,290,655; capital Aleppo. Reference members: Aleppo. Provinces: 10309, 10310, 10311, 10312, 10313, 10314, 10315, 14010, 14011, 14012.
- **Idlib (1840)** — population 493,176; capital Idlib administrative centre. Reference members: Idlib. Provinces: 10316, 10317, 14013, 14014.

### SYR_1800

- **Damascus and Rif Dimashq (1800)** — population 3,362,403; capital Damascus. Reference members: At-Tall, Darayya, Duma, MarkazRifDimashq, Qatana, Zabadani. Provinces: 10287, 10288, 10290, 10291, 10292, 10293, 10334, 10336, 13999, 14000, 14001.
- **Qalamoun (1841)** — population 178,632; capital Qalamoun administrative centre. Reference members: Al-Qutayfah, An-Nabk, Yabrud. Provinces: 10289, 10294.

### SYR_1804

- **Northern Deir ez-Zor (1804)** — population 781,078; capital Dayr az Zawr. Reference members: Deirez-Zor. Provinces: 10325, 10326, 10327, 14019, 14020, 14021, 14022, 14024, 14026.
- **Southern Deir ez-Zor (1842)** — population 115,504; capital Southern Deir ez-Zor administrative centre. Reference members: AbuKamal, Mayadin. Provinces: 14017, 14018, 14023, 14025.

### RAJ_904

- **Maharashtra (904)** — population 80,443,985; capital Mumbai. Reference members: Ahmadnagar, Aurangabad, Bid, Dhule, Hingoli, Jalgaon, Jalna, Kolhapur, Latur, Nanded, Nandurbar, Nashik, Osmanabad, Palghar, Parbhani, Pune, Raigarh, Ratnagiri, Sangli, Satara, Sindhudurg, Solapur, Thane. Provinces: 7744, 7745, 7747, 7748, 7749, 7750, 7751, 7753, 7754, 7755, 7758, 7759, 7760, 7761, 7762, 7765, 7766, 7767, 7768, 7769, 7770.
- **Vidarbha (1843)** — population 18,259,018; capital Nagpur. Reference members: Akola, Amravati, Bhandara, Buldana, Chandrapur, Garhchiroli, Gondiya, Nagpur, Wardha, Washim, Yavatmal. Provinces: 7746, 7752, 7756, 7757, 7763, 7764.

### RAJ_915

- **Madhya Pradesh (915)** — population 53,203,132; capital Bhopal. Reference members: Anuppur, Ashoknagar, Balaghat, Betul, Bhind, Bhopal, Chhatarpur, Chhindwara, Damoh, Datia, Dindori, Guna, Gwalior, Harda, Hoshangabad, Jabalpur, Katni, Mandla, Morena, Narsimhapur, Panna, Raisen, Rajgarh, Rewa, Sagar, Satna, Sehore, Seoni, Shahdol, Sheopur, Shivpuri, Sidhi, Singrauli, Tikamgarh, Umaria, Vidisha. Provinces: 7837, 7838, 7839, 7841, 7843, 7844, 7845, 7846, 7847, 7850, 7852, 7853, 7854, 7855, 7856, 7857, 7858, 7859, 7860, 7861, 7863, 7864.
- **Malwa–Nimar (1845)** — population 26,040,574; capital Indore. Reference members: AgarMalwa, Alirajpur, Barwani, Burhanpur, Dewas, Dhar, EastNimar, Indore, Jhabua, Mandsaur, Neemuch, Ratlam, Shajapur, Ujjain, WestNimar. Provinces: 7836, 7840, 7842, 7848, 7849, 7851, 7862.

Boundary/source-fit review: province 7855: 51.8% winning share, 86.8% source coverage. Full per-province vote counts are in data/state_plan_0226.json. Zero coverage occurs at source shoreline/remote-island mismatches, assigned to the nearest existing regional group, never a new island state.

### RAJ_892

- **Rajasthan (892)** — population 53,245,839; capital Jaipur. Reference members: Ajmer, Alwar, Banswara, Baran, Bharatpur, Bhilwara, Bikaner, Bundi, Chittaurgarh, Churu, Dausa, Dhaulpur, Dungarpur, Ganganagar, Hanumangarh, Jaipur, Jhalawar, Jhunjhunun, Karauli, Kota, Pratapgarh, Rajsamand, SawaiMadhopur, Sikar, Tonk, Udaipur. Provinces: 7611, 7613, 7614, 7615, 7616, 7617, 7618, 7619, 7621, 7622, 7623, 7626, 7627, 7628, 7629, 7630, 7632, 7636, 7637, 7638, 7639, 7641.
- **Marwar (1846)** — population 16,733,681; capital Jodhpur. Reference members: Barmer, Jaisalmer, Jalor, Jodhpur, Nagaur, Pali, Sirohi. Provinces: 7612, 7620, 7624, 7625, 7631, 7633, 7634, 7635, 7640.

Boundary/source-fit review: province 7634: 52.3% winning share, 98.7% source coverage. Full per-province vote counts are in data/state_plan_0226.json. Zero coverage occurs at source shoreline/remote-island mismatches, assigned to the nearest existing regional group, never a new island state.

### RAJ_893

- **Gujarat (893)** — population 34,096,946; capital Ahmedabad. Reference members: Ahmadabad, Anand, Aravalli, BanasKantha, Bharuch, ChhotaUdaipur, Dahod, Gandhinagar, Kheda, Mahesana, Mahisagar, Narmada, Navsari, PanchMahals, Patan, SabarKantha, Surat, Tapi, TheDangs, Vadodara, Valsad. Provinces: 7642, 7643, 7644, 7648, 7649, 7650, 7651, 7652, 7743.
- **Saurashtra–Kutch (1847)** — population 14,659,292; capital Rajkot. Reference members: Amreli, Bhavnagar, Botad, DevbhumiDwarka, GirSomnath, Jamnagar, Junagadh, Kachchh, Morbi, Porbandar, Rajkot, Surendranagar. Provinces: 7645, 7646, 7647, 7653, 7654, 7655, 7656.

Boundary/source-fit review: province 7651: 56.8% winning share, 95.4% source coverage. Full per-province vote counts are in data/state_plan_0226.json. Zero coverage occurs at source shoreline/remote-island mismatches, assigned to the nearest existing regional group, never a new island state.

### PAK_764

- **Central Punjab (764)** — population 41,020,600; capital Lahore. Reference members: Faisalabad, Gujranwala, Lahore. Provinces: 6834, 6835, 6838, 6841, 6842, 6844, 6845, 6846.
- **Northern Punjab (1848)** — population 12,346,317; capital Rawalpindi. Reference members: Rawalpindi, Sargodha. Provinces: 6836, 6840, 6847.
- **Southern Punjab (1849)** — population 23,650,078; capital Multan. Reference members: Bahawalpur, DeraGhaziKhan, Multan. Provinces: 6837, 6839, 6843, 6848, 6849, 6850.

### PAK_761

- **Khyber Pakhtunkhwa (761)** — population 12,370,176; capital Peshawar. Reference members: Bannu, DeraIsmailKhan, F.A.T.A., Hazara, Kohat, Mardan, Peshawar. Provinces: 6805, 6806, 6807, 6808, 6809, 6812, 6813, 6814.
- **Malakand (1850)** — population 6,716,609; capital Saidu. Reference members: Malakand. Provinces: 6804, 6810, 6811.

### MOR_mainland

- **Oriental (694)** — population 1,955,031; capital Oujda. Reference members: Oriental. Provinces: 6324, 6325, 6326, 6327, 6329, 6332, 6335, 6337, 6340.
- **Tanger–Tetouan (1851)** — population 1,867,136; capital Tangier. Reference members: Tangier-Tetouan. Provinces: 6343, 6346, 6350, 6358, 6363, 6365, 6408.
- **Fès–Taza (1852)** — population 4,125,165; capital Fes. Reference members: Taza-Al Hoceïma-Taounate, Fès-méknas-boulmane. Provinces: 6323, 6328, 6330, 6331, 6333, 6334, 6336, 6338.
- **Rabat–Salé–Gharb (1853)** — population 3,410,061; capital Rabat. Reference members: Gharb-Chrarda-Béni Hssen, Rabat-Salé-Zemmour-Zaër. Provinces: 6342, 6345, 6357, 6360, 6364, 6366, 6368, 6369.
- **Meknès–Tafilalet (695)** — population 3,196,558; capital Meknes. Reference members: Meknès-Tafilalet. Provinces: 6344, 6348, 6351, 6354, 6356, 6362.
- **Casablanca–Chaouia–Doukkala (1854)** — population 6,071,609; capital Casablanca. Reference members: Chaouia-Ouardigha, Grand Casablanca, Doukkala Abda. Provinces: 6341, 6352, 6353, 6359, 6361, 6367, 6370, 6383, 6384, 6391, 6392.
- **Marrakech–Tadla (697)** — population 4,506,628; capital Marrakesh. Reference members: Marrakesh-Tensift-El Haouz, Tadla-Azilal. Provinces: 6347, 6349, 6355, 6382, 6385, 6386, 6387, 6388, 6389, 6390, 6393.
- **Souss–Massa–Draa (696)** — population 3,011,893; capital Agadir. Reference members: Suss-Massa-Draa. Provinces: 6371, 6372, 6373, 6374, 6375, 6376, 6377, 6378, 6379, 6380, 6381.

Boundary/source-fit review: province 6346: 59.4% winning share, 100.0% source coverage; province 6349: 52.8% winning share, 100.0% source coverage; province 6353: 53.8% winning share, 100.0% source coverage; province 6387: 50.9% winning share, 100.0% source coverage; province 6408: 0.0% winning share, 0.0% source coverage. Full per-province vote counts are in data/state_plan_0226.json. Zero coverage occurs at source shoreline/remote-island mismatches, assigned to the nearest existing regional group, never a new island state.

### COL_regions

- **Amazonia (234)** — population 1,320,047; capital Amazonia administrative centre. Reference members: Putumayo, Vaupés, Amazonas, Caquetá, Guaviare. Provinces: 2990, 2991, 2992, 2993, 2994, 2996, 2999, 3000.
- **Orinoquía (235)** — population 3,943,318; capital Yopal. Reference members: Guainía, Arauca, Vichada, Casanare, Meta. Provinces: 3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3026, 3027, 3028, 3029, 3030, 3031.
- **Caribe (236)** — population 8,886,550; capital Barranquilla. Reference members: La Guajira, Cesar, Córdoba, Sucre, Bolívar, Atlántico, Magdalena, Archipelago of Saint Andréws. Provinces: 3009, 3011, 3013, 3014, 3015, 3018, 3021, 3022, 3023, 3037, 3042, 3047, 3048, 4994.
- **Cundinamarca–Boyacá (239)** — population 5,875,825; capital Bogota. Reference members: Boyacá, Bogotá, Cundinamarca. Provinces: 3016, 3020, 3025.
- **Antioquia (240)** — population 5,532,625; capital Medellín. Reference members: Antioquia. Provinces: 3032, 3039, 3046.
- **Santander (1855)** — population 3,237,972; capital Bucaramanga. Reference members: Norte de Santander, Santander. Provinces: 3010, 3012, 3019.
- **Central Andes (1856)** — population 2,929,678; capital Ibagué. Reference members: Huila, Caldas, Tolima, Quindío, Risaralda. Provinces: 2988, 3035, 3036, 3041, 3045.
- **Pacífico (1857)** — population 8,011,517; capital Pasto. Reference members: Nariño, Chocó, Cauca, Valle del Cauca. Provinces: 2987, 2989, 2995, 2997, 2998, 3033, 3034, 3038, 3040, 3043, 3044.

Boundary/source-fit review: province 2988: 54.7% winning share, 100.0% source coverage; province 3019: 51.2% winning share, 100.0% source coverage; province 3034: 57.7% winning share, 100.0% source coverage; province 3045: 59.4% winning share, 100.0% source coverage; province 3047: 0.0% winning share, 0.0% source coverage; province 3048: 0.0% winning share, 0.0% source coverage; province 4994: 0.0% winning share, 0.0% source coverage. Full per-province vote counts are in data/state_plan_0226.json. Zero coverage occurs at source shoreline/remote-island mismatches, assigned to the nearest existing regional group, never a new island state.

## Renamed retained states

| State ID | Previous name | New name |
|---:|---|---|
| 187 | Guangdong — North | Guangdong |
| 234 | Amazonas / Cauca | Amazonia |
| 236 | Magdalena / Santander | Caribe |
| 239 | Cundinamarca | Cundinamarca–Boyacá |
| 240 | Tolima / Antioquia | Antioquia |
| 694 | Oriental / Taza-Al Hoceïma-Taounate | Oriental |
| 695 | Meknès-Tafilalet / Rabat-Salé-Zemmour-Zaër | Meknès–Tafilalet |
| 696 | Suss-Massa-Draa | Souss–Massa–Draa |
| 697 | Casablanca-Settat | Marrakech–Tadla |
| 761 | Khyber Pakhtunkhwa — South | Khyber Pakhtunkhwa |
| 764 | Punjab — South | Central Punjab |
| 1797 | Southern Syria | Daraa–Quneitra |
| 1798 | Central Syria | Homs |
| 1799 | Syrian Coast | Latakia |
| 1800 | Damascus | Damascus and Rif Dimashq |
| 1801 | Jazira | Al-Hasakah |
| 1803 | Northern Syria | Aleppo |
| 1804 | Deir ez-Zor | Northern Deir ez-Zor |

## Skipped and unresolved choices

- **Mumbai** — No whole province fits the municipal footprint; retained in Maharashtra. Options: retain combined state, or revisit after a future province subdivision.
- **Damascus municipal state** — The city has no separate whole-province footprint. Kept with Rif Dimashq; Qalamoun uses northern administrative districts instead. Options: retain the combined state or subdivide provinces in a later patch.
- **Uttar Pradesh / Braj** — Braj, Awadh and Purvanchal lack a single agreed administrative division at this scale. Options: official district groups, or real administrative divisions grouped into larger states. Existing state and name retained pending that decision.
- **Balochistan ethnic split** — Pashtun/Baloch boundaries and an appropriate year-2000 grouping need more evidence. Options: official divisions or a documented cultural grouping. Kept intact; Pakistan is already within one of MD.
- **Optional countries** — Germany, Spain, United Kingdom, Indonesia, Argentina, Chile, Madagascar and Angola unchanged. No optional split selected in this pass; these need a separate review of missing populous regions rather than count-driven additions.
- **Taiwan, Afghanistan and all explicit exclusions** — Unchanged as requested, including Philippines and all previously approved territory merges.

Optional-country states were not audited to the same regional depth as the six core countries in this patch. This report does not claim that none could benefit from a future split.

## Population, buildings and references

Modeled subdivision shares: 40% of each old state total by province land area and 60% by existing mapped settlement population ranks; 100% area if no ranked settlements. Retains a rural floor and reconciles each old state independently. Not local census counts. Historical GHSL cache rejected because its registration is not reliable for current geography. Demographic refinement remains a separate task.

These population shares are explicit coarse estimates, not researched regional census counts. This patch does not implement the separate state-specific religion/education/age overhaul; new states inherit the existing complete national demographic profile. The next demographic pass should refine these shares. World population remains 6,144,737,528.

Each old state total is apportioned independently with largest-remainder rounding; regrouped states sum their contributions. Buildings and slots use the same retained-total allocation, with no cap that deletes inventory and no copying that duplicates it. Source-state IDs/cores/claims remain inherited metadata; regroupings union parent metadata, so those legacy claims remain coarse state-level annotations. No starting province owner changes.

Country capitals follow their existing capital province. Existing state capitals remain where possible; new states use an already mapped settlement, otherwise an explicitly marked province administrative anchor. City references, scenery state references/weights, urban accounting, protected-territory references, country lists and adjacency are refreshed.

## Sources and reproducibility

- Natural Earth ADM1: tools/cartography/geographic_subdivisions.geojson (public domain, already in the project).
- GADM 4.1 ADM2 local references for China, India, Pakistan and Syria: https://gadm.org/data.html . Download URLs/checksums in data/state_plan_0226.json. Source archives and polygon geometry are not included; https://gadm.org/license.html .
- Existing mapped settlement population ranks in data/cities.json and current province areas supply the disclosed allocation proxy.
- MD reference: data/md_geography_reference.json, previously verified against the supplied MD state-history archive in the .25 audit.
- Review: python tools/review_states_0226.py --references /path/to/local/gadm/archives (run against .25, archives named CHN_2.zip, IND_2.zip, PAK_2.zip and SYR_2.zip).
- Apply once to .25: python tools/apply_states_0226.py .
- Build: python tools/build_map.py --godot /path/to/Godot_4.5.1 . A fresh checkout needs the normal Godot editor/import step first so global script classes are registered.
- Validate: python tests/geography_0226_tests.py ; python tools/build_map.py --check ; python tools/restore_repository_assets.py --verify-only .

## Validation and your short test

Data validator: 65301 checks passed, including exact country totals, exclusions, identical province tiles, references and mainland connectivity.

Godot runtime: 330 checks passed, including new-state selection/highlight and live ownership lookup.

Native Windows graphics have not been tested here. In your fresh campaign, inspect one new state in each target country; hover it in the country state browser; check a new state capital and inline demographics; transfer a new state with the existing owner command; confirm its provinces and color update. Briefly check Taiwan/Afghanistan, Micronesia, Papua New Guinea and Antarctica. Map performance changes are outside this patch.
