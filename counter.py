# Counters.py
# simple class to help keep some running counts/averages


class Counter:

    def __init__(self, name=None):
        self.name = name
        self.c_cnt = 0
        self.c_min = None
        self.c_ave = None
        self.c_max = None

    def add(self, item):
        if self.c_cnt == 0:
            self.c_min = item
            self.c_max = item
            self.c_ave = item
        else:
            if item < self.c_min:
                self.c_min = item
            if item > self.c_max:
                self.c_max = item
            self.c_ave = round(((self.c_ave * self.c_cnt) + item) / (self.c_cnt + 1), 2)
        self.c_cnt += 1
        return self.c_cnt

    def min(self):
        return self.c_min

    def ave(self):
        return self.c_ave

    def max(self):
        return self.c_max

    def count(self):
        return self.c_cnt

    def show(self):
        if self.c_cnt > 0:
            print("Counter:{}\t#:{}\tMin:{}\tAve:{}\t Max:{}".format(self.name, self.c_cnt, self.c_min,
                                                                     format(self.c_ave, ".2f"), self.c_max))
        else:
            print("Counter:{}\t#:{}\tMin:{}\tAve:{}\t Max:{}".format(self.name, self.c_cnt, 0, 0, 0))

    def reset(self):
        self.c_cnt = 0
        self.c_min = None
        self.c_ave = None
        self.c_max = None
