import warnings

import torch
from torch.nn import functional as F

from onnx2pytorch.operations.base import Operator

empty_tensor = torch.Tensor([])


class Resize(Operator):
    def __init__(self, mode="nearest", align_corners=None, **kwargs):
        self.mode = mode
        self.align_corners = align_corners
        for key in kwargs.keys():
            warnings.warn(
                "Pytorch's interpolate uses no {}. " "Result might differ.".format(key)
            )
        super().__init__()

    def forward(self, inp, roi=empty_tensor, scales=empty_tensor, sizes=empty_tensor):
        if roi.nelement() > 0:
            warnings.warn("Pytorch's interpolate uses no roi. Result might differ.")

        scales = list(scales)
        sizes = list(sizes)
        shape = list(inp.shape)
        if shape[:2] == sizes[:2]:
            sizes = sizes[2:]  # Pytorch's interpolate takes only H and W params
        elif scales[:2] == [1, 1]:
            scales = scales[2:]
        elif len(scales) == 0 and len(sizes) == 0:
            raise ValueError("One of the two, scales or sizes, needs to be defined.")
        else:
            raise NotImplementedError(
                "Pytorch's interpolate does not scale batch and channel dimensions."
            )

        if len(scales) == 0:
            scales = None
            for i in range(len(sizes)):
                if isinstance(sizes[i], torch.Tensor):
                    sizes[i] = float(sizes[i])
        elif len(sizes) == 0:
            sizes = None
            for i in range(len(scales)):
                if isinstance(scales[i], torch.Tensor):
                    scales[i] = float(scales[i])
        else:
            raise ValueError(
                "Only one of the two, scales or sizes, needs to be defined."
            )
            
        # inside the scales, if each element is a one-element tensor, extract it to a float. 
        scales = tuple([tmp.item() if isinstance(tmp, torch.Tensor) else tmp for tmp in scales])
        return F.interpolate(
            inp,
            scale_factor=scales,
            size=sizes,
            mode=self.mode,
            align_corners=self.align_corners,
        )


class Upsample(Resize):
    """Deprecated onnx operator."""

    def forward(self, inp, scales):
        return super().forward(inp, torch.tensor([]), scales, torch.tensor([]))
