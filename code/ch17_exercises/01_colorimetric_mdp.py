"""第17章 练习1：把“移液—显色—测量”写成马尔可夫决策过程（MDP）

问题：铁(II)–邻二氮菲显色法（510 nm）测定未知样品中的铁。操作者（或智能体）
每一步只能选择一个动作：加一份显色剂、等待显色、稀释、读数报告。
这一问题为什么是“连续决策”而不是“一次性优化”？
  1. 加入的试剂、已经过去的时间和是否稀释会留在状态里，影响以后哪些动作有效；
  2. 加试剂、稀释不可撤销；
  3. 只有在“报告”时才知道结果是否可信，奖励是延迟的。

本程序做三件事：
  (a) 显式写出状态 S、动作 A、转移 P、奖励 R、折扣 γ；
  (b) 用值迭代求最优闭环策略 π*(s)，打印关键状态下的 Q 值；
  (c) 与“一次性优化”的固定流程（开环协议）比较期望回报和报告正确率。

运行：python code/ch17_exercises/01_colorimetric_mdp.py
依赖：numpy
所有参数为教学用的简化值，只用于说明决策结构，不能代替真实方法验证。
"""
from itertools import product

import numpy as np

# ---------------------------------------------------------------- 1. MDP 定义
CONC = ("低", "高")             # 样品浓度等级：高浓度显色后 A>1，超出线性范围，需稀释
NEED = {"低": 1, "高": 2}       # 达到邻二氮菲过量（>=3:1）所需的显色剂份数
ACTIONS = ("加试剂", "等待", "稀释", "报告")
GAMMA = 0.95
P_DEVELOP = 0.75                # 试剂充足时，每个等待步显色推进一级的概率

COST = {"加试剂": -0.4, "等待": -0.6, "稀释": -1.0}   # 试剂/时间/样品消耗
R_GOOD, R_BAD = 10.0, -10.0
INVALID = -2.0                  # 不可执行动作（如第4次加试剂、重复稀释）

# 状态 s = (c, r, d, u)
#   c 浓度等级（本练习假设已由快速预读获得，故可观测）
#   r 已加试剂份数 0..3；d 显色进度 0=未显色,1=部分,2=完全；u 是否已稀释
#   "END" 为吸收终止态
STATES = [s for s in product(CONC, range(4), range(3), range(2))] + ["END"]
IDX = {s: i for i, s in enumerate(STATES)}


def report_ok(s):
    c, r, d, u = s
    return r >= NEED[c] and d == 2 and (c == "低" or u == 1)


def transitions(s, a):
    """返回 [(概率, 下一状态, 即时奖励), ...]。"""
    if s == "END":
        return [(1.0, "END", 0.0)]
    c, r, d, u = s
    if a == "报告":
        return [(1.0, "END", R_GOOD if report_ok(s) else R_BAD)]
    if a == "加试剂":
        if r == 3:
            return [(1.0, s, INVALID)]
        return [(1.0, (c, r + 1, d, u), COST[a])]
    if a == "稀释":
        if u == 1:
            return [(1.0, s, INVALID)]
        return [(1.0, (c, r, d, 1), COST[a])]
    # 等待：试剂充足才能完全显色；试剂不足最多“部分显色”
    if r == 0:
        return [(1.0, s, COST[a])]
    cap = 2 if r >= NEED[c] else 1
    if d >= cap:
        return [(1.0, s, COST[a])]
    return [(P_DEVELOP, (c, r, d + 1, u), COST[a]), (1 - P_DEVELOP, s, COST[a])]


# ---------------------------------------------------------------- 2. 值迭代
def value_iteration(gamma=GAMMA, tol=1e-10):
    V = np.zeros(len(STATES))
    while True:
        Q = np.array([[sum(p * (rew + gamma * V[IDX[s2]]) for p, s2, rew in transitions(s, a))
                       for a in ACTIONS] for s in STATES])
        V_new = Q.max(axis=1)
        if np.max(np.abs(V_new - V)) < tol:
            return V_new, Q
        V = V_new


V, Q = value_iteration()
policy = {s: ACTIONS[int(np.argmax(Q[IDX[s]]))] for s in STATES if s != "END"}

print("=" * 68)
print("(1) 最优闭环策略：从初始状态出发的一条典型轨迹（显色以期望方式推进）")
for c in CONC:
    s, path = (c, 0, 0, 0), []
    for _ in range(12):
        a = policy[s]
        path.append(a)
        if a == "报告":
            break
        outs = transitions(s, a)
        s = max(outs, key=lambda o: o[0])[1]   # 取最可能的下一状态
    print(f"  浓度={c}: {' → '.join(path)}    V*(s0)={V[IDX[(c, 0, 0, 0)]]:.2f}")

print("\n(2) 关键状态的 Q 值：同一个“读数报告”动作，在不同状态下价值完全不同")
for s in [("高", 2, 2, 0), ("高", 2, 2, 1), ("高", 1, 1, 0), ("低", 1, 1, 0)]:
    q = ", ".join(f"{a}={Q[IDX[s]][i]:6.2f}" for i, a in enumerate(ACTIONS))
    print(f"  s=(c={s[0]}, r={s[1]}, d={s[2]}, u={s[3]}): {q}  → π*={policy[s]}")


# ---------------------------------------------------------------- 3. 与开环“一次性优化”比较
rng = np.random.default_rng(17)


def rollout_open_loop(protocol, c):
    """固定流程：按顺序执行动作列表，不看中间状态。"""
    s, G, disc = (c, 0, 0, 0), 0.0, 1.0
    for a in protocol:
        outs = transitions(s, a)
        k = rng.choice(len(outs), p=[o[0] for o in outs])
        _, s, rew = outs[k]
        G += disc * rew
        disc *= GAMMA
        if s == "END":
            return G, rew == R_GOOD
    return G, False


def rollout_policy(c, max_steps=40):
    s, G, disc = (c, 0, 0, 0), 0.0, 1.0
    for _ in range(max_steps):
        outs = transitions(s, policy[s])
        k = rng.choice(len(outs), p=[o[0] for o in outs])
        _, s, rew = outs[k]
        G += disc * rew
        disc *= GAMMA
        if s == "END":
            return G, rew == R_GOOD
    return G, False


def evaluate(fn, conc_prior, n=4000):
    G, ok = [], []
    for _ in range(n):
        c = rng.choice(CONC, p=conc_prior)
        g, good = fn(c)
        G.append(g)
        ok.append(good)
    return float(np.mean(G)), float(np.mean(ok))


candidates = []
for n_add, n_wait, dil in product(range(4), range(9), range(2)):
    proto = ["加试剂"] * n_add + ["等待"] * n_wait + ["稀释"] * dil + ["报告"]
    candidates.append(proto)

print("\n(3) 闭环策略 vs. 开环固定流程（样品浓度先验：低 50%，高 50%）")
prior = [0.5, 0.5]
best_open = max(candidates, key=lambda p: evaluate(lambda c: rollout_open_loop(p, c), prior, 600)[0])
g_open, ok_open = evaluate(lambda c: rollout_open_loop(best_open, c), prior)
g_closed, ok_closed = evaluate(rollout_policy, prior)
print(f"  最佳开环流程: {'→'.join(best_open)}")
print(f"    期望折扣回报={g_open:6.2f}   报告正确率={ok_open:.1%}")
print(f"  最优闭环策略: 期望折扣回报={g_closed:6.2f}   报告正确率={ok_closed:.1%}")
print("  解读：开环流程必须为“最坏的样品 + 最慢的显色”预留试剂和等待步，")
print("        闭环策略依据 (c, d) 决定是否继续等待或稀释，因而更省且更可靠。")

print("\n(4) 折扣因子 γ 与错误报告惩罚共同决定“是否值得等下去”（高浓度样品）")


def greedy_path(Qm, c="高"):
    pol = {st: ACTIONS[int(np.argmax(Qm[IDX[st]]))] for st in STATES if st != "END"}
    st, path = (c, 0, 0, 0), []
    for _ in range(12):
        a = pol[st]
        path.append(a)
        if a == "报告":
            break
        st = max(transitions(st, a), key=lambda o: o[0])[1]
    return "→".join(path)


for r_bad in (-10.0, 0.0):
    for g in (0.95, 0.60):
        R_BAD = r_bad
        Vg, Qg = value_iteration(gamma=g)
        print(f"  R_bad={r_bad:5.1f}, γ={g:.2f}: V*={Vg[IDX[('高', 0, 0, 0)]]:6.2f}  轨迹: {greedy_path(Qg)}")
R_BAD = -10.0
print("  解读：错误报告惩罚太轻、折扣太强时，最优策略是“不做实验直接报告”。")
print("        这不是算法错误，而是奖励函数没有表达分析结果错误的真实代价（见17.3）。")
