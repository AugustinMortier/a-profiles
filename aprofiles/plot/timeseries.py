#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Time Series plot

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import seaborn as sns
sns.set_theme()


def plot(da, var='aod', ymin=0, ymax=None, log=False, show_fog=False, show_pbl=False, show_clouds=False, cmap='coolwarm'):
    pass