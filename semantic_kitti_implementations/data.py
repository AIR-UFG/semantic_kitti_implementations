# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/data.ipynb.

# %% auto 0
__all__ = ['SemanticDataset', 'remap_segmentation_masks']

# %% ../nbs/data.ipynb 1
import torch, os
import numpy as np
from torch.utils.data import Dataset
from PIL import Image

# %% ../nbs/data.ipynb 2
class SemanticDataset(Dataset):
    def __init__(self, image_path, mask_path, transform=None):
        self.image_path = image_path
        self.mask_path = mask_path
        self.transform = transform
        self.image_filenames = os.listdir(image_path)
        self.mask_filenames = os.listdir(mask_path)

    def __len__(self):
        return len(self.image_filenames)

    def __getitem__(self, idx):
        img_name = os.path.join(self.image_path, self.image_filenames[idx])
        mask_name = os.path.join(self.mask_path, self.mask_filenames[idx])

        image = np.array(Image.open(img_name))
        mask = np.array(Image.open(mask_name))

        if self.transform:
            image = self.transform(image)
            mask = torch.from_numpy(mask.astype(np.int64))

        return image, mask

# %% ../nbs/data.ipynb 3
def remap_segmentation_masks(origin_path, output_dir, remapping_rules):
    for filename in os.listdir(origin_path):
      if filename.endswith(".png"):
          image_path = os.path.join(origin_path, filename)
          img = Image.open(image_path)
    
          img_array = np.array(img)
    
          remapped_array = np.zeros_like(img_array)
          for old_value, new_value in remapping_rules.items():
              remapped_array[img_array == old_value] = new_value
    
          remapped_img = Image.fromarray(remapped_array)
    
          output_path = os.path.join(output_dir, filename)
          remapped_img.save(output_path)
