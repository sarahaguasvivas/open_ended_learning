import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
import ipdb
import heapq
import copy
import numpy as np
from collections import OrderedDict

# import numpy as np
# from sklearn.model_selection import StratifiedShuffleSplit

MAX_TEST_CLASSES = 3
MAX_TRAIN_CLASSES = 2


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 20, 5, 1)
        self.conv2 = nn.Conv2d(20, 50, 5, 1)
        self.fc1 = nn.Linear(4 * 4 * 50, 500)
        self.fc2 = nn.Linear(500, MAX_TRAIN_CLASSES)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2, 2)
        x = x.view(-1, 4 * 4 * 50)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        softmax = F.log_softmax(x, dim=1)
        return softmax

    @staticmethod
    def getOutputRatios(output):
        output_top_two_ratios = []
        for _output in output:
            two_largest = heapq.nlargest(2, _output)
            output_top_two_ratios.append(two_largest[0] / two_largest[1])
        return np.array(output_top_two_ratios)

    def addCategory(self, output, output_ratios, threshold):
        model = self
        max_ratio_idx = np.argmax(output_ratios)
        most_uncertain_output = output[max_ratio_idx]
        output_probs = torch.exp(most_uncertain_output)
        first_layers = list(model.children())[:-1]
        last_layer = list(model.children())[-1]
        old_state_dict = last_layer.state_dict()
        old_weight = old_state_dict['weight']
        old_bias = old_state_dict['bias']
        new_bias_layer = torch.zeros(1)
        new_weight_layer = torch.zeros(1, old_weight.shape[1])
        for idx, prob in enumerate(output_probs):
            new_weight_layer += prob * old_weight[idx]
            new_bias_layer += prob * old_bias[idx]
        new_bias = torch.cat([old_bias, new_bias_layer], dim=0)
        new_weight = torch.cat([old_weight, new_weight_layer], dim=0)
        new_state_dict = OrderedDict({
            'weight': new_weight,
            'bias': new_bias
        })
        new_last_layer = nn.Linear(500, last_layer.out_features + 1)
        new_last_layer.load_state_dict(new_state_dict)
        model._modules['fc2'] = new_last_layer

    def addNewCategories(self, data, threshold):
        with torch.no_grad():
            model = self
            output = model(data)
            output_ratios = self.getOutputRatios(output)
            # ipdb.set_trace()
            while any(output_ratios > threshold):
                print(np.where(output_ratios > threshold))
                # TODO: adding a new category creates more above threshold output ratios,
                # leading to lots of new categories here. Need to avoid this somehow
                ipdb.set_trace()
                model.addCategory(output, output_ratios, threshold)
                output = model(data)
                output_ratios = self.getOutputRatios(output)
        return output


def train(args, model, device, train_loader, optimizer, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        # restrict data. TODO: do this in DataLoader
        data = data[target < MAX_TRAIN_CLASSES]
        target = target[target < MAX_TRAIN_CLASSES]

        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % args.log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))


def test(args, model, device, test_loader):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            # restrict data. TODO: do this in DataLoader
            data = data[target < MAX_TEST_CLASSES]
            target = target[target < MAX_TEST_CLASSES]

            data, target = data.to(device), target.to(device)

            output = model(data)
            threshold = 0.5
            output_ratios = model.getOutputRatios(output)

            if any(output_ratios > threshold):
                output = model.addNewCategories(data, threshold)

            test_loss += F.nll_loss(
                output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(
                dim=1,
                keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)

    print(
        '\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
            test_loss, correct, len(test_loader.dataset),
            100. * correct / len(test_loader.dataset)))


def main():
    # Training settings
    parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
    parser.add_argument(
        '--batch-size',
        type=int,
        default=64,
        metavar='N',
        help='input batch size for training (default: 64)')
    parser.add_argument(
        '--test-batch-size',
        type=int,
        default=1000,
        metavar='N',
        help='input batch size for testing (default: 1000)')
    parser.add_argument(
        '--epochs',
        type=int,
        default=10,
        metavar='N',
        help='number of epochs to train (default: 10)')
    parser.add_argument(
        '--lr',
        type=float,
        default=0.01,
        metavar='LR',
        help='learning rate (default: 0.01)')
    parser.add_argument(
        '--momentum',
        type=float,
        default=0.5,
        metavar='M',
        help='SGD momentum (default: 0.5)')
    parser.add_argument(
        '--no-cuda',
        action='store_true',
        default=False,
        help='disables CUDA training')
    parser.add_argument(
        '--seed',
        type=int,
        default=1,
        metavar='S',
        help='random seed (default: 1)')
    parser.add_argument(
        '--log-interval',
        type=int,
        default=10,
        metavar='N',
        help='how many batches to wait before logging training status')
    parser.add_argument(
        '--save-model',
        action='store_true',
        default=False,
        help='For Saving the current Model')
    args = parser.parse_args()
    use_cuda = not args.no_cuda and torch.cuda.is_available()

    torch.manual_seed(args.seed)

    device = torch.device("cuda" if use_cuda else "cpu")

    kwargs = {'num_workers': 1, 'pin_memory': True} if use_cuda else {}

    train_dataset = datasets.MNIST(
        '../data',
        train=True,
        download=True,
        transform=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307, ), (0.3081, ))
        ]))
    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=args.batch_size, shuffle=True, **kwargs)

    test_dataset = datasets.MNIST(
        '../data',
        train=False,
        transform=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307, ), (0.3081, ))
        ]))
    test_loader = torch.utils.data.DataLoader(
        test_dataset, batch_size=args.test_batch_size, shuffle=True, **kwargs)

    model = Net().to(device)
    optimizer = optim.SGD(
        model.parameters(), lr=args.lr, momentum=args.momentum)

    for epoch in range(1, args.epochs + 1):
        train(args, model, device, train_loader, optimizer, epoch)
        test(args, model, device, test_loader)

    if (args.save_model):
        torch.save(model.state_dict(), "mnist_cnn.pt")


if __name__ == '__main__':
    main()
