# -*- coding: utf-8 -*-
"""


@author: Giuseppe Armenise
"""
import operator

Dict_unit = {
#        Time units
        "s": 1.0,
        "ms": 1000.0,
        "ns": 10.**9,
        "min": 1./60.,
        "h": 1./3600.,
        "d": 1./(86400.0),
        "y": 1./31536000.0,
        }

class Dim_Value:
    def __init__(self,val,unit):
        self.val=val
        self.num_unit=unit

    def unit_to_basic(self, num_unit1):
        def calc_conv(conversion,unit):
            conversion *= (Dict_unit[unit])
            return conversion
        
        conversion0=calc_conv(1.0, self.num_unit)
        conversion1=calc_conv(1.0, num_unit1)
        
        return conversion1/conversion0
            
    def converter(self,num_actual_unit):
        rate_conv=self.unit_to_basic(num_actual_unit)
        self.val *= rate_conv
        self.num_unit = num_actual_unit


