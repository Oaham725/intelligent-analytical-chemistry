"""第17章 代码实践入口：实验决策、强化学习与具身自主实验室

依次运行本章三个练习（均只依赖 numpy）：
  01_colorimetric_mdp.py      状态—动作—奖励建模、值迭代、闭环 vs 开环
  02_reward_and_shield.py     奖励投机、Q-learning、安全屏蔽器
  03_fsm_fault_injection.py   技能状态机、幂等重试、故障注入与静默错误

运行：python code/ch17.py            （全部，约 30 s）
      python code/ch17.py 1 3        （只运行练习 1 和 3）
"""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent / "ch17_exercises"
SCRIPTS = {
    "1": "01_colorimetric_mdp.py",
    "2": "02_reward_and_shield.py",
    "3": "03_fsm_fault_injection.py",
}

if __name__ == "__main__":
    chosen = sys.argv[1:] or list(SCRIPTS)
    for key in chosen:
        name = SCRIPTS[key]
        print("\n" + "#" * 72 + f"\n# 练习 {key}: {name}\n" + "#" * 72)
        runpy.run_path(str(HERE / name), run_name="__main__")
