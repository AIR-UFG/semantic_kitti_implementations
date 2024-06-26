# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/train.ipynb.

# %% auto 0
__all__ = ['DEVICE', 'PIN_MEMORY', 'Learner', 'Evaluator', 'Trainer']

# %% ../nbs/train.ipynb 1
from collections import defaultdict
from torchvision import transforms
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import torch.nn as nn
import torch

# %% ../nbs/train.ipynb 4
DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)
print(f"Using {DEVICE} device")
PIN_MEMORY = True if DEVICE == "cuda" else False

# %% ../nbs/train.ipynb 5
class Learner:
    def __init__(self, model, optimizer, lr, num_classes):
        self.model = model(num_classes).to(DEVICE)
        self.optimizer = optimizer(self.model.parameters(), lr=lr)

    def predict(self, x):
        return self.model(x)

    def update(self, loss):
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

# %% ../nbs/train.ipynb 8
class Evaluator:
    def __init__(self, loss_fn):
        self.loss_fn = loss_fn

    def get_loss(self, y, y_hat):
        bin_mask_train = (y !=0).int()
        loss = self.loss_fn(y_hat, y)
        loss = loss * bin_mask_train
        loss = loss.mean()
        return loss

# %% ../nbs/train.ipynb 11
class Trainer:
    def __init__(self, train_dataset, test_dataset, learner: Learner, evaluator: Evaluator, batch_size):
        self.train_dataset = train_dataset
        self.test_dataset = test_dataset
        self.learner = learner
        self.batch_size = batch_size
        self.evaluator = evaluator
        self.log = defaultdict()

    def train(self):
        self.learner.model.train()
        dataloader = DataLoader(self.train_dataset, batch_size=self.batch_size)
        epoch_loss = 0
        num_batches = len(dataloader)

        for batch_idx, (X,y) in enumerate(dataloader):
            (X,y) = (X.to(DEVICE), y.to(DEVICE))
            y_hat = self.learner.predict(X)
            loss = self.evaluator.get_loss(y,y_hat)
            epoch_loss += loss.item()
            self.learner.update(loss)

        # perguntar a divisão
        self.log['train_loss'] = epoch_loss / num_batches

    def test(self):
        self.learner.model.eval()
        dataloader = DataLoader(self.test_dataset, batch_size=self.batch_size)
        epoch_loss = 0
        num_batches = len(dataloader)

        with torch.no_grad():
            for X,y in dataloader:
                (X,y) = (X.to(DEVICE), y.to(DEVICE))
                y_hat = self.learner.predict(X)
                loss = self.evaluator.get_loss(y,y_hat)
                epoch_loss += loss.item()

        # perguntar a divisão
        self.log['test_loss'] = epoch_loss / num_batches

    def run(self, wandb, n_epochs: int):
        for t in range(n_epochs):
            self.train()
            self.test()
            wandb.log({"train_loss": self.log["train_loss"], "test_loss": self.log["test_loss"]})
            if (t+1) % 20 == 0:
                print(f"Epoch {t+1}\n------------")
                print(f"Train loss {self.log['train_loss']}\nTest loss {self.log['test_loss']}")
        print("Done!")
