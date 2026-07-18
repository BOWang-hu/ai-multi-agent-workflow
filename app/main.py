"""
多 Agent 工作流系统 - FastAPI 主入口
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import settings
from app.agents import get_engine, AgentRole, Task

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ===== 数据模型 =====

class WorkflowRequest(BaseModel):
    topic: str
    workflow_type: str = "standard"  # standard / custom


class TaskDef(BaseModel):
    title: str
    description: str
    role: str  # researcher / writer / reviewer / coordinator


class CustomWorkflowRequest(BaseModel):
    tasks: list[TaskDef]


class StepInfo(BaseModel):
    step: int
    agent: str
    task: str = ""
    output: str


class WorkflowResponse(BaseModel):
    task_title: str
    final_output: str
    steps: list[dict]
    status: str
    summary: str
    error: str | None = None


class HealthResponse(BaseModel):
    status: str
    api_key_configured: bool
    version: str = "1.0.0"


# ===== 生命周期 =====

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🤖 多 Agent 工作流系统启动中...")
    if not settings.is_api_key_set:
        logger.warning("⚠️ OPENAI_API_KEY 未配置")
    yield
    logger.info("👋 多 Agent 工作流系统已关闭")


# ===== 应用 =====

app = FastAPI(
    title="多 Agent 工作流系统 API",
    description="多 Agent 协作工作流引擎，支持研究员、写手、审查员、协调员角色",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


# ===== 路由 =====

@app.get("/health", response_model=HealthResponse, tags=["系统"])
async def health_check():
    return HealthResponse(status="ok", api_key_configured=settings.is_api_key_set)


@app.post("/workflow/standard", response_model=WorkflowResponse, tags=["工作流"])
async def standard_workflow(request: WorkflowRequest):
    """运行标准工作流: 研究 → 撰写 → 审查 → 整合"""
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="主题不能为空")

    engine = get_engine()
    try:
        result = await engine.run_standard_workflow(request.topic)
        return WorkflowResponse(
            task_title=result.task_title,
            final_output=result.final_output,
            steps=result.steps,
            status=result.status,
            summary=result.summary,
        )
    except Exception as e:
        logger.error(f"工作流执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflow/custom", response_model=WorkflowResponse, tags=["工作流"])
async def custom_workflow(request: CustomWorkflowRequest):
    """运行自定义工作流"""
    if not request.tasks:
        raise HTTPException(status_code=400, detail="请提供至少一个任务")

    role_map = {
        "researcher": AgentRole.RESEARCHER,
        "writer": AgentRole.WRITER,
        "reviewer": AgentRole.REVIEWER,
        "coordinator": AgentRole.COORDINATOR,
    }

    tasks = []
    for t in request.tasks:
        role = role_map.get(t.role)
        if role is None:
            raise HTTPException(status_code=400, detail=f"无效的角色: {t.role}")
        tasks.append(Task(title=t.title, description=t.description, assigned_role=role))

    engine = get_engine()
    try:
        result = await engine.run_custom_workflow(tasks)
        return WorkflowResponse(
            task_title=result.task_title,
            final_output=result.final_output,
            steps=result.steps,
            status=result.status,
            summary=result.summary,
        )
    except Exception as e:
        logger.error(f"自定义工作流执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port, reload=True)
