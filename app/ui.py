"""
多 Agent 工作流系统 - Streamlit 界面
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))
from app import settings
from app.agents import ROLE_PROFILES, AgentRole

st.set_page_config(
    page_title="多 Agent 工作流系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .step-box { border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; margin: 10px 0; }
    .role-tag { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 0.85em; font-weight: bold; }
    .researcher { background: #e8eaf6; color: #283593; }
    .writer { background: #e0f2f1; color: #00695c; }
    .reviewer { background: #fff3e0; color: #e65100; }
    .coordinator { background: #f3e5f5; color: #6a1b9a; }
    .stApp { max-width: 1200px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

ROLE_COLORS = {
    "researcher": "researcher", "writer": "writer",
    "reviewer": "reviewer", "coordinator": "coordinator",
}

# 侧边栏
with st.sidebar:
    st.title("🤖 多 Agent 工作流")
    st.markdown("---")

    if settings.is_api_key_set:
        st.success("✅ API 已配置")
    else:
        st.warning("⚠️ 未配置 API Key")

    st.markdown("### Agent 角色")
    for role in AgentRole:
        profile = ROLE_PROFILES[role]
        color = ROLE_COLORS.get(role.value, "")
        st.markdown(
            f'<span class="role-tag {color}">{profile["name"]}</span> '
            f'<small>{profile["description"]}</small>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 工作流说明")
    st.markdown("""
    **标准工作流** 按以下顺序执行：
    1. 🔍 研究员 → 研究主题
    2. ✍️ 写手 → 撰写内容
    3. ✅ 审查员 → 审查改进
    4. 🎯 协调员 → 整合输出
    """)

# 主界面
st.title("📋 多 Agent 协作工作流")
st.markdown("让多个 AI Agent 角色协同完成复杂任务")

tab1, tab2 = st.tabs(["⭐ 标准工作流", "🔧 自定义工作流"])

with tab1:
    st.markdown("### 标准工作流")
    st.markdown("输入一个主题，4 个 Agent 角色协作完成：研究 → 撰写 → 审查 → 整合")

    topic = st.text_input(
        "输入工作流主题",
        placeholder="例如：AI Agent 在电商领域的应用前景",
        key="standard_topic",
    )

    if st.button("🚀 启动标准工作流", type="primary", use_container_width=True):
        if not topic.strip():
            st.error("请输入主题")
        else:
            with st.spinner("4 个 Agent 正在协作中..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/workflow/standard",
                        json={"topic": topic, "workflow_type": "standard"},
                        timeout=300,
                    )

                    if resp.status_code == 200:
                        result = resp.json()
                        st.success(result["summary"])

                        # 显示各步骤
                        st.markdown("### 🔄 执行步骤")
                        for step in result["steps"]:
                            s = step["step"]
                            agent = step["agent"]
                            output = step["output"]

                            st.markdown(
                                f'<div class="step-box">'
                                f'<strong>Step {s}: {agent}</strong><br>'
                                f'<small>{output}</small>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                        # 最终输出
                        st.markdown("### 📄 最终输出")
                        st.markdown(result["final_output"])
                    else:
                        st.error(f"失败: {resp.text}")

                except requests.exceptions.ConnectionError:
                    st.error("无法连接 API 服务")
                except Exception as e:
                    st.error(f"错误: {str(e)}")

with tab2:
    st.markdown("### 自定义工作流")
    st.markdown("自由组合 Agent 角色，定义自己的任务流水线")

    num_tasks = st.number_input("任务数量", 1, 6, 2, key="num_tasks")

    custom_tasks = []
    for i in range(num_tasks):
        st.markdown(f"#### 任务 {i+1}")
        col1, col2 = st.columns([1, 2])

        with col1:
            role = st.selectbox(
                "Agent 角色",
                options=["researcher", "writer", "reviewer", "coordinator"],
                index=i % 4,
                key=f"role_{i}",
                format_func=lambda r: ROLE_PROFILES[AgentRole(r)]["name"],
            )

        with col2:
            title = st.text_input(f"任务标题 {i+1}", f"任务{i+1}", key=f"title_{i}")
            desc = st.text_area(
                f"任务描述 {i+1}",
                height=80,
                key=f"desc_{i}",
                placeholder="描述这个任务需要做什么...",
            )
            custom_tasks.append({"title": title, "description": desc, "role": role})

        st.markdown("---")

    if st.button("🚀 启动自定义工作流", type="primary", use_container_width=True):
        valid_tasks = [t for t in custom_tasks if t["description"].strip()]
        if not valid_tasks:
            st.error("请至少填写一个有效任务")
        else:
            with st.spinner(f"{len(valid_tasks)} 个 Agent 正在协作..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/workflow/custom",
                        json={"tasks": valid_tasks},
                        timeout=300,
                    )

                    if resp.status_code == 200:
                        result = resp.json()
                        st.success(result["summary"])

                        for step in result["steps"]:
                            st.markdown(
                                f'<div class="step-box">'
                                f'<strong>Step {step["step"]}: {step["agent"]}</strong>'
                                f' — {step.get("task", "")}<br>'
                                f'<small>{step["output"]}</small>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                        st.markdown("### 📄 最终输出")
                        st.markdown(result["final_output"])
                    else:
                        st.error(f"失败: {resp.text}")

                except requests.exceptions.ConnectionError:
                    st.error("无法连接 API 服务")
                except Exception as e:
                    st.error(f"错误: {str(e)}")

st.markdown("---")
st.caption("💡 选择一个工作流模式，输入任务主题后启动")
