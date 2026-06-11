"""Deep trace of mixed-precision training on XOR."""

from trinary.ai2.trit_module import TritLinearMixed, TritSequential
from trinary.ai2.trit_loss import TritCrossEntropyLoss, _argmax
from trinary.ai2.trit_graph import TritTape
from trinary.ai2.trit_trainer import TritTrainerMixed

dataset = [([0, 0], 0), ([0, 2], 1), ([2, 0], 1), ([2, 2], 0)]

model = TritSequential(
    TritLinearMixed(2, 4, bias=True, seed=42, lr=0.1),
    TritLinearMixed(4, 2, bias=True, seed=99, lr=0.1),
)
criterion = TritCrossEntropyLoss()
trainer = TritTrainerMixed(model, criterion)

for epoch in range(50):
    acc_grads = {}
    total_loss = 0
    for x, target in dataset:
        loss, grads = trainer._compute_grads(x, target)
        total_loss += loss
        for path, g in grads.items():
            if path not in acc_grads:
                acc_grads[path] = [0] * len(g)
            for i in range(len(g)):
                acc_grads[path][i] += (-1 if g[i] == 0 else (0 if g[i] == 1 else 1))
    
    for path, acc in acc_grads.items():
        parts = path.split('.')
        mod = trainer._resolve_module(parts[:-1])
        if mod and hasattr(mod, '_apply_ste_raw'):
            mod._apply_ste_raw(acc, parts[-1], mod.lr)
    
    correct = sum(1 for x, t in dataset if _argmax(model(x)) == t)
    
    if (epoch + 1) % 10 == 0:
        fw0 = [f'{v:.2f}' for v in model._modules['0']._float_weight]
        fw1 = [f'{v:.2f}' for v in model._modules['1']._float_weight]
        fb0 = [f'{v:.2f}' for v in (model._modules['0']._float_bias or [])]
        fb1 = [f'{v:.2f}' for v in (model._modules['1']._float_bias or [])]
        trit0 = model._modules['0']._params['weight']
        trit1 = model._modules['1']._params['weight']
        print(f'Epoch {epoch+1}: acc={correct}/4')
        print(f'  pushes: {dict((p, a) for p, a in acc_grads.items())}')
        print(f'  float0: {fw0}')
        print(f'  float1: {fw1}')
        print(f'  bias0: {fb0}  bias1: {fb1}')
        print(f'  trit0: {trit0}')
        print(f'  trit1: {trit1}')
