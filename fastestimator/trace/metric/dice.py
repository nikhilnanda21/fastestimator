# Copyright 2019 The FastEstimator Authors. All Rights Reserved.
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
from typing import Iterable, Union

import numpy as np

from fastestimator.backend._dice_score import dice_score
from fastestimator.trace.meta._per_ds import per_ds
from fastestimator.trace.trace import Trace
from fastestimator.util import Data
from fastestimator.util.traceability_util import traceable
from fastestimator.util.util import to_number


@per_ds
@traceable()
class Dice(Trace):
    """Dice score for binary classification between y_true and y_predicted.

    Args:
        true_key: The key of the ground truth mask.
        pred_key: The key of the prediction values.
        threshold: The threshold for binarizing the prediction.
        channel_average: Whether the average channel-wise dice loss.
        mode: What mode(s) to execute this Trace in. For example, "train", "eval", "test", or "infer". To execute
            regardless of mode, pass None. To execute in all modes except for a particular one, you can pass an argument
            like "!infer" or "!train".
        ds_id: What dataset id(s) to execute this Trace in. To execute regardless of ds_id, pass None. To execute in all
            ds_ids except for a particular one, you can pass an argument like "!ds1".
        output_name: What to call the output from this trace (for example in the logger output).
        per_ds: Whether to automatically compute this metric individually for every ds_id it runs on, in addition to
            computing an aggregate across all ds_ids on which it runs. This is automatically False if `output_name`
            contains a "|" character.
    """

    def __init__(self,
                 true_key: str,
                 pred_key: str,
                 threshold: float = 0.5,
                 channel_average: bool = False,
                 mode: Union[None, str, Iterable[str]] = ("eval", "test"),
                 ds_id: Union[None, str, Iterable[str]] = None,
                 output_name: str = "Dice",
                 per_ds: bool = True) -> None:
        super().__init__(inputs=(true_key, pred_key),
                         mode=mode, outputs=output_name, ds_id=ds_id)
        self.threshold = threshold
        self.smooth = 1e-8
        self.channel_average = channel_average
        self.dice = []
        self.per_ds = per_ds

    @property
    def true_key(self) -> str:
        return self.inputs[0]

    @property
    def pred_key(self) -> str:
        return self.inputs[1]

    def on_epoch_begin(self, data: Data) -> None:
        self.dice = []

    def on_batch_end(self, data: Data) -> None:
        y_true, y_pred = to_number(
            data[self.true_key]), to_number(data[self.pred_key])

        y_pred = np.where(y_pred > self.threshold, 1.0,
                          0.0).astype(y_pred.dtype)

        dice = dice_score(y_pred=y_pred, y_true=y_true,
                          channel_average=self.channel_average, epsilon=self.smooth)

        data.write_per_instance_log(self.outputs[0], dice)
        self.dice.extend(list(dice))

    def on_epoch_end(self, data: Data) -> None:
        data.write_with_log(self.outputs[0], np.mean(self.dice))
