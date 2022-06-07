import collections
import io
import math
import os
import random

import numpy as np
import matplotlib.pyplot as plt

import tensorflow as tf
import tensorflow_datasets as tfds

dataset = tfds.image_classification.OxfordFlowers102()
