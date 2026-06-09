import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
import time

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)

SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Device: {DEVICE}")

DATA_PATH = r"/Lab/hw/3/data.csv"

df = pd.read_csv(DATA_PATH)
df['diagnosis'] = df['diagnosis'].map({'M': 1, 'B': 0})

feature_cols = [c for c in df.columns if c not in ('id', 'diagnosis') and not c.startswith('Unnamed')]
X = df[feature_cols].values.astype(np.float32)
y = df['diagnosis'].values.astype(np.float32)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


class BreastCancerDataset(Dataset):
    def __init__(self, features, targets):
        self.features = torch.tensor(features, dtype=torch.float32)
        self.targets = torch.tensor(targets, dtype=torch.float32).view(-1, 1)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx], self.targets[idx]


train_dataset = BreastCancerDataset(X_train, y_train)
test_dataset = BreastCancerDataset(X_test, y_test)

BATCH_SIZE = 32
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)


class BreastCancerNN(nn.Module):
    def __init__(self, input_dim=30, hidden_dims=(64, 32, 16), dropout_rates=(0.3, 0.2, 0.1)):
        super().__init__()
        self.layers = nn.ModuleList()
        self.dropouts = nn.ModuleList()
        prev_dim = input_dim
        for hidden_dim, drop_rate in zip(hidden_dims, dropout_rates):
            self.layers.append(nn.Linear(prev_dim, hidden_dim))
            self.dropouts.append(nn.Dropout(drop_rate))
            prev_dim = hidden_dim
        self.output_layer = nn.Linear(prev_dim, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        for layer, dropout in zip(self.layers, self.dropouts):
            x = dropout(torch.relu(layer(x)))
        x = self.sigmoid(self.output_layer(x))
        return x


model_config = {
    'input_dim': 30,
    'hidden_dims': (64, 32, 16),
    'dropout_rates': (0.3, 0.2, 0.1),
}


class CustomAdagrad(optim.Optimizer):
    def __init__(self, params, lr=1e-2, lr_decay=0, eps=1e-10, weight_decay=0):
        if lr < 0.0:
            raise ValueError(f"Invalid learning rate: {lr}")
        if weight_decay < 0.0:
            raise ValueError(f"Invalid weight_decay: {weight_decay}")
        defaults = dict(lr=lr, lr_decay=lr_decay, eps=eps, weight_decay=weight_decay)
        super().__init__(params, defaults)
        self._step_count = 0

    def step(self, closure=None):
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()
        self._step_count += 1
        for group in self.param_groups:
            lr = group['lr']
            lr_decay = group['lr_decay']
            eps = group['eps']
            weight_decay = group['weight_decay']
            clr = lr / (1 + (self._step_count - 1) * lr_decay)
            for p in group['params']:
                if p.grad is None:
                    continue
                grad = p.grad.data
                if grad.is_sparse:
                    raise RuntimeError('CustomAdagrad does not support sparse gradients')
                state = self.state[p]
                if len(state) == 0:
                    state['sum'] = torch.zeros_like(p.data)
                r = state['sum']
                if weight_decay != 0:
                    grad = grad.add(p.data, alpha=weight_decay)
                r.addcmul_(grad, grad, value=1)
                std = r.sqrt().add_(eps)
                p.data.addcdiv_(grad, std, value=-clr)
        return loss


def train_epoch(model, loader, optimizer, criterion):
    model.train()
    total_loss = 0.0
    all_preds, all_targets = [], []
    for features, targets in loader:
        features, targets = features.to(DEVICE), targets.to(DEVICE)
        optimizer.zero_grad()
        outputs = model(features)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * features.size(0)
        all_preds.extend((outputs.detach().cpu().numpy() > 0.5).astype(int).flatten())
        all_targets.extend(targets.cpu().numpy().flatten().astype(int))
    avg_loss = total_loss / len(loader.dataset)
    acc = accuracy_score(all_targets, all_preds)
    return avg_loss, acc


@torch.no_grad()
def evaluate(model, loader, criterion):
    model.eval()
    total_loss = 0.0
    all_preds, all_probs, all_targets = [], [], []
    for features, targets in loader:
        features, targets = features.to(DEVICE), targets.to(DEVICE)
        outputs = model(features)
        loss = criterion(outputs, targets)
        total_loss += loss.item() * features.size(0)
        all_probs.extend(outputs.cpu().numpy().flatten())
        all_preds.extend((outputs.cpu().numpy() > 0.5).astype(int).flatten())
        all_targets.extend(targets.cpu().numpy().flatten().astype(int))
    avg_loss = total_loss / len(loader.dataset)
    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)
    all_probs = np.array(all_probs)
    return {
        'loss': avg_loss,
        'accuracy': accuracy_score(all_targets, all_preds),
        'precision': precision_score(all_targets, all_preds, zero_division=0),
        'recall': recall_score(all_targets, all_preds, zero_division=0),
        'f1': f1_score(all_targets, all_preds, zero_division=0),
        'roc_auc': roc_auc_score(all_targets, all_probs),
        'preds': all_preds,
        'targets': all_targets,
    }


def train_model(model, train_loader, test_loader, optimizer, criterion, epochs=100,
                early_stop_patience=15, verbose=True):
    history = defaultdict(list)
    best_test_acc = 0.0
    best_epoch = 0
    patience_counter = 0
    best_state = None
    for epoch in range(1, epochs + 1):
        train_loss, train_acc = train_epoch(model, train_loader, optimizer, criterion)
        train_eval = evaluate(model, train_loader, criterion)
        test_eval = evaluate(model, test_loader, criterion)
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['test_loss'].append(test_eval['loss'])
        history['test_acc'].append(test_eval['accuracy'])
        if test_eval['accuracy'] > best_test_acc:
            best_test_acc = test_eval['accuracy']
            best_epoch = epoch
            patience_counter = 0
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            patience_counter += 1
        if verbose and epoch % 20 == 0:
            print(f"  Epoch {epoch:3d}/{epochs} | "
                  f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
                  f"Test Loss: {test_eval['loss']:.4f} Acc: {test_eval['accuracy']:.4f}")
        if patience_counter >= early_stop_patience:
            if verbose:
                print(f"  Early stopping at epoch {epoch} (best: {best_epoch})")
            break
    if best_state is not None:
        model.load_state_dict(best_state)
    history['best_epoch'] = best_epoch
    return history


EPOCHS = 200
LR = 1e-2
LR_DECAY = 0
EPS = 1e-10
WEIGHT_DECAY = 0

criterion = nn.BCELoss()

print("\n--- Training with torch.optim.Adagrad ---")
model_std = BreastCancerNN(**model_config).to(DEVICE)
optimizer_std = optim.Adagrad(model_std.parameters(), lr=LR, lr_decay=LR_DECAY,
                              eps=EPS, weight_decay=WEIGHT_DECAY)
start_time = time.time()
history_std = train_model(model_std, train_loader, test_loader, optimizer_std, criterion,
                          epochs=EPOCHS, early_stop_patience=15, verbose=True)
train_time_std = time.time() - start_time

print("\n--- Training with CustomAdagrad ---")
model_custom = BreastCancerNN(**model_config).to(DEVICE)
optimizer_custom = CustomAdagrad(model_custom.parameters(), lr=LR, lr_decay=LR_DECAY,
                                 eps=EPS, weight_decay=WEIGHT_DECAY)
start_time = time.time()
history_custom = train_model(model_custom, train_loader, test_loader, optimizer_custom, criterion,
                             epochs=EPOCHS, early_stop_patience=15, verbose=True)
train_time_custom = time.time() - start_time

test_eval_std = evaluate(model_std, test_loader, criterion)
test_eval_custom = evaluate(model_custom, test_loader, criterion)

metrics = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
print(f"\n{'Metric':<20} {'torch.Adagrad':>15} {'CustomAdagrad':>15}")
print("-" * 52)
for m in metrics:
    print(f"{m:<20} {test_eval_std[m]:>15.4f} {test_eval_custom[m]:>15.4f}")

print(f"\n{'Train time (s)':<20} {train_time_std:>15.2f} {train_time_custom:>15.2f}")
print(f"{'Best epoch':<20} {history_std['best_epoch']:>15} {history_custom['best_epoch']:>15}")

print("\n--- Confusion Matrix (torch.Adagrad) ---")
print(confusion_matrix(test_eval_std['targets'], test_eval_std['preds']))
print("\nClassification Report (torch.Adagrad):")
print(classification_report(test_eval_std['targets'], test_eval_std['preds'],
                            target_names=['Benign (B)', 'Malignant (M)']))

print("\n--- Confusion Matrix (CustomAdagrad) ---")
print(confusion_matrix(test_eval_custom['targets'], test_eval_custom['preds']))
print("\nClassification Report (CustomAdagrad):")
print(classification_report(test_eval_custom['targets'], test_eval_custom['preds'],
                            target_names=['Benign (B)', 'Malignant (M)']))

print(f"\nissubclass(CustomAdagrad, optim.Optimizer) = {issubclass(CustomAdagrad, optim.Optimizer)}")
print(f"hasattr(optimizer_custom, 'zero_grad') = {hasattr(optimizer_custom, 'zero_grad')}")
print(f"hasattr(optimizer_custom, 'step') = {hasattr(optimizer_custom, 'step')}")

fig, axes = plt.subplots(2, 2, figsize=(14, 8))
fig.subplots_adjust(left=0.05, right=0.99, top=0.96, bottom=0.04, wspace=0.16, hspace=0.22)

ax1 = axes[0, 0]
ax1.plot(history_std['train_loss'], label='torch.Adagrad (train)', linewidth=2)
ax1.plot(history_std['test_loss'], '--', label='torch.Adagrad (test)', linewidth=2)
ax1.plot(history_custom['train_loss'], label='CustomAdagrad (train)', linewidth=2)
ax1.plot(history_custom['test_loss'], '--', label='CustomAdagrad (test)', linewidth=2)
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Loss')
ax1.set_title('Loss (BCE)')
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

ax2 = axes[0, 1]
ax2.plot(history_std['train_acc'], label='torch.Adagrad (train)', linewidth=2)
ax2.plot(history_std['test_acc'], '--', label='torch.Adagrad (test)', linewidth=2)
ax2.plot(history_custom['train_acc'], label='CustomAdagrad (train)', linewidth=2)
ax2.plot(history_custom['test_acc'], '--', label='CustomAdagrad (test)', linewidth=2)
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Accuracy')
ax2.set_title('Accuracy')
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)

ax3 = axes[1, 0]
x_pos = np.arange(len(metrics))
width = 0.35
std_vals = [test_eval_std[m] for m in metrics]
custom_vals = [test_eval_custom[m] for m in metrics]
ax3.bar(x_pos - width/2, std_vals, width, label='torch.Adagrad', color='#2196F3')
ax3.bar(x_pos + width/2, custom_vals, width, label='CustomAdagrad', color='#FF9800')
ax3.set_ylabel('Score')
ax3.set_title('Metrics Comparison')
ax3.set_xticks(x_pos)
ax3.set_xticklabels(metrics, fontsize=8)
ax3.set_ylim(0.85, 1.0)
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3, axis='y')

ax4 = axes[1, 1]
diff_vals = [custom_vals[i] - std_vals[i] for i in range(len(metrics))]
bar_colors = ['#4CAF50' if d >= 0 else '#F44336' for d in diff_vals]
bars = ax4.bar(metrics, diff_vals, color=bar_colors)
ax4.set_ylabel('Difference (Custom - torch)')
ax4.set_title('Metrics Difference')
ax4.axhline(y=0, color='black', linewidth=0.5)
ax4.grid(True, alpha=0.3, axis='y')
for bar, val in zip(bars, diff_vals):
    ax4.text(bar.get_x() + bar.get_width()/2.,
             bar.get_height() + 0.002 * (1 if val >= 0 else -1),
             f'{val:+.4f}', ha='center', va='bottom' if val >= 0 else 'top',
             fontsize=8)
ax4.set_xticks(x_pos)
ax4.set_xticklabels(metrics, fontsize=8)

plot_path = r"C:\develop\NOTE_UTP\StudyNote\4 Методы оптимизации\Lab\7\results_comparison.png"
fig.savefig(plot_path, dpi=150, facecolor='white', edgecolor='none')
plt.close(fig)
print(f"\nPlot saved to results_comparison.png")
print("Done.")
