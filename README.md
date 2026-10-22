# LeWM 复现与分析

本仓库记录对 **LeWorldModel（LeWM）** 的复现、实验与分析，重点关注基于 JEPA 的动作条件潜在动力学建模，以及利用 CEM / MPC 进行机器人任务规划。

本仓库基于 LeWM 官方实现：

https://github.com/lucas-maes/le-wm

原始模型设计与代码版权归 LeWM 作者所有。本仓库中我的工作主要包括训练与评估流程复现、模型结构分析、规划流程分析，以及额外的小规模实验。

## 我完成的工作

- 复现了 LeWM 在 Push-T 任务上的训练流程；
- 使用单张 NVIDIA A100 40GB 从头训练 Push-T LeWM 模型至第 12 个 epoch；
- 成功加载自己训练得到的 checkpoint，并使用原始 CEM / MPC 流程进行规划评估；
- 完成 Random Policy 与 LeWM + CEM/MPC 的对照实验；
- 对 epoch 1 / 3 / 6 / 12 checkpoint 进行了 Training Progress vs. Planning Ability 对比；
- 阅读并分析了 LeWM 的视觉编码器、动作条件预测器、SIGReg、latent rollout 与 CEM / MPC 规划流程；
- 运行并学习了 LeWM 在 Two-Room 导航和 OGBench Cube manipulation 上的预训练模型推理与规划流程；
- 探索将 JEPA-based World Model 应用于真实草莓采摘机器人的可行性。

## 仓库结构

```text
.
├── config/
├── results/
│   └── pusht/
│       ├── experiment_summary.md
│       ├── *_eval_*.txt
│       └── env_0.mp4
├── scripts/
├── train.py
├── eval.py
├── jepa.py
├── module.py
├── README.md
└── README_UPSTREAM.md
```

数据集和模型 checkpoint 体积较大，因此不会上传到本仓库。

## Push-T 复现

### 训练配置

| 项目 | 配置 |
|---|---|
| 视觉编码器 | ViT-Tiny |
| 输入图像尺寸 | 224 × 224 |
| Hidden Dimension | 192 |
| Transformer 层数 | 12 |
| Attention Heads | 3 |
| Patch Size | 14 |
| History Size | 3 |
| Action Dimension | 2 |
| Frameskip | 5 |
| 计划训练轮数 | 100 epochs |
| 实际完成训练 | 12 epochs |
| GPU | NVIDIA A100 40GB |

原计划按照官方设置训练 100 epochs，但该次训练任务在第 12 个 epoch 后因远程任务中断而停止。

因此，本仓库只是将保存下来的 early-stage checkpoint 用于分析：

> 在训练早期，LeWM 学到的 latent dynamics 是否已经足以支持基于 CEM / MPC 的规划。

## Epoch-12 Push-T 评估

使用自己训练得到的 epoch-12 checkpoint，通过 LeWM 官方的 CEM / MPC evaluation pipeline 进行测试。

目前完成的 Push-T 小规模实验主要包括：

1. **Random Policy vs. LeWM + CEM/MPC**：验证 learned latent dynamics 是否能够为 goal-directed planning 提供有效信息；
2. **Training Progress vs. Planning Ability**：比较 epoch 1 / 3 / 6 / 12 checkpoint 的下游规划能力变化。

具体实验设置、评估结果、结果分析、可视化示例、局限性与后续实验方向统一记录在：

**[查看完整 Push-T 实验总结 →](./results/pusht/experiment_summary.md)**

原始 evaluation logs 与评估视频也保存在 [`results/pusht/`](./results/pusht/) 目录中。

## LeWM 模型理解

LeWM 的整体流程可以概括为：

```text
视觉观测
   ↓
Encoder
   ↓
Latent Representation
   ↓
Action-Conditioned Predictor
   ↓
未来 Latent State
   ↓
规划目标计算
   ↓
CEM
   ↓
MPC
   ↓
执行动作
```

与直接预测未来像素不同，LeWM 主要在 latent space 中预测未来表示。

训练过程中主要包含两部分目标：

1. **未来 latent prediction loss**
2. **SIGReg regularization**

其中，SIGReg 用于约束 latent representation 的统计分布，降低 representation collapse 的风险。

## CEM / MPC 规划流程

LeWM 本身负责：

> 给定当前视觉观测和动作序列，预测未来 latent trajectory。

模型并不会直接输出最优动作。

规划器使用 CEM 对候选动作序列进行搜索：

```text
采样多组候选动作序列
        ↓
LeWM rollout
        ↓
预测未来 latent trajectory
        ↓
计算 planning cost
        ↓
选择 elite action sequences
        ↓
更新动作分布
        ↓
重复优化
```

得到较优动作序列之后，MPC 采用 receding-horizon 的方式执行动作：

```text
规划
 ↓
执行部分动作
 ↓
重新获取视觉观测
 ↓
重新规划
```

因此可以将二者理解为：

- **LeWM：负责预测**
- **CEM：负责搜索**
- **MPC：负责闭环执行与重规划**

## SIGReg

LeWM 中使用 SIGReg 对 latent representation 进行正则化。

其基本思想是：

1. 将高维 latent 随机投影到大量一维方向；
2. 计算这些一维投影的经验特征函数；
3. 将其与标准高斯分布的特征函数进行比较；
4. 对多个投影方向与多个采样点上的误差进行统计。

通过这种方式，使 latent distribution 接近各向同性高斯分布。

如果 representation 完全 collapse 到某个常数，其一维投影显然无法满足标准高斯分布，因此 SIGReg 可以对 collapse 产生较强惩罚。

## Acknowledgement

本仓库基于 Lucas Maes 等人发布的 LeWorldModel 官方实现。

官方仓库：

https://github.com/lucas-maes/le-wm

LeWM 的模型设计、官方实现、预训练模型以及 benchmark 结果请以官方项目为准。

## License

LeWM 官方代码使用 MIT License。

本仓库保留原始版权声明与 LICENSE 文件。