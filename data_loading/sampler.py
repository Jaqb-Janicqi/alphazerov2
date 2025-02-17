import torch
import numpy as np
from torch.utils.data import Sampler


class SliceSampler(Sampler):
    def __init__(self, data_source, slice_size, batch_size):
        self.data_source = data_source
        self.slice_size = slice_size
        self.batch_size = batch_size
        self.slices_per_batch = batch_size // slice_size
        self.num_samples = len(data_source) - len(data_source) % batch_size
        self.num_slices = self.num_samples // slice_size
        self.num_batches = self.num_samples // batch_size

    def __iter__(self):
        slice_indices = np.arange(self.num_slices).tolist()
        np.random.shuffle(slice_indices)

        for _ in range(self.num_batches):
            indices = []
            for _ in range(self.slices_per_batch):
                slice_idx = slice_indices.pop()
                slice_start = slice_idx * self.slice_size
                indices.extend(
                    range(slice_start, slice_start + self.slice_size))
            yield indices

    def __len__(self):
        return self.num_batches
