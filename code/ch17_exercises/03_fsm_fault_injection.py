"""第17章 练习3：技能有限状态机（FSM）、故障注入与恢复

一个低成本“移液—显色—光谱”工作站连续处理样品。每个样品由若干“技能”串成：
  取枪头 → 吸液 → 分液 → 体积核验 → 等待显色 → 测量 → 质控 → 回传结果
每个技能都写明前置条件（pre）和后置条件（post）；后置条件不满足就进入恢复分支。

我们向仿真硬件注入 5 类故障，比较两种控制器：
  naive   ：只发命令、不核验后置条件；超时就“再发一次”；不做参比质控
  robust  ：核验后置条件；带命令编号的幂等重试；超时上限；参比质控；不可恢复则进入安全态并请人接管

重点不是“谁跑得快”，而是“静默错误”（系统没报警、结果却错了）——它比停机更危险。

运行：python code/ch17_exercises/03_fsm_fault_injection.py
依赖：numpy
"""
import numpy as np

FAULT_RATE = {
    "气泡吸液不足": 0.04,     # 实际分液体积只有目标的 60–80%
    "应答丢失": 0.03,         # 泵已执行，但确认帧丢失（超时）
    "光谱仪通信超时": 0.03,   # 命令未执行
    "灯源漂移": 0.02,         # 此后读数系统偏移 5–10%，直到重新校准
    "枪头缺失": 0.02,         # 取枪头失败
    "溢出/漏液": 0.003,       # 液位传感器报警：不可自动恢复
    "显色剂分装失效": 0.01,   # 本样品显色不完全（约 70%）；两种控制器的传感器都看不到
}
TOL_VOLUME, TOL_REF = 0.05, 0.03
MAX_RETRY = 2


class Hardware:
    """仿真硬件：真实状态对控制器部分不可见。"""

    def __init__(self, rng):
        self.rng = rng
        self.lamp_bias = 0.0
        self.pump_counter = 0          # 泵内部计数器：带命令编号的查询接口可读取
        self.executed_ids = set()

    def fault(self, name):
        return self.rng.random() < FAULT_RATE[name]

    def pick_tip(self):
        return not self.fault("枪头缺失")

    def dispense(self, target, cmd_id, idempotent):
        """返回 (是否收到确认, 实际体积)。idempotent=True 时泵拒绝重复的命令编号。"""
        if idempotent and cmd_id in self.executed_ids:
            return True, 0.0
        vol = target * (self.rng.uniform(0.6, 0.8) if self.fault("气泡吸液不足") else 1.0)
        self.executed_ids.add(cmd_id)
        self.pump_counter += 1
        return (not self.fault("应答丢失")), vol

    def measure(self, true_a):
        if self.fault("光谱仪通信超时"):
            return None
        if self.fault("灯源漂移"):
            self.lamp_bias = self.rng.choice([-1, 1]) * self.rng.uniform(0.05, 0.10)
        return true_a * (1 + self.lamp_bias) + self.rng.normal(0, 0.003)

    def recalibrate(self):
        self.lamp_bias = 0.0

    def leak(self):
        return self.fault("溢出/漏液")


def run(controller, n_samples=1000, seed=17):
    rng = np.random.default_rng(seed)
    hw = Hardware(rng)
    robust = controller == "robust"
    stats = dict(valid=0, silent_wrong=0, flagged=0, human=0, safe=0, minutes=0.0)
    log, since_human, autonomy_runs = [], 0, []

    for k in range(n_samples):
        target = 50.0
        true_conc = rng.uniform(0.2, 1.0)            # 以“目标体积下的真实吸光度”表示
        reagent_ok = not hw.fault("显色剂分装失效")
        if not robust and k % 50 == 0:
            hw.recalibrate()                          # naive 只做固定周期校准（每 50 个样品）
        state, volume, retries, cmd = "取枪头", 0.0, 0, 0
        result, corrupted = None, False
        while state not in ("完成", "安全态"):
            stats["minutes"] += 0.5
            if state == "取枪头":
                if hw.pick_tip():
                    state = "分液"
                elif retries < MAX_RETRY:
                    retries += 1                      # 换一个枪头位置重试
                else:
                    state = "安全态"
                    log.append((k, "枪头连续缺失：请补充枪头盒"))
            elif state == "分液":
                if hw.leak():
                    state = "安全态"                 # 急停：关泵、断加热、报警
                    log.append((k, "液位报警：急停并等待人工"))
                    continue
                cmd += 1
                ack, v = hw.dispense(target - volume if robust else target, cmd_id=(k, cmd), idempotent=robust)
                volume += v
                if not ack:
                    if robust:
                        # 幂等重试：先读泵计数器/体积传感器，确认是否已执行，再决定是否补液
                        state = "体积核验"
                    else:
                        cmd += 1                     # naive：换新编号再发一次 → 可能重复分液
                        _, v2 = hw.dispense(target, cmd_id=(k, cmd), idempotent=False)
                        volume += v2
                        state = "等待显色"
                else:
                    state = "体积核验" if robust else "等待显色"
            elif state == "体积核验":
                err = (volume - target) / target
                if abs(err) <= TOL_VOLUME:
                    state, retries = "等待显色", 0
                elif err < 0 and retries < MAX_RETRY:
                    retries += 1
                    state = "分液"                   # 只补差额：分液动作对目标体积幂等
                else:
                    state = "安全态"
                    log.append((k, f"体积偏差 {err:+.0%} 无法修正：弃样"))
            elif state == "等待显色":
                stats["minutes"] += 5
                state = "测量"
            elif state == "测量":
                true_a = true_conc * volume / target * (1.0 if reagent_ok else 0.7)
                corrupted = abs(volume - target) / target > TOL_VOLUME
                reading = hw.measure(true_a)
                if reading is None:
                    if retries < MAX_RETRY:
                        retries += 1
                        stats["minutes"] += 1     # 超时等待后重连
                    else:
                        state = "安全态"
                        log.append((k, "光谱仪连续超时"))
                    continue
                result = reading * (target / volume if robust else 1.0)
                state = "质控" if robust else "完成"
            elif state == "质控":
                ref = hw.measure(0.500)               # 参比标准溶液
                if ref is None:
                    continue
                if abs(ref - 0.5) / 0.5 > TOL_REF:
                    hw.recalibrate()                  # 空白 + 标准重新校准后重测样品
                    stats["minutes"] += 3
                    retries += 1
                    state = "测量" if retries <= MAX_RETRY else "安全态"
                else:
                    state = "完成"

        if state == "安全态":
            stats["safe"] += 1
            stats["human"] += 1
            stats["flagged"] += 1
            stats["minutes"] += 15                    # 人工处理时间
            autonomy_runs.append(since_human)
            since_human = 0
            continue
        since_human += 1
        rel = abs(result - true_conc) / true_conc
        if rel > 0.05 or corrupted and not robust:
            stats["silent_wrong"] += 1                # 系统未报警但结果错误
        else:
            stats["valid"] += 1
    autonomy_runs.append(since_human)
    stats["mean_autonomy"] = float(np.mean(autonomy_runs))
    stats["throughput_per_h"] = n_samples / (stats["minutes"] / 60)
    return stats, log


if __name__ == "__main__":
    print("注入故障率：", ", ".join(f"{k} {v:.1%}" for k, v in FAULT_RATE.items()))
    names = {"valid": "有效结果", "silent_wrong": "静默错误(未报警)", "flagged": "已标记弃样",
             "human": "人工接管次数", "mean_autonomy": "平均连续自治样品数",
             "throughput_per_h": "吞吐(样品/小时)"}
    res = {c: run(c) for c in ("naive", "robust")}
    print("\n" + "指标".ljust(20) + "naive".ljust(14) + "robust")
    for key, label in names.items():
        a, b = res["naive"][0][key], res["robust"][0][key]
        fmt = (lambda x: f"{x:.1f}") if isinstance(a, float) else str
        print(label.ljust(20) + fmt(a).ljust(14) + fmt(b))
    print("\nrobust 控制器的前 5 条人工接管记录：")
    for k, msg in res["robust"][1][:5]:
        print(f"  样品 {k:4d}: {msg}")
    print("""
解读：
  · naive 看起来“从不停机、吞吐更高”，但气泡、应答丢失（重复分液）和灯源漂移都会变成
    没有报警的错误结果。下游的优化算法会把这些错误当成真实数据学习。
    它的“平均连续自治样品数”更高，恰恰是因为它不检查——自治时长必须与静默错误一起报告。
  · robust 用“后置条件核验 + 幂等补液 + 参比质控”把大多数故障转成可恢复事件，
    只把不可恢复的（漏液、耗材耗尽）交给人工；静默错误显著减少。
  · 自治能力的指标应当同时报告：有效结果、静默错误、人工接管间隔与吞吐，不能只报吞吐。""")
