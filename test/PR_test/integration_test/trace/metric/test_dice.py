# Copyright 2020 The FastEstimator Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import unittest

import numpy as np

from fastestimator.test.unittest_util import sample_system_object
from fastestimator.trace.metric import Dice
from fastestimator.util import Data


class TestDice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        x = np.array([[[[0, 1, 1], [1, 0, 1], [1, 0, 1]],
                       [[0, 0, 1], [1, 1, 1], [1, 0, 1]],
                       [[0, 1, 1], [1, 0, 1], [1, 0, 1]]]], dtype=np.float32)

        x_pred = np.array([[[[0, 1, 0], [1, 0, 0], [1, 0, 1]],
                            [[1, 0, 1], [1, 0, 1], [0, 1, 0]],
                            [[0, 0, 1], [1, 0, 1], [1, 0, 1]]]], dtype=np.float32)
        cls.data = Data({'x': x, 'x_pred': x_pred})
        cls.dice_output = [0.750]
        cls.dice = Dice(true_key='x', pred_key='x_pred')
        cls.dice.system = sample_system_object()

    def test_on_epoch_begin(self):
        self.dice.on_epoch_begin(data=self.data)
        self.assertEqual(self.dice.dice, [])

    def test_on_batch_end(self):
        self.dice.dice = []
        self.dice.on_batch_end(data=self.data)
        self.assertEqual(self.dice.dice, self.dice_output)

    def test_on_epoch_end(self):
        self.dice.dice = [0.750]
        self.dice.on_epoch_end(data=self.data)
        with self.subTest('Check if dice exists'):
            self.assertIn('Dice', self.data)
        with self.subTest('Check the value of dice'):
            self.assertEqual(self.data['Dice'], 0.750)
