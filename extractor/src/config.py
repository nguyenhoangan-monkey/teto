from typing import ClassVar


class JapanCustoms:
    _ENGLISH_BASE: ClassVar = "https://www.customs.go.jp/english/tariff/"
    _SCHEDULES: ClassVar = {
        "2026_08_08": "2026_08_08/data/print_e_{chap:02d}.htm",
        "2026_08_01": "2026_08_01/data/print_e_{chap:02d}.htm",
        "2026_07_09": "2026_07_09/data/print_e_{chap:02d}.htm",
        "2026_04_01": "2026_04_01/data/print_e_{chap:02d}.htm",
        "2026_01_01": "2026_01_01/data/print_e_{chap:02d}.htm",
        "2025_04_01": "2025_04_01/data/print_e_{chap:02d}.htm",
        "2025_01_01": "2025_01_01/data/print_e_{chap:02d}.htm",
        "2024_04_01": "2024_04_01/data/print_e_{chap:02d}.htm",
        "2024_02_01": "2024_02_01/data/print_e_{chap:02d}.htm",
        "2024_01_01": "2024_01_01/data/print_e_{chap:02d}.htm",
        "2023_04_01": "2023_04_01/data/print_e_{chap:02d}.htm",
        "2023_02_21": "2023_02_21/data/print_e_{chap:02d}.htm",
        "2023_01_01": "2023_01_01/data/print_e_{chap:02d}.htm",
        "2022_12_08": "2022_12_08/data/print_e_{chap:02d}.htm",
        "2022_12_01": "2022_12_01/data/print_e_{chap:02d}.htm",
        "2022_11_29": "2022_11_29/data/print_e_{chap:02d}.htm",
        "2022_04_01": "2022_04_01/data/print_e_{chap:02d}.htm",
        "2022_01_01": "2022_1_1/data/print_e_{chap:02d}.htm",
        "2021_10_22": "2021_10_22/data/print_e_{chap:02d}.htm",
        "2021_09_19": "2021_9/data/print_e_{chap:02d}.htm",
        "2021_04_01": "2021_4/data/print_e_{chap:02d}.htm",
        "2021_01_01": "2021_1/data/print_e_{chap:02d}.htm",
        "2020_10_01": "2020_10/data/print_e_{chap:02d}.htm",
        "2020_06_27": "2020_6/data/print_e_{chap:02d}.htm",
        "2020_04_01": "2020_4/data/print_e_{chap:02d}.htm",
        "2020_01_01": "2020_1/data/print_e_{chap:02d}.htm",
        "2019_04_01": "2019_4/data/print_e_{chap:02d}.htm",
        "2019_02_01": "2019_2/data/print_e_{chap:02d}.htm",
        "2019_01_14": "2019_1/data/print_e_{chap:02d}.htm",
        "2018_12_30": "2018_12/data/print_e_{chap:02d}.htm",
        "2018_04_01": "2018_4/data/print_e_{chap:02d}.htm",
        "2018_01_01": "2018_1/data/print_e_{chap:02d}.htm",
        "2017_05_16": "2017_5/data/print_e_{chap:02d}.htm",
        "2017_04_01": "2017_4/data/print_e_{chap:02d}.htm",
        "2017_01_01": "2017_1/data/print_e_{chap:02d}.htm",
        "2016_06_07": "2016_6/data/print_e_{chap:02d}.htm",
        "2016_04_01": "2016_4/data/print_e_{chap:02d}.htm",
        "2016_01_01": "2016_1/data/print_e_{chap:02d}.htm",
        "2015_04_01": "2015_4/data/print_e_{chap:02d}.htm",
        "2015_01_15": "2015_115/data/print_e_{chap:02d}.htm",
        "2015_01_01": "2015_1/data/print_e_{chap:02d}.htm",
        "2014_04_01": "2014_4/data/print_e_{chap:02d}.htm",
        "2014_01_01": "2014_1/data/print_i201401e_{chap:02d}.htm",
        "2013_04_01": "2013_4/data/print_i201304e_{chap:02d}.htm",
        "2013_01_01": "2013_1/data/print_i201301e_{chap:02d}.htm",
        "2012_04_01": "2012_4/data/print_i201204e_{chap:02d}.htm",
        "2012_03_01": "2012_3/data/print_i201203e_{chap:02d}.htm",
        "2012_01_01": "2012_1/data/print_i201201e_{chap:02d}.htm",
        "2011_08_01": "2011_8/data/print_i201108e_{chap:02d}.htm",
        "2011_04_01": "2011_4/data/print_i201104e_{chap:02d}.htm",
        "2011_01_01": "2011/data/print_i201101e_{chap:02d}.htm",
        "2010_04_01": "2010_4/data/print_i201004e_{chap:02d}.htm",
        "2010_01_01": "2010/data/print_i201001e_{chap:02d}.htm",
        "2009_06_01": "2009_6/data/print_200910e_{chap:02d}.htm",
        "2009_04_01": "2009_4/data/print_{chap:02d}.htm",
        "2009_01_01": "2009/data/print_{chap:02d}.htm",
        "2008_04_01": "2008_4/data/print_{chap:02d}.htm",
        "2008_01_01": "2008/data/print_{chap:02d}.htm",
        "2007_04_01": "2007_4/data/print_{chap:02d}.htm",
    }
    @classmethod
    def english_schedules(cls):
        for date, path in cls._SCHEDULES.items():
            yield date, cls._ENGLISH_BASE + path

    @classmethod
    def japanese_schedules(cls):
        # japanese version
        # https://www.customs.go.jp/tariff/2003/data/print_01.htm
        # https://www.customs.go.jp/tariff/2024_04_01/data/print_j_01.htm
        pass
