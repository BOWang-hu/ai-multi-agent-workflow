"""
多 Agent 工作流系统 - Agent 定义
实现多个专业 Agent 的协作工作流
"""
from __future__ import annotations

import json
import logging
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app import settings

logger = logging.getLogger(__name__)


# ===== Agent 角色定义 =====

class AgentRole(str, Enum):
    """Agent 角色枚举"""
    RESEARCHER = "researcher"      # 研究员 - 收集和分析信息
    WRITER = "writer"              # 写手 - 撰写内容
    REVIEWER = "reviewer"          # 审查员 - 审查和改进内容
    COORDINATOR = "coordinator"    # 协调员 - 统筹协调


ROLE_PROFILES = {
    AgentRole.RESEARCHER: {
        "name": "研究员 (Researcher)",
        "description": "擅长信息收集、分析和整理",
        "prompt": """你是一个专业的研究员 Agent。你的职责是：
1. 深入研究用户提出的主题
2. 收集关键信息、数据、事实
3. 分析不同角度和观点
4. 输出结构化的研究报告

请对以下任务进行深入研究，输出包含：主要发现、关键数据、不同观点、信息来源。""",
    },
    AgentRole.WRITER: {
        "name": "写手 (Writer)",
        "description": "擅长内容创作和表达",
        "prompt": """你是一个专业的写手 Agent。你的职责是：
1. 基于研究材料编写优质内容
2. 确保内容结构清晰、逻辑连贯
3. 使用适当的语言风格和表达方式
4. 输出最终可交付的内容

请基于以下研究结果，编写高质量的内容。注意语言的流畅性和可读性。""",
    },
    AgentRole.REVIEWER: {
        "name": "审查员 (Reviewer)",
        "description": "擅长质量审查和改进建议",
        "prompt": """你是一个专业的审查员 Agent。你的职责是：
1. 审查内容的准确性、完整性
2. 检查逻辑漏洞和错误
3. 提出具体的改进建议
4. 评估内容质量并打分（1-10）

请审查以下内容，输出审查意见，包括：优点、问题、改进建议、质量评分。""",
    },
    AgentRole.COORDINATOR: {
        "name": "协调员 (Coordinator)",
        "description": "擅长任务分解和流程管理",
        "prompt": """你是一个专业的协调员 Agent。你的职责是：
1. 将复杂任务分解为子任务
2. 分配任务给合适的 Agent
3. 整合多个 Agent 的输出
4. 确保最终结果满足用户需求

作为协调员，请根据用户需求和各 Agent 的输出，生成最终的综合报告。""",
    },
}


# ===== 任务定义 =====

@dataclass
class Task:
    """工作流任务"""
    title: str
    description: str
    assigned_role: AgentRole
    input_data: str = ""
    output: str = ""
    status: str = "pending"  # pending, running, completed, failed


@dataclass
class WorkflowResult:
    """工作流执行结果"""
    task_title: str
    final_output: str
    steps: list[dict]
    status: str  # success, partial, failed
    summary: str


# ===== Agent 执行器 =====

class AgentExecutor:
    """单个 Agent 执行器"""

    def __init__(self, role: AgentRole):
        self.role = role
        profile = ROLE_PROFILES[role]
        self.name = profile["name"]

    async def execute(self, task_description: str, context: str = "") -> str:
        """执行任务"""
        if not settings.is_api_key_set:
            return f"[{self.name} 模拟输出] 关于「{task_description[:30]}...」的分析结果。请配置 API Key。"

        try:
            llm = ChatOpenAI(
                model=settings.openai_model_name,
                temperature=0.7,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )

            profile = ROLE_PROFILES[self.role]
            system_prompt = profile["prompt"]

            if context:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    ("human", "## 上下文/研究材料\n{context}\n\n## 任务\n{task}"),
                ])
            else:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    ("human", "## 任务\n{task}"),
                ])

            chain = prompt | llm | StrOutputParser()
            result = await chain.ainvoke({"task": task_description, "context": context})

            return result

        except Exception as e:
            logger.error(f"Agent {self.name} 执行失败: {e}")
            return f"[{self.name} 执行出错] {str(e)}"


# ===== 工作流引擎 =====

class WorkflowEngine:
    """多 Agent 工作流引擎"""

    def __init__(self):
        self.agents = {
            AgentRole.RESEARCHER: AgentExecutor(AgentRole.RESEARCHER),
            AgentRole.WRITER: AgentExecutor(AgentRole.WRITER),
            AgentRole.REVIEWER: AgentExecutor(AgentRole.REVIEWER),
            AgentRole.COORDINATOR: AgentExecutor(AgentRole.COORDINATOR),
        }

    async def run_standard_workflow(self, topic: str) -> WorkflowResult:
        """运行标准工作流: 研究 → 撰写 → 审查 → 协调输出"""
        steps = []
        logger.info(f"开始标准工作流，主题: {topic}")

        # Step 1: 研究
        logger.info("Step 1: 研究员工作中...")
        research_result = await self.agents[AgentRole.RESEARCHER].execute(
            f"研究以下主题：{topic}\n请提供详细的研究报告，包括背景、现状、关键数据和趋势。"
        )
        steps.append({
            "step": 1,
            "agent": "研究员",
            "output": research_result[:200] + "..." if len(research_result) > 200 else research_result,
        })

        # Step 2: 撰写
        logger.info("Step 2: 写手工作中...")
        writer_result = await self.agents[AgentRole.WRITER].execute(
            f"基于研究材料撰写关于「{topic}」的优质内容",
            context=research_result,
        )
        steps.append({
            "step": 2,
            "agent": "写手",
            "output": writer_result[:200] + "..." if len(writer_result) > 200 else writer_result,
        })

        # Step 3: 审查
        logger.info("Step 3: 审查员工作中...")
        review_result = await self.agents[AgentRole.REVIEWER].execute(
            f"审查以下关于「{topic}」的内容，提供改进建议",
            context=writer_result,
        )
        steps.append({
            "step": 3,
            "agent": "审查员",
            "output": review_result[:200] + "..." if len(review_result) > 200 else review_result,
        })

        # Step 4: 协调输出
        logger.info("Step 4: 协调员整合中...")
        coordinator_input = f"""
## 原始任务
{topic}

## 研究报告
{research_result}

## 撰写内容
{writer_result}

## 审查意见
{review_result}
"""
        final_output = await self.agents[AgentRole.COORDINATOR].execute(
            f"整合所有 Agent 的输出，生成关于「{topic}」的最终版本",
            context=coordinator_input,
        )
        steps.append({
            "step": 4,
            "agent": "协调员",
            "output": final_output[:200] + "..." if len(final_output) > 200 else final_output,
        })

        summary = f"工作流完成！4 个 Agent 协作处理了「{topic}」，最终输出已生成。"

        return WorkflowResult(
            task_title=topic,
            final_output=final_output,
            steps=steps,
            status="success",
            summary=summary,
        )

    async def run_custom_workflow(self, tasks: list[Task]) -> WorkflowResult:
        """运行自定义工作流"""
        steps = []
        previous_output = ""

        for i, task in enumerate(tasks):
            logger.info(f"Step {i+1}: {task.assigned_role.value} 工作中...")
            agent = self.agents[task.assigned_role]

            result = await agent.execute(
                task.description,
                context=task.input_data or previous_output,
            )

            task.output = result
            task.status = "completed"

            steps.append({
                "step": i + 1,
                "agent": ROLE_PROFILES[task.assigned_role]["name"],
                "task": task.title,
                "output": result[:200] + "..." if len(result) > 200 else result,
            })

            previous_output = result

        # 最后协调员整合
        if tasks:
            coordinator = self.agents[AgentRole.COORDINATOR]
            all_outputs = "\n\n".join([
                f"## Step {i+1}: {t.title}\n{t.output}"
                for i, t in enumerate(tasks)
            ])
            final = await coordinator.execute(
                "整合所有步骤的输出，生成最终报告",
                context=all_outputs,
            )

            steps.append({
                "step": len(tasks) + 1,
                "agent": "协调员",
                "task": "最终整合",
                "output": final[:200] + "..." if len(final) > 200 else final,
            })
        else:
            final = "无任务执行"

        return WorkflowResult(
            task_title="自定义工作流",
            final_output=final,
            steps=steps,
            status="success",
            summary=f"自定义工作流完成！共执行 {len(tasks)} 个任务。",
        )


# 全局引擎
_engine: Optional[WorkflowEngine] = None


def get_engine() -> WorkflowEngine:
    global _engine
    if _engine is None:
        _engine = WorkflowEngine()
    return _engine
