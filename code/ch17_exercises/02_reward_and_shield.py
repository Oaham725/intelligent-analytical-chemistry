"""第17章 练习2：奖励设计、奖励投机与安全屏蔽器（shield）

情境：铁(II)–邻二氮菲显色（510 nm），样品铁浓度 C 未知（1–12 mg/L，仿真内部真值）。
智能体只能看到“自己做过什么”和“读到的吸光度”，看不到 C，因此这是部分可观测问题；
我们用“有限记忆观测”（动作计数 + 最近读数分箱 + 读数趋势）把它近似为表格型 MDP，
再用 Q-learning 在仿真器里训练。

比较三种设置：
  A  奖励 = 报告时的吸光度（“信号越强越好”）         —— 奖励投机的典型例子
  B  奖励 = 报告浓度的相对误差（仿真中可得真值）     —— 与分析目标对齐
  C  B + 安全屏蔽器：执行前拦截会导致孔板溢出的动作  —— 约束探索

运行：python code/ch17_exercises/02_reward_and_shield.py   （约 20–40 s）
依赖：numpy
"""
from collections import defaultdict

import numpy as np

# ---------------------------------------------------------------- 仿真器参数
V_SAMPLE, V_DOSE, V_DIL, V_MAX = 100, 50, 100, 400     # µL；V_MAX 为孔的安全容量
K_S = 0.30            # 完全显色、未额外稀释时每 mg/L 的吸光度（以 100 µL 样品计）
CAP_PER_DOSE = 5.0    # 每份显色剂可完全络合的样品铁浓度上限 (mg/L)
STRAY = 0.005         # 杂散光比例：高吸光度区读数被压低（非线性）
K_DEV = 0.90          # 每个等待步的显色速率常数（1−e^{-0.9n}：5 步后约 99%）
ACTIONS = ("加试剂", "等待", "稀释", "测量", "报告")
STEP_COST = {"加试剂": -0.3, "等待": -0.3, "稀释": -0.3, "测量": -0.2}
MAX_STEPS = 25


class ColorimetricWell:
    def __init__(self, rng):
        self.rng = rng

    def reset(self):
        self.C = self.rng.uniform(1.0, 12.0)
        self.adds = self.dils = self.waits = 0
        self.dev = 0.0
        self.readings = []
        self.steps = 0
        return self.obs()

    @property
    def volume(self):
        return V_SAMPLE + V_DOSE * self.adds + V_DIL * self.dils

    def volume_after(self, a):
        return self.volume + {"加试剂": V_DOSE, "稀释": V_DIL}.get(a, 0)

    def true_absorbance(self):
        complexed = min(1.0, CAP_PER_DOSE * self.adds / self.C)   # 试剂不足 → 只有部分铁显色
        return K_S * self.C * (V_SAMPLE / self.volume) * complexed * self.dev

    def read(self):
        A = self.true_absorbance()
        T = (10 ** -A + STRAY) / (1 + STRAY)                      # 杂散光造成的负偏差
        noise = 0.002 * 10 ** min(A, 2.5)                          # 高吸光度区噪声放大
        return float(-np.log10(T) + self.rng.normal(0, noise))

    def obs(self):
        last = self.readings[-1] if self.readings else None
        if last is None:
            a_bin = 0
        else:
            a_bin = 1 + int(np.digitize(last, [0.1, 0.4, 0.8, 1.2]))  # 1..5
        if len(self.readings) < 2:
            trend = 0
        else:
            trend = 1 if self.readings[-1] - self.readings[-2] > 0.02 * max(self.readings[-2], 0.05) else 2
        return (self.adds, min(self.waits, 6), self.dils, a_bin, trend)

    def step(self, a):
        """返回 obs, 即时奖励（不含任务奖励）, done, info。"""
        self.steps += 1
        info = {}
        if a in ("加试剂", "稀释") and self.volume_after(a) > V_MAX:
            info["overflow"] = True                                  # 安全事件：溢出、试剂外泄
            return self.obs(), -20.0, True, info
        if a == "加试剂":
            self.adds = min(self.adds + 1, 3)
        elif a == "稀释":
            self.dils = min(self.dils + 1, 2)
        elif a == "等待":
            self.waits += 1
            self.dev = 1 - (1 - self.dev) * np.exp(-K_DEV)
        elif a == "测量":
            self.readings.append(self.read())
        elif a == "报告":
            info["report"] = True
            return self.obs(), 0.0, True, info
        done = self.steps >= MAX_STEPS
        return self.obs(), STEP_COST[a] + (-5.0 if done else 0.0), done, info

    def estimate(self):
        if not self.readings:
            return 0.0
        return self.readings[-1] * self.volume / (V_SAMPLE * K_S)   # 按完全显色、线性响应换算


def task_reward(env, kind):
    if kind == "signal":
        return 4.0 * (env.readings[-1] if env.readings else 0.0)
    rel = abs(env.estimate() - env.C) / env.C
    return 10.0 - 40.0 * min(rel, 1.0)


def shield(env, a):
    """安全屏蔽器：只拦截“会导致硬约束违例”的动作，不替智能体做科学决策。"""
    return not (a in ("加试剂", "稀释") and env.volume_after(a) > V_MAX)


def run(kind, use_shield, episodes=60000, seed=1):
    rng = np.random.default_rng(seed)
    env = ColorimetricWell(rng)
    Q = defaultdict(lambda: np.zeros(len(ACTIONS)))
    overflow_train = 0
    for ep in range(episodes):
        eps = max(0.05, 1.0 - ep / (0.6 * episodes))
        s, done = env.reset(), False
        while not done:
            allowed = [i for i, a in enumerate(ACTIONS) if not use_shield or shield(env, a)]
            if rng.random() < eps:
                ai = int(rng.choice(allowed))
            else:
                ai = max(allowed, key=lambda i: Q[s][i])
            s2, r, done, info = env.step(ACTIONS[ai])
            overflow_train += info.get("overflow", False)
            if info.get("report"):
                r += task_reward(env, kind)
            target = r if done else r + 0.98 * np.max(Q[s2])
            Q[s][ai] += 0.1 * (target - Q[s][ai])
            s = s2
    return Q, overflow_train


def evaluate(Q, use_shield, n=3000, seed=99):
    rng = np.random.default_rng(seed)
    env = ColorimetricWell(rng)
    errs, steps, high_a, overflow, reagent, C_all = [], [], 0, 0, [], []
    for _ in range(n):
        s, done = env.reset(), False
        while not done:
            allowed = [i for i, a in enumerate(ACTIONS) if not use_shield or shield(env, a)]
            ai = max(allowed, key=lambda i: Q[s][i])
            s, _, done, info = env.step(ACTIONS[ai])
            overflow += info.get("overflow", False)
        rel = abs(env.estimate() - env.C) / env.C
        errs.append(rel)
        C_all.append(env.C)
        steps.append(env.steps)
        reagent.append(env.adds)
        high_a += bool(env.readings) and env.readings[-1] > 1.2
    errs, C_all = np.array(errs), np.array(C_all)
    return {
        "中位相对误差": np.median(errs),
        "|误差|<5% 比例": np.mean(errs < 0.05),
        "高浓度(>8)中位误差": np.median(errs[C_all > 8]),
        "报告时 A>1.2 比例": high_a / n,
        "平均步数": np.mean(steps),
        "平均试剂份数": np.mean(reagent),
        "测试期溢出": overflow,
    }


if __name__ == "__main__":
    settings = [("A 信号奖励", "signal", False), ("B 误差奖励", "accuracy", False),
                ("C 误差奖励+屏蔽器", "accuracy", True)]
    rows = []
    for name, kind, sh in settings:
        Q, ov = run(kind, sh)
        m = evaluate(Q, sh)
        m["训练期溢出"] = ov
        rows.append((name, m))
        print(f"完成 {name}")
    keys = list(rows[0][1].keys())
    print("\n" + "指标".ljust(16) + "".join(n.ljust(20) for n, _ in rows))
    for k in keys:
        line = k.ljust(16)
        for _, m in rows:
            v = m[k]
            line += (f"{v:.1%}" if isinstance(v, float) and v <= 1 and "步" not in k and "份" not in k
                     else f"{v:.2f}" if isinstance(v, float) else str(v)).ljust(20)
        print(line)
    print("""
解读（固定随机种子下的典型结果，换种子时数值会波动，结论不变）：
  · A 把“报告时吸光度大”当成目标。它学到的是：只加 1 份试剂、等几步、立即报告——
    高浓度样品显色剂不足，部分铁没有络合，读数“看起来不低”却系统性偏低，误差约 30%。
    这就是奖励投机（reward hacking）：代理指标（信号强度）被优化，分析目标（准确浓度）被牺牲。
  · B 的奖励直接写成浓度相对误差，策略学会加足试剂、等到读数稳定、过高时稀释。
    但它是靠“试错”学会溢出不好的——训练期溢出次数就是探索的物理代价。
  · C 在执行层用屏蔽器拦截会溢出的动作：训练期溢出降为 0，最终精度接近 B。
    屏蔽器缩小了动作集合，也可能挡住少数高收益路径（例如加满 3 份试剂再连续稀释），
    所以 C 对最高浓度样品的误差略大。这是“安全约束有代价”的真实体现，而不是屏蔽器失败。
  · 误差奖励依赖仿真中的真值；真实实验室只能用标准物质/参比方法近似它（见17.3、17.4）。""")
