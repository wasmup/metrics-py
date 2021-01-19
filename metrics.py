#!/usr/bin/python3

import time
import sys
import struct
import subprocess


class Metrics:
    temp_file = '/dev/shm/my_usage_metrics_py.bin'
    mem_limit_MB = 512
    retry_sec = 30

    def __init__(self):
        self.freq = 0
        self.temp = 0
        self.mem = 0
        self.cpu = 0
        self.__idle = 0
        self.__idle_old = 0
        self.__total = 0
        self.__total_old = 0
        self.__notified = 0

    def run(self):
        self.temperature('/sys/class/thermal/thermal_zone2/temp')
        self.available_mem()
        self.frequency()
        self.read()
        self.cpu_ticks()
        self.cpu_usage_delta()
        if self.mem < Metrics.mem_limit_MB:
            now = int(time.time())
            sec = now - self.__notified
            if sec > Metrics.retry_sec:
                self.__notified = now
                subprocess.run([
                    'notify-send',
                    'metrics',
                    'Available memory is low: Close some programs to free up some RAM.',
                    '-a',
                    'metrics',
                    '-u',
                    'normal',
                    '-i',
                    'face-smile',
                ])
        self.write()

    def write(self):
        with open(Metrics.temp_file, 'wb') as f:
            f.write(struct.pack('3Q', self.__idle,
                                self.__total, self.__notified))

    def read(self):
        try:
            with open(Metrics.temp_file, 'rb') as f:
                record = struct.Struct('3Q')
                buf = f.read(record.size)
                (self.__idle_old, self.__total_old,
                 self.__notified) = record.unpack(buf)
        except FileNotFoundError:
            pass

    def cpu_usage_delta(self):
        i = self.__idle - self.__idle_old
        t = self.__total - self.__total_old
        self.cpu = 100 * (t - i) // t

    def cpu_ticks(self):
        with open('/proc/stat') as f:
            for s in f:
                st = s.split()
                if 'cpu' == st[0]:
                    self.__total = 0
                    for i in range(1, len(st)):
                        u = int(st[i])
                        self.__total += u
                        if i == 4:  # cpu user nice system idle iowait irq softirq guest guest_nice
                            self.__idle = u

    def frequency(self):
        """CPU frequency in MHz.
        """
        st = 'cpu MHz\t\t:'
        with open('/proc/cpuinfo', 'r') as f:
            for s in f:
                i = s.find(st)
                if i >= 0:
                    s = s[i + len(st):].strip()
                    i = s.find('.')
                    if i >= 0:
                        s = s[:i]
                    self.freq = int(s)

    def temperature(self, zone):
        """The zone temperature in the Celsius scale.
        """
        with open(zone) as f:
            s = f.read()
            self.temp = int(s.strip()) // 1000

    def available_mem(self):
        """available memory including cached memory in MB
        """
        with open('/proc/meminfo') as f:
            st = 'MemAvailable:'
            for s in f:
                i = s.find(st)
                if i >= 0:
                    s = s[i + len(st):].strip()
                    i = s.find('kB')
                    if i >= 0:
                        s = s[:i]
                    s = s.strip()
                    self.mem = int(s) // 1024

    def __str__(self):
        return str(self.mem)+'MB ' + str(self.cpu)+'% ' + str(self.temp)+'°C ' + str(self.freq)+'MHz'


def main(argv):
    for i in range(1, len(argv)):
        if argv[i] == '-lmt':
            Metrics.mem_limit_MB = int(argv[i+1])
        elif argv[i] == '-try':
            Metrics.retry_sec = int(argv[i+1])
        elif argv[i] == '-tmp':
            Metrics.temp_file = argv[i+1]

    app = Metrics()
    app.run()
    print(app)


if __name__ == '__main__':
    main(sys.argv)
