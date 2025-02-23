from unittest import TestCase
from index import split_group, parse_split_setting_time, parse_split_setting_size


class TestParseSetting(TestCase):
    def test_parse_split_setting_time(self):
        self.assertEqual(parse_split_setting_time(None), None)
        self.assertEqual(parse_split_setting_time(""), None)
        self.assertRaisesRegex(ValueError, "时间范围错误", parse_split_setting_time, "0")
        self.assertRaisesRegex(ValueError, "时间范围错误", parse_split_setting_time, "25")
        self.assertRaisesRegex(ValueError, "时间范围错误", parse_split_setting_time, "0.24")
        self.assertRaisesRegex(ValueError, "1小时以上只允许填写整数", parse_split_setting_time, "1.25")
        self.assertRaisesRegex(ValueError, "could not convert string to float: 'abc'", parse_split_setting_time, "abc")
        self.assertEqual(parse_split_setting_time("0.25"), int(0.25 * 60 * 60))
        self.assertEqual(parse_split_setting_time("0.9"), int(0.9 * 60 * 60))
        self.assertEqual(parse_split_setting_time("1"), 60 * 60)
        self.assertEqual(parse_split_setting_time("24"), 24 * 60 * 60)

    def test_parse_split_setting_size(self):
        self.assertEqual(parse_split_setting_size(None), None)
        self.assertEqual(parse_split_setting_size(""), None)
        self.assertRaisesRegex(ValueError, "文件大小错误", parse_split_setting_size, "0")
        self.assertRaisesRegex(ValueError, "文件大小错误", parse_split_setting_size, "10001")
        self.assertEqual(parse_split_setting_size("1"), 1048576*1)
        self.assertEqual(parse_split_setting_size("10000"), 1048576*10000)


class TestParseSplit(TestCase):
    def test_split_group_time(self):
        flist = [
            ("1636297100.1.txt", 1),
            ("1636297200.1.txt", 1),
            ("1636297300.1.txt", 1),
        ]
        self.assertEqual(split_group(flist, 99, None), [
            [('1636297100.1.txt', 1, 1636297100, '1636297100.1')],
            [('1636297200.1.txt', 1, 1636297200, '1636297200.1')]
        ], "time_limit小于文件的时间区间， 且小于文件之间的时间间隔")
        self.assertEqual(split_group(flist, 100, None), [
            [
                ('1636297100.1.txt', 1, 1636297100, '1636297100.1'),
                ('1636297200.1.txt', 1, 1636297200, '1636297200.1')
            ]
        ], "time_limit小于文件的时间区间， 且等于文件之间的时间间隔")
        self.assertEqual(split_group(flist, 200, None), [
            [
                ('1636297100.1.txt', 1, 1636297100, '1636297100.1'),
                ('1636297200.1.txt', 1, 1636297200, '1636297200.1'),
                ('1636297300.1.txt', 1, 1636297300, '1636297300.1')
            ]
        ], "time_limit等于文件的时间区间")
        self.assertEqual(split_group(flist, 300, None), [], "time_limit大于文件的时间区间")

    def test_split_group_size(self):
        flist1 = [
            ("1636297100.1.txt", 1024),
            ("1636297200.1.txt", 1024),
            ("1636297300.1.txt", 1024),
        ]
        self.assertEqual(split_group(flist1, None, 1024), [
            [('1636297100.1.txt', 1024, 1636297100, '1636297100.1')],
            [('1636297200.1.txt', 1024, 1636297200, '1636297200.1')],
            [('1636297300.1.txt', 1024, 1636297300, '1636297300.1')]
        ], "3个文件均满足 size_limit, 拆为3个group")
        self.assertEqual(split_group(flist1, None, 2048), [
            [
                ('1636297100.1.txt', 1024, 1636297100, '1636297100.1'),
                ('1636297200.1.txt', 1024, 1636297200, '1636297200.1')
            ]
        ], "文件1+2满足 size_limit, 文件3不满足， 拆为1个group")
        flist2 = [
            ("1636297100.1.txt", 1024),
            ("1636297200.1.txt", 1024),
            ("1636297300.1.txt", 2048),
        ]
        self.assertEqual(split_group(flist2, None, 2048), [
            [
                ('1636297100.1.txt', 1024, 1636297100, '1636297100.1'),
                ('1636297200.1.txt', 1024, 1636297200, '1636297200.1')
            ],
            [
                ('1636297300.1.txt', 2048, 1636297300, '1636297300.1'),
            ],
        ], "文件1+2满足 size_limit, 文件3满足， 拆为2个group")
        self.assertEqual(split_group(flist2, None, 4096), [
            [
                ('1636297100.1.txt', 1024, 1636297100, '1636297100.1'),
                ('1636297200.1.txt', 1024, 1636297200, '1636297200.1'),
                ('1636297300.1.txt', 2048, 1636297300, '1636297300.1'),
            ],
        ], "文件1+2+3满足 size_limit, 拆为1个group")
        self.assertEqual(split_group(flist2, None, 4097), [], "文件1+2+3不满足 size_limit, 拆为0个group")

    def test_split_group_mix(self):
        self.assertRaisesRegex(ValueError, "时间和文件大小至少需要设置一个", split_group, [], None, None)
        self.assertRaisesRegex(ValueError, "时间和文件大小至少需要设置一个", split_group, [], "", "")
        flist = [
            ("1636297100.1.txt", 1024),
            ("1636297200.1.txt", 1024),
            ("1636297300.1.txt", 1024),
            ("1636297400.1.txt", 1024),
        ]
        self.assertEqual(split_group(flist, 100, 2048), [
            [
                ('1636297100.1.txt', 1024, 1636297100, '1636297100.1'),
                ('1636297200.1.txt', 1024, 1636297200, '1636297200.1')
            ],
            [
                ('1636297300.1.txt', 1024, 1636297300, '1636297300.1'),
                ('1636297400.1.txt', 1024, 1636297400, '1636297400.1')
            ]
        ], "time size同时满足")
        self.assertEqual(split_group(flist, 200, 4096), [
            [
                ('1636297100.1.txt', 1024, 1636297100, '1636297100.1'),
                ('1636297200.1.txt', 1024, 1636297200, '1636297200.1'),
                ('1636297300.1.txt', 1024, 1636297300, '1636297300.1')
            ]
        ], "时间满足")
        self.assertEqual(split_group(flist, 500, 2048), [
            [
                ('1636297100.1.txt', 1024, 1636297100, '1636297100.1'),
                ('1636297200.1.txt', 1024, 1636297200, '1636297200.1')
            ], [
                ('1636297300.1.txt', 1024, 1636297300, '1636297300.1'),
                ('1636297400.1.txt', 1024, 1636297400, '1636297400.1')
            ]
        ], "仅size满足1")
        self.assertEqual(split_group(flist, 500, 3000), [
            [
                ('1636297100.1.txt', 1024, 1636297100, '1636297100.1'),
                ('1636297200.1.txt', 1024, 1636297200, '1636297200.1')
            ]
        ], "仅size满足2")
        self.assertEqual(split_group(flist, 1000, 5000), [], "所有条件都不满足")



