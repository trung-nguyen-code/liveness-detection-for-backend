import numpy as np  # linear algebra

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the
# files in the input directory
from sklearn import metrics
from torch.autograd import Variable
import torch
from torch import nn
import torch.optim as optim

from utils import EarlyStopping

import matplotlib.pyplot as plt
import random

# plotting rondom images from dataset
def class_plot(data, encoder, inv_normalize=None, n_figures=12):
    n_row = int(n_figures / 4)
    fig, axes = plt.subplots(figsize=(14, 10), nrows=n_row, ncols=4)
    for ax in axes.flatten():
        a = random.randint(0, len(data))
        (image, label) = data[a]
        print(type(image))
        label = int(label)
        l = encoder[label]
        if inv_normalize != None:
            image = inv_normalize(image)

        image = image.numpy().transpose(1, 2, 0)
        im = ax.imshow(image)
        ax.set_title(l)
        ax.axis("off")
    plt.show()


def error_plot(loss):
    plt.figure(figsize=(10, 5))
    plt.plot(loss)
    plt.title("Training loss plot")
    plt.xlabel("epochs")
    plt.ylabel("Loss")
    plt.show()


def acc_plot(acc):
    plt.figure(figsize=(10, 5))
    plt.plot(acc)
    plt.title("Training accuracy plot")
    plt.xlabel("epochs")
    plt.ylabel("accuracy")
    plt.show()


# To plot the wrong predictions given by model
def wrong_plot(n_figures, true, ima, pred, encoder, inv_normalize):
    print("Classes in order Actual and Predicted")
    n_row = int(n_figures / 3)
    fig, axes = plt.subplots(figsize=(14, 10), nrows=n_row, ncols=3)
    for ax in axes.flatten():
        a = random.randint(0, len(true) - 1)

        image, correct, wrong = ima[a], true[a], pred[a]
        image = torch.from_numpy(image)
        correct = int(correct)
        c = encoder[correct]
        wrong = int(wrong)
        w = encoder[wrong]
        f = "A:" + c + "," + "P:" + w
        if inv_normalize != None:
            image = inv_normalize(image)
        image = image.numpy().transpose(1, 2, 0)
        im = ax.imshow(image)
        ax.set_title(f)
        ax.axis("off")
    plt.show()


def plot_confusion_matrix(
    y_true, y_pred, classes, normalize=False, title=None, cmap=plt.cm.Blues
):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if not title:
        if normalize:
            title = "Normalized confusion matrix"
        else:
            title = "Confusion matrix, without normalization"

    # Compute confusion matrix
    cm = metrics.confusion_matrix(y_true, y_pred)
    # Only use the labels that appear in the data
    if normalize:
        cm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print("Confusion matrix, without normalization")

    print(cm)

    fig, ax = plt.subplots()
    im = ax.imshow(cm, interpolation="nearest", cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        # ... and label them with the respective list entries
        xticklabels=classes,
        yticklabels=classes,
        title=title,
        ylabel="True label",
        xlabel="Predicted label",
    )

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = ".2f" if normalize else "d"
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j,
                i,
                format(cm[i, j], fmt),
                ha="center",
                va="center",
                color="white" if cm[i, j] > thresh else "black",
            )
    fig.tight_layout()
    return ax


def performance_matrix(true, pred):
    precision = metrics.precision_score(true, pred, average="macro")
    recall = metrics.recall_score(true, pred, average="macro")
    accuracy = metrics.accuracy_score(true, pred)
    f1_score = metrics.f1_score(true, pred, average="macro")
    print(
        "Precision: {} Recall: {}, Accuracy: {}: ,f1_score: {}".format(
            precision * 100, recall * 100, accuracy * 100, f1_score * 100
        )
    )


class Trainer:
    def __init__(
        self,
        model,
        dataloaders,
        criterion,
        num_epochs,
        lr,
        batch_size,
        inv_normalize,
        encoder,
        train_writer,
        test_writer,
        patience=None,
    ):
        self.model = model
        self.dataloaders = dataloaders
        self.criterion = criterion
        self.num_epochs = num_epochs
        self.lr = lr
        self.batch_size = batch_size
        self.patience = patience
        self.inv_normalize = inv_normalize
        self.encoder = encoder
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.accuracy = list()
        self.losses = list()
        self.train_writer = train_writer
        self.test_writer = test_writer
    
    # flake8: noqa: C901
    def train(self, dataloaders):
        # since = time.time()
        self.model.to(self.device)
        # best_acc = 0.0
        # i = 0
        phase1 = dataloaders.keys()
        losses = list()
        acc = list()
        if self.patience:
            earlystop = EarlyStopping(patience=self.patience, verbose=True)
        for epoch in range(self.num_epochs):
            print("Epoch:", epoch)
            optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
            self.lr = self.lr * 0.8
            if epoch % 10 == 0:
                self.lr = 0.0001

            for phase in phase1:
                if phase == "train":
                    self.model.train()
                else:
                    self.model.eval()
                running_loss = 0.0
                running_corrects = 0
                # total = 0
                j = 0
                for batch_idx, (data, target) in enumerate(dataloaders[phase]):
                    data, target = Variable(data), Variable(target)
                    data = data.type(torch.cuda.FloatTensor)
                    target = target.type(torch.cuda.LongTensor)
                    optimizer.zero_grad()
                    output = self.model(data)
                    loss = self.criterion(output, target)
                    _, preds = torch.max(output, 1)
                    running_corrects = running_corrects + torch.sum(
                        preds == target.data
                    )
                    running_loss += loss.item() * data.size(0)
                    j = j + 1
                    if phase == "train":
                        loss.backward()
                        optimizer.step()

                    if batch_idx % 300 == 0:
                        print(
                            "{} Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f} \tAcc: {:.6f}"
                            .format(
                                phase,
                                epoch,
                                batch_idx * len(data),
                                len(dataloaders[phase].dataset),
                                100.0 * batch_idx / len(dataloaders[phase]),
                                running_loss / (j * self.batch_size),
                                running_corrects.double() / (j * self.batch_size),
                            )
                        )
                epoch_acc = running_corrects.double() / (
                    len(dataloaders[phase]) * self.batch_size
                )
                epoch_loss = running_loss / (len(dataloaders[phase]) * self.batch_size)
                self.train_writer.add_scalar("Loss", epoch_loss, epoch)
                self.train_writer.add_scalar("Accuracy", epoch_acc, epoch)

                if phase == "val":
                    earlystop(epoch_loss, self.model)

                if phase == "train":
                    losses.append(epoch_loss)
                    acc.append(epoch_acc)
                print(earlystop.early_stop)
            if earlystop.early_stop:
                print("Early stopping")
                self.model.load_state_dict(torch.load("./checkpoint.pt"))
                break
            print("{} Accuracy: ".format(phase), epoch_acc.item())
            if phase == "val":
                self.accuracy.append(epoch_acc.item())
                self.losses.append(epoch_loss)
        return losses, acc

    def test(self, dataloaders):
        running_corrects = 0
        running_loss = 0
        pred = []
        true = []
        pred_wrong = []
        true_wrong = []
        image = []
        sm = nn.Softmax(dim=1)
        for batch_idx, (data, target) in enumerate(dataloaders):
            data, target = Variable(data), Variable(target)
            data = data.type(torch.cuda.FloatTensor)
            target = target.type(torch.cuda.LongTensor)
            self.model.eval()
            output = self.model(data)
            loss = self.criterion(output, target)
            output = sm(output)
            _, preds = torch.max(output, 1)
            running_corrects = running_corrects + torch.sum(preds == target.data)
            running_loss += loss.item() * data.size(0)
            preds = preds.cpu().numpy()
            target = target.cpu().numpy()
            preds = np.reshape(preds, (len(preds), 1))
            target = np.reshape(target, (len(preds), 1))
            data = data.cpu().numpy()
            self.test_writer.add_scalar("Loss", running_loss, batch_idx)
            self.test_writer.add_scalar("Accuracy", running_corrects.double() / (
                    len(dataloaders)), batch_idx)

            for i in range(len(preds)):
                pred.append(preds[i])
                true.append(target[i])
                if preds[i] != target[i]:
                    pred_wrong.append(preds[i])
                    true_wrong.append(target[i])
                    image.append(data[i])

        epoch_acc = running_corrects.double() / (len(dataloaders) * self.batch_size)
        epoch_loss = running_loss / (len(dataloaders) * self.batch_size)
        print(epoch_acc, epoch_loss)
        
        return true, pred, image, true_wrong, pred_wrong

    def train_model(self):
        dataloader_train = {}
        losses = list()
        accuracy = list()
        key = self.dataloaders.keys()
        for phase in key:
            if phase == "test":
                perform_test = True
            else:
                dataloader_train.update([(phase, self.dataloaders[phase])])
        losses, accuracy = self.train(dataloader_train)
        print("Loss: {}, accuracy: {}".format(losses, accuracy))
        # error_plot(losses)
        # acc_plot(accuracy)
        if perform_test:
            # true, pred, image, true_wrong, pred_wrong = self.test(
            #     self.dataloaders["test"]
            # )
            self.test(
                self.dataloaders["test"]
            )

        return self.model
