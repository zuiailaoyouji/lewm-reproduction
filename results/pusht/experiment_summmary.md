# Push-T 实验总结

本实验主要围绕两个问题展开：

1. **经过训练的 LeWM latent dynamics 是否真的能够为 CEM / MPC 规划提供有效信息？**
2. **随着 World Model 训练推进，其下游 planning ability 如何变化？**

---

## 1. 实验设置

任务为 **Push-T**，评估使用 LeWM 官方的 CEM / MPC planning pipeline。

主要规划配置如下：

| 配置项 | 数值 |
|---|---:|
| Random Seed | 42 |
| CEM Samples | 300 |
| CEM Optimization Steps | 30 |
| CEM Top-K | 30 |
| Planning Horizon | 5 |
| Receding Horizon | 5 |
| Action Block | 5 |
| Goal Offset Steps | 25 |
| Evaluation Budget | 50 |
| Max Episode Steps | 100 |
| Image Size | 224 × 224 |

模型使用 ViT-Tiny 作为视觉编码器：

| 配置项 | 数值 |
|---|---:|
| Hidden Dimension | 192 |
| Transformer Layers | 12 |
| Attention Heads | 3 |
| Patch Size | 14 |

为了减少不同初始条件带来的影响，同一组对比实验中的不同 policy / checkpoint 使用相同的 evaluation starting points。

---

# 实验一：Random Policy vs. LeWM + CEM/MPC

## 目的

首先验证 Push-T 评估任务是否能够通过随机动作轻易完成，并判断经过训练的 LeWM latent dynamics 是否真正为 goal-directed planning 提供了有效信息。

这里比较：

- **Random Policy**
- **Epoch-12 LeWM + CEM/MPC**

两者均在相同的 **20 个 evaluation starting points** 上测试。

## 结果

| Policy | Episodes | Successes | Success Rate |
|---|---:|---:|---:|
| Random Policy | 20 | 0 | 0% |
| Epoch-12 LeWM + CEM/MPC | 20 | 18 | 90% |

Random policy 在 20 个 episode 中全部失败，而 epoch-12 checkpoint 配合 CEM/MPC 成功完成了其中 18 个任务。

### 结果分析

这一结果至少说明：

> Push-T 当前这组 evaluation initial states 并不是随机动作就能轻易完成的。

在完全相同的 20 个初始条件下，random policy 的成功率为 0%，而使用 epoch-12 LeWM 进行 latent rollout，并通过 CEM 搜索候选动作序列后，成功率达到 90%。

因此，该结果支持这样一个结论：

> 即使训练只进行到第 12 个 epoch，LeWM 学习到的 action-conditioned latent dynamics 已经包含了足以支持有效 model-based planning 的信息。


---

## 可视化结果

仓库中的：

```text
env_0.mp4
```

来自 epoch-12 checkpoint 的 **20-episode Push-T evaluation**，作为 CEM/MPC closed-loop planning 的一个可视化示例。

[查看评估视频](./env_0.mp4)

---

# 实验二：Training Progress vs. Planning Ability

## 目的

第二个实验希望观察：

> 随着 LeWM 训练推进，latent dynamics 从什么时候开始具备用于下游 planning 的能力？

由于完整训练计划为 100 epochs，但当前训练仅保存到 epoch 12，因此选取四个不同训练阶段的 checkpoint：

```text
Epoch 1
Epoch 3
Epoch 6
Epoch 12
```

所有 checkpoint 均使用：

- 相同 Push-T evaluation 配置；
- 相同 CEM / MPC 参数；
- 相同 random seed；
- 相同的 10 个 evaluation starting points。

因此可以直接观察模型训练进度与 planning success rate 之间的关系。

## 结果

| Checkpoint | Successes | Success Rate |
|---|---:|---:|
| Epoch 1 | 2 / 10 | 20% |
| Epoch 3 | 8 / 10 | 80% |
| Epoch 6 | 9 / 10 | 90% |
| Epoch 12 | 10 / 10 | 100% |

## 结果分析

这个小规模实验出现了一个比较明显的现象：

> LeWM 的下游 planning ability 在训练早期快速形成。

epoch 1 时只有 2/10 的任务能够成功完成，说明此时模型虽然已经开始学习 representation 和 action-conditioned dynamics，但其预测还不足以稳定支撑 CEM planning。

到 epoch 3 时，成功率从 20% 快速提升到 80%，表明模型在很早的训练阶段就开始学习到对 planning 有用的动力学信息。

随后：

```text
Epoch 3 → Epoch 6
80% → 90%

Epoch 6 → Epoch 12
90% → 100%
```

性能继续提高，但增幅逐渐减小。

---

# 两个实验合起来说明了什么？

两个实验分别回答了不同问题。

### Experiment 1：模型有没有真正提供有用信息？

```text
Random:
0 / 20

Epoch-12 LeWM + CEM/MPC:
18 / 20
```

说明经过训练的 latent dynamics 能够为 goal-directed planning 提供明显比随机动作更有效的信息。

### Experiment 2：这种能力什么时候形成？

```text
Epoch 1   → 20%
Epoch 3   → 80%
Epoch 6   → 90%
Epoch 12  → 100%
```

说明 planning ability 在训练早期快速出现，并随着训练继续推进而进一步提高。

两个实验共同支持：

> LeWM 学到的 latent representation 不仅能够完成 future embedding prediction，而且其 action-conditioned dynamics 可以实际用于下游 CEM/MPC planning。

---

# 局限性

主要局限包括：

1. **训练尚未完成**

   官方训练计划为 100 epochs，而当前 checkpoint 最多只训练到 epoch 12。

2. **Evaluation episode 数量较少**

   Training Progress 实验每个 checkpoint 只有 10 个 episode。

3. **仅使用单一 evaluation seed**

   当前实验主要用于控制 initial states 并比较不同 checkpoint，而不是估计跨 seed 的统计性能。

4. **尚未与 official pretrained checkpoint 对比**